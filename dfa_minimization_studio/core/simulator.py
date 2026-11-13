"""
String Execution Simulator for DFA acceptance testing.
"""

from typing import List, Tuple, Dict, Any
from core.dfa import DFA


def simulate_string(dfa: DFA, input_str: str) -> Tuple[bool, List[str], List[str]]:
    """
    Executes input_str on dfa.
    Returns:
        (is_accepted, state_path, symbols_read)
    """
    curr = dfa.initial_state
    path = [curr]
    symbols = []

    for char in input_str:
        if char not in dfa.alphabet:
            # Undefined symbol: rejected
            return False, path, symbols
        dest = dfa.get_transition(curr, char)
        if not dest:
            return False, path, symbols
        curr = dest
        path.append(curr)
        symbols.append(char)

    accepted = curr in dfa.final_states
    return accepted, path, symbols


def simulate_both(original_dfa: DFA, minimal_dfa: DFA, input_str: str) -> Dict[str, Any]:
    """Runs input_str on both original and minimized DFAs and confirms agreement."""
    orig_acc, orig_path, symbols = simulate_string(original_dfa, input_str)
    min_acc, min_path, _ = simulate_string(minimal_dfa, input_str)

    # Detailed step records
    steps = []
    for i in range(len(symbols) + 1):
        char = symbols[i - 1] if i > 0 else None
        steps.append({
            "step": i,
            "char": char if char is not None else "Start",
            "original_state": orig_path[i] if i < len(orig_path) else "Error",
            "minimal_state": min_path[i] if i < len(min_path) else "Error",
        })

    return {
        "input_string": input_str if input_str != "" else "ε (empty string)",
        "original_accepted": orig_acc,
        "minimal_accepted": min_acc,
        "agreement": orig_acc == min_acc,
        "original_path": orig_path,
        "minimal_path": min_path,
        "steps": steps
    }


def batch_simulate(original_dfa: DFA, minimal_dfa: DFA, test_strings: List[str]) -> List[Dict[str, Any]]:
    return [simulate_both(original_dfa, minimal_dfa, s) for s in test_strings]
