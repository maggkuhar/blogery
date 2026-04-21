from flask import Blueprint, render_template, request, redirect, url_for
from .logic import (get_all_smm_accounts, get_smm_account, add_smm_account, update_smm_account, delete_smm_account,
                    get_all_smm_posts, get_smm_post, add_smm_post, update_smm_post, delete_smm_post)
from constants import PLATFORMS, SMM_STATUSES_ACCOUNT, SMM_STATUSES_POST

bp = Blueprint('smm_bp', __name__, template_folder='templates')


@bp.route("/smm")
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


@bp.route("/smm/add", methods=["GET", "POST"])
def smm_add():
    if request.method == "POST":
        add_smm_account(request.form)
        return redirect(url_for("smm_bp.smm"))
    return render_template("smm_account_form.html",
        item=None, platforms=PLATFORMS,
        smm_statuses=SMM_STATUSES_ACCOUNT, action="Добавить аккаунт")


@bp.route("/smm/edit/<int:account_id>", methods=["GET", "POST"])
def smm_edit(account_id):
    account = get_smm_account(account_id)
    if not account:
        return redirect(url_for("smm_bp.smm"))
    if request.method == "POST":
        update_smm_account(account_id, request.form)
        return redirect(url_for("smm_bp.smm"))
    return render_template("smm_account_form.html",
        item=account, platforms=PLATFORMS,
        smm_statuses=SMM_STATUSES_ACCOUNT, action="Сохранить")


@bp.route("/smm/delete/<int:account_id>", methods=["POST"])
def smm_delete(account_id):
    delete_smm_account(account_id)
    return redirect(url_for("smm_bp.smm"))


@bp.route("/smm/posts")
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


@bp.route("/smm/posts/add", methods=["GET", "POST"])
def smm_posts_add():
    if request.method == "POST":
        add_smm_post(request.form)
        return redirect(url_for("smm_bp.smm_posts"))
    accounts = get_all_smm_accounts(status="активен")
    return render_template("smm_post_form.html",
        item=None, accounts=accounts,
        platforms=PLATFORMS, smm_statuses=SMM_STATUSES_POST, action="Создать пост")


@bp.route("/smm/posts/edit/<int:post_id>", methods=["GET", "POST"])
def smm_posts_edit(post_id):
    post = get_smm_post(post_id)
    if not post:
        return redirect(url_for("smm_bp.smm_posts"))
    if request.method == "POST":
        update_smm_post(post_id, request.form)
        return redirect(url_for("smm_bp.smm_posts"))
    accounts = get_all_smm_accounts(status="активен")
    return render_template("smm_post_form.html",
        item=post, accounts=accounts,
        platforms=PLATFORMS, smm_statuses=SMM_STATUSES_POST, action="Сохранить")


@bp.route("/smm/posts/delete/<int:post_id>", methods=["POST"])
def smm_posts_delete(post_id):
    delete_smm_post(post_id)
    return redirect(url_for("smm_bp.smm_posts"))


@bp.route("/smm/stats")
def smm_stats():
    return render_template("smm_stub.html", tab="smm_stats", title="Статистика", desc="Охват, подписчики, активность по аккаунтам")


@bp.route("/smm/content")
def smm_content():
    return render_template("smm_stub.html", tab="smm_content", title="Контент", desc="Редактор контента — в разработке")


@bp.route("/smm/templates")
def smm_templates():
    return render_template("smm_stub.html", tab="smm_templates", title="Шаблоны постов", desc="Шаблоны для публикаций в соцсетях")


@bp.route("/smm/images")
def smm_images():
    return render_template("smm_stub.html", tab="smm_images", title="Картинки", desc="Генерация изображений через AI")


@bp.route("/smm/video")
def smm_video():
    return render_template("smm_stub.html", tab="smm_video", title="Видео", desc="Генерация и монтаж видео через AI")


@bp.route("/smm/text")
def smm_text():
    return render_template("smm_stub.html", tab="smm_text", title="Текст", desc="Генерация текстов постов через AI")


@bp.route("/smm/history")
def smm_history():
    posts = get_all_smm_posts()
    accounts = get_all_smm_accounts()
    accounts_map = {a["id"]: a for a in accounts}
    return render_template("smm_history.html", tab="smm_history", posts=posts, accounts_map=accounts_map)
