from django.shortcuts import render
from thatcomputerscientist.utils import i18npatterns
from apps.pagoda.models import PagodaSites
from django.contrib.auth.decorators import login_required
from internal.pagoda_utilities import (
    pagoda_unique_site_id_generator,
    pagoda_verification_record_generator,
    pagoda_url_sanitizer,
)
from django.http import (
    HttpResponse,
    HttpResponseNotFound,
    HttpResponseRedirect,
)
from django.urls import reverse
from django.contrib import messages
import dns.resolver
import requests
from bs4 import BeautifulSoup


# Create your views here.
@login_required
def home(request):
    META = {
        "title": "The Pagoda Realm",
    }
    LANGUAGE_CODE = i18npatterns(request.LANGUAGE_CODE)
    request.meta.update(META)

    pagoda_sites = PagodaSites.get_sites_created_by_user(request.user)
    if request.method == "GET":
        context = {
            "pagoda_sites": pagoda_sites,
        }
        return render(request, f"{LANGUAGE_CODE}/pagoda/home.html", context)
    elif request.method == "POST":
        name = request.POST.get("site_name")
        url = request.POST.get("root_url")
        url = pagoda_url_sanitizer(url)
        verificationMethod = request.POST.get("verification_method")
        siteUniqueIdentifier = pagoda_unique_site_id_generator()
        verficationRecordName, verificationRecordValue = (
            pagoda_verification_record_generator(verificationMethod)
        )
        if not url:
            messages.error(
                request,
                "The URL provided is not valid. Please provide a valid URL.",
                extra_tags="pagodaError",
            )
            return HttpResponseRedirect(request.META.get("HTTP_REFERER"))

        if url.replace("http://", "").replace("https://", "") in [
            site.url.replace("http://", "").replace("https://", "")
            for site in pagoda_sites
        ]:
            messages.error(
                request,
                "This site can not be added to The Pagoda Realm at this moment. If you alredy have this site listed in The Pagoda Realm, please verify it or delete and re-add the website if you wish to change the verification method.",
                extra_tags="pagodaError",
            )
            return HttpResponseRedirect(request.META.get("HTTP_REFERER"))

        PagodaSites.objects.create(
            owner=request.user,
            name=name,
            url=url,
            siteUniqueIdentifier=siteUniqueIdentifier,
            verificationMethod=verificationMethod,
            verficationRecordName=verficationRecordName,
            verificationRecordValue=verificationRecordValue,
        )

        return HttpResponseRedirect(reverse("pagoda:home"))
    else:
        pass

    return render(request, f"{LANGUAGE_CODE}/pagoda/home.html")


@login_required
def site_dashboard(request, site_id):
    LANGUAGE_CODE = i18npatterns(request.LANGUAGE_CODE)
    try:
        site = PagodaSites.objects.get(siteUniqueIdentifier=site_id, owner=request.user)
        context = {
            "site": site,
        }
        META = {
            "title": f"Manage {site.name} — The Pagoda Realm",
        }
        request.meta.update(META)
        if site.verified:
            return render(
                request, f"{LANGUAGE_CODE}/pagoda/site_dashboard.html", context
            )

        if not site.verified:
            return render(
                request, f"{LANGUAGE_CODE}/pagoda/site_verification.html", context
            )
    except PagodaSites.DoesNotExist:
        return HttpResponseNotFound()


@login_required
def check_verification_status(request, site_id):
    site = PagodaSites.objects.get(siteUniqueIdentifier=site_id, owner=request.user)

    if site.verified:
        return HttpResponseRedirect(request.META.get("HTTP_REFERER"))

    if site.verificationMethod == "DNS":
        domain = site.url.replace("http://", "").replace("https://", "")
        txt_name = site.verficationRecordName
        txt_value = site.verificationRecordValue
        domain = txt_name + "." + domain.split("/")[0]

        try:
            txt_records = dns.resolver.resolve(domain, "TXT")
            for txt_record in txt_records:
                for txt_string in txt_record.strings:
                    if txt_string.decode("utf-8") == txt_value:
                        site.verified = True
                        site.save()
                        return HttpResponseRedirect(request.META.get("HTTP_REFERER"))
        except dns.resolver.NoAnswer:
            pass
        return HttpResponseRedirect(request.META.get("HTTP_REFERER"))
    elif site.verificationMethod == "Meta":
        domain = site.url
        response = requests.get(domain)
        soup = BeautifulSoup(response.text, "html.parser")
        meta_tags = soup.find_all("meta")
        for meta_tag in meta_tags:
            if (
                meta_tag.get("name") == site.verficationRecordName
                and meta_tag.get("content") == site.verificationRecordValue
            ):
                site.verified = True
                site.save()
                return HttpResponseRedirect(request.META.get("HTTP_REFERER"))
        return HttpResponseRedirect(request.META.get("HTTP_REFERER"))
    else:
        pass

    return HttpResponseNotFound()


@login_required
def delete_site(request, site_id):
    site = PagodaSites.objects.get(siteUniqueIdentifier=site_id, owner=request.user)
    if site:
        site.delete()
        return HttpResponseRedirect(reverse("pagoda:home"))
    else:
        messages.error(
            request,
            "The site could not be deleted. Please try again.",
            extra_tags="pagodaError",
        )
        return HttpResponseRedirect(reverse("pagoda:home"))
