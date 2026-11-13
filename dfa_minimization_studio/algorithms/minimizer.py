"""
Minimization Coordinator and Algorithm Comparator.
"""

import time
from typing import Dict, Any, Tuple
from core.dfa import DFA
from algorithms.hopcroft import hopcroft_minimize
from algorithms.moore import moore_minimize
from core.simulator import batch_simulate


def run_minimization(dfa: DFA, algorithm: str = "hopcroft") -> Dict[str, Any]:
    """
    Runs either Hopcroft or Moore minimization with metrics and history.
    """
    start_time = time.perf_counter()

    if algorithm.lower() == "moore":
        min_dfa, steps, mapping = moore_minimize(dfa)
        algo_name = "Moore's Algorithm"
    else:
        min_dfa, steps, mapping = hopcroft_minimize(dfa)
        algo_name = "Hopcroft's Algorithm"

    duration_ms = (time.perf_counter() - start_time) * 1000

    orig_count = len(dfa.states)
    min_count = len(min_dfa.states)
    states_removed = orig_count - min_count

    # Identify merged states
    merged_groups: Dict[str, list] = {}
    for orig, macro in mapping.items():
        merged_groups.setdefault(macro, []).append(orig)

    merged_only = {macro: sorted(members) for macro, members in merged_groups.items() if len(members) > 1}

    # Verify language equivalence with test strings
    test_strings = ["", "0", "1", "00", "01", "10", "11", "000", "010", "110", "1001", "0101"]
    # Filter symbols to match alphabet
    clean_tests = [s for s in test_strings if all(ch in dfa.alphabet for ch in s)]
    sim_res = batch_simulate(dfa, min_dfa, clean_tests)
    all_agreed = all(r["agreement"] for r in sim_res)

    return {
        "algorithm": algo_name,
        "algorithm_key": algorithm.lower(),
        "original_dfa": dfa,
        "minimal_dfa": min_dfa,
        "steps": steps,
        "state_mapping": mapping,
        "original_state_count": orig_count,
        "minimized_state_count": min_count,
        "states_removed": states_removed,
        "merged_states": merged_only,
        "final_partitions": list(merged_groups.values()),
        "iteration_count": len(steps),
        "execution_time_ms": round(duration_ms, 3),
        "equivalence_verified": all_agreed
    }


def compare_algorithms(dfa: DFA) -> Dict[str, Any]:
    """Runs both algorithms on the identical DFA and gathers comparative metrics."""
    hopcroft_res = run_minimization(dfa, "hopcroft")
    moore_res = run_minimization(dfa, "moore")

    return {
        "hopcroft": hopcroft_res,
        "moore": moore_res,
        "state_counts_match": hopcroft_res["minimized_state_count"] == moore_res["minimized_state_count"],
        "both_correct": hopcroft_res["equivalence_verified"] and moore_res["equivalence_verified"]
    }
