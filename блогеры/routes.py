from flask import Blueprint, render_template, request, redirect, url_for
from .logic import get_all_bloggers, get_blogger, add_blogger, update_blogger, delete_blogger
from constants import PLATFORMS, STATUSES

bp = Blueprint('bloggers', __name__, template_folder='templates')


@bp.route("/")
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


@bp.route("/add", methods=["GET", "POST"])
def add():
    if request.method == "POST":
        add_blogger(request.form)
        return redirect(url_for("bloggers.index"))
    return render_template("form.html", item=None, platforms=PLATFORMS, statuses=STATUSES, action="Добавить", tab="bloggers", field_count="subscribers")


@bp.route("/edit/<int:blogger_id>", methods=["GET", "POST"])
def edit(blogger_id):
    blogger = get_blogger(blogger_id)
    if not blogger:
        return redirect(url_for("bloggers.index"))
    if request.method == "POST":
        update_blogger(blogger_id, request.form)
        return redirect(url_for("bloggers.index"))
    return render_template("form.html", item=blogger, platforms=PLATFORMS, statuses=STATUSES, action="Сохранить", tab="bloggers", field_count="subscribers")


@bp.route("/delete/<int:blogger_id>", methods=["POST"])
def delete(blogger_id):
    delete_blogger(blogger_id)
    return redirect(url_for("bloggers.index"))
