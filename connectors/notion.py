import requests
from core.secrets import SecretsManager

def run(params: dict, context: dict = None):
    secrets = SecretsManager()
    notion_token = secrets.get("NOTION_TOKEN")

    parent_id = params.get("parent_id")
    parent_type = params.get("parent_type", "database")
    if not parent_id:
        raise ValueError("Missing 'parent_id' for Notion page creation.")

    title = params.get("title", "Untitled Page")
    input_properties = params.get("properties", {})
    children = params.get("children", [])

    headers = {
        "Authorization": f"Bearer {notion_token}",
        "Notion-Version": "2022-06-28",
        "Content-Type": "application/json"
    }

    # Determine parent type
    if parent_type == "database":
        parent = {"database_id": parent_id}
    elif parent_type == "page":
        parent = {"page_id": parent_id}
    else:
        raise ValueError("Invalid 'parent_type'. Must be 'database' or 'page'.")

    valid_properties = {}
    title_property_name = None

    if parent_type == "database":
        db_response = requests.get(f"https://api.notion.com/v1/databases/{parent_id}", headers=headers)
        if db_response.status_code != 200:
            print(f"❌ Failed to retrieve database schema: {db_response.status_code} {db_response.text}")
            return None

        db_schema = db_response.json()
        db_properties = db_schema.get("properties", {})

        # Identify title field
        for prop_name, prop_info in db_properties.items():
            if prop_info.get("type") == "title":
                title_property_name = prop_name
                break

        if not title_property_name:
            print("❌ No title property found in the database schema.")
            return None

        # Convert input properties if possible
        for prop_name, prop_value in input_properties.items():
            expected_type = db_properties.get(prop_name, {}).get("type")

            # If it's in the schema and type matches, use it directly
            if expected_type:
                if isinstance(prop_value, dict) and expected_type in prop_value:
                    valid_properties[prop_name] = prop_value
                elif isinstance(prop_value, str) and expected_type in {"title", "rich_text"}:
                    # Convert plain string to rich_text or title
                    valid_properties[prop_name] = {
                        expected_type: [
                            {"text": {"content": prop_value}}
                        ]
                    }
                else:
                    print(f"⚠️ Property '{prop_name}' has mismatched or unsupported value. Skipping.")
            else:
                print(f"⚠️ Property '{prop_name}' not found in database schema. Skipping.")

        # Ensure title property is always present
        if title_property_name not in valid_properties:
            valid_properties[title_property_name] = {
                "title": [
                    {"text": {"content": title}}
                ]
            }

    else:
        # Page parent: title is enough
        valid_properties = {
            "title": [
                {"text": {"content": title}}
            ]
        }

    # Build and send request
    body = {
        "parent": parent,
        "properties": valid_properties,
        "children": children
    }

    response = requests.post("https://api.notion.com/v1/pages", headers=headers, json=body)

    if response.status_code != 200:
        print(f"❌ Failed to create Notion page: {response.status_code} {response.text}")
        return None

    print("✅ Notion page created successfully")
    return response.json().get("url")
