def run(params: dict, context: dict) -> str:
    filename = params.get("filename", "output.md")
    content = params.get("content", "")
    print(f"📄 [Doc] Writing content to {filename}")
    return f"Saved to {filename} (mocked)"
