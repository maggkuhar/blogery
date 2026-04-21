from flask import Blueprint, render_template, request, redirect, url_for
from .logic import get_all_contacts, get_all_scout_tasks, add_scout_task, delete_scout_task
from constants import SCOUT_PLATFORMS, SCOUT_TOPICS, SCOUT_REGIONS, SCOUT_CONTACT_TYPES, SCOUT_ENTRY_POINTS, SCOUT_OFFERS

bp = Blueprint('scout_bp', __name__, template_folder='templates')


@bp.route("/contacts")
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


@bp.route("/scout")
def scout():
    return redirect(url_for("scout_bp.contacts"))


@bp.route("/scout/add-task", methods=["POST"])
def scout_add_task():
    add_scout_task(request.form)
    return redirect(url_for("scout_bp.scout"))


@bp.route("/scout/delete-task/<int:task_id>", methods=["POST"])
def scout_delete_task(task_id):
    delete_scout_task(task_id)
    return redirect(url_for("scout_bp.scout"))


@bp.route("/ads")
def ads():
    return render_template("ads.html", tab="ads")


@bp.route("/mailing")
def mailing():
    return render_template("mailing.html", tab="mailing")
