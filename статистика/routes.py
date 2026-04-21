from flask import Blueprint, render_template
from .logic import get_stats
from constants import STATUSES, PLATFORMS

bp = Blueprint('stats_bp', __name__, template_folder='templates')


@bp.route("/stats")
def stats():
    data = get_stats()
    return render_template("stats.html", tab="stats", data=data, statuses=STATUSES, platforms=PLATFORMS)
