import os
from flask import Flask, render_template, request, redirect, url_for, jsonify, session
from database import (init_db,
    get_all_bloggers, get_blogger, add_blogger, update_blogger, delete_blogger,
    get_all_groups, get_group, add_group, update_group, delete_group,
    get_all_channels, get_channel, add_channel, update_channel, delete_channel,
    get_all_bots, get_bot, add_bot, update_bot, delete_bot, toggle_bot_status, bot_banned,
    get_all_templates, get_template, add_template, update_template, delete_template, increment_template_usage,
    get_all_smm_accounts, get_smm_account, add_smm_account, update_smm_account, delete_smm_account,
    get_all_smm_posts, get_smm_post, add_smm_post, update_smm_post, delete_smm_post,
    get_all_contacts, get_all_scout_tasks, add_scout_task, delete_scout_task)

app = Flask(__name__)
app.secret_key = "vt_smm_2026_secret"

@app.context_processor
def inject_nav():
    path = request.path
    current_block = "smm" if path.startswith("/smm") else "traffic"
    return dict(current_block=current_block)

PLATFORMS = ["Telegram", "WhatsApp", "Instagram", "ВКонтакте", "TikTok", "YouTube", "Rutube", "Одноклассники", "Дзен"]
STATUSES = ["новый", "в работе", "сотрудничество", "отказ"]


# --- Блогеры ---

@app.route("/")
def index():
    platform = request.args.get("platform", "")
    status = request.args.get("status", "")
    folder = request.args.get("folder", "")
    topic = request.args.get("topic", "")
    bloggers = get_all_bloggers(
        platform=platform or None,
        status=status or None,
        folder=folder or None,
        topic=topic or None,
    )
    return render_template("index.html",
        bloggers=bloggers,
        platforms=PLATFORMS,
        statuses=STATUSES,
        filters={"platform": platform, "status": status, "folder": folder, "topic": topic},
        tab="bloggers",
    )


@app.route("/add", methods=["GET", "POST"])
def add():
    if request.method == "POST":
        add_blogger(request.form)
        return redirect(url_for("index"))
    return render_template("form.html", item=None, platforms=PLATFORMS, statuses=STATUSES, action="Добавить", tab="bloggers", field_count="subscribers")


@app.route("/edit/<int:blogger_id>", methods=["GET", "POST"])
def edit(blogger_id):
    blogger = get_blogger(blogger_id)
    if not blogger:
        return redirect(url_for("index"))
    if request.method == "POST":
        update_blogger(blogger_id, request.form)
        return redirect(url_for("index"))
    return render_template("form.html", item=blogger, platforms=PLATFORMS, statuses=STATUSES, action="Сохранить", tab="bloggers", field_count="subscribers")


@app.route("/delete/<int:blogger_id>", methods=["POST"])
def delete(blogger_id):
    delete_blogger(blogger_id)
    return redirect(url_for("index"))


# --- Группы ---

@app.route("/groups")
def groups():
    platform = request.args.get("platform", "")
    status = request.args.get("status", "")
    folder = request.args.get("folder", "")
    topic = request.args.get("topic", "")
    items = get_all_groups(
        platform=platform or None,
        status=status or None,
        folder=folder or None,
        topic=topic or None,
    )
    return render_template("groups.html",
        groups=items,
        platforms=PLATFORMS,
        statuses=STATUSES,
        filters={"platform": platform, "status": status, "folder": folder, "topic": topic},
        tab="groups",
    )


@app.route("/groups/add", methods=["GET", "POST"])
def groups_add():
    if request.method == "POST":
        add_group(request.form)
        return redirect(url_for("groups"))
    return render_template("form.html", item=None, platforms=PLATFORMS, statuses=STATUSES, action="Добавить", tab="groups", field_count="members")


@app.route("/groups/edit/<int:group_id>", methods=["GET", "POST"])
def groups_edit(group_id):
    group = get_group(group_id)
    if not group:
        return redirect(url_for("groups"))
    if request.method == "POST":
        update_group(group_id, request.form)
        return redirect(url_for("groups"))
    return render_template("form.html", item=group, platforms=PLATFORMS, statuses=STATUSES, action="Сохранить", tab="groups", field_count="members")


