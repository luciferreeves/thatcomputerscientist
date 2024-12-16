from apps.pagoda.models import PagodaSites
import random
import string
import re


def pagoda_unique_site_id_generator():
    site_id = "".join(random.choices(string.ascii_letters + string.digits, k=16))
    if PagodaSites.objects.filter(siteUniqueIdentifier=site_id).exists():
        return pagoda_unique_site_id_generator()
    return site_id


def pagoda_verification_record_generator(record_type):
    if record_type == "DNS":
        txtName = "".join(random.choices(string.ascii_letters + string.digits, k=8))
        txtValue = "".join(random.choices(string.ascii_letters + string.digits, k=48))
        return txtName, txtValue
    elif record_type == "Meta":
        metaName = "".join(random.choices(string.ascii_letters + string.digits, k=8))
        metaValue = "".join(random.choices(string.ascii_letters + string.digits, k=48))
        return metaName, metaValue
    else:
        return None, None


def pagoda_url_sanitizer(url):
    if not url.startswith("http://") and not url.startswith("https://"):
        url = f"http://{url}"

    # Validate if the URL is valid
    regex = re.compile(
        r"^(?:http|ftp)s?://"
        r"(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}|"
        r"localhost|"
        r"\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})"
        r"(?::\d+)?"
        r"(?:/?|[/?]\S+)$",
        re.IGNORECASE,
    )

    if not regex.match(url):
        return None
    return url
