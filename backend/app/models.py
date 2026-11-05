from typing import List, Dict, Optional, Literal
from pydantic import BaseModel, Field


class DFAModel(BaseModel):
    states: List[str]
    alphabet: List[str]
    start_state: str
    accept_states: List[str]
    transitions: Dict[str, Dict[str, str]]


class ValidationRequest(BaseModel):
    dfa: DFAModel


class ValidationResponse(BaseModel):
    is_valid: bool
    is_complete: bool
    errors: List[str]
    warnings: List[str]
    missing_transitions: List[Dict[str, str]]
    dead_state_candidate: Optional[str] = "dead"


class TraceStepHighlights(BaseModel):
    active_states: List[str] = Field(default_factory=list)
    splitter_block: List[str] = Field(default_factory=list)
    unreachable_states: List[str] = Field(default_factory=list)
    split_blocks: List[List[str]] = Field(default_factory=list)
    marked_pairs: List[List[str]] = Field(default_factory=list)
    active_pair: List[str] = Field(default_factory=list)
    target_pair: List[str] = Field(default_factory=list)
    mark_reason: Optional[str] = None


class TraceStep(BaseModel):
    step_id: int
    total_steps: int
    phase: Literal["unreachable_removal", "initial_partition", "refinement", "done"]
    title: str
    description: str
    notation: Optional[str] = None
    highlights: TraceStepHighlights = Field(default_factory=TraceStepHighlights)
    partition_state: List[List[str]] = Field(default_factory=list)


class MinimizeRequest(BaseModel):
    dfa: DFAModel
    algorithm: Literal["table_filling", "moore"] = "table_filling"


class MinimizeResponse(BaseModel):
    algorithm: str
    original_dfa: DFAModel
    unreachable_states: List[str]
    pruned_dfa: DFAModel
    trace: List[TraceStep]
    minimal_dfa: DFAModel
    state_mapping: Dict[str, str]
    is_already_minimal: bool


class SimulateRequest(BaseModel):
    original_dfa: DFAModel
    minimal_dfa: Optional[DFAModel] = None
    input_string: str


class ExecutionResult(BaseModel):
    accepted: bool
    path: List[str]
    error: Optional[str] = None


class SimulateResponse(BaseModel):
    input_string: str
    is_valid_alphabet: bool
    alphabet_error: Optional[str] = None
    original_result: ExecutionResult
    minimized_result: Optional[ExecutionResult] = None
    agreement: bool
