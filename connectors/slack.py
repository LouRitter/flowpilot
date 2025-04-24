def run(params: dict, context: dict) -> str:
    channel = params.get("channel")
    message = params.get("message")
    print(f"💬 [Slack] Posting to #{channel}: {message}")
    return f"Message sent to Slack channel: #{channel}"
