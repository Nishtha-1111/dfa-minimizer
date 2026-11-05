from typing import List, Dict, Set, Tuple
from ..models import DFAModel, TraceStep, TraceStepHighlights
from .unreachable import format_block, remove_unreachable_states


def run_hopcroft(dfa_input: DFAModel) -> Tuple[List[TraceStep], DFAModel, Dict[str, str], List[str], DFAModel]:
    """
    Hopcroft's DFA Minimization Algorithm (O(n log n)).
    Uses a waiting set of potential splitters W and refines partition P.
    Every step produces an accurate mathematical trace with no duplicate blocks.
    """
    pruned_dfa, unreachable_states, unreach_steps = remove_unreachable_states(dfa_input)

    states = sorted(pruned_dfa.states)
    alphabet = sorted(pruned_dfa.alphabet)
    accept_set = set(pruned_dfa.accept_states)

    F = sorted([s for s in states if s in accept_set])
    non_F = sorted([s for s in states if s not in accept_set])

    # Initial partition P_0 = { non_F, F } (if both exist)
    if F and non_F:
        P: List[List[str]] = [sorted(non_F), sorted(F)]
        # Add smaller group to waiting set W
        W: List[List[str]] = [sorted(F)] if len(F) <= len(non_F) else [sorted(non_F)]
    elif F:
        P = [sorted(F)]
        W = [sorted(F)]
    else:
        P = [sorted(non_F)]
        W = [sorted(non_F)]

    raw_steps: List[TraceStep] = []

    # Step 1: Initial partition
    init_desc = (
        f"Partition all states into non-accepting states {format_block(non_F)} and accepting states {format_block(F)}. "
        "States in different groups are 0-distinguishable by the empty string ε."
        if F and non_F else "All reachable states share the same acceptance status (single initial group)."
    )
    p0_str = f"{format_block(non_F)}, {format_block(F)}" if F and non_F else (format_block(F) if F else format_block(non_F))
    raw_steps.append(
        TraceStep(
            step_id=1,
            total_steps=1,
            phase="initial_partition",
            title="Initial partition: Accepting vs Non-accepting",
            description=init_desc,
            notation=rf"P_0 = \{{{p0_str}\}}",
            highlights=TraceStepHighlights(
                active_states=F if F else non_F,
                splitter_block=W[0] if W else []
            ),
            partition_state=[list(b) for b in P]
        )
    )

    # Precompute predecessors: inv[sym][target] = list of states transitioning to target on sym
    inv: Dict[str, Dict[str, List[str]]] = {c: {} for c in alphabet}
    for c in alphabet:
        for s in states:
            tgt = pruned_dfa.transitions.get(s, {}).get(c)
            if tgt:
                inv[c].setdefault(tgt, []).append(s)

    # Refinement loop
    while W:
        A = W.pop(0)
        A_sorted = sorted(A)
        fb_A = format_block(A_sorted)

        for c in alphabet:
            # Predecessors of A on symbol c
            X_set: Set[str] = set()
            for tgt in A:
                for src in inv[c].get(tgt, []):
                    X_set.add(src)
            X = sorted(list(X_set))
            x_str = ", ".join(X) if X else r"\emptyset"

            any_split = False
            i = 0
            while i < len(P):
                Y = P[i]
                Y1 = sorted([s for s in Y if s in X_set])
                Y2 = sorted([s for s in Y if s not in X_set])

                if Y1 and Y2:
                    any_split = True
                    fb_Y = format_block(Y)
                    fb_Y1 = format_block(Y1)
                    fb_Y2 = format_block(Y2)

                    # Replace Y in P with Y1 and insert Y2
                    P[i] = Y1
                    P.insert(i + 1, Y2)

                    # Update W: if Y is in W, replace it with Y1 and Y2; otherwise add min(Y1, Y2)
                    found_in_w = False
                    for idx_w, w_b in enumerate(W):
                        if set(w_b) == set(Y):
                            W.pop(idx_w)
                            W.append(sorted(Y1))
                            W.append(sorted(Y2))
                            found_in_w = True
                            break
                    if not found_in_w:
                        W.append(sorted(Y1) if len(Y1) <= len(Y2) else sorted(Y2))

                    raw_steps.append(
                        TraceStep(
                            step_id=len(raw_steps) + 1,
                            total_steps=1,
                            phase="refinement",
                            title=f"Split group {fb_Y} on symbol '{c}'",
                            description=(
                                f"Using splitter {fb_A} on input '{c}': states {fb_Y1} move into {fb_A}, "
                                f"while states {fb_Y2} do not. Group {fb_Y} splits into {fb_Y1} and {fb_Y2}."
                            ),
                            notation=rf"X = \delta^{{-1}}({fb_A}, '{c}') = \{{{x_str}\}} \implies {fb_Y} \to {fb_Y1}, {fb_Y2}",
                            highlights=TraceStepHighlights(
                                active_states=Y,
                                splitter_block=A_sorted,
                                split_blocks=[Y1, Y2]
                            ),
                            partition_state=[list(b) for b in P]
                        )
                    )
                    i += 2
                else:
                    i += 1

            if not any_split:
                if X:
                    desc = (
                        f"States {{{', '.join(X)}}} transition into splitter {fb_A} on input '{c}'. "
                        "Every group in the current partition is either completely inside this set or completely outside it, "
                        "so no group needs to be split."
                    )
                    notation_str = rf"\delta^{{-1}}({fb_A}, '{c}') = \{{{x_str}\}} \quad (\text{{consistent with partition}})"
                else:
                    desc = (
                        f"No states transition into splitter {fb_A} on input '{c}'. "
                        "The predecessor set is empty, so no group splits."
                    )
                    notation_str = rf"\delta^{{-1}}({fb_A}, '{c}') = \emptyset \quad (\text{{no states}})"

                raw_steps.append(
                    TraceStep(
                        step_id=len(raw_steps) + 1,
                        total_steps=1,
                        phase="refinement",
                        title=f"Check splitter {fb_A} on symbol '{c}'",
                        description=desc,
                        notation=notation_str,
                        highlights=TraceStepHighlights(
                            active_states=X,
                            splitter_block=A_sorted
                        ),
                        partition_state=[list(b) for b in P]
                    )
                )

    # Construct Minimal DFA
    state_mapping: Dict[str, str] = {}
    P_sorted = sorted([sorted(b) for b in P], key=lambda b: (0 if pruned_dfa.start_state in b else 1, b[0]))
    for block in P_sorted:
        label = format_block(block)
        for s in block:
            state_mapping[s] = label

    min_states = [format_block(b) for b in P_sorted]
    min_start = state_mapping[pruned_dfa.start_state]
    min_accept = sorted(list({state_mapping[s] for s in pruned_dfa.accept_states if s in state_mapping}))

    min_transitions: Dict[str, Dict[str, str]] = {}
    for block in P_sorted:
        b_label = format_block(block)
        rep = block[0]
        min_transitions[b_label] = {}
        for c in alphabet:
            tgt = pruned_dfa.transitions.get(rep, {}).get(c)
            if tgt and tgt in state_mapping:
                min_transitions[b_label][c] = state_mapping[tgt]

    minimal_dfa = DFAModel(
        states=min_states,
        alphabet=alphabet,
        start_state=min_start,
        accept_states=min_accept,
        transitions=min_transitions
    )

    # Final completion step
    final_states_str = ", ".join(min_states)
    raw_steps.append(
        TraceStep(
            step_id=len(raw_steps) + 1,
            total_steps=1,
            phase="done",
            title="Minimization Complete",
            description=(
                f"Worklist W is empty and partition refinement has stabilized with {len(P_sorted)} equivalence classes. "
                "Merging equivalent states produces the minimal DFA."
            ),
            notation=rf"|Q_{{\min}}| = {len(P_sorted)}, \quad P_{{\text{{final}}}} = \{{{final_states_str}\}}",
            highlights=TraceStepHighlights(
                active_states=min_states
            ),
            partition_state=[list(b) for b in P_sorted]
        )
    )

    all_steps = unreach_steps + raw_steps
    tot = len(all_steps)
    for idx, stp in enumerate(all_steps):
        stp.step_id = idx + 1
        stp.total_steps = tot

    return all_steps, minimal_dfa, state_mapping, unreachable_states, pruned_dfa
