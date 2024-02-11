import math
import os

import requests
from django.shortcuts import render
from dotenv import load_dotenv
from github import Github

load_dotenv()
g = Github(os.getenv("GH_TOKEN"))


# Create your views here.
def home(request):
    page = request.GET.get("page") or 1
    items = request.GET.get("items") or 10
    sort = request.GET.get("sort") or "pushed"
    direction = request.GET.get("direction") or "desc"
    search = request.GET.get("search") or ""
    context = {}
    sort_map = {
        "updated": "UPDATED_AT",
        "stars": "STARGAZERS",
        "pushed": "PUSHED_AT",
        "created": "CREATED_AT",
        "name": "NAME",
    }
    direction_map = {"desc": "DESC", "asc": "ASC"}

    # make request to github api to get page of repos and total count of repos
    url = "https://api.github.com/graphql"
    headers = {"Authorization": "token " + os.getenv("GH_TOKEN")}
    user = "luciferreeves"

    query = """
    query {{
        user(login: "{user}") {{
            repositories(
                first: 100
                orderBy: {{field: {sort}, direction: {direction}}}
                ownerAffiliations: OWNER
                privacy: PUBLIC
            ) {{
                totalCount
                edges {{
                    node {{
                        name
                        description
                        forkCount
                        homepageUrl
                        isArchived
                        isFork
                        licenseInfo {{
                            name
                        }}
                        pushedAt
                        stargazerCount
                    }}
                }}
            }}
        }}
    }}
    """.format(
        user=user, sort=sort_map[sort], direction=direction_map[direction]
    )
    data = requests.post(url, json={"query": query}, headers=headers).json()
    repos = [
        {"name": repo["node"]["name"], "description": repo["node"]["description"], "forkCount": repo["node"]["forkCount"], "homepageUrl": repo["node"]["homepageUrl"], "isArchived": repo["node"]["isArchived"], "isFork": repo["node"]["isFork"], "licenseInfo": repo["node"]["licenseInfo"], "pushedAt": repo["node"]["pushedAt"], "stargazerCount": repo["node"]["stargazerCount"]}
        for repo in data["data"]["user"]["repositories"]["edges"]
    ]
    total_count = data["data"]["user"]["repositories"]["totalCount"]

    # convert pushedAt to date
    for repo in repos:
        repo["pushedAt"] = repo["pushedAt"].split("T")[0]


    context["search"] = search
    if search:
        context["repos"] = [
            repo
            for repo in repos
            if search.lower() in repo["name"].lower()
            or search.lower() in repo["description"].lower()
        ]
        context["total_count"] = len(context["repos"])
    else:
        context["repos"] = repos
        context["total_count"] = total_count

    # calculate pagination
    context["page"] = int(page)
    context["items"] = int(items)
    context["sort"] = sort
    context["direction"] = direction
    context["num_pages"] = math.ceil(context["total_count"] / context["items"])
    context["repos"] = context["repos"][
        (context["page"] - 1) * context["items"] : context["page"] * context["items"]
    ]

    return render(request, "dev_status/home.html", context)


def get_repo(request, r="thatcomputerscientist", p=None):
    repository = "luciferreeves/{}".format(r)
    parent = None
    if p and not len(p.split("/")) == 0:
        parent = "/".join(p.split("/")[:-1])
    contents = g.get_repo(repository).get_contents(p or "")
    context = {}
    try:
        files = []
        while contents:
            file_content = contents.pop(0)
            files.append(file_content)
        context["title"] = "Tree - {}".format(p)
        context["files"] = files
        context["parent"] = parent
        context["repo"] = r
    except:
        context["title"] = "File - {}".format(p)
        context["file"] = contents.html_url
        context["parent"] = parent
        context["repo"] = r
    finally:
        return render(request, "dev_status/repo.html", context)
