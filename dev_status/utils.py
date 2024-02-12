from datetime import datetime


def relative_date(entry):
    committedDate = datetime.strptime(
        entry["commit"]["committedDate"], "%Y-%m-%dT%H:%M:%SZ"
    )
    now = datetime.now()
    diff = now - committedDate
    if diff.days > 365:
        entry["commit"]["committedDate"] = str(diff.days // 365) + " year" + ("s" if diff.days // 365 > 1 else "") + " ago"
    elif diff.days > 30:
        entry["commit"]["committedDate"] = str(diff.days // 30) + " month" + ("s" if diff.days // 30 > 1 else "") + " ago"
    elif diff.days > 7:
        entry["commit"]["committedDate"] = str(diff.days // 7) + " week" + ("s" if diff.days // 7 > 1 else "") + " ago"
    elif diff.days > 0:
        entry["commit"]["committedDate"] = str(diff.days) + " day" + ("s" if diff.days > 1 else "") + " ago"
    elif diff.seconds > 3600:
        entry["commit"]["committedDate"] = str(diff.seconds // 3600) + " hour" + ("s" if diff.seconds // 3600 > 1 else "") + " ago"
    elif diff.seconds > 60:
        entry["commit"]["committedDate"] = str(diff.seconds // 60) + " minute" + ("s" if diff.seconds // 60 > 1 else "") + " ago"
    else:
        entry["commit"]["committedDate"] = "just now"

    return entry
