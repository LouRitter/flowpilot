def run(params: dict, context: dict) -> str:
    url = params.get("url")
    print(f"🌐 [HTTP] Making GET request to: {url}")
    return f"Fetched from {url} (mocked)"
