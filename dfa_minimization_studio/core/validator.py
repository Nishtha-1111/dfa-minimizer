"""
DFA Validation, Reachability Analysis, and Dead State Synthesis.
"""

from typing import List, Tuple, Set
from core.dfa import DFA


class ValidationResult:
    def __init__(self):
        self.is_valid: bool = True
        self.is_complete: bool = True
        self.errors: List[str] = []
        self.warnings: List[str] = []
        self.missing_transitions: List[Tuple[str, str]] = []
        self.unreachable_states: List[str] = []

    def add_error(self, message: str):
        self.is_valid = False
        self.errors.append(message)

    def add_warning(self, message: str):
        self.warnings.append(message)


def compute_reachable_states(dfa: DFA) -> Set[str]:
    """Computes all states reachable from the initial state using BFS."""
    if not dfa.initial_state or dfa.initial_state not in dfa.states:
        return set()

    visited: Set[str] = {dfa.initial_state}
    queue: List[str] = [dfa.initial_state]

    while queue:
        curr = queue.pop(0)
        for sym in dfa.alphabet:
            nxt = dfa.get_transition(curr, sym)
            if nxt and nxt in dfa.states and nxt not in visited:
                visited.add(nxt)
                queue.append(nxt)

    return visited


def remove_unreachable_states(dfa: DFA) -> Tuple[DFA, Set[str]]:
    """Prunes states not reachable from the initial state."""
    reachable = compute_reachable_states(dfa)
    unreachable = dfa.states - reachable

    new_states = set(reachable)
    new_final = dfa.final_states & reachable
    new_transitions = {
        (s, sym): dest for (s, sym), dest in dfa.transitions.items()
        if s in reachable and dest in reachable
    }

    pruned_dfa = DFA(
        states=new_states,
        alphabet=set(dfa.alphabet),
        transitions=new_transitions,
        initial_state=dfa.initial_state,
        final_states=new_final
    )
    return pruned_dfa, unreachable


def validate_dfa(dfa: DFA) -> ValidationResult:
    result = ValidationResult()

    if not dfa.states:
        result.add_error("The DFA must contain at least one state.")
    if not dfa.alphabet:
        result.add_error("The alphabet Σ must contain at least one input symbol.")
    if not dfa.initial_state:
        result.add_error("An initial start state must be designated.")
    elif dfa.initial_state not in dfa.states:
        result.add_error(f"Initial state '{dfa.initial_state}' is not in the set of states.")

    for f in dfa.final_states:
        if f not in dfa.states:
            result.add_error(f"Final state '{f}' is not defined in the set of states.")

    # Check transition targets and symbols
    for (s, sym), dest in dfa.transitions.items():
        if s not in dfa.states:
            result.add_error(f"Transition originates from undefined state '{s}'.")
        if dest not in dfa.states:
            result.add_error(f"Transition targets undefined state '{dest}'.")
        if sym not in dfa.alphabet:
            result.add_error(f"Transition uses symbol '{sym}' outside the defined alphabet.")

    # Check completeness
    for s in dfa.states:
        for sym in dfa.alphabet:
            if (s, sym) not in dfa.transitions or not dfa.transitions[(s, sym)]:
                result.missing_transitions.append((s, sym))

    if result.missing_transitions:
        result.is_complete = False
        result.add_warning(
            f"DFA is incomplete: {len(result.missing_transitions)} transition(s) are missing. "
            "A complete DFA defines δ(q, σ) for every state and symbol."
        )

    # Reachability
    if dfa.initial_state in dfa.states:
        reachable = compute_reachable_states(dfa)
        unreach = dfa.states - reachable
        if unreach:
            result.unreachable_states = sorted(list(unreach))
            result.add_warning(
                f"Unreachable state(s) detected: {', '.join(result.unreachable_states)}. "
                "These will be pruned prior to partition minimization."
            )

    return result


def make_complete_with_dead_state(dfa: DFA) -> DFA:
    """Completes an incomplete DFA by routing missing transitions to a trap/dead state."""
    dead_name = "TRAP"
    counter = 1
    while dead_name in dfa.states:
        dead_name = f"TRAP_{counter}"
        counter += 1

    completed = dfa.clone()
    completed.states.add(dead_name)

    # Route existing missing transitions to dead state
    for s in dfa.states:
        for sym in dfa.alphabet:
            if (s, sym) not in completed.transitions or not completed.transitions[(s, sym)]:
                completed.transitions[(s, sym)] = dead_name

    # Add self loops on dead state
    for sym in dfa.alphabet:
        completed.transitions[(dead_name, sym)] = dead_name

    return completed
