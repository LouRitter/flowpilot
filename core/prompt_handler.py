# core/prompt_handler.py

import os
import json
from openai import OpenAI
from dotenv import load_dotenv
from core.schema import Workflow
from pydantic import ValidationError

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def generate_workflow(prompt: str) -> Workflow:
    system_msg = "You are an workflow prompt generator. Generate a valid JSON object for a workflow based on the user's description."

    examples = """
User: When a GitHub issue is created, summarize it and create a Notion task.
JSON:
{
  "name": "issue_to_notion",
  "type": "workflow",
  "trigger": {
    "type": "github",
    "event": "issue_created",
    "params": {
      "repo": "my-org/my-repo"
    }
  },
  "steps": [
    {
      "type": "ai.summarize",
      "params": {
        "text": "{{ trigger.body }}"
      }
    },
    {
      "type": "notion.create_task",
      "params": {
        "title": "{{ trigger.title }}",
        "content": "{{ steps.0.output }}"
      }
    }
  ]
}
"""

    full_prompt = f"{examples}\nUser: {prompt}\nJSON:\n"

    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": system_msg},
            {"role": "user", "content": full_prompt}
        ],
        temperature=0.2,
        max_tokens=800
    )
    

    try:
        content = response.choices[0].message.content
        data = json.loads(content)
        data = sanitize_workflow_dict(data)
        return Workflow(**data)
    except (json.JSONDecodeError, ValidationError) as e:
        raise ValueError(f"Invalid workflow output: {e}")

def sanitize_workflow_dict(data: dict) -> dict:
    # 🧹 Fix misnamed or malformed trigger
    if "trigger" in data:
        trigger = data["trigger"]
        if trigger.get("type") == "schedule":  # AI often uses "schedule"
            trigger["type"] = "scheduler"
            trigger["event"] = "cron"
            trigger.setdefault("params", {"expression": "0 9 * * *"})

    # 🧹 Fix unknown step types
    allowed_types = {
        "ai.summarize",
        "email.send",
        "api.fetch_hacker_news",
        "notion.create_task"
    }

    for i, step in enumerate(data.get("steps", [])):
        if step["type"] not in allowed_types:
            print(f"⚠️ Unknown step type '{step['type']}' — replacing with 'ai.summarize'")
            step["type"] = "ai.summarize"
            step.setdefault("params", {"text": "Weather for New York"})
    print("🧼 Sanitized workflow:", json.dumps(data, indent=2))
    return data
