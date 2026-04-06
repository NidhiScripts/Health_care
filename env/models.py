from pydantic import BaseModel, ConfigDict
from typing import List, Dict, Literal

class Observation(BaseModel):
    model_config = ConfigDict(extra='forbid')
    
    symptoms: List[str]
    medical_history: List[str]
    current_medication: List[str]
    tests_done: List[str]
    test_results: Dict[str, str]
    step_count: int

class Action(BaseModel):
    model_config = ConfigDict(extra='forbid')
    
    action_type: Literal["test", "diagnose"]
    value: str
