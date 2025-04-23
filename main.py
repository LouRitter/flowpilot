from core.prompt_handler import generate_workflow

if __name__ == "__main__":
    user_prompt = "Describe your workflow here:"
    try:
        workflow = generate_workflow(user_prompt)
        print("Generated Workflow:")
        print(workflow.model_dump_json(indent=2))
    except ValueError as e:
        print(f"Failed to generate workflow: {e}")