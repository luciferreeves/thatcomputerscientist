from datetime import datetime


def relative_date(entry):
    committedDate = datetime.strptime(
        entry["commit"]["committedDate"], "%Y-%m-%dT%H:%M:%SZ"
    )
    now = datetime.now()
    diff = now - committedDate
    if diff.days > 365:
        entry["commit"]["committedDate"] = str(diff.days // 365) + " years ago"
    elif diff.days > 30:
        entry["commit"]["committedDate"] = str(diff.days // 30) + " months ago"
    elif diff.days > 7:
        entry["commit"]["committedDate"] = str(diff.days // 7) + " weeks ago"
    elif diff.days > 0:
        entry["commit"]["committedDate"] = str(diff.days) + " days ago"
    elif diff.seconds > 3600:
        entry["commit"]["committedDate"] = str(diff.seconds // 3600) + " hours ago"
    elif diff.seconds > 60:
        entry["commit"]["committedDate"] = str(diff.seconds // 60) + " minutes ago"
    else:
        entry["commit"]["committedDate"] = "just now"

    return entry
