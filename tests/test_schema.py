# tests/test_schema.py (or try in main.py if you prefer)
from core.schema import Workflow

sample_workflow = {
    "name": "issue_to_notion",
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

# Validate and create Workflow object
wf = Workflow(**sample_workflow)

print(wf)
