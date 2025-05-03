import os
import json
from openai import OpenAI
from dotenv import load_dotenv
from core.schema import Workflow
from pydantic import ValidationError
from connectors.registry import REGISTRY
from core.parameter_hooks import HOOKS

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

MISSING = "[MISSING]"

def generate_workflow(prompt: str) -> Workflow:
    system_msg = (
        "You are a helpful AI that generates automation workflows in JSON format. "
        "Each workflow must include:\n"
        "- A trigger of type 'scheduler' (event: 'cron') or 'webhook' (event: 'receive')\n"
        "- A list of steps where each step has a valid 'type' from the registry\n"
        "- All required 'params' for each step based on its type\n"
        "If you do not know the value of a required param, use '[MISSING]'.\n"
        "Do not invent unsupported triggers or step types. "
        "The JSON should be valid and parsable."
    )

    examples = """
User: Summarize GitHub issues and save to Notion
JSON:
{
  "name": "github_issues_to_notion_summary",
  "type": "workflow",
  "trigger": {
    "type": "scheduler",
    "event": "cron",
    "params": {
      "expression": "0 9 * * *"
    }
  },
  "steps": [
    {
      "type": "github.query_issues",
      "params": {
        "repo": "[MISSING]"
      }
    },
    {
      "type": "ai.summarize",
      "params": {
        "text": "{{ steps.0.output }}"
      }
    },
    {
      "type": "notion.create_page",
      "params": {
        "parent_id": "[MISSING]",
        "title": "GitHub Summary",
        "properties": {
          "Summary": "{{ steps.1.output }}"
        }
      }
    }
  ]
}
"""

    def build_connector_reference():
        lines = ["Available connector steps:\n"]
        for step_type, meta in REGISTRY.items():
            desc = meta.get("description", "")
            params = ", ".join(meta.get("required_params", []))
            lines.append(f"- {step_type}: {desc} (params: {params})")
        return "\n".join(lines)

    capability_list = build_connector_reference()
    full_prompt = f"{capability_list}\n\n{examples}\nUser: {prompt}\nJSON:\n"

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
        data = complete_trigger(data)
        data = inject_step_metadata(data)
        data = fill_missing_parameters(data)
        return Workflow(**data)
    except (json.JSONDecodeError, ValidationError) as e:
        raise ValueError(f"Invalid workflow output: {e}")

def sanitize_workflow_dict(data: dict) -> dict:
    if "trigger" in data:
        trigger = data["trigger"]
        trigger_type = trigger.get("type", "")
        if "." in trigger_type:
            type_part, event_part = trigger_type.split(".", 1)
            trigger["type"] = type_part
            trigger["event"] = event_part
        if "params" not in trigger:
            trigger["params"] = {}

        key = f"{trigger['type']}.{trigger.get('event', '')}"
        if key not in REGISTRY:
            print(f"⚠️ Unknown trigger type '{trigger['type']}' — replacing with 'scheduler.cron'")
            trigger["type"] = "scheduler"
            trigger["event"] = "cron"
            trigger["params"] = {"expression": "0 9 * * *"}

    for i, step in enumerate(data.get("steps", [])):
        step_type = step.get("type")
        if step_type not in REGISTRY:
            print(f"⚠️ Unknown step type '{step_type}' — replacing with 'ai.summarize'")
            step["type"] = "ai.summarize"
            step["params"] = {"text": "Top news stories"}
        else:
            required = REGISTRY[step_type].get("required_params", [])
            step["params"] = scrub_fake_placeholders(step["params"], required)
            validate_step(step, i)

    print("🧼 Sanitized workflow:", json.dumps(data, indent=2))
    return data

def scrub_fake_placeholders(params: dict, keys: list) -> dict:
    for key in keys:
        val = params.get(key, "")
        if val.lower() in {"my_repo", "notion_parent_id", "your-email@example.com", "abc123", "xyz456"}:
            params[key] = MISSING
    return params

def complete_trigger(workflow: dict) -> dict:
    trigger = workflow.get("trigger")

    if trigger and trigger.get("type") in {"scheduler", "webhook"} and "event" in trigger:
        return workflow

    step_types = [step.get("type", "") for step in workflow.get("steps", [])]

    for step_type in step_types:
        meta = REGISTRY.get(step_type)
        suggestion = meta.get("suggested_trigger") if meta else None
        if suggestion:
            type_part, event_part = suggestion.split(".")
            print(f"🔍 Inferred trigger: {suggestion} (from step '{step_type}')")
            workflow["trigger"] = {
                "type": type_part,
                "event": event_part,
                "params": {}
            }
            if suggestion == "scheduler.cron":
                workflow["trigger"]["params"]["expression"] = "0 9 * * *"
            return workflow

    print("⚠️ This workflow doesn't specify when or how it should run.")
    print("💡 What should trigger this workflow?")
    print("1. Scheduler (run every day at 9am)")
    print("2. Webhook (trigger manually or from another system)")
    choice = input("Enter 1 or 2: ").strip()

    if choice == "1":
        cron = input("Enter cron expression (default '0 9 * * *'): ").strip() or "0 9 * * *"
        workflow["trigger"] = {
            "type": "scheduler",
            "event": "cron",
            "params": {
                "expression": cron
            }
        }
    elif choice == "2":
        workflow["trigger"] = {
            "type": "webhook",
            "event": "receive",
            "params": {}
        }
    else:
        print("❌ Invalid choice. Exiting.")
        exit(1)

    return workflow

def validate_step(step: dict, step_index: int):
    step_type = step["type"]
    required_params = REGISTRY[step_type]["required_params"]
    missing = [p for p in required_params if p not in step.get("params", {})]
    if missing:
        raise ValueError(f"Missing parameters {missing} for step {step_index} ({step_type})")


def fill_missing_parameters(data: dict) -> dict:
    for i, step in enumerate(data.get("steps", [])):
        step_type = step.get("type")
        step_params = step.setdefault("params", {})

        if step_type not in REGISTRY:
            continue

        required = REGISTRY[step_type]["required_params"]
        for param in required:
            value = step_params.get(param)
            if value in (MISSING, "", None):
                user_value = input(f"🔧 Step {i} ({step_type}): Please enter value for '{param}': ")
                step_params[param] = user_value

        # 🔁 Run step-specific parameter hook
        if step_type in HOOKS:
            step["params"] = HOOKS[step_type](step_params)

    return data

def inject_step_metadata(data: dict) -> dict:
    for step in data.get("steps", []):
        step_type = step.get("type", "")
        dynamic_prefixes = ("github.", "notion.", "slack.", "discord.")
        if any(step_type.startswith(prefix) for prefix in dynamic_prefixes):
            step.setdefault("params", {})["_step_type"] = step_type
    return data
