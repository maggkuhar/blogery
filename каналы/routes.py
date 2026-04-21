from flask import Blueprint, render_template, request, redirect, url_for
from .logic import get_all_channels, get_channel, add_channel, update_channel, delete_channel
from constants import PLATFORMS, STATUSES

bp = Blueprint('channels_bp', __name__, template_folder='templates')


@bp.route("/channels")
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


@bp.route("/channels/add", methods=["GET", "POST"])
def channels_add():
    if request.method == "POST":
        add_channel(request.form)
        return redirect(url_for("channels_bp.channels"))
    return render_template("form.html", item=None, platforms=PLATFORMS, statuses=STATUSES, action="Добавить", tab="channels", field_count="subscribers")


@bp.route("/channels/edit/<int:channel_id>", methods=["GET", "POST"])
def channels_edit(channel_id):
    channel = get_channel(channel_id)
    if not channel:
        return redirect(url_for("channels_bp.channels"))
    if request.method == "POST":
        update_channel(channel_id, request.form)
        return redirect(url_for("channels_bp.channels"))
    return render_template("form.html", item=channel, platforms=PLATFORMS, statuses=STATUSES, action="Сохранить", tab="channels", field_count="subscribers")


@bp.route("/channels/delete/<int:channel_id>", methods=["POST"])
def channels_delete(channel_id):
    delete_channel(channel_id)
    return redirect(url_for("channels_bp.channels"))
