from flask import Flask, render_template, request, redirect, url_for, jsonify, session
from database import (init_db,
    get_all_bloggers, get_blogger, add_blogger, update_blogger, delete_blogger,
    get_all_groups, get_group, add_group, update_group, delete_group,
    get_all_channels, get_channel, add_channel, update_channel, delete_channel,
    get_all_bots, get_bot, add_bot, update_bot, delete_bot, toggle_bot_status, bot_banned,
    get_all_templates, get_template, add_template, update_template, delete_template, increment_template_usage,
    get_all_smm_accounts, get_smm_account, add_smm_account, update_smm_account, delete_smm_account,
    get_all_smm_posts, get_smm_post, add_smm_post, update_smm_post, delete_smm_post)

app = Flask(__name__)
app.secret_key = "vt_smm_2026_secret"

@app.context_processor
def inject_nav():
    path = request.path
    current_block = "smm" if path.startswith("/smm") else "traffic"
    return dict(current_block=current_block)

PLATFORMS = ["Instagram", "ВКонтакте", "TikTok", "YouTube", "Одноклассники"]
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


@app.route("/bots/add", methods=["GET", "POST"])
def bots_add():
    if request.method == "POST":
        add_bot(request.form)
        return redirect(url_for("bots"))
    return render_template("bot_form.html", item=None, platforms=PLATFORMS, roles=ROLES, bot_statuses=BOT_STATUSES, action="Добавить бота")


@app.route("/bots/edit/<int:bot_id>", methods=["GET", "POST"])
def bots_edit(bot_id):
    bot = get_bot(bot_id)
    if not bot:
        return redirect(url_for("bots"))
    if request.method == "POST":
        update_bot(bot_id, request.form)
        return redirect(url_for("bots"))
    return render_template("bot_form.html", item=bot, platforms=PLATFORMS, roles=ROLES, bot_statuses=BOT_STATUSES, action="Сохранить")


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
