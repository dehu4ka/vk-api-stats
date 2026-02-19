from flask import Blueprint, render_template, request, current_app
from services.cache import get_cached_archives

bp = Blueprint("archives", __name__, url_prefix="/archives")

ITEMS_PER_PAGE = 50

STATUS_LABELS = {0: "NEW", 1: "ENQUEUED", 2: "ERROR", 3: "DONE"}


@bp.get("/")
def archive_list():
    client = current_app.config["RT_CLIENT"]
    page = max(1, request.args.get("page", 1, type=int))
    status_filter = request.args.get("status", "", type=str)
    offset = (page - 1) * ITEMS_PER_PAGE

    cache_key = f"archives:{offset}:{status_filter}"

    def fetch():
        return client.get_baked_archives(offset=offset, limit=ITEMS_PER_PAGE)

    data = get_cached_archives(client, cache_key, fetch)
    archives = data if isinstance(data, list) else data.get("baked_archives", data.get("archives", []))

    if status_filter:
        status_int = {v: k for k, v in STATUS_LABELS.items()}.get(status_filter.upper())
        if status_int is not None:
            archives = [a for a in archives if a.get("status") == status_int]

    has_next = len(archives) == ITEMS_PER_PAGE

    return render_template("archives.html",
                           archives=archives,
                           page=page,
                           has_next=has_next,
                           status_filter=status_filter,
                           STATUS_LABELS=STATUS_LABELS)
