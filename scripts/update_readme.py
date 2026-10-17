#!/usr/bin/env python3
"""Refresh the generated sections of README.md from live GitHub data.

Run daily by .github/workflows/refresh.yml. Only the text between the
<!-- stats:start/end --> and <!-- oss:start/end --> markers is rewritten.
"""
import json
import os
import re
import sys
import urllib.parse
import urllib.request
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

USER = "Abhishek1106kr"
TEAM_REPOS = ["BIS-Standards-AI-Assistant/BIS", "SIH-2026-Celestials/pulli_kolam"]
README = Path(__file__).resolve().parent.parent / "README.md"
TOKEN = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")


def request(url, body=None):
    headers = {"Accept": "application/vnd.github+json", "User-Agent": f"{USER}-profile"}
    if TOKEN:
        headers["Authorization"] = f"Bearer {TOKEN}"
    data = json.dumps(body).encode() if body is not None else None
    with urllib.request.urlopen(urllib.request.Request(url, data=data, headers=headers), timeout=30) as resp:
        return json.load(resp)


def api(path, **params):
    query = f"?{urllib.parse.urlencode(params)}" if params else ""
    return request(f"https://api.github.com{path}{query}")


def graphql(query, **variables):
    result = request("https://api.github.com/graphql", {"query": query, "variables": variables})
    if result.get("errors"):
        raise RuntimeError(result["errors"][0]["message"])
    return result["data"]


def merged_prs_elsewhere():
    items, page = [], 1
    while True:
        batch = api("/search/issues", q=f"is:pr is:merged author:{USER} -user:{USER}",
                    sort="created", order="desc", per_page=100, page=page)["items"]
        items += batch
        if len(batch) < 100 or page == 10:
            return items
        page += 1


def team_commits(repo):
    for person in api(f"/repos/{repo}/contributors", per_page=100):
        if person["login"].lower() == USER.lower():
            return person["contributions"]
    return 0


def stats_section(now, merged):
    year_start = datetime(now.year, 1, 1, tzinfo=timezone.utc).isoformat()
    user = graphql("""
        query($login: String!, $from: DateTime!) {
          user(login: $login) {
            createdAt
            repositories(ownerAffiliations: OWNER, privacy: PUBLIC, isFork: false) { totalCount }
            contributionsCollection(from: $from) {
              contributionCalendar { totalContributions }
              totalPullRequestContributions
              totalIssueContributions
            }
          }
        }""", login=USER, **{"from": year_start})["user"]
    year = user["contributionsCollection"]
    projects = {pr["repository_url"].split("/repos/")[1] for pr in merged}
    commits = [team_commits(repo) for repo in TEAM_REPOS]
    since = datetime.fromisoformat(user["createdAt"].replace("Z", "+00:00")).strftime("%b %Y")
    return "\n".join([
        "| | |",
        "|:--|:--|",
        f"| **{year['contributionCalendar']['totalContributions']:,}** contributions in {now.year} "
        f"| **{year['totalPullRequestContributions']}** PRs · **{year['totalIssueContributions']}** issues opened |",
        f"| **{len(merged)}** PRs merged outside my own repos | across **{len(projects)}** projects |",
        f"| top contributor on **2** Smart India Hackathon 2026 repos | **{' + '.join(map(str, commits))}** commits |",
        f"| **{user['repositories']['totalCount']}** public repos of my own | on GitHub since **{since}** |",
        "",
        "<sub>pulled from the GitHub API by a daily Action — commits only when a number changes</sub>",
    ])


def oss_section(now, merged):
    by_repo = defaultdict(list)
    for pr in merged:
        by_repo[pr["repository_url"].split("/repos/")[1]].append(pr)
    rows = ["| project | license | merged | latest |", "|:--|:--|--:|:--|"]
    for repo, prs in sorted(by_repo.items(), key=lambda kv: -len(kv[1])):
        meta = api(f"/repos/{repo}")
        license_id = (meta.get("license") or {}).get("spdx_id") or "—"
        latest = "<br>".join(f"[{pr['title'].replace('|', '/')}]({pr['html_url']})" for pr in prs[:3])
        if len(prs) > 3:
            latest += f"<br><sub>+{len(prs) - 3} more</sub>"
        rows.append(f"| [{repo}](https://github.com/{repo})<br><sub>★ {meta['stargazers_count']:,}</sub> "
                    f"| `{license_id}` | {len(prs)} | {latest} |")
    return "\n".join(rows)


def replace_between(text, name, body):
    pattern = re.compile(rf"(<!-- {name}:start -->\n).*?(<!-- {name}:end -->)", re.S)
    if not pattern.search(text):
        sys.exit(f"README is missing the {name} markers")
    return pattern.sub(lambda m: m.group(1) + body + "\n" + m.group(2), text)


def main():
    now = datetime.now(timezone.utc)
    merged = merged_prs_elsewhere()
    text = README.read_text(encoding="utf-8")
    updated = replace_between(text, "stats", stats_section(now, merged))
    updated = replace_between(updated, "oss", oss_section(now, merged))
    if updated != text:
        README.write_text(updated, encoding="utf-8")
        print("README updated")
    else:
        print("README already current")


if __name__ == "__main__":
    main()
