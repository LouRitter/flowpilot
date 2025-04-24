# core/prompt_handler.py

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
        "Only use step types and params from the provided list. The JSON must match the schema exactly. "
        "Each step must have a 'type' from the list, and include all required 'params'."
    )
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
    def build_trigger_reference() -> str:
      lines = ["\nAvailable triggers:\n"]
      for key, meta in REGISTRY.items():
          if meta.get("category") != "trigger":
              continue
          desc = meta.get("description", "")
          params = ", ".join(meta["params"].keys())
          lines.append(f"- {key}: {desc} (params: {params})")
      return "\n".join(lines)

    def build_connector_reference() -> str:
        lines = ["Available connector steps:\n"]
        for step_type, meta in REGISTRY.items():
            if meta.get("category") == "trigger":
                continue  # skip triggers for now
            desc = meta.get("description", "")
            param_list = []
            for param, config in meta.get("params", {}).items():
                flag = "required" if config.get("required", True) else "optional"
                default = config.get("default", None)
                if default is not None:
                    param_list.append(f"{param} ({flag}, default: {default})")
                else:
                    param_list.append(f"{param} ({flag})")
            params_str = ", ".join(param_list)
            lines.append(f"- {step_type}: {desc} | params: {params_str}")
        return "\n".join(lines)

    capability_list = build_connector_reference() + build_trigger_reference()

    full_prompt = (
        f"{capability_list}\n\n"
        f"{examples}\n"
        f"User: {prompt}\nJSON:\n"
    )

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

def validate_step(step: dict, step_index: int):
    step_type = step.get("type")
    if step_type not in REGISTRY:
        raise ValueError(f"Unknown step type '{step_type}' at index {step_index}")
    
    schema = REGISTRY[step_type].get("params", {})
    for param, meta in schema.items():
      if meta.get("required", True) and param not in step.get("params", {}):
          raise ValueError(
            f"Missing required parameter '{param}' for step type '{step_type}' at index {step_index}"
          )

def validate_trigger(trigger: dict):
    key = f"{trigger.get('type')}.{trigger.get('event')}"
    if key not in REGISTRY:
        raise ValueError(f"Unknown trigger type '{key}'")

    schema = REGISTRY[key].get("params", {})
    for param, meta in schema.items():
        if meta.get("required", True) and param not in trigger.get("params", {}):
            raise ValueError(
                f"Missing required parameter '{param}' for trigger type '{key}'"
            )

def sanitize_workflow_dict(data: dict) -> dict:
    # --- Fix malformed trigger ---
  if "trigger" in data:
    trigger = data["trigger"]

    # Normalize "type.event" into type + event
    if "." in trigger.get("type", ""):
        type_part, event_part = trigger["type"].split(".", 1)
        trigger["type"] = type_part
        trigger["event"] = event_part

    trigger.setdefault("params", {})

    # Validate + fill required trigger params
    key = f"{trigger['type']}.{trigger['event']}"
    if key in REGISTRY:
        schema = REGISTRY[key]["params"]
        for param, meta in schema.items():
            if meta.get("required", True) and param not in trigger["params"]:
                print(f"⚠️ Trigger missing param '{param}' — inserting default.")
                trigger["params"][param] = meta.get("default", "[MISSING]")
    else:
        print(f"⚠️ Unknown trigger type '{key}' — workflow may not run properly.")
    validate_trigger(trigger)

    # --- Fix steps ---
    for i, step in enumerate(data.get("steps", [])):
        step_type = step.get("type")

        if step_type not in REGISTRY:
            print(f"⚠️ Unknown step type '{step_type}' — replacing with 'ai.summarize'")
            step_type = "ai.summarize"
            step["type"] = step_type
            step["params"] = {
                param: meta.get("default", "[MISSING]")
                for param, meta in REGISTRY[step_type]["params"].items()
                if meta.get("required", True)
            }
        else:
            # Validate required params and fill defaults
            step.setdefault("params", {})
            schema = REGISTRY[step_type]["params"]
            for param, meta in schema.items():
                if meta.get("required", True) and param not in step["params"]:
                    print(f"⚠️ Step {i} missing param '{param}', inserting default.")
                    step["params"][param] = meta.get("default", "[MISSING]")

        validate_step(step, i)

    print("🧼 Sanitized workflow:", json.dumps(data, indent=2))
    return data
