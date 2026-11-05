from typing import Tuple, Optional
from ..models import DFAModel, ExecutionResult, SimulateResponse


def simulate_dfa(dfa: DFAModel, input_str: str) -> ExecutionResult:
    current = dfa.start_state
    path = [current]

    for char in input_str:
        trans = dfa.transitions.get(current, {})
        nxt = trans.get(char)
        if not nxt:
            return ExecutionResult(
                accepted=False,
                path=path,
                error=f"No transition defined from state '{current}' on input '{char}'"
            )
        current = nxt
        path.append(current)

    is_accepted = current in dfa.accept_states
    return ExecutionResult(
        accepted=is_accepted,
        path=path,
        error=None
    )


def run_simulation(original_dfa: DFAModel, minimal_dfa: Optional[DFAModel], input_str: str) -> SimulateResponse:
    # Validate alphabet
    alphabet_set = set(original_dfa.alphabet)
    invalid_chars = [c for c in input_str if c not in alphabet_set]

    if invalid_chars:
        return SimulateResponse(
            input_string=input_str,
            is_valid_alphabet=False,
            alphabet_error=f"Invalid character(s) '{', '.join(sorted(set(invalid_chars)))}' not in alphabet {{{', '.join(sorted(alphabet_set))}}}",
            original_result=ExecutionResult(accepted=False, path=[original_dfa.start_state], error="Invalid alphabet character"),
            minimized_result=None,
            agreement=False
        )

    orig_result = simulate_dfa(original_dfa, input_str)
    min_result = simulate_dfa(minimal_dfa, input_str) if minimal_dfa else None

    agreement = (orig_result.accepted == min_result.accepted) if min_result else True

    return SimulateResponse(
        input_string=input_str,
        is_valid_alphabet=True,
        alphabet_error=None,
        original_result=orig_result,
        minimized_result=min_result,
        agreement=agreement
    )
