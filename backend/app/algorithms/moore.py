from typing import List, Dict, Tuple
from ..models import DFAModel, TraceStep, TraceStepHighlights
from .unreachable import format_block, remove_unreachable_states


def run_moore(dfa_input: DFAModel) -> Tuple[List[TraceStep], DFAModel, Dict[str, str], List[str], DFAModel]:
    pruned_dfa, unreachable_states, unreach_steps = remove_unreachable_states(dfa_input)

    states = sorted(pruned_dfa.states)
    alphabet = sorted(pruned_dfa.alphabet)
    accept_set = set(pruned_dfa.accept_states)

    F = sorted([s for s in states if s in accept_set])
    non_F = sorted([s for s in states if s not in accept_set])

    if F and non_F:
        P: List[List[str]] = [sorted(non_F), sorted(F)]
    elif F:
        P = [sorted(F)]
    else:
        P = [sorted(non_F)]

    raw_steps: List[TraceStep] = []

    init_desc = (
        f"0-Equivalence: States are partitioned into accepting {format_block(F)} and non-accepting {format_block(non_F)}. "
        "Two states are 0-equivalent iff they have the same acceptance behavior on the empty string ε."
        if F and non_F else "All states belong to the same initial class."
    )
    p0_str = f"{format_block(non_F)}, {format_block(F)}" if F and non_F else (format_block(F) if F else format_block(non_F))
    raw_steps.append(
        TraceStep(
            step_id=1,
            total_steps=1,
            phase="initial_partition",
            title="0-Equivalence (Distinguished by ε)",
            description=init_desc,
            notation=rf"\Pi_0 = \{{{p0_str}\}}",
            highlights=TraceStepHighlights(
                active_states=F,
                splitter_block=F if F else non_F
            ),
            partition_state=[list(b) for b in P]
        )
    )

    k = 1
    changed = True

    while changed:
        changed = False
        block_idx_map = {}
        for idx, block in enumerate(P):
            for s in block:
                block_idx_map[s] = idx

        next_P: List[List[str]] = []

        for group in P:
            if len(group) <= 1:
                next_P.append(group)
                continue

            sig_map: Dict[Tuple[int, ...], List[str]] = {}
            for s in group:
                sig = tuple(block_idx_map.get(pruned_dfa.transitions.get(s, {}).get(c), -1) for c in alphabet)
                sig_map.setdefault(sig, []).append(s)

            sub_blocks = [sorted(sub) for sub in sig_map.values()]
            if len(sub_blocks) > 1:
                changed = True
                for sb in sub_blocks:
                    next_P.append(sb)

                fb_group = format_block(group)
                sub_str = ", ".join([format_block(sb) for sb in sub_blocks])
                raw_steps.append(
                    TraceStep(
                        step_id=len(raw_steps) + 1,
                        total_steps=1,
                        phase="refinement",
                        title=f"{k}-Equivalence: Split group {fb_group}",
                        description=f"In round {k}, states in {fb_group} transition to different target groups on input symbols. "
                                    f"The group splits into: {sub_str}.",
                        notation=rf"\Pi_{{{k}}}: {fb_group} \longrightarrow \{{{sub_str}\}}",
                        highlights=TraceStepHighlights(
                            active_states=group,
                            split_blocks=sub_blocks
                        ),
                        partition_state=[list(b) for b in next_P] + [list(b) for b in P if b != group]
                    )
                )
            else:
                next_P.append(group)

        if not changed:
            raw_steps.append(
                TraceStep(
                    step_id=len(raw_steps) + 1,
                    total_steps=1,
                    phase="refinement",
                    title=f"{k}-Equivalence: Partition is stable",
                    description=f"In round {k}, no group splits. All states within each group have identical transition signatures. "
                                f"Since Π_{k} = Π_{k-1}, Moore's algorithm terminates.",
                    notation=rf"\Pi_{{{k}}} = \Pi_{{{k-1}}} \implies \text{{Equivalence reached}}",
                    highlights=TraceStepHighlights(),
                    partition_state=[list(b) for b in P]
                )
            )

        P = next_P
        k += 1

    # Minimal DFA Construction
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

    final_states_str = ", ".join(min_states)
    raw_steps.append(
        TraceStep(
            step_id=len(raw_steps) + 1,
            total_steps=1,
            phase="done",
            title="Minimization Complete",
            description=f"Moore's algorithm found {len(P_sorted)} equivalence classes. Merging equivalent states produces the minimal DFA.",
            notation=rf"|Q_{{\min}}| = {len(P_sorted)}, \quad \Pi_{{\text{{final}}}} = \{{{final_states_str}\}}",
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
