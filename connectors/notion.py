# connectors/notion.py

import requests
from core.secrets import SecretsManager

def run(params: dict, context: dict = None):
    secrets = SecretsManager()
    notion_token = secrets.get("NOTION_TOKEN")

    # User must now specify parent_id (page_id or database_id)
    parent_id = params.get("parent_id")
    if not parent_id:
        raise ValueError("Missing 'parent_id' for Notion page creation.")

    title = params.get("title", "Untitled Page")
    properties = params.get("properties", {})
    children = params.get("children", [])

    headers = {
        "Authorization": f"Bearer {notion_token}",
        "Notion-Version": "2022-06-28",
        "Content-Type": "application/json"
    }

    body = {
        "parent": {"database_id": parent_id},  # Or page_id (later improve detection)
        "properties": properties or {
            "Name": {
                "title": [
                    {"text": {"content": title}}
                ]
            }
        },
        "children": children
    }

    response = requests.post("https://api.notion.com/v1/pages", headers=headers, json=body)

    if response.status_code != 200:
        print(f"❌ Failed to create Notion page: {response.text}")
        return None

    print("✅ Notion page created successfully")
    return response.json().get("url")
