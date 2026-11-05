# Backend Architecture & API Reference

This document details the backend service powering the **DFA Minimizer**, including module structure, data models, endpoints, and automated tests.

---

## 1. Directory Structure

```
backend/
├── app/
│   ├── algorithms/
│   │   ├── __init__.py
│   │   ├── moore.py             # Moore's signature partition refinement
│   │   ├── simulator.py         # Dual-DFA string simulation engine
│   │   ├── table_filling.py     # Myhill-Nerode lower-triangular table method
│   │   ├── unreachable.py       # BFS reachability and state elimination
│   │   └── validator.py         # DFA validation & dead-state autofill
│   ├── __init__.py
│   ├── main.py                  # FastAPI application and route handlers
│   └── models.py                # Strongly typed Pydantic models
└── tests/
    ├── __init__.py
    └── test_api.py              # Pytest test suite (7 automated tests)
```

---

## 2. Core Data Models (`models.py`)

### `DFAModel`
Represents any valid deterministic finite automaton:
```python
class DFAModel(BaseModel):
    states: List[str]
    alphabet: List[str]
    start_state: str
    accept_states: List[str]
    transitions: Dict[str, Dict[str, str]]  # transitions[state][symbol] = target_state
```

### `TraceStepHighlights`
Metadata attached to each step to instruct the frontend visualizer what to illuminate:
```python
class TraceStepHighlights(BaseModel):
    active_states: List[str] = Field(default_factory=list)
    splitter_block: List[str] = Field(default_factory=list)
    unreachable_states: List[str] = Field(default_factory=list)
    split_blocks: List[List[str]] = Field(default_factory=list)
    marked_pairs: List[List[str]] = Field(default_factory=list) # [{p, q}, ...]
    active_pair: List[str] = Field(default_factory=list)        # [p, q] currently tested
    target_pair: List[str] = Field(default_factory=list)        # [p', q'] that caused mark
    mark_reason: Optional[str] = None
```

### `TraceStep`
An individual atomic step in the algorithm playback:
```python
class TraceStep(BaseModel):
    step_id: int
    total_steps: int
    phase: Literal["unreachable_removal", "initial_partition", "refinement", "done"]
    title: str
    description: str
    notation: Optional[str] = None
    highlights: TraceStepHighlights = Field(default_factory=TraceStepHighlights)
    partition_state: List[List[str]] = Field(default_factory=list)
```

---

## 3. API Endpoints (`main.py`)

### 1. `POST /api/validate`
Validates DFA completeness, verifies single start state, and identifies missing transitions.
- **Request Body**:
  ```json
  {
    "dfa": { ...DFAModel... }
  }
  ```
- **Response**:
  ```json
  {
    "is_valid": true,
    "is_complete": true,
    "errors": [],
    "warnings": [],
    "missing_transitions": [],
    "dead_state_candidate": "dead"
  }
  ```

### 2. `POST /api/minimize`
Executes unreachable state pruning followed by the requested minimization algorithm (`table_filling` or `moore`).
- **Request Body**:
  ```json
  {
    "dfa": { ...DFAModel... },
    "algorithm": "table_filling"
  }
  ```
- **Response**:
  ```json
  {
    "algorithm": "table_filling",
    "original_dfa": { ... },
    "unreachable_states": ["u1"],
    "pruned_dfa": { ... },
    "trace": [ ...TraceStep[]... ],
    "minimal_dfa": { ... },
    "state_mapping": { "A": "{A, B}", "B": "{A, B}", ... },
    "is_already_minimal": false
  }
  ```

### 3. `POST /api/simulate`
Simulates an input string across both the original DFA and the minimal DFA simultaneously.
- **Request Body**:
  ```json
  {
    "original_dfa": { ... },
    "minimal_dfa": { ... },
    "input_string": "010"
  }
  ```
- **Response**:
  ```json
  {
    "input_string": "010",
    "original_accepted": true,
    "minimal_accepted": true,
    "agreement": true,
    "original_path": ["A", "B", "D", "E"],
    "minimal_path": ["{A, B}", "{A, B}", "{C, D}", "{E, F}"],
    "steps": [
      {
        "char_index": 0,
        "symbol": "0",
        "original_current": "A",
        "original_next": "B",
        "minimal_current": "{A, B}",
        "minimal_next": "{A, B}"
      },
      ...
    ]
  }
  ```

### 4. `GET /api/health`
Health check endpoint returning `{"status": "ok", "service": "DFA Minimizer API"}`.

---

## 4. Automated Testing Suite (`tests/test_api.py`)

The test suite exercises all core features using `pytest`:
1. `test_health`: Verifies API uptime.
2. `test_validation`: Verifies complete DFAs pass and missing transitions are caught.
3. `test_minimize_textbook_table_filling_and_moore`: Confirms both Table-Filling and Moore reduce the textbook 6-state DFA to identical 3-state quotient machines: `{A, B}`, `{C, D}`, `{E, F}`.
4. `test_minimize_already_minimal`: Validates that already-minimal DFAs are detected and returned intact.
5. `test_minimize_unreachable_removal`: Confirms unreachable states are pruned via BFS before minimization.
6. `test_edge_cases`: Verifies single-state, all-accepting, and no-accepting DFAs.
7. `test_simulate_endpoint`: Verifies dual-machine simulation with string path generation.

Run the test suite:
```powershell
$env:PYTHONPATH="."
python -m pytest backend/tests/test_api.py -v
```
