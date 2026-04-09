#!/usr/bin/env python3
"""
Разведчик — бот для сбора контактов.
Запуск: python3 scout.py <bot_id>
"""

import sys
import os
import time
import random
import sqlite3
import logging
from datetime import datetime

# Путь к БД
DB_PATH = os.path.join(os.path.dirname(__file__), '..', 'blogery.db')
LOG_PATH = os.path.join(os.path.dirname(__file__), '..', 'logs', 'scout.log')

# Логирование
os.makedirs(os.path.dirname(LOG_PATH), exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler(LOG_PATH, encoding='utf-8'),
        logging.StreamHandler(sys.stdout),
    ]
)
log = logging.getLogger(__name__)


def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def get_bot(bot_id):
    conn = get_db()
    row = conn.execute("SELECT * FROM bots WHERE id = ?", (bot_id,)).fetchone()
    conn.close()
    return dict(row) if row else None


def save_contact(data: dict):
    """Сохраняет контакт в БД. Если уже есть — пропускает."""
    conn = get_db()
    # Проверяем дубли по source_url
    if data.get('source_url'):
        exists = conn.execute(
            "SELECT id FROM contacts WHERE source_url = ?", (data['source_url'],)
        ).fetchone()
        if exists:
            conn.close()
            return False

    conn.execute("""
        INSERT INTO contacts (
            name, email, phone, telegram, contact_url,
            source_url, source_platform, source_name,
            topic, region, description, audience_size,
            entry_point, offer, status
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'новый')
    """, (
        data.get('name'), data.get('email'), data.get('phone'),
        data.get('telegram'), data.get('contact_url'),
        data.get('source_url'), data.get('source_platform'), data.get('source_name'),
        data.get('topic'), data.get('region'), data.get('description'),
        data.get('audience_size', 0),
        data.get('entry_point'), data.get('offer'),
    ))
    conn.commit()
    conn.close()
    return True


def update_bot_status(bot_id, status, found_count=None):
    conn = get_db()
    if found_count is not None:
        conn.execute(
            "UPDATE bots SET status=?, notes=COALESCE(notes,'') || ?, updated_at=CURRENT_TIMESTAMP WHERE id=?",
            (status, f"\n[{datetime.now().strftime('%d.%m %H:%M')}] Найдено: {found_count}", bot_id)
        )
    else:
        conn.execute(
            "UPDATE bots SET status=?, updated_at=CURRENT_TIMESTAMP WHERE id=?",
            (status, bot_id)
        )
    conn.commit()
    conn.close()


def random_delay(delay_min, delay_max):
    t = random.randint(int(delay_min), int(delay_max))
    log.info(f"  Пауза {t} сек...")
    time.sleep(t)


# ─── МОДУЛЬ: Telegram ─────────────────────────────────────────────────────────

def scout_telegram(bot, keywords, topics, regions, contact_types, entry_point, offer, daily_limit):
    """
    Поиск каналов и групп в Telegram по ключевым словам.
    Требует: telethon, API_ID, API_HASH, SESSION файл.
    """
    try:
        from telethon.sync import TelegramClient
        from telethon.tl.functions.contacts import SearchRequest
        from telethon.tl.types import InputPeerEmpty
    except ImportError:
        log.error("Telethon не установлен. Выполни: pip3 install telethon")
        return 0

    # API данные берём из токена бота: формат "api_id:api_hash:phone"
    account = bot.get('account', '')
    parts = account.split(':')
    if len(parts) < 3:
        log.error("Неверный формат токена для Telegram. Нужно: api_id:api_hash:phone")
        return 0

    api_id = int(parts[0])
    api_hash = parts[1]
    phone = parts[2]
    session_file = os.path.join(os.path.dirname(__file__), '..', 'sessions', f'tg_{bot["id"]}')
    os.makedirs(os.path.dirname(session_file), exist_ok=True)

    found = 0
    kw_list = [k.strip() for k in keywords.split(',') if k.strip()]
    topic = topics.split(',')[0].strip() if topics else ''
    region = regions.split(',')[0].strip() if regions else ''

    log.info(f"Telegram: ищем по словам: {kw_list}")

    with TelegramClient(session_file, api_id, api_hash) as client:
        client.start(phone=phone)

        for keyword in kw_list[:daily_limit]:
            try:
                log.info(f"  Поиск: '{keyword}'")
                result = client(SearchRequest(
                    q=keyword,
                    limit=20,
                    peer=InputPeerEmpty()
                ))

                for chat in result.chats:
                    try:
                        title = getattr(chat, 'title', '') or ''
                        username = getattr(chat, 'username', '') or ''
                        participants = getattr(chat, 'participants_count', 0) or 0

                        if not title:
                            continue

                        contact_url = f"https://t.me/{username}" if username else None
                        source_url = contact_url

                        # Извлекаем email из описания если доступен
                        email = None
                        description = ''
                        try:
                            full = client.get_entity(chat.id)
                            if hasattr(full, 'about'):
                                description = full.about or ''
                                # Простой поиск email в описании
                                import re
                                emails = re.findall(r'[\w.+-]+@[\w-]+\.[\w.]+', description)
                                if emails:
                                    email = emails[0]
                        except Exception:
                            pass

                        saved = save_contact({
                            'name': title,
                            'email': email,
                            'telegram': f"@{username}" if username else None,
                            'contact_url': contact_url,
                            'source_url': source_url,
                            'source_platform': 'Telegram',
                            'source_name': title,
                            'topic': topic,
                            'region': region,
                            'description': description[:300],
                            'audience_size': participants,
                            'entry_point': entry_point,
                            'offer': offer,
                        })

                        if saved:
                            found += 1
                            log.info(f"  ✓ Найден: {title} (@{username}) — {participants} участников")

                    except Exception as e:
                        log.warning(f"  Ошибка обработки чата: {e}")

                random_delay(bot.get('delay_min', 30), bot.get('delay_max', 120))

            except Exception as e:
                log.error(f"  Ошибка поиска по '{keyword}': {e}")

    return found


