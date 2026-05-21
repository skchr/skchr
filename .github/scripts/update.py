#!/usr/bin/env python3
import sys
import json
import urllib.request
from datetime import datetime


MONTH_EMOJIS = {
    1: '\U0001f305',
    2: '\U0001f338',
    3: '\U0001f33f',
    4: '\U0001f30a',
    5: '\U0001f304',
    6: '\U0001f333',
    7: '\U0001f3d4\ufe0f',
    8: '\u2601\ufe0f',
    9: '\U0001f343',
    10: '\U0001f33e',
    11: '\U0001f332',
    12: '\u26f0\ufe0f',
}


def fetch_gists(username):
    gists = []
    page = 1
    per_page = 100
    while True:
        url = f"https://api.github.com/users/{username}/gists?per_page={per_page}&page={page}"
        req = urllib.request.Request(url, headers={"User-Agent": "skchr-readme-update/1.0"})
        with urllib.request.urlopen(req) as response:
            data = json.loads(response.read())
            if not data:
                break
            gists.extend(data)
            link_header = response.headers.get("Link", "")
            if 'rel="next"' not in link_header:
                break
            page += 1
    return gists


def format_date(dt):
    suffixes = {1: 'st', 2: 'nd', 3: 'rd'}
    day = dt.day
    suffix = suffixes.get(day % 10, 'th') if day < 20 else 'th'
    return f"{day}{suffix} of {dt.strftime('%B')} \U0001f4c5"


def format_flat_date(dt):
    return dt.strftime('%B %d, %Y')


def generate_readme(gists_data):
    parsed = []
    for gist in gists_data:
        gist_id = gist["id"]
        description = gist["description"] or list(gist["files"].keys())[0]
        html_url = gist["html_url"]
        created_dt = datetime.fromisoformat(gist["created_at"].replace("Z", "+00:00")).replace(tzinfo=None)
        parsed.append({
            "id": gist_id,
            "description": description,
            "html_url": html_url,
            "created_dt": created_dt,
        })

    parsed.sort(key=lambda g: g["created_dt"], reverse=True)

    latest = parsed[0] if parsed else None
    remaining = parsed[1:] if len(parsed) > 1 else []

    readme = " "

    if latest:
        preview_url = f"https://skchbk.prjctimg.me/sketch/{latest['id']}"
        readme += f"""> [!important]
> > ##### **{format_date(latest['created_dt'])}**
> 
> ### [{latest['description']}]({latest['html_url']})
> - [Gist]({latest['html_url']})
> - [Preview]({preview_url})
>
> > > > > > > > > > > > > > > > > >
"""

    if remaining:
        readme += "\n\n## \U0001f5bc In case you missed it\n\n"
        for gist in remaining:
            preview_url = f"https://skchbk.prjctimg.me/sketch/{gist['id']}"
            readme += f"#### {format_flat_date(gist['created_dt'])} — {gist['description']}\n"
            readme += f"- [Gist]({gist['html_url']})\n"
            readme += f"- [Preview]({preview_url})\n\n"

    readme += f"""\
> [`skchr`](https://github.com/skchr) is a facet of [@prjctimg](https://github.com/prjctimg)
> 
> Updated daily from gists

"""
    return readme


def main():
    print("Fetching gists...", file=sys.stderr)
    gists_data = fetch_gists("skchr")
    print(f"Found {len(gists_data)} gists", file=sys.stderr)
    readme_content = generate_readme(gists_data)
    if len(sys.argv) > 1 and sys.argv[1] == "--write":
        with open("README.md", "w") as f:
            f.write(readme_content)
        print("README.md updated!", file=sys.stderr)
    else:
        print(readme_content)


if __name__ == "__main__":
    main()
