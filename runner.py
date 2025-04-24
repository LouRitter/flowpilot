import json
import sys
from core.schema import Workflow
from core.prompt_handler import sanitize_workflow_dict
from connectors import ai, email, notion, github, slack, api, doc, weather
from jinja2 import Template

# Maps step type to handler
STEP_HANDLERS = {
    "ai.summarize": ai.run,
    "email.send": email.run,
    "notion.create_task": notion.run,
    "notion.append_block": notion.run,
    "github.comment_pr": github.run,
    "github.label_check": github.run,
    "github.create_issue": github.run,
    "slack.send_message": slack.run,
    "discord.send_message": slack.run,
    "api.fetch_hacker_news": api.run,
    "api.http_get": api.run,
    "weather.fetch_forecast": weather.run,
    "doc.generate_summary": doc.run,
    "doc.save_to_file": doc.run
}


def resolve_templates(params: dict, context: dict) -> dict:
    resolved = {}
    for key, value in params.items():
        if isinstance(value, str):
            try:
                resolved[key] = Template(value).render(context)
            except Exception as e:
                resolved[key] = f"[Template error: {e}]"
        else:
            resolved[key] = value
    return resolved


def run_step(step, context):
    step_type = step.type
    params = resolve_templates(step.params, context)
    print(f"\n➡️ Running step: {step_type}")

    if step_type in STEP_HANDLERS:
        output = STEP_HANDLERS[step_type](params, context)
        return output
    else:
        print(f"⚠️ Unknown step type: {step_type}")
        return None


def run_workflow(workflow: Workflow):
    print(f"\n🚀 Running workflow: {workflow.name}")
    context = {
        "trigger": workflow.trigger.params,
        "steps": {}
    }

    for i, step in enumerate(workflow.steps):
        output = run_step(step, context)
        context["steps"][i] = {"output": output}
        print(f"✅ Step {i} output: {output}")

    print("\n🎉 Workflow complete.")


if __name__ == "__main__":
    print("🏁 Runner started")

    if len(sys.argv) < 2:
        print("Usage: python runner.py workflows/your_workflow.json")
        sys.exit(1)

    # Load workflow JSON
    with open(sys.argv[1], "r") as f:
        raw_data = json.load(f)

    # Sanitize and parse as Pydantic model
    sanitized = sanitize_workflow_dict(raw_data)
    workflow = Workflow(**sanitized)

    # Run the workflow
    run_workflow(workflow)