@app.route("/groups/delete/<int:group_id>", methods=["POST"])
def groups_delete(group_id):
    delete_group(group_id)
    return redirect(url_for("groups"))


# --- Каналы ---

@app.route("/channels")
def channels():
    platform = request.args.get("platform", "")
    status = request.args.get("status", "")
    folder = request.args.get("folder", "")
    topic = request.args.get("topic", "")
    items = get_all_channels(
        platform=platform or None,
        status=status or None,
        folder=folder or None,
        topic=topic or None,
    )
    return render_template("channels.html",
        channels=items,
        platforms=PLATFORMS,
        statuses=STATUSES,
        filters={"platform": platform, "status": status, "folder": folder, "topic": topic},
        tab="channels",
    )


@app.route("/channels/add", methods=["GET", "POST"])
def channels_add():
    if request.method == "POST":
        add_channel(request.form)
        return redirect(url_for("channels"))
    return render_template("form.html", item=None, platforms=PLATFORMS, statuses=STATUSES, action="Добавить", tab="channels", field_count="subscribers")


@app.route("/channels/edit/<int:channel_id>", methods=["GET", "POST"])
def channels_edit(channel_id):
    channel = get_channel(channel_id)
    if not channel:
        return redirect(url_for("channels"))
    if request.method == "POST":
        update_channel(channel_id, request.form)
        return redirect(url_for("channels"))
    return render_template("form.html", item=channel, platforms=PLATFORMS, statuses=STATUSES, action="Сохранить", tab="channels", field_count="subscribers")


@app.route("/channels/delete/<int:channel_id>", methods=["POST"])
def channels_delete(channel_id):
    delete_channel(channel_id)
    return redirect(url_for("channels"))


# --- Боты ---

ROLES = ["разведчик", "контакт"]
BOT_STATUSES = ["активен", "отключён", "заблокирован", "прогрев"]

def base_fields(name_placeholder):
    return [
        {"name": "bot_name", "label": "Имя бота", "type": "text", "placeholder": name_placeholder, "required": True},
        {"name": "platform", "label": "Платформа", "type": "select", "options": PLATFORMS, "required": True},
        {"name": "token", "label": "API токен / аккаунт", "type": "password", "placeholder": "Токен или @username", "required": True},
    ]

BOT_TEMPLATES = [
    {
        "id": "scout",
        "name": "Разведчик",
        "icon": "🔍",
        "color": "#1a7f4b",
        "description": "Мониторит группы и каналы, собирает данные об участниках сообщества",
        "use_case": "Нужно найти целевую аудиторию и собрать контакты",
        "hint": "После создания зайди в Настройки бота и укажи платформы, тематики и ключевые слова",
        "fields": base_fields("Разведчик-TG-1"),
    },
    {
        "id": "parser",
        "name": "Парсер",
        "icon": "🕷",
        "color": "#8e44ad",
        "description": "Парсит списки участников, посты, контакты и контент из групп и каналов",
        "use_case": "Нужно собрать базу контактов или выгрузить все посты из канала",
        "hint": "После создания укажи источник и что именно парсить в Настройках",
        "fields": base_fields("Парсер-VK-1"),
    },
    {
        "id": "poster",
        "name": "Постер",
        "icon": "📢",
        "color": "#e67e22",
        "description": "Автоматически размещает контент по расписанию в группах и каналах",
        "use_case": "Нужно публиковать посты по расписанию без ручного труда",
        "hint": "После создания укажи канал и расписание публикаций в Настройках",
        "fields": base_fields("Постер-TG-1"),
    },
    {
        "id": "commenter",
        "name": "Комментатор",
        "icon": "💬",
        "color": "#2980b9",
        "description": "Оставляет комментарии под постами по ключевым словам для привлечения внимания",
        "use_case": "Нужно прогреть аккаунт или привлечь внимание через комментарии",
        "hint": "После создания укажи хэштег, шаблон комментария и задержки в Настройках",
        "fields": base_fields("Комментатор-IG-1"),
    },
    {
        "id": "inviter",
        "name": "Инвайтер",
        "icon": "🤝",
        "color": "#16a085",
        "description": "Приглашает пользователей в группы и каналы из других источников",
        "use_case": "Нужно набрать участников в свою группу из целевой аудитории",
        "hint": "После создания укажи откуда брать и куда приглашать в Настройках",
        "fields": base_fields("Инвайтер-TG-1"),
    },
    {
        "id": "analyst",
        "name": "Аналитик",
        "icon": "📊",
        "color": "#c0392b",
        "description": "Отслеживает статистику каналов и профилей: охваты, рост, активность",
        "use_case": "Нужно следить за конкурентами или своими показателями в динамике",
        "hint": "После создания укажи профиль для анализа и частоту сбора в Настройках",
        "fields": base_fields("Аналитик-TG-1"),
    },
]