# ─── МОДУЛЬ: ВКонтакте ────────────────────────────────────────────────────────

def scout_vk(bot, keywords, topics, regions, contact_types, entry_point, offer, daily_limit):
    """
    Поиск сообществ ВКонтакте через API.
    Требует: токен доступа VK (access_token).
    """
    try:
        import requests
    except ImportError:
        log.error("requests не установлен. Выполни: pip3 install requests")
        return 0

    access_token = bot.get('account', '')
    if not access_token:
        log.error("Токен VK не указан")
        return 0

    found = 0
    kw_list = [k.strip() for k in keywords.split(',') if k.strip()]
    topic = topics.split(',')[0].strip() if topics else ''
    region = regions.split(',')[0].strip() if regions else ''

    log.info(f"ВКонтакте: ищем по словам: {kw_list}")

    for keyword in kw_list[:daily_limit]:
        try:
            log.info(f"  Поиск: '{keyword}'")
            resp = requests.get('https://api.vk.com/method/groups.search', params={
                'q': keyword,
                'count': 20,
                'type': 'group,page,event',
                'access_token': access_token,
                'v': '5.131',
            }, timeout=10).json()

            if 'error' in resp:
                log.error(f"  VK API ошибка: {resp['error'].get('error_msg')}")
                break

            for group in resp.get('response', {}).get('items', []):
                name = group.get('name', '')
                screen_name = group.get('screen_name', '')
                members = group.get('members_count', 0)
                source_url = f"https://vk.com/{screen_name}"

                saved = save_contact({
                    'name': name,
                    'contact_url': source_url,
                    'source_url': source_url,
                    'source_platform': 'ВКонтакте',
                    'source_name': name,
                    'topic': topic,
                    'region': region,
                    'description': group.get('description', '')[:300],
                    'audience_size': members,
                    'entry_point': entry_point,
                    'offer': offer,
                })

                if saved:
                    found += 1
                    log.info(f"  ✓ Найден: {name} — {members} участников")

            random_delay(bot.get('delay_min', 5), bot.get('delay_max', 15))

        except Exception as e:
            log.error(f"  Ошибка поиска по '{keyword}': {e}")

    return found


# ─── МОДУЛЬ: Instagram ────────────────────────────────────────────────────────

