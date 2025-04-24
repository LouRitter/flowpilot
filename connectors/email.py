def run(params: dict, context: dict) -> str:
    to = params.get("to")
    subject = params.get("subject")
    body = params.get("body")

    print(f"📧 [Email] Sending to {to}:\nSubject: {subject}\nBody:\n{body}")
    return "Email sent (mocked)"