@app.route("/bots/create")
def bots_create():
    return render_template("bot_create.html", templates=BOT_TEMPLATES, tab="bots")

TEMPLATE_ROLE = {
    "scout": "разведчик", "parser": "парсер", "poster": "постер",
    "commenter": "комментатор", "inviter": "инвайтер", "analyst": "аналитик",
}

@app.route("/bots/from-template/<template_id>", methods=["GET", "POST"])
def bots_from_template(template_id):
    tmpl = next((t for t in BOT_TEMPLATES if t["id"] == template_id), None)
    if not tmpl:
        return redirect(url_for("bots_create"))
    if request.method == "POST":
        form = request.form
        clone_id = form.get("clone_bot_id", "")
        clone = get_bot(int(clone_id)) if clone_id else None

        from werkzeug.datastructures import ImmutableMultiDict
        data = ImmutableMultiDict({
            "name": form.get("bot_name", ""),
            "platform": form.get("platform", ""),
            "role": TEMPLATE_ROLE.get(template_id, "разведчик"),
            "status": "новый",
            "account": form.get("token", ""),
            "daily_limit": str(clone["daily_limit"]) if clone else "50",
            "delay_min": str(clone["delay_min"]) if clone else "30",
            "delay_max": str(clone["delay_max"]) if clone else "120",
            "schedule": clone["schedule"] if clone else "09:00-22:00",
            "target": clone["target"] if clone else "",
            "keywords": clone["keywords"] if clone else "",
            "entry_point": clone["entry_point"] if clone else "",
            "offer": clone["offer"] if clone else "",
        })
        add_bot(data)

        # Копируем многозначные поля (topics, regions, contact_types)
        conn = __import__('database').get_db()
        new_bot_id = conn.execute("SELECT id FROM bots ORDER BY id DESC LIMIT 1").fetchone()[0]
        if clone:
            conn.execute("""UPDATE bots SET topics=?, regions=?, contact_types=? WHERE id=?""", (
                clone.get("topics", ""), clone.get("regions", ""), clone.get("contact_types", ""), new_bot_id
            ))
            conn.commit()
        conn.close()
        return redirect(url_for("bots_auth", bot_id=new_bot_id))
    return render_template("bot_template_form.html", tmpl=tmpl, tab="bots")


@app.route("/bots/by-platform/<platform>")
def bots_by_platform(platform):
    items = get_all_bots(platform=platform)
    return jsonify([{"id": b["id"], "name": b["name"]} for b in items])


@app.route("/bots/auth/<int:bot_id>", methods=["GET", "POST"])
def bots_auth(bot_id):
    bot = get_bot(bot_id)
    if not bot:
        return redirect(url_for("bots"))
    msg = request.args.get("msg", "")
    error = request.args.get("error", "")
    return render_template("bot_auth.html", bot=bot, tab="bots", msg=msg, error=error)


