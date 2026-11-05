from typing import List, Dict
from ..models import DFAModel, ValidationResponse


def validate_dfa_model(dfa: DFAModel) -> ValidationResponse:
    errors: List[str] = []
    warnings: List[str] = []
    missing_transitions: List[Dict[str, str]] = []

    state_set = set(dfa.states)

    if not dfa.states:
        errors.append("DFA must have at least one state.")

    if not dfa.alphabet:
        errors.append("Alphabet cannot be empty.")

    if dfa.start_state not in state_set:
        errors.append(f"Start state '{dfa.start_state}' is not in the states list.")

    for acc in dfa.accept_states:
        if acc not in state_set:
            errors.append(f"Accept state '{acc}' is not in the states list.")

    for s in dfa.states:
        for sym in dfa.alphabet:
            dest = dfa.transitions.get(s, {}).get(sym)
            if not dest or dest not in state_set:
                missing_transitions.append({"state": s, "symbol": sym})

    if not dfa.accept_states:
        warnings.append("No accepting states defined (DFA will reject all strings).")

    is_complete = len(missing_transitions) == 0
    is_valid = len(errors) == 0 and is_complete

    # Determine dead state candidate name
    candidate = "dead"
    idx = 1
    while candidate in state_set:
        candidate = f"dead{idx}"
        idx += 1

    return ValidationResponse(
        is_valid=is_valid,
        is_complete=is_complete,
        errors=errors,
        warnings=warnings,
        missing_transitions=missing_transitions,
        dead_state_candidate=candidate
    )
