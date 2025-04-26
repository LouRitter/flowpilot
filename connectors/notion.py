import requests
import os
import json

def run(params: dict, context: dict = None):
    with open(".secrets.json") as f:
        secrets = json.load(f)

    NOTION_TOKEN = secrets["NOTION_TOKEN"]
    DATABASE_ID = secrets["NOTION_DATABASE_ID"]

    title = params.get("title", "Untitled Task")
    content = params.get("content", "No content")

    headers = {
        "Authorization": f"Bearer {NOTION_TOKEN}",
        "Notion-Version": "2022-06-28",
        "Content-Type": "application/json"
    }

    body = {
        "parent": {"database_id": DATABASE_ID},
        "properties": {
            "Name": {
                "title": [
                    {"text": {"content": title}}
                ]
            }
        },
        "children": [
            {
                "object": "block",
                "type": "paragraph",
                "paragraph": {
                    "rich_text": [{"text": {"content": content}}]
                }
            }
        ]
    }

    res = requests.post("https://api.notion.com/v1/pages", headers=headers, json=body)

    if res.status_code != 200:
        print("❌ Failed to create Notion task:", res.text)
        return None

    print("✅ Notion task created")
    return res.json().get("url")