@app.route("/bots/auth/<int:bot_id>/send-code", methods=["POST"])
def bots_auth_send_code(bot_id):
    """Отправляет код подтверждения в Telegram."""
    bot = get_bot(bot_id)
    if not bot or bot["platform"] != "Telegram":
        return redirect(url_for("bots_auth", bot_id=bot_id))

    account = bot.get("account", "")
    parts = account.split(":")
    if len(parts) < 3:
        return redirect(url_for("bots_auth", bot_id=bot_id, error="Неверный формат токена. Нужно: api_id:api_hash:+7номер"))

    try:
        from telethon.sync import TelegramClient
        api_id = int(parts[0])
        api_hash = parts[1]
        phone = parts[2]
        session_file = os.path.join(os.path.dirname(__file__), "sessions", f"tg_{bot_id}")
        os.makedirs(os.path.dirname(session_file), exist_ok=True)

        client = TelegramClient(session_file, api_id, api_hash)
        client.connect()
        result = client.send_code_request(phone)
        session["tg_phone_hash"] = result.phone_code_hash
        session["tg_bot_id"] = bot_id
        client.disconnect()
        return redirect(url_for("bots_auth", bot_id=bot_id, msg="Код отправлен в Telegram"))
    except Exception as e:
        return redirect(url_for("bots_auth", bot_id=bot_id, error=str(e)))


@app.route("/bots/auth/<int:bot_id>/verify", methods=["POST"])
def bots_auth_verify(bot_id):
    """Проверяет код из Telegram и сохраняет сессию."""
    bot = get_bot(bot_id)
    if not bot:
        return redirect(url_for("bots"))

    code = request.form.get("code", "").strip()
    phone_hash = session.get("tg_phone_hash", "")

    account = bot.get("account", "")
    parts = account.split(":")
    if len(parts) < 3:
        return redirect(url_for("bots_auth", bot_id=bot_id, error="Ошибка токена"))

    try:
        from telethon.sync import TelegramClient
        api_id = int(parts[0])
        api_hash = parts[1]
        phone = parts[2]
        session_file = os.path.join(os.path.dirname(__file__), "sessions", f"tg_{bot_id}")

        client = TelegramClient(session_file, api_id, api_hash)
        client.connect()
        client.sign_in(phone=phone, code=code, phone_code_hash=phone_hash)
        me = client.get_me()
        client.disconnect()

        # Обновляем статус бота
        from database import get_db as _get_db
        conn = _get_db()
        conn.execute("UPDATE bots SET status='отключён', updated_at=CURRENT_TIMESTAMP WHERE id=?", (bot_id,))
        conn.commit()
        conn.close()

        return redirect(url_for("bots_auth", bot_id=bot_id, msg=f"Авторизован: @{me.username or me.first_name}"))
    except Exception as e:
        return redirect(url_for("bots_auth", bot_id=bot_id, error=str(e)))

@app.route("/bots")
def bots():
    platform = request.args.get("platform", "")
    role = request.args.get("role", "")
    status = request.args.get("status", "")
    items = get_all_bots(
        platform=platform or None,
        role=role or None,
        status=status or None,
    )
    return render_template("bots.html",
        bots=items,
        platforms=PLATFORMS,
        roles=ROLES,
        bot_statuses=BOT_STATUSES,
        filters={"platform": platform, "role": role, "status": status},
        tab="bots",
    )


def _bot_scout_ctx():
    return dict(
        scout_platforms=SCOUT_PLATFORMS,
        scout_topics=SCOUT_TOPICS,
        scout_regions=SCOUT_REGIONS,
        scout_contact_types=SCOUT_CONTACT_TYPES,
        scout_entry_points=SCOUT_ENTRY_POINTS,
        scout_offers=SCOUT_OFFERS,
    )

@app.route("/bots/add", methods=["GET", "POST"])
def bots_add():
    if request.method == "POST":
        add_bot(request.form)
        return redirect(url_for("bots"))
    return render_template("bot_form.html", item=None, platforms=PLATFORMS, roles=ROLES,
        bot_statuses=BOT_STATUSES, action="Добавить бота", **_bot_scout_ctx())


@app.route("/bots/edit/<int:bot_id>", methods=["GET", "POST"])
def bots_edit(bot_id):
    bot = get_bot(bot_id)
    if not bot:
        return redirect(url_for("bots"))
    if request.method == "POST":
        update_bot(bot_id, request.form)
        return redirect(url_for("bots"))
    return render_template("bot_form.html", item=bot, platforms=PLATFORMS, roles=ROLES,
        bot_statuses=BOT_STATUSES, action="Сохранить", **_bot_scout_ctx())


