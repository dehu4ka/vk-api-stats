import time
from flask import Blueprint, render_template, request, current_app, abort
from services.cache import get_cameras
from services.stats import format_duration, analyze_archive

bp = Blueprint("cameras", __name__, url_prefix="/cameras")

ITEMS_PER_PAGE = 50


@bp.get("/")
def camera_list():
    client = current_app.config["RT_CLIENT"]
    cameras = get_cameras(client)

    q = request.args.get("q", "").strip().lower()
    status = request.args.get("status", "")
    vendor = request.args.get("vendor", "")
    dc = request.args.get("dc", "")

    filtered = cameras
    if q:
        filtered = [c for c in filtered
                    if q in (c.get("name") or "").lower()
                    or q in (c.get("address") or "").lower()
                    or q in (c.get("sn") or "").lower()
                    or q in (c.get("uid") or "").lower()]
    if status == "online":
        filtered = [c for c in filtered if c.get("is_online")]
    elif status == "offline":
        filtered = [c for c in filtered if not c.get("is_online")]
    if vendor:
        filtered = [c for c in filtered if c.get("vendor") == vendor]
    if dc:
        filtered = [c for c in filtered
                    if (c.get("data_center") or {}).get("name") == dc]

    vendors = sorted({c.get("vendor") or "Unknown" for c in cameras})
    dcs = sorted({(c.get("data_center") or {}).get("name", "Unknown") for c in cameras})

    page = max(1, request.args.get("page", 1, type=int))
    total = len(filtered)
    total_pages = max(1, (total + ITEMS_PER_PAGE - 1) // ITEMS_PER_PAGE)
    page = min(page, total_pages)
    start = (page - 1) * ITEMS_PER_PAGE
    page_cameras = filtered[start:start + ITEMS_PER_PAGE]

    return render_template("cameras.html",
                           cameras=page_cameras,
                           page=page,
                           total_pages=total_pages,
                           total=total,
                           vendors=vendors,
                           dcs=dcs,
                           q=request.args.get("q", ""),
                           status=status,
                           vendor=vendor,
                           dc=dc,
                           now=time.time(),
                           format_duration=format_duration)


@bp.get("/<uid>")
def camera_detail(uid: str):
    client = current_app.config["RT_CLIENT"]
    cameras = get_cameras(client)
    camera = next((c for c in cameras if c.get("uid") == uid), None)
    if not camera:
        abort(404)

    now_ts = time.time()
    now_int = int(now_ts)
    since_90d = now_int - 90 * 86400
    try:
        fragments = client.get_camera_fragments(uid, since_90d, now_int)
    except Exception:
        fragments = []

    archive = analyze_archive(fragments, now_ts)

    return render_template("camera_detail.html",
                           camera=camera,
                           archive=archive,
                           now=now_ts,
                           format_duration=format_duration)
