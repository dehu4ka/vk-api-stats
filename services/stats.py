import time
from collections import defaultdict


def compute_summary(cameras: list[dict]) -> dict:
    total = len(cameras)
    online = sum(1 for c in cameras if c.get("is_online"))
    offline = total - online

    by_vendor = defaultdict(lambda: {"total": 0, "online": 0, "offline": 0})
    by_model = defaultdict(lambda: {"total": 0, "online": 0, "offline": 0})
    by_dc = defaultdict(lambda: {"total": 0, "online": 0, "offline": 0})
    memory_issues = []
    long_offline = []

    now = time.time()

    for cam in cameras:
        vendor = cam.get("vendor") or "Unknown"
        model = cam.get("model") or "Unknown"
        dc = (cam.get("data_center") or {}).get("name", "Unknown")
        is_on = cam.get("is_online", False)
        status_key = "online" if is_on else "offline"

        by_vendor[vendor]["total"] += 1
        by_vendor[vendor][status_key] += 1
        by_model[model]["total"] += 1
        by_model[model][status_key] += 1
        by_dc[dc]["total"] += 1
        by_dc[dc][status_key] += 1

        mc = cam.get("memory_card_state") or {}
        mc_state = mc.get("state", "")
        if mc_state and mc_state not in ("CardOK", "CardNotFound", "Unknown", ""):
            memory_issues.append(cam)

        if not is_on and cam.get("offline_since"):
            duration = now - cam["offline_since"]
            if duration > 3600:
                long_offline.append((cam, duration))

    long_offline.sort(key=lambda x: x[1], reverse=True)

    top_vendors = sorted(by_vendor.items(), key=lambda x: x[1]["total"], reverse=True)[:10]

    return {
        "total": total,
        "online": online,
        "offline": offline,
        "online_pct": round(online / total * 100, 1) if total else 0,
        "offline_pct": round(offline / total * 100, 1) if total else 0,
        "by_vendor": dict(by_vendor),
        "top_vendors": top_vendors,
        "by_model": dict(by_model),
        "by_dc": dict(by_dc),
        "memory_issues": memory_issues[:20],
        "long_offline": long_offline[:10],
    }


def analyze_archive(fragments: list[dict], now: float) -> dict:
    if not fragments:
        return {
            "total_fragments": 0,
            "depth_days": 0,
            "total_recorded": 0,
            "total_span": 0,
            "coverage_pct": 0,
            "avg_fragment": 0,
            "gaps_count": 0,
            "max_gap": 0,
            "total_gap_time": 0,
            "daily": [],
        }

    sorted_frags = sorted(fragments, key=lambda f: f["since"])
    earliest = sorted_frags[0]["since"]
    latest = sorted_frags[-1]["till"]
    total_span = latest - earliest
    total_recorded = sum(f["till"] - f["since"] for f in sorted_frags)
    depth_days = (now - earliest) / 86400

    gaps = []
    for i in range(1, len(sorted_frags)):
        gap = sorted_frags[i]["since"] - sorted_frags[i - 1]["till"]
        if gap > 60:
            gaps.append(gap)

    # per-day breakdown
    daily_data = defaultdict(lambda: {
        "recorded": 0, "fragments": 0, "gaps": [], "frags_list": [],
    })
    for f in sorted_frags:
        day = time.strftime("%Y-%m-%d", time.localtime(f["since"]))
        daily_data[day]["recorded"] += f["till"] - f["since"]
        daily_data[day]["fragments"] += 1
        daily_data[day]["frags_list"].append(f)

    for i in range(1, len(sorted_frags)):
        gap = sorted_frags[i]["since"] - sorted_frags[i - 1]["till"]
        if gap > 60:
            day = time.strftime("%Y-%m-%d", time.localtime(sorted_frags[i]["since"]))
            daily_data[day]["gaps"].append(gap)

    daily = []
    for day_str in sorted(daily_data.keys()):
        d = daily_data[day_str]
        day_start = time.mktime(time.strptime(day_str, "%Y-%m-%d"))
        day_end = day_start + 86400
        actual_end = min(day_end, now)
        day_span = actual_end - day_start

        # timeline segments as percentages of 24h for visual bar
        timeline = []
        for f in d["frags_list"]:
            seg_start = max(f["since"], day_start)
            seg_end = min(f["till"], day_end)
            if seg_end > seg_start:
                left_pct = (seg_start - day_start) / 86400 * 100
                width_pct = (seg_end - seg_start) / 86400 * 100
                t_from = time.strftime("%H:%M:%S", time.localtime(seg_start))
                t_to = time.strftime("%H:%M:%S", time.localtime(seg_end))
                dur = format_duration(seg_end - seg_start)
                timeline.append({
                    "left": round(left_pct, 2),
                    "width": round(max(width_pct, 0.3), 2),
                    "title": f"{t_from} — {t_to} ({dur})",
                })

        coverage = (d["recorded"] / day_span * 100) if day_span > 0 else 0

        daily.append({
            "date": day_str,
            "fragments": d["fragments"],
            "recorded": d["recorded"],
            "recorded_h": round(d["recorded"] / 3600, 1),
            "coverage_pct": round(coverage, 1),
            "gaps_count": len(d["gaps"]),
            "max_gap": max(d["gaps"]) if d["gaps"] else 0,
            "timeline": timeline,
        })

    return {
        "total_fragments": len(sorted_frags),
        "depth_days": round(depth_days, 1),
        "total_recorded": total_recorded,
        "total_span": total_span,
        "coverage_pct": round(total_recorded / total_span * 100, 1) if total_span else 0,
        "avg_fragment": total_recorded / len(sorted_frags) if sorted_frags else 0,
        "gaps_count": len(gaps),
        "max_gap": max(gaps) if gaps else 0,
        "total_gap_time": sum(gaps),
        "daily": daily,
    }


def format_duration(seconds: float) -> str:
    if seconds < 60:
        return f"{int(seconds)} сек"
    elif seconds < 3600:
        return f"{int(seconds // 60)} мин"
    elif seconds < 86400:
        h = int(seconds // 3600)
        m = int((seconds % 3600) // 60)
        return f"{h} ч {m} мин"
    else:
        d = int(seconds // 86400)
        h = int((seconds % 86400) // 3600)
        return f"{d} дн {h} ч"