@app.route("/bots/delete/<int:bot_id>", methods=["POST"])
def bots_delete(bot_id):
    delete_bot(bot_id)
    return redirect(url_for("bots"))


@app.route("/bots/toggle/<int:bot_id>", methods=["POST"])
def bots_toggle(bot_id):
    toggle_bot_status(bot_id)
    return redirect(url_for("bots"))


@app.route("/bots/ban/<int:bot_id>", methods=["POST"])
def bots_ban(bot_id):
    reason = request.form.get("reason", "")
    bot_banned(bot_id, reason)
    return redirect(url_for("bots"))


@app.route("/bots/auth/<int:bot_id>/test", methods=["POST"])
def bots_auth_test(bot_id):
    bot = get_bot(bot_id)
    if not bot:
        return redirect(url_for("bots"))

    platform = bot.get("platform", "")
    account = bot.get("account", "")
    ok = False
    detail = ""

    try:
        if platform == "Telegram":
            from telethon.sync import TelegramClient
            parts = account.split(":")
            session_file = os.path.join(os.path.dirname(__file__), "sessions", f"tg_{bot_id}")
            client = TelegramClient(session_file, int(parts[0]), parts[1])
            client.connect()
            ok = client.is_user_authorized()
            if ok:
                me = client.get_me()
                detail = f"@{me.username or me.first_name}"
            client.disconnect()

        elif platform == "ВКонтакте":
            import requests as req
            r = req.get("https://api.vk.com/method/users.get",
                params={"access_token": account, "v": "5.131"}, timeout=5).json()
            ok = "response" in r
            if ok:
                u = r["response"][0]
                detail = f"{u.get('first_name','')} {u.get('last_name','')}"

        elif platform == "Instagram":
            from instagrapi import Client
            from instagrapi.exceptions import BadPassword, ChallengeRequired
            parts = account.split(":", 1)
            if len(parts) < 2:
                detail = "Неверный формат токена. Нужно: username:password"
            else:
                username, password = parts[0].strip(), parts[1].strip()
                session_path = os.path.join(os.path.dirname(__file__), "sessions", f"ig_{bot_id}.json")
                os.makedirs(os.path.dirname(session_path), exist_ok=True)
                cl = Client()
                try:
                    if os.path.exists(session_path):
                        cl.load_settings(session_path)
                    cl.login(username, password)
                    cl.dump_settings(session_path)
                    me = cl.account_info()
                    ok = True
                    detail = f"@{me.username} ({me.full_name})"
                except BadPassword:
                    detail = "Неверный логин или пароль"
                except ChallengeRequired:
                    detail = "Instagram требует подтверждение — войди вручную в браузере с этого IP и повтори тест"
                except Exception as e:
                    detail = str(e)

        else:
            ok = bool(account)
            detail = "Токен сохранён"

    except Exception as e:
        detail = str(e)

    msg = f"Успешно: {detail}" if ok else ""
    error = f"Ошибка: {detail}" if not ok else ""
    return redirect(url_for("bots_auth", bot_id=bot_id, msg=msg, error=error))


