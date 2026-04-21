import os
import subprocess
from flask import Blueprint, render_template, request, redirect, url_for, jsonify, session
from .logic import get_all_bots, get_bot, add_bot, update_bot, delete_bot, toggle_bot_status, bot_banned
from database import get_db
from constants import (PLATFORMS, ROLES, BOT_STATUSES, BOT_TEMPLATES, TEMPLATE_ROLE,
                       SCOUT_PLATFORMS, SCOUT_TOPICS, SCOUT_REGIONS,
                       SCOUT_CONTACT_TYPES, SCOUT_ENTRY_POINTS, SCOUT_OFFERS)

bp = Blueprint('bots_bp', __name__, template_folder='templates')


def _bot_scout_ctx():
    return dict(
        scout_platforms=SCOUT_PLATFORMS,
        scout_topics=SCOUT_TOPICS,
        scout_regions=SCOUT_REGIONS,
        scout_contact_types=SCOUT_CONTACT_TYPES,
        scout_entry_points=SCOUT_ENTRY_POINTS,
        scout_offers=SCOUT_OFFERS,
    )


@bp.route("/bots/create")
def bots_create():
    return render_template("bot_create.html", templates=BOT_TEMPLATES, tab="bots")


@bp.route("/bots/connect", methods=["POST"])
def bots_connect():
    name = request.form.get("name", "").strip()
    platform = request.form.get("platform", "").strip()
    role = request.form.get("role", "").strip()
    account = request.form.get("account", "").strip()
    if not name or not platform or not role:
        return redirect(url_for("bots_bp.bots"))
    bot_id = add_bot({
        "name": name, "platform": platform, "role": role,
        "account": account, "status": "новый",
    })
    return redirect(url_for("bots_bp.bots_auth", bot_id=bot_id))


@bp.route("/bots/from-template/<template_id>", methods=["GET", "POST"])
def bots_from_template(template_id):
    tmpl = next((t for t in BOT_TEMPLATES if t["id"] == template_id), None)
    if not tmpl:
        return redirect(url_for("bots_bp.bots_create"))
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

        conn = get_db()
        new_bot_id = conn.execute("SELECT id FROM bots ORDER BY id DESC LIMIT 1").fetchone()[0]
        if clone:
            conn.execute("""UPDATE bots SET topics=?, regions=?, contact_types=? WHERE id=?""", (
                clone.get("topics", ""), clone.get("regions", ""), clone.get("contact_types", ""), new_bot_id
            ))
            conn.commit()
        conn.close()
        return redirect(url_for("bots_bp.bots_auth", bot_id=new_bot_id))
    return render_template("bot_template_form.html", tmpl=tmpl, tab="bots")


@bp.route("/bots/by-platform/<platform>")
def bots_by_platform(platform):
    items = get_all_bots(platform=platform)
    return jsonify([{"id": b["id"], "name": b["name"]} for b in items])


@bp.route("/bots/auth/<int:bot_id>", methods=["GET", "POST"])
def bots_auth(bot_id):
    bot = get_bot(bot_id)
    if not bot:
        return redirect(url_for("bots_bp.bots"))
    msg = request.args.get("msg", "")
    error = request.args.get("error", "")
    return render_template("bot_auth.html", bot=bot, tab="bots", msg=msg, error=error)


@bp.route("/bots/auth/<int:bot_id>/send-code", methods=["POST"])
def bots_auth_send_code(bot_id):
    """Отправляет код подтверждения в Telegram."""
    bot = get_bot(bot_id)
    if not bot or bot["platform"] != "Telegram":
        return redirect(url_for("bots_bp.bots_auth", bot_id=bot_id))

    account = bot.get("account", "")
    parts = account.split(":")
    if len(parts) < 3:
        return redirect(url_for("bots_bp.bots_auth", bot_id=bot_id, error="Неверный формат токена. Нужно: api_id:api_hash:+7номер"))

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
        return redirect(url_for("bots_bp.bots_auth", bot_id=bot_id, msg="Код отправлен в Telegram"))
    except Exception as e:
        return redirect(url_for("bots_bp.bots_auth", bot_id=bot_id, error=str(e)))


@bp.route("/bots/auth/<int:bot_id>/verify", methods=["POST"])
def bots_auth_verify(bot_id):
    """Проверяет код из Telegram и сохраняет сессию."""
    bot = get_bot(bot_id)
    if not bot:
        return redirect(url_for("bots_bp.bots"))

    code = request.form.get("code", "").strip()
    phone_hash = session.get("tg_phone_hash", "")

    account = bot.get("account", "")
    parts = account.split(":")
    if len(parts) < 3:
        return redirect(url_for("bots_bp.bots_auth", bot_id=bot_id, error="Ошибка токена"))

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

        conn = get_db()
        conn.execute("UPDATE bots SET status='отключён', updated_at=CURRENT_TIMESTAMP WHERE id=?", (bot_id,))
        conn.commit()
        conn.close()

        return redirect(url_for("bots_bp.bots_auth", bot_id=bot_id, msg=f"Авторизован: @{me.username or me.first_name}"))
    except Exception as e:
        return redirect(url_for("bots_bp.bots_auth", bot_id=bot_id, error=str(e)))


@bp.route("/bots")
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


@bp.route("/bots/add", methods=["GET", "POST"])
def bots_add():
    if request.method == "POST":
        add_bot(request.form)
        return redirect(url_for("bots_bp.bots"))
    return render_template("bot_form.html", item=None, platforms=PLATFORMS, roles=ROLES,
        bot_statuses=BOT_STATUSES, action="Добавить бота", **_bot_scout_ctx())


@bp.route("/bots/edit/<int:bot_id>", methods=["GET", "POST"])
def bots_edit(bot_id):
    bot = get_bot(bot_id)
    if not bot:
        return redirect(url_for("bots_bp.bots"))
    if request.method == "POST":
        update_bot(bot_id, request.form)
        return redirect(url_for("bots_bp.bots"))
    return render_template("bot_form.html", item=bot, platforms=PLATFORMS, roles=ROLES,
        bot_statuses=BOT_STATUSES, action="Сохранить", **_bot_scout_ctx())


@bp.route("/bots/delete/<int:bot_id>", methods=["POST"])
def bots_delete(bot_id):
    delete_bot(bot_id)
    return redirect(url_for("bots_bp.bots"))


@bp.route("/bots/toggle/<int:bot_id>", methods=["POST"])
def bots_toggle(bot_id):
    toggle_bot_status(bot_id)
    return redirect(url_for("bots_bp.bots"))


@bp.route("/bots/ban/<int:bot_id>", methods=["POST"])
def bots_ban(bot_id):
    reason = request.form.get("reason", "")
    bot_banned(bot_id, reason)
    return redirect(url_for("bots_bp.bots"))


@bp.route("/bots/auth/<int:bot_id>/test", methods=["POST"])
def bots_auth_test(bot_id):
    bot = get_bot(bot_id)
    if not bot:
        return redirect(url_for("bots_bp.bots"))

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
    return redirect(url_for("bots_bp.bots_auth", bot_id=bot_id, msg=msg, error=error))


@bp.route("/bots/run/<int:bot_id>", methods=["POST"])
def bots_run(bot_id):
    bot = get_bot(bot_id)
    if not bot:
        return redirect(url_for("bots_bp.bots"))
    script = os.path.join(os.path.dirname(os.path.dirname(__file__)), "bots", "scout.py")
    subprocess.Popen(
        ["python3", script, str(bot_id)],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    return redirect(url_for("bots_bp.bots"))
