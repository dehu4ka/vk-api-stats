import time
from flask import Blueprint, render_template, current_app
from services.cache import get_cameras, get_health, invalidate_cameras
from services.stats import compute_summary

bp = Blueprint("dashboard", __name__)


@bp.get("/")
def index():
    client = current_app.config["RT_CLIENT"]
    cameras = get_cameras(client)
    summary = compute_summary(cameras)
    health = get_health(client)
    return render_template("dashboard.html",
                           summary=summary,
                           health=health,
                           now=time.time())


@bp.get("/api/stats")
def api_stats():
    client = current_app.config["RT_CLIENT"]
    invalidate_cameras()
    cameras = get_cameras(client)
    summary = compute_summary(cameras)
    health = get_health(client)
    return render_template("partials/stats_cards.html",
                           summary=summary,
                           health=health)
