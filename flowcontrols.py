from connectors.registry import REGISTRY

def list_connectors():
    print("🔌 Available Connectors:\n")
    for step_type, meta in REGISTRY.items():
        desc = meta.get("description", "")
        params = ", ".join(meta.get("required_params", []))
        print(f"- {step_type} → {desc} (params: {params}) \n")

if __name__ == "__main__":
    import sys
    if sys.argv[1] == "list-connectors":
        list_connectors()
