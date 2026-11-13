"""
Hopcroft's O(|Σ| · |Q| log |Q|) Partition Refinement Algorithm
with granular step-by-step execution history.
"""

from typing import List, Dict, Set, Tuple, Any
from core.dfa import DFA, Transition
from core.validator import remove_unreachable_states


def format_set(s: Set[str]) -> str:
    return "{" + ", ".join(sorted(list(s))) + "}"


def hopcroft_minimize(dfa: DFA) -> Tuple[DFA, List[Dict[str, Any]], Dict[str, str]]:
    """
    Executes Hopcroft's partition refinement algorithm.
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

    # Record unreachable states removal if any occurred
    if pruned_states:
        steps.append({
            "step_id": step_num,
            "operation": "Unreachable State Elimination",
            "title": "Phase 1: Remove Unreachable States",
            "explanation": (
                f"Before partition refinement, states that cannot be reached from the start state "
                f"'{working_dfa.initial_state}' are pruned: {format_set(pruned_states)}. "
                "These states have no impact on the accepted language."
            ),
            "partition": [sorted(list(working_dfa.states))],
            "active_splitter": None,
            "active_symbol": None,
            "preimage": [],
            "split_info": f"Pruned {len(pruned_states)} unreachable state(s)",
            "dfa_state": working_dfa.clone()
        })
        step_num += 1

    # Edge cases: 0 or 1 state
    if len(states) <= 1:
        mapping = {s: s for s in states}
        steps.append({
            "step_id": step_num,
            "operation": "Trivial Minimality",
            "title": "Automaton is Already Minimal",
            "explanation": f"The automaton has {len(states)} state(s), which is already minimal.",
            "partition": [states],
            "active_splitter": None,
            "active_symbol": None,
            "preimage": [],
            "split_info": "No minimization required",
            "dfa_state": working_dfa.clone()
        })
        return working_dfa, steps, mapping

    # Step 1: Initial Partition P = {F, Q \ F}
    raw_partition: List[Set[str]] = []
    if final_states:
        raw_partition.append(set(final_states))
    if non_final_states:
        raw_partition.append(set(non_final_states))

    # Initial Worklist W: add smaller set (or both to guarantee full exploration)
    worklist: List[Set[str]] = []
    for block in raw_partition:
        worklist.append(set(block))

    steps.append({
        "step_id": step_num,
        "operation": "Initial Partition",
        "title": "Step 1: Partition into Final vs Non-Final States",
        "explanation": (
            f"We start by dividing all states into accepting states {format_set(final_states)} "
            f"and non-accepting states {format_set(non_final_states)}. "
            "These two groups are fundamentally distinguishable on the empty string ε."
        ),
        "partition": [sorted(list(b)) for b in raw_partition],
        "worklist": [format_set(w) for w in worklist],
        "active_splitter": None,
        "active_symbol": None,
        "preimage": [],
        "split_info": f"Initial 2 blocks: F and Q\\F",
        "dfa_state": working_dfa.clone()
    })
    step_num += 1

    # Inverted transitions: inverted[sym][dest] -> set of source states
    inverted: Dict[str, Dict[str, Set[str]]] = {sym: {s: set() for s in states} for sym in alphabet}
    for (s, sym), dest in working_dfa.transitions.items():
        if s in working_dfa.states and dest in working_dfa.states and sym in alphabet:
            inverted[sym][dest].add(s)

    # Refinement Loop
    iteration = 0
    while worklist:
        iteration += 1
        A = worklist.pop(0)
        A_str = format_set(A)

        for sym in alphabet:
            # Pre-image X = δ⁻¹(A, sym)
            X: Set[str] = set()
            for target in A:
                X.update(inverted[sym].get(target, set()))

            if not X:
                continue

            # Check if any block Y in P is split by X
            snapshot = list(raw_partition)
            for Y in snapshot:
                if Y not in raw_partition:
                    continue

                intersection = Y & X
                difference = Y - X

                if intersection and difference:
                    # Y splits!
                    Y_str = format_set(Y)
                    int_str = format_set(intersection)
                    diff_str = format_set(difference)

                    raw_partition.remove(Y)
                    raw_partition.append(intersection)
                    raw_partition.append(difference)

                    # Update worklist
                    in_w = False
                    for idx_w, w_block in enumerate(worklist):
                        if w_block == Y:
                            worklist.pop(idx_w)
                            worklist.append(intersection)
                            worklist.append(difference)
                            in_w = True
                            break

                    if not in_w:
                        if len(intersection) <= len(difference):
                            worklist.append(intersection)
                        else:
                            worklist.append(difference)

                    steps.append({
                        "step_id": step_num,
                        "operation": "Partition Split",
                        "title": f"Split: Block {Y_str} is Divided by '{sym}'",
                        "explanation": (
                            f"Using candidate splitter A = {A_str} on input '{sym}'. "
                            f"The states transitioning into A on '{sym}' are {format_set(X)}. "
                            f"Block {Y_str} is split into {int_str} (which reach A on '{sym}') "
                            f"and {diff_str} (which do not reach A on '{sym}')."
                        ),
                        "partition": [sorted(list(b)) for b in raw_partition],
                        "worklist": [format_set(w) for w in worklist],
                        "active_splitter": A_str,
                        "active_symbol": sym,
                        "preimage": sorted(list(X)),
                        "split_info": f"{Y_str} → {int_str} + {diff_str}",
                        "dfa_state": working_dfa.clone()
                    })
                    step_num += 1

    # Stabilization
    steps.append({
        "step_id": step_num,
        "operation": "Convergence",
        "title": "Hopcroft Algorithm Stabilized",
        "explanation": (
            "The candidate splitter worklist W is now completely empty. "
            "No further splits are possible, meaning each resulting block contains strictly equivalent states."
        ),
        "partition": [sorted(list(b)) for b in raw_partition],
        "worklist": [],
        "active_splitter": None,
        "active_symbol": None,
        "preimage": [],
        "split_info": f"Final {len(raw_partition)} equivalence classes",
        "dfa_state": working_dfa.clone()
    })
    step_num += 1

    # Construct quotient DFA
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
            f"Equivalence classes are merged into macro-states: {', '.join(sorted(list(minimal_states)))}. "
            f"The original automaton with {len(dfa.states)} states has been reduced to {len(minimal_states)} minimal states."
        ),
        "partition": sorted_classes,
        "worklist": [],
        "active_splitter": None,
        "active_symbol": None,
        "preimage": [],
        "split_info": f"Minimized from {len(dfa.states)} to {len(minimal_states)} states",
        "dfa_state": minimal_dfa.clone()
    })

    return minimal_dfa, steps, state_mapping
