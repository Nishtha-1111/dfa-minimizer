from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from .models import (
    ValidationRequest,
    ValidationResponse,
    MinimizeRequest,
    MinimizeResponse,
    SimulateRequest,
    SimulateResponse,
)
from .algorithms.validator import validate_dfa_model
from .algorithms.table_filling import run_table_filling
from .algorithms.hopcroft import run_hopcroft
from .algorithms.moore import run_moore
from .algorithms.simulator import run_simulation

app = FastAPI(
    title="DFA Minimizer API",
    description="FastAPI service for step-by-step DFA minimization via Hopcroft and Moore algorithms",
    version="1.0.0",
)

# Enable CORS for Vite frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/health")
def health_check():
    return {"status": "ok", "service": "DFA Minimizer API"}


@app.post("/api/validate", response_model=ValidationResponse)
def validate_endpoint(req: ValidationRequest):
    return validate_dfa_model(req.dfa)


@app.post("/api/minimize", response_model=MinimizeResponse)
def minimize_endpoint(req: MinimizeRequest):
    val = validate_dfa_model(req.dfa)
    if val.errors:
        raise HTTPException(status_code=400, detail="; ".join(val.errors))

    if req.algorithm == "table_filling":
        trace, minimal_dfa, state_mapping, unreach, pruned = run_table_filling(req.dfa)
    elif req.algorithm == "moore":
        trace, minimal_dfa, state_mapping, unreach, pruned = run_moore(req.dfa)
    else:
        raise HTTPException(status_code=400, detail=f"Unsupported algorithm '{req.algorithm}'. Must be 'table_filling' or 'moore'.")

    is_already_minimal = (len(unreach) == 0) and (len(minimal_dfa.states) == len(req.dfa.states))

    return MinimizeResponse(
        algorithm=req.algorithm,
        original_dfa=req.dfa,
        unreachable_states=unreach,
        pruned_dfa=pruned,
        trace=trace,
        minimal_dfa=minimal_dfa,
        state_mapping=state_mapping,
        is_already_minimal=is_already_minimal,
    )


@app.post("/api/simulate", response_model=SimulateResponse)
def simulate_endpoint(req: SimulateRequest):
    return run_simulation(req.original_dfa, req.minimal_dfa, req.input_string)
