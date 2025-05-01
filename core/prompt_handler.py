import os
import json
from openai import OpenAI
from dotenv import load_dotenv
from core.schema import Workflow
from pydantic import ValidationError
from connectors.registry import REGISTRY

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def generate_workflow(prompt: str) -> Workflow:
    system_msg = (
        "You are a helpful AI that generates automation workflows in JSON format. "
        "Use only step types and parameters from the provided list. "
        "Each step must have a valid 'type' and all required 'params'."
    )

    examples = """
User: When a GitHub issue is created, summarize it and create a Notion page.
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
      "type": "notion.create_page",
      "params": {
        "parent_id": "abc123",
        "title": "{{ trigger.title }}",
        "properties": {
          "Summary": "{{ steps.0.output }}"
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
        if key in REGISTRY:
            for param in REGISTRY[key]["required_params"]:
                if param not in trigger["params"]:
                    trigger["params"][param] = "[MISSING]"

    for i, step in enumerate(data.get("steps", [])):
        step_type = step.get("type")
        if step_type not in REGISTRY:
            print(f"⚠️ Unknown step type '{step_type}' — replacing with 'ai.summarize'")
            step["type"] = "ai.summarize"
            step["params"] = {"text": "Top news stories"}
        else:
            validate_step(step, i)

    print("🧼 Sanitized workflow:", json.dumps(data, indent=2))
    return data

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
            if not step_params.get(param):
                user_value = input(f"🔧 Step {i}: Please enter value for required param '{param}' (for '{step_type}'): ")
                step_params[param] = user_value

    return data

def inject_step_metadata(data: dict) -> dict:
    """
    Adds _step_type to steps that require dynamic dispatch (e.g., github.*)
    """
    for step in data.get("steps", []):
        step_type = step.get("type", "")
        dynamic_prefixes = ("github.", "notion.", "slack.", "discord.")  # Add others as needed

        if any(step_type.startswith(prefix) for prefix in dynamic_prefixes):
            step.setdefault("params", {})["_step_type"] = step_type
    return data

