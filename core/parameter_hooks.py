def notion_create_page_hook(params):
    if "parent_type" not in params:
        choice = input("🔧 Notion: Is the parent a 'database' or a 'page'? [database/page]: ").strip().lower()
        if choice not in {"database", "page"}:
            print("⚠️ Invalid choice. Defaulting to 'database'.")
            choice = "database"
        params["parent_type"] = choice
    return params


HOOKS = {
    "notion.create_page": notion_create_page_hook
}