@app.route("/bots/run/<int:bot_id>", methods=["POST"])
def bots_run(bot_id):
    import subprocess
    bot = get_bot(bot_id)
    if not bot:
        return redirect(url_for("bots"))
    script = os.path.join(os.path.dirname(__file__), "bots", "scout.py")
    subprocess.Popen(
        ["python3", script, str(bot_id)],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    return redirect(url_for("bots"))


# --- Разведчик ---

SCOUT_PLATFORMS = {
    "Мессенджеры": ["Telegram", "WhatsApp"],
    "Социальные сети": ["ВКонтакте", "Instagram", "TikTok", "YouTube", "Rutube", "Одноклассники", "Дзен", "Facebook"],
    "Бизнес каталоги": ["2GIS", "Яндекс.Карты", "Google Maps", "Zoon", "Flamp"],
    "Доски объявлений": ["Авито", "Юла", "HH.ru", "SuperJob"],
    "Профессиональные": ["LinkedIn", "Behance", "GitHub"],
    "Поисковики": ["Google Поиск", "Яндекс Поиск"],
    "Маркетплейсы": ["Wildberries (продавцы)", "Ozon (продавцы)"],
}

SCOUT_TOPICS = [
    "Саморазвитие", "Психология", "Бизнес и предпринимательство", "Маркетинг и SMM",
    "Здоровье и фитнес", "Красота и уход", "Образование", "Финансы и инвестиции",
    "Путешествия", "Еда и кулинария", "Мода и стиль", "Искусство и творчество",
    "Технологии и IT", "Недвижимость", "Авто", "Спорт", "Семья и дети",
    "Экология", "Религия и духовность", "Юмор и развлечения",
]

SCOUT_REGIONS = [
    "Вся Россия", "Москва", "Санкт-Петербург", "Новосибирск", "Екатеринбург",
    "Казань", "Нижний Новгород", "Краснодар", "Ростов-на-Дону", "Уфа",
    "СНГ", "Беларусь", "Казахстан", "Украина", "Весь мир",
]

SCOUT_CONTACT_TYPES = ["Email", "Телефон", "Telegram", "WhatsApp", "Ссылка на профиль"]

SCOUT_ENTRY_POINTS = {
    "Telegram": "Написать админу в личку",
    "ВКонтакте": "Сообщение в сообщество",
    "Instagram": "Комментарий + директ",
    "TikTok": "Комментарий + директ",
    "YouTube": "Комментарий + email из описания",
    "Одноклассники": "Сообщение в сообщество",
    "Facebook": "Сообщение в группу",
    "2GIS": "Звонок или email",
    "Яндекс.Карты": "Звонок или email",
    "Google Maps": "Звонок или email",
    "Авито": "Написать продавцу",
    "HH.ru": "Email из профиля",
    "LinkedIn": "Запрос в контакты + сообщение",
    "Сайт": "Форма обратной связи",
    "Google Поиск": "Email с сайта",
    "Яндекс Поиск": "Email с сайта",
}

SCOUT_OFFERS = [
    "IWS — Умный дневник 365 дней",
    "IWS — Колода МАК карт",
    "IWS — Настольная игра",
    "IWS — Онлайн игра @iwsgamebot",
    "SMM — Ведение соцсетей",
    "SMM — Создание контента",
    "Внешний трафик — Продвижение через блогеров",
    "Alex Wake — Продажа картин",
    "Партнёрство — Реферальная программа",
    "Сотрудничество — Взаимный пиар",
]

@app.route("/contacts")
def contacts():
    topic = request.args.get("topic", "")
    platform = request.args.get("platform", "")
    status = request.args.get("status", "")
    mailed = request.args.get("mailed", "")
    items = get_all_contacts(
        topic=topic or None,
        platform=platform or None,
        status=status or None,
        mailed=True if mailed == "1" else (False if mailed == "0" else None),
    )
    all_platforms = [p for group in SCOUT_PLATFORMS.values() for p in group]
    return render_template("contacts.html",
        contacts=items,
        scout_topics=SCOUT_TOPICS,
        all_platforms=all_platforms,
        filters={"topic": topic, "platform": platform, "status": status, "mailed": mailed},
        tab="contacts",
    )

@app.route("/scout")
def scout():
    return redirect(url_for("contacts"))

@app.route("/scout/add-task", methods=["POST"])
def scout_add_task():
    add_scout_task(request.form)
    return redirect(url_for("scout"))

@app.route("/scout/delete-task/<int:task_id>", methods=["POST"])
def scout_delete_task(task_id):
    delete_scout_task(task_id)
    return redirect(url_for("scout"))

# --- Реклама ---

@app.route("/ads")
def ads():
    return render_template("ads.html", tab="ads")


# --- Email рассылка ---

@app.route("/mailing")
def mailing():
    return render_template("mailing.html", tab="mailing")


# --- Шаблоны ---

TEMPLATE_FORMATS = {
    "сообщения": ["Первый контакт", "Вопросы", "Ответы", "Фолоу-ап", "Ответ на отказ"],
    "предложения": ["Платное сотрудничество", "Бартер"],
}

@app.route("/templates")
def templates():
    fmt = request.args.get("format", "")
    subgroup = request.args.get("subgroup", "")
    items = get_all_templates(format=fmt or None, subgroup=subgroup or None)
    return render_template("templates.html",
        templates=items,
        template_formats=TEMPLATE_FORMATS,
        filters={"format": fmt, "subgroup": subgroup},
        tab="templates",
    )


@app.route("/templates/add", methods=["GET", "POST"])
def templates_add():
    if request.method == "POST":
        add_template(request.form)
        return redirect(url_for("templates"))
    fmt = request.args.get("format", "")
    subgroup = request.args.get("subgroup", "")
    return render_template("template_form.html",
        item=None, template_formats=TEMPLATE_FORMATS,
        action="Добавить шаблон", preset_format=fmt, preset_subgroup=subgroup)


@app.route("/templates/edit/<int:template_id>", methods=["GET", "POST"])
def templates_edit(template_id):
    tmpl = get_template(template_id)
    if not tmpl:
        return redirect(url_for("templates"))
    if request.method == "POST":
        update_template(template_id, request.form)
        return redirect(url_for("templates"))
    return render_template("template_form.html",
        item=tmpl, template_formats=TEMPLATE_FORMATS,
        action="Сохранить", preset_format="", preset_subgroup="")


@app.route("/templates/delete/<int:template_id>", methods=["POST"])
def templates_delete(template_id):
    delete_template(template_id)
    return redirect(url_for("templates"))


@app.route("/templates/use/<int:template_id>", methods=["POST"])
def templates_use(template_id):
    increment_template_usage(template_id)
    return redirect(url_for("templates"))


# --- SMM платформа ---

SMM_STATUSES_ACCOUNT = ["активен", "заморожен", "забанен", "отключён"]
SMM_STATUSES_POST = ["черновик", "запланирован", "опубликован", "ошибка"]


@app.route("/smm")
def smm():
    platform = request.args.get("platform", "")
    status = request.args.get("status", "")
    accounts = get_all_smm_accounts(platform=platform or None, status=status or None)
    return render_template("smm_accounts.html",
        accounts=accounts,
        platforms=PLATFORMS,
        smm_statuses=SMM_STATUSES_ACCOUNT,
        filters={"platform": platform, "status": status},
        tab="smm_accounts",
    )


@app.route("/smm/add", methods=["GET", "POST"])
def smm_add():
    if request.method == "POST":
        add_smm_account(request.form)
        return redirect(url_for("smm"))
    return render_template("smm_account_form.html",
        item=None, platforms=PLATFORMS,
        smm_statuses=SMM_STATUSES_ACCOUNT, action="Добавить аккаунт")


@app.route("/smm/edit/<int:account_id>", methods=["GET", "POST"])
def smm_edit(account_id):
    account = get_smm_account(account_id)
    if not account:
        return redirect(url_for("smm"))
    if request.method == "POST":
        update_smm_account(account_id, request.form)
        return redirect(url_for("smm"))
    return render_template("smm_account_form.html",
        item=account, platforms=PLATFORMS,
        smm_statuses=SMM_STATUSES_ACCOUNT, action="Сохранить")


@app.route("/smm/delete/<int:account_id>", methods=["POST"])
def smm_delete(account_id):
    delete_smm_account(account_id)
    return redirect(url_for("smm"))


@app.route("/smm/posts")
def smm_posts():
    status = request.args.get("status", "")
    posts = get_all_smm_posts(status=status or None)
    accounts = get_all_smm_accounts()
    return render_template("smm_posts.html",
        posts=posts,
        accounts=accounts,
        smm_statuses=SMM_STATUSES_POST,
        filters={"status": status},
        tab="smm_posts",
    )


@app.route("/smm/posts/add", methods=["GET", "POST"])
def smm_posts_add():
    if request.method == "POST":
        add_smm_post(request.form)
        return redirect(url_for("smm_posts"))
    accounts = get_all_smm_accounts(status="активен")
    return render_template("smm_post_form.html",
        item=None, accounts=accounts,
        platforms=PLATFORMS, smm_statuses=SMM_STATUSES_POST, action="Создать пост")


@app.route("/smm/posts/edit/<int:post_id>", methods=["GET", "POST"])
def smm_posts_edit(post_id):
    post = get_smm_post(post_id)
    if not post:
        return redirect(url_for("smm_posts"))
    if request.method == "POST":
        update_smm_post(post_id, request.form)
        return redirect(url_for("smm_posts"))
    accounts = get_all_smm_accounts(status="активен")
    return render_template("smm_post_form.html",
        item=post, accounts=accounts,
        platforms=PLATFORMS, smm_statuses=SMM_STATUSES_POST, action="Сохранить")


@app.route("/smm/posts/delete/<int:post_id>", methods=["POST"])
def smm_posts_delete(post_id):
    delete_smm_post(post_id)
    return redirect(url_for("smm_posts"))


@app.route("/smm/stats")
def smm_stats():
    return render_template("smm_stub.html", tab="smm_stats", title="Статистика", desc="Охват, подписчики, активность по аккаунтам")

@app.route("/smm/content")
def smm_content():
    return render_template("smm_stub.html", tab="smm_content", title="Контент", desc="Редактор контента — в разработке")

@app.route("/smm/templates")
def smm_templates():
    return render_template("smm_stub.html", tab="smm_templates", title="Шаблоны постов", desc="Шаблоны для публикаций в соцсетях")

@app.route("/smm/images")
def smm_images():
    return render_template("smm_stub.html", tab="smm_images", title="Картинки", desc="Генерация изображений через AI")

@app.route("/smm/video")
def smm_video():
    return render_template("smm_stub.html", tab="smm_video", title="Видео", desc="Генерация и монтаж видео через AI")

@app.route("/smm/text")
def smm_text():
    return render_template("smm_stub.html", tab="smm_text", title="Текст", desc="Генерация текстов постов через AI")

@app.route("/smm/history")
def smm_history():
    posts = get_all_smm_posts()
    accounts = get_all_smm_accounts()
    accounts_map = {a["id"]: a for a in accounts}
    return render_template("smm_history.html", tab="smm_history", posts=posts, accounts_map=accounts_map)


# --- Статистика Внешний трафик ---

@app.route("/stats")
def stats():
    from database import get_db
    conn = get_db()

    def count(table, where="1=1", params=[]):
        return conn.execute(f"SELECT COUNT(*) FROM {table} WHERE {where}", params).fetchone()[0]

    def count_by(table, field):
        rows = conn.execute(f"SELECT {field}, COUNT(*) as cnt FROM {table} GROUP BY {field}").fetchall()
        return {r[field]: r["cnt"] for r in rows}

    data = {
        "bloggers": {
            "total": count("bloggers"),
            "by_status": count_by("bloggers", "status"),
            "by_platform": count_by("bloggers", "platform"),
            "this_month": count("bloggers", "strftime('%Y-%m', created_at) = strftime('%Y-%m', 'now')"),
        },
        "groups": {
            "total": count("groups"),
            "by_status": count_by("groups", "status"),
            "by_platform": count_by("groups", "platform"),
            "this_month": count("groups", "strftime('%Y-%m', created_at) = strftime('%Y-%m', 'now')"),
        },
        "channels": {
            "total": count("channels"),
            "by_status": count_by("channels", "status"),
            "by_platform": count_by("channels", "platform"),
            "this_month": count("channels", "strftime('%Y-%m', created_at) = strftime('%Y-%m', 'now')"),
        },
        "bots": {
            "total": count("bots"),
            "active": count("bots", "status = 'активен'"),
            "banned": count("bots", "status = 'заблокирован'"),
        },
    }
    conn.close()
    return render_template("stats.html", tab="stats", data=data, statuses=STATUSES, platforms=PLATFORMS)


if __name__ == "__main__":
    init_db()
    app.run(host="0.0.0.0", port=5000, debug=False)