def scout_instagram(bot, keywords, topics, regions, contact_types, entry_point, offer, daily_limit):
    """
    Поиск блогеров в Instagram по хэштегам.
    Токен формата: username:password
    """
    try:
        from instagrapi import Client
        from instagrapi.exceptions import LoginRequired, ChallengeRequired, BadPassword
    except ImportError:
        log.error("instagrapi не установлена. Выполни: pip3 install instagrapi")
        return 0

    account = bot.get('account', '')
    parts = account.split(':', 1)
    if len(parts) < 2:
        log.error("Неверный формат токена для Instagram. Нужно: username:password")
        return 0

    username, password = parts[0].strip(), parts[1].strip()
    session_path = os.path.join(os.path.dirname(__file__), '..', 'sessions', f'ig_{bot["id"]}.json')
    os.makedirs(os.path.dirname(session_path), exist_ok=True)

    import re

    cl = Client()
    cl.delay_range = [2, 5]  # задержка между запросами

    # Авторизация — пробуем загрузить сессию, иначе входим заново
    try:
        if os.path.exists(session_path):
            cl.load_settings(session_path)
            cl.login(username, password)
            log.info(f"Instagram: сессия загружена для @{username}")
        else:
            cl.login(username, password)
            cl.dump_settings(session_path)
            log.info(f"Instagram: вход выполнен для @{username}")
    except BadPassword:
        log.error("Instagram: неверный логин или пароль")
        return 0
    except ChallengeRequired:
        log.error("Instagram: требуется подтверждение (challenge). Войди вручную через браузер и попробуй снова.")
        return 0
    except Exception as e:
        log.error(f"Instagram: ошибка авторизации — {e}")
        return 0

    found = 0
    kw_list = [k.strip() for k in keywords.split(',') if k.strip()]
    topic = topics.split(',')[0].strip() if topics else ''
    region = regions.split(',')[0].strip() if regions else ''
    need_email = 'email' in contact_types
    need_phone = 'phone' in contact_types

    log.info(f"Instagram: ищем по хэштегам: {kw_list}")

    for keyword in kw_list:
        if found >= daily_limit:
            break

        # Убираем # если есть
        tag = keyword.lstrip('#')

        try:
            log.info(f"  Хэштег: #{tag}")
            medias = cl.hashtag_medias_recent(tag, amount=20)

            for media in medias:
                if found >= daily_limit:
                    break
                try:
                    user_id = media.user.pk
                    user_info = cl.user_info(user_id)

                    bio = user_info.biography or ''
                    name = user_info.full_name or user_info.username
                    uname = user_info.username
                    followers = user_info.follower_count or 0
                    profile_url = f"https://www.instagram.com/{uname}/"

                    # Извлекаем email и телефон из bio
                    email = None
                    phone = None
                    if need_email:
                        emails = re.findall(r'[\w.+-]+@[\w-]+\.[\w.]+', bio)
                        if emails:
                            email = emails[0]
                    if need_phone:
                        phones = re.findall(r'[\+\d][\d\s\-\(\)]{8,}', bio)
                        if phones:
                            phone = phones[0].strip()

                    saved = save_contact({
                        'name': name,
                        'email': email,
                        'phone': phone,
                        'contact_url': profile_url,
                        'source_url': profile_url,
                        'source_platform': 'Instagram',
                        'source_name': f"@{uname}",
                        'topic': topic,
                        'region': region,
                        'description': bio[:300],
                        'audience_size': followers,
                        'entry_point': entry_point,
                        'offer': offer,
                    })

                    if saved:
                        found += 1
                        log.info(f"  ✓ {name} (@{uname}) — {followers} подписчиков")

                    random_delay(bot.get('delay_min', 3), bot.get('delay_max', 8))

                except Exception as e:
                    log.warning(f"  Ошибка обработки профиля: {e}")

            random_delay(bot.get('delay_min', 5), bot.get('delay_max', 15))

        except Exception as e:
            log.error(f"  Ошибка по хэштегу #{tag}: {e}")

    # Сохраняем сессию
    cl.dump_settings(session_path)
    return found


# ─── ГЛАВНАЯ ФУНКЦИЯ ──────────────────────────────────────────────────────────

PLATFORM_HANDLERS = {
    'Telegram': scout_telegram,
    'ВКонтакте': scout_vk,
    'Instagram': scout_instagram,
}

def run_scout(bot_id):
    bot = get_bot(bot_id)
    if not bot:
        log.error(f"Бот #{bot_id} не найден в БД")
        sys.exit(1)

    log.info(f"=== Запуск Разведчика: {bot['name']} (#{bot_id}) ===")

    # Читаем настройки
    keywords = bot.get('keywords') or ''
    topics = bot.get('topics') or ''
    regions = bot.get('regions') or ''
    contact_types = bot.get('contact_types') or ''
    entry_point = bot.get('entry_point') or ''
    offer = bot.get('offer') or ''
    daily_limit = int(bot.get('daily_limit') or 50)
    search_platforms = bot.get('target') or ''  # платформы для поиска хранятся в target

    if not keywords:
        log.error("Ключевые слова не заданы. Укажи в настройках бота.")
        sys.exit(1)

    platforms = [p.strip() for p in search_platforms.split(',') if p.strip()]
    if not platforms:
        log.error("Платформы для поиска не выбраны. Укажи в настройках бота.")
        sys.exit(1)

    log.info(f"Платформы: {platforms}")
    log.info(f"Ключевые слова: {keywords}")
    log.info(f"Тематики: {topics}")
    log.info(f"Лимит: {daily_limit}/день")

    # Обновляем статус
    update_bot_status(bot_id, 'в работе')

    total_found = 0

    for platform in platforms:
        handler = PLATFORM_HANDLERS.get(platform)
        if not handler:
            log.warning(f"Платформа '{platform}' пока не поддерживается — пропускаем")
            continue

        log.info(f"\n--- Платформа: {platform} ---")
        found = handler(bot, keywords, topics, regions, contact_types, entry_point, offer, daily_limit)
        total_found += found
        log.info(f"Платформа {platform}: найдено {found} контактов")

    log.info(f"\n=== Итого найдено: {total_found} контактов ===")
    update_bot_status(bot_id, 'отключён', total_found)

    return total_found


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Использование: python3 scout.py <bot_id>")
        sys.exit(1)

    bot_id = int(sys.argv[1])
    run_scout(bot_id)
