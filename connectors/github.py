# connectors/github.py

import requests
import json

def run(params: dict, context: dict = None):
    with open(".secrets.json") as f:
        secrets = json.load(f)

    token = secrets["GITHUB_TOKEN"]
    repo = secrets["GITHUB_REPO"]

    title = params.get("title", "New issue")
    body = params.get("body", "No description")

    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github+json"
    }

    url = f"https://api.github.com/repos/{repo}/issues"
    payload = {"title": title, "body": body}

    res = requests.post(url, headers=headers, json=payload)

    if res.status_code != 201:
        print("❌ Failed to create GitHub issue:", res.text)
        return None

    print("✅ GitHub issue created")
    return res.json().get("html_url")
