from flask import Blueprint, render_template, request, redirect, url_for
from .logic import get_all_groups, get_group, add_group, update_group, delete_group
from constants import PLATFORMS, STATUSES

bp = Blueprint('groups_bp', __name__, template_folder='templates')


@bp.route("/groups")
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


@bp.route("/groups/add", methods=["GET", "POST"])
def groups_add():
    if request.method == "POST":
        add_group(request.form)
        return redirect(url_for("groups_bp.groups"))
    return render_template("form.html", item=None, platforms=PLATFORMS, statuses=STATUSES, action="Добавить", tab="groups", field_count="members")


@bp.route("/groups/edit/<int:group_id>", methods=["GET", "POST"])
def groups_edit(group_id):
    group = get_group(group_id)
    if not group:
        return redirect(url_for("groups_bp.groups"))
    if request.method == "POST":
        update_group(group_id, request.form)
        return redirect(url_for("groups_bp.groups"))
    return render_template("form.html", item=group, platforms=PLATFORMS, statuses=STATUSES, action="Сохранить", tab="groups", field_count="members")


@bp.route("/groups/delete/<int:group_id>", methods=["POST"])
def groups_delete(group_id):
    delete_group(group_id)
    return redirect(url_for("groups_bp.groups"))
