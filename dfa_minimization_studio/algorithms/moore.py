"""
Moore's k-Equivalence Partition Refinement Algorithm
with state transition signatures and detailed iteration history.
"""

from typing import List, Dict, Set, Tuple, Any
from core.dfa import DFA
from core.validator import remove_unreachable_states


def format_set(s: Set[str]) -> str:
    return "{" + ", ".join(sorted(list(s))) + "}"


def moore_minimize(dfa: DFA) -> Tuple[DFA, List[Dict[str, Any]], Dict[str, str]]:
    """
    Executes Moore's algorithm.
    Returns:
        (minimal_dfa, step_history, state_mapping)
    """
    # Phase 1: Prune unreachable states first
    working_dfa, pruned_states = remove_unreachable_states(dfa)

    steps: List[Dict[str, Any]] = []
    step_num = 1

    states = sorted(list(working_dfa.states))
    alphabet = sorted(list(working_dfa.alphabet))
    final_states = set(working_dfa.final_states)
    non_final_states = working_dfa.states - final_states

    if pruned_states:
        steps.append({
            "step_id": step_num,
            "operation": "Unreachable State Elimination",
            "title": "Phase 1: Remove Unreachable States",
            "explanation": (
                f"Pruned unreachable state(s) {format_set(pruned_states)}. "
                "Only states reachable from the initial state contribute to the accepted language."
            ),
            "partition": [sorted(list(working_dfa.states))],
            "k": 0,
            "signatures": {},
            "split_info": f"Pruned {len(pruned_states)} unreachable state(s)",
            "dfa_state": working_dfa.clone()
        })
        step_num += 1

    if len(states) <= 1:
        mapping = {s: s for s in states}
        steps.append({
            "step_id": step_num,
            "operation": "Trivial Minimality",
            "title": "Automaton is Already Minimal",
            "explanation": f"The automaton has {len(states)} state(s), which is already minimal.",
            "partition": [states],
            "k": 0,
            "signatures": {},
            "split_info": "No minimization required",
            "dfa_state": working_dfa.clone()
        })
        return working_dfa, steps, mapping

    # Round 0: 0-equivalence (agree on string length 0, i.e., acceptance)
    raw_partition: List[Set[str]] = []
    if final_states:
        raw_partition.append(set(final_states))
    if non_final_states:
        raw_partition.append(set(non_final_states))

    steps.append({
        "step_id": step_num,
        "operation": "0-Equivalence",
        "title": "Step 1: 0-Equivalence (k = 0)",
        "explanation": (
            f"Two states are 0-equivalent if they agree on the empty string ε. "
            f"Partitioning Q into final states {format_set(final_states)} "
            f"and non-final states {format_set(non_final_states)}."
        ),
        "partition": [sorted(list(b)) for b in raw_partition],
        "k": 0,
        "signatures": {},
        "split_info": "P0 = {F, Q\\F}",
        "dfa_state": working_dfa.clone()
    })
    step_num += 1

    k = 1
    while True:
        # Assign a block ID to each state based on raw_partition
        state_to_block_id: Dict[str, str] = {}
        for idx, block in enumerate(raw_partition):
            for s in block:
                state_to_block_id[s] = f"P{idx}"

        # Generate transition signatures for all states
        signatures: Dict[str, Dict[str, str]] = {}
        for s in states:
            sig: Dict[str, str] = {}
            for sym in alphabet:
                target = working_dfa.get_transition(s, sym)
                sig[sym] = state_to_block_id.get(target, "None")
            signatures[s] = sig

        # Refine blocks: within each block, group states by identical signature tuples
        new_partition: List[Set[str]] = []
        any_split = False

        for block in raw_partition:
            sig_groups: Dict[Tuple[str, ...], Set[str]] = {}
            for s in block:
                sig_tuple = tuple(signatures[s][sym] for sym in alphabet)
                sig_groups.setdefault(sig_tuple, set()).add(s)

            if len(sig_groups) > 1:
                any_split = True

            for sub_group in sig_groups.values():
                new_partition.append(sub_group)

        # Sort partition deterministically
        new_partition.sort(key=lambda b: sorted(list(b))[0])

        if not any_split:
            # Convergence reached!
            steps.append({
                "step_id": step_num,
                "operation": "Convergence",
                "title": f"Step {step_num}: Algorithm Converged at k = {k}",
                "explanation": (
                    f"At k = {k}, all states in the same partition have identical transition signatures. "
                    f"No partition was split (≡_{k} = ≡_{k-1}). The partition has stabilized."
                ),
                "partition": [sorted(list(b)) for b in new_partition],
                "k": k,
                "signatures": signatures,
                "split_info": f"Converged with {len(new_partition)} blocks",
                "dfa_state": working_dfa.clone()
            })
            step_num += 1
            raw_partition = new_partition
            break
        else:
            steps.append({
                "step_id": step_num,
                "operation": f"{k}-Equivalence",
                "title": f"Step {step_num}: {k}-Equivalence Refinement (k = {k})",
                "explanation": (
                    f"Generated transition signatures for all states across Σ = {alphabet}. "
                    f"States with divergent destination blocks were separated into new sub-partitions. "
                    f"Partition expanded from {len(raw_partition)} to {len(new_partition)} blocks."
                ),
                "partition": [sorted(list(b)) for b in new_partition],
                "k": k,
                "signatures": signatures,
                "split_info": f"Partition refined: {len(raw_partition)} → {len(new_partition)} blocks",
                "dfa_state": working_dfa.clone()
            })
            step_num += 1
            raw_partition = new_partition
            k += 1

    # Quotient Construction
    sorted_classes = [sorted(list(b)) for b in raw_partition]
    sorted_classes.sort(key=lambda c: c[0])

    state_mapping: Dict[str, str] = {}
    minimal_states: Set[str] = set()

    for grp in sorted_classes:
        name = "[" + ",".join(grp) + "]" if len(grp) > 1 else grp[0]
        minimal_states.add(name)
        for s in grp:
            state_mapping[s] = name

    minimal_transitions: Dict[Tuple[str, str], str] = {}
    for grp in sorted_classes:
        rep = grp[0]
        rep_macro = state_mapping[rep]
        for sym in alphabet:
            dest = working_dfa.get_transition(rep, sym)
            if dest:
                minimal_transitions[(rep_macro, sym)] = state_mapping[dest]

    min_initial = state_mapping[working_dfa.initial_state]
    min_final = {state_mapping[s] for s in working_dfa.final_states if s in state_mapping}

    minimal_dfa = DFA(
        states=minimal_states,
        alphabet=set(alphabet),
        transitions=minimal_transitions,
        initial_state=min_initial,
        final_states=min_final
    )

    steps.append({
        "step_id": step_num,
        "operation": "Quotient Construction",
        "title": "Final Minimized DFA Constructed",
        "explanation": (
            f"The final equivalence classes form the states of the minimal DFA: {', '.join(sorted(list(minimal_states)))}. "
            f"The state count reduced from {len(dfa.states)} to {len(minimal_states)}."
        ),
        "partition": sorted_classes,
        "k": k,
        "signatures": signatures,
        "split_info": f"Minimized from {len(dfa.states)} to {len(minimal_states)} states",
        "dfa_state": minimal_dfa.clone()
    })

    return minimal_dfa, steps, state_mapping
