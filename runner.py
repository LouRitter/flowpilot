import json
import sys
import os
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
    "github.get_pr_description": github.run,
    "slack.send_message": slack.run,
    "discord.send_message": slack.run,
    "api.fetch_hacker_news": api.run,
    "api.http_get": api.run,
    "weather.fetch_forecast": weather.run,
    "doc.generate_summary": doc.run,
    "doc.save_to_file": doc.run
}

def resolve_templates(obj, context):
    if isinstance(obj, str):
        try:
            return Template(obj).render(context)
        except Exception as e:
            return f"[Template error: {e}]"
    elif isinstance(obj, dict):
        return {k: resolve_templates(v, context) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [resolve_templates(v, context) for v in obj]
    else:
        return obj

def run_step(step, context):
    step_type = step.type
    params = resolve_templates(step.params, context)
    print(f"\n➡️ Running step: {step_type}")

    # Check static handlers first
    if step_type in STEP_HANDLERS:
        output = STEP_HANDLERS[step_type](params, context)
        return output

    # Check if _step_type is defined (e.g. github.query_issues)
    step_meta_type = step.params.get("_step_type", "")
    if "." in step_meta_type:
        module_name = step_meta_type.split(".")[0]
        try:
            module = __import__(f"connectors.{module_name}", fromlist=["run"])
            return module.run(params, context)
        except Exception as e:
            print(f"❌ Failed to run {step_type} from connector '{module_name}': {e}")
            return None

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

    workflow_path = sys.argv[1]

    if not os.path.exists(workflow_path):
        print(f"❌ Workflow file not found: {workflow_path}")
        sys.exit(1)

    with open(workflow_path) as f:
        raw_data = json.load(f)

    sanitized = sanitize_workflow_dict(raw_data)
    workflow = Workflow(**sanitized)
    run_workflow(workflow)