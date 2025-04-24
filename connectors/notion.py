def run(params: dict, context: dict) -> str:
    title = params.get("title")
    content = params.get("content")
    print(f"📝 [Notion] Creating task: {title}\nContent: {content}")
    return f"Created Notion task: {title}"
