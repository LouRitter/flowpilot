from __future__ import annotations
from pydantic import BaseModel, create_model, model_validator, TypeAdapter
from typing import Literal, Union, List, Dict, Any
from connectors.registry import REGISTRY

# === Dynamically generate connector models from REGISTRY ===

step_models = {}
trigger_models = {}

for key, meta in REGISTRY.items():
    model_name = meta["model_name"]
    fields = {
        "params": (Dict[str, Any], ...)
    }

    if meta.get("category") == "trigger":
        # Example: "scheduler.cron" → type = scheduler, event = cron
        type_part, event_part = key.split(".", 1)
        fields["type"] = (Literal[type_part], type_part)
        fields["event"] = (Literal[event_part], event_part)
        trigger_models[key] = create_model(model_name, **fields, __base__=BaseModel)
    else:
        # Regular step
        fields["type"] = (Literal[key], key)
        step_models[key] = create_model(model_name, **fields, __base__=BaseModel)

# === Build dynamic type unions ===
Step = Union[tuple(step_models.values())]
Trigger = Union[tuple(trigger_models.values())]

# === Workflow Schema ===
class Workflow(BaseModel):
    type: Literal["workflow"]
    name: str
    version: str = "1.0"
    trigger: Trigger
    steps: List[Step]

    @model_validator(mode="before")
    @classmethod
    def ensure_parsed_models(cls, values: dict) -> dict:
        # Use TypeAdapter to validate Trigger and Step union types
        trigger_adapter = TypeAdapter(Trigger)
        step_adapter = TypeAdapter(Step)

        if isinstance(values.get("trigger"), dict):
            values["trigger"] = trigger_adapter.validate_python(values["trigger"])

        values["steps"] = [
            step_adapter.validate_python(step) if isinstance(step, dict) else step
            for step in values.get("steps", [])
        ]
        return values
