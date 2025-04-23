from pydantic import BaseModel
from typing import Optional, List, Dict, Any

class Trigger(BaseModel):
    type: str
    event: str
    params: Optional[Dict] = {}

class Step(BaseModel):
    type: str
    params: Optional[Dict] = {}
    condition: Optional[Dict] = None

class Workflow(BaseModel):
    name: str
    trigger: Trigger
    steps: List[Step]
