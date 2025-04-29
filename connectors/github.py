# connectors/github.py

import requests
import json
from core.secrets import SecretsManager

def run(params: dict, context: dict = None):
    secrets = SecretsManager()

    token = secrets.get("GITHUB_TOKEN")
    if not token:
        print("❌ GitHub token not found in secrets.")
        return None
    repo = secrets.get("GITHUB_REPO")
    if not repo:
        print("❌ GitHub repository not found in secrets.")
        return None

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
