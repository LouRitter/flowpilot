import json
from core.schema import Workflow
from pydantic import ValidationError
from  openai import OpenAI
import os
from dotenv import load_dotenv
import re

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def resolve_template(template: str, context: dict):
    pattern = r"{{\s*(.*?)\s*}}"
    matches = re.findall(pattern, template)

    for match in matches:
        # Split by dots for deep lookup
        parts = match.split(".")
        value = context
        try:
            for part in parts:
                if part.isdigit():
                    value = value[int(part)]
                else:
                    value = value[part]
            template = template.replace(f"{{{{ {match} }}}}", str(value))
        except Exception as e:
            template = template.replace(f"{{{{ {match} }}}}", f"[ERROR: {e}]")
    return template

def run_step(step, context):
    step_type = step.type
    params = step.params

    if step_type == "ai.summarize":
        input_text = resolve_template(params.get("text", ""), context)
        print("🧠 Calling OpenAI to summarize...")
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "user", "content": f"Summarize this:\n\n{input_text}"}
            ],
            temperature=0.2
        )
        return response.choices[0].message.content

    elif step_type == "email.send":
        to = resolve_template(params["to"], context)
        subject = resolve_template(params["subject"], context)
        body = resolve_template(params["body"], context)
        print(f"📧 Sending email to {to}:\nSubject: {subject}\nBody:\n{body}")
        return "Email sent (mocked)"

    elif step_type == "api.fetch_hacker_news":
        print("🌐 Fetching Hacker News top stories (mock)...")
        return "1. Story A\n2. Story B\n3. Story C"

    else:
        print(f"⚠️ Unknown step type: {step_type}")
        return None

def run_workflow_from_file(filepath):
    with open(filepath, "r") as f:
        data = json.load(f)
    try:
        wf = Workflow(**data)
    except ValidationError as e:
        print("❌ Invalid workflow:", e)
        return

    print(f"🚀 Running workflow: {wf.name}")
    context = {"trigger": wf.trigger.params, "steps": {}}

    for i, step in enumerate(wf.steps):
        print(f"\n➡️ Step {i}: {step.type}")
        output = run_step(step, context)
        context["steps"][i] = {"output": output}
        print(f"✅ Output:\n{output}")

    print("\n🎉 Workflow complete.")

if __name__ == "__main__":
    run_workflow_from_file("workflows/weekly_hn.json")
