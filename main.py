import os
from core.prompt_handler import generate_workflow
from dotenv import load_dotenv
import json
import datetime

load_dotenv()

WORKFLOWS_DIR = "workflows"

def prompt_for_workflow():
    print("🧠 Describe your desired workflow (e.g., 'Summarize GitHub issues and create Notion tasks'):")
    user_prompt = input("> ")

    try:
        wf = generate_workflow(user_prompt)
        print("\n✅ Generated Workflow:\n")
        print(wf.model_dump_json(indent=2))

        save = input("\n💾 Save this workflow to file? (y/n): ").strip().lower()
        if save == "y":
            name = wf.name or f"workflow_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}"
            filename = f"{name}.json"
            filepath = os.path.join(WORKFLOWS_DIR, filename)

            with open(filepath, "w") as f:
                f.write(wf.model_dump_json(indent=2))

            print(f"✅ Saved to: {filepath}")

    except Exception as e:
        print("\n❌ Error generating workflow:")
        print(e)

if __name__ == "__main__":
    prompt_for_workflow()
