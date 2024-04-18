import math
import os
import re

import requests
from django.shortcuts import render
from dotenv import load_dotenv
from github import Github
from dev_status.utils import (
    relative_date,
    text_lines,
    text_loc,
    size_format,
    highlight_code,
)

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
        {
            "name": repo["node"]["name"],
            "description": repo["node"]["description"],
            "forkCount": repo["node"]["forkCount"],
            "homepageUrl": repo["node"]["homepageUrl"],
            "isArchived": repo["node"]["isArchived"],
            "isFork": repo["node"]["isFork"],
            "licenseInfo": repo["node"]["licenseInfo"],
            "pushedAt": repo["node"]["pushedAt"],
            "stargazerCount": repo["node"]["stargazerCount"],
        }
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
    context["title"] = "My Repositories" if not search else ": Search " + search
    context["direction"] = direction
    context["num_pages"] = math.ceil(context["total_count"] / context["items"])
    context["repos"] = context["repos"][
        (context["page"] - 1) * context["items"] : context["page"] * context["items"]
    ]

    return render(request, "dev_status/home.html", context)


def get_repo(request, r=None, p=None):
    # this function handles request for browsing the contents of a repository
    # the path parameter is optional and is used to browse the contents of a directory
    # if the path is not provided, the root directory is displayed
    # if the path is a file, the file is displayed

    r = r or "thatcomputerscientist"  # repository.
    p = p or ""  # path.

    url = "https://api.github.com/graphql"
    headers = {"Authorization": "token " + os.getenv("GH_TOKEN")}
    parent = "/".join(p.split("/")[:-1]) if p and not len(p.split("/")) == 0 else None

    # get the contents of the repository along with the latest commit associated with each file or directory
    query = """
    query {{
        repository(owner: "luciferreeves", name: "{repo}") {{
            defaultBranchRef {{
                name
            }}
            object(expression: "HEAD:{path}") {{
                ... on Tree {{
                    entries {{
                        oid
                        name
                        type
                        path
                    }}
                }}
                ... on Blob {{
                    oid
                    byteSize
                    text
                    isBinary
                }}
            }}
        }}
    }}
    """.format(
        repo=r, path=p
    )

    data = requests.post(url, json={"query": query}, headers=headers).json()

    tree = []
    try:
        viewMode = (
            "tree" if "entries" in data["data"]["repository"]["object"] else "blob"
        )
    except:
        viewMode = "blob"

    # default_branch = data["data"]["repository"]["defaultBranchRef"]["name"]

    # order tree by name and folder first if it is a tree
    if viewMode == "tree":
        tree = sorted(
            data["data"]["repository"]["object"]["entries"],
            key=lambda x: (x["type"], x["name"]),
        )
        # place folders first
        tree = sorted(tree, key=lambda x: x["type"], reverse=True)
    else:
        # if it is a blob, display the file
        tree = data["data"]["repository"]["object"]
        tree["path"] = p
        tree["name"] = p.split("/")[-1]
        if not tree["isBinary"]:
            tree["lines"] = text_lines(tree["text"])
            tree["loc"] = text_loc(tree["text"])
            tree["text"] = highlight_code(tree["text"], tree["name"])

    # get commit information for each file or directory
    if viewMode == "tree":
        query = """
        query {{
            repository(owner: "luciferreeves", name: "{repo}") {{
                defaultBranchRef {{
                    target {{
                        ... on Commit {{
        """.format(
            repo=r
        )

        for entry in tree:
            # make path character only
            entry["uniquename"] = re.sub(r"[^a-zA-Z]", "", entry["path"])

            query += """
            {uniquename}: history(first: 1, path: "{path}") {{
                nodes {{
                    committedDate
                    message
                }}
            }}
            """.format(
                path=entry["path"], uniquename=entry["uniquename"]
            )

        query += "\n}\n}\n}\n}\n}"

        commit_data = requests.post(url, json={"query": query}, headers=headers).json()
        try:
            for entry in tree:
                entry["commit"] = commit_data["data"]["repository"]["defaultBranchRef"][
                    "target"
                ][entry["uniquename"]]["nodes"][0]
                entry = relative_date(entry)
        except:
            pass

    context = {}
    context["title"] = "Repository: " + r + " - " + p
    context["files"] = tree
    context["parent"] = parent
    context["repo"] = r

    if "byteSize" in tree:
        tree["size"] = size_format(tree["byteSize"])
    # isImage?
    if viewMode == "blob":
        context["files"]["def_branch"] = data["data"]["repository"]["defaultBranchRef"]["name"]
        if tree["name"].endswith((".png", ".jpg", ".jpeg", ".gif", ".svg", ".webp", ".ico", ".bmp")):
            context["files"]["isImage"] = True

    return render(request, "dev_status/repo.html", context)
