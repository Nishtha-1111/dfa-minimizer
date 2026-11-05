from typing import List, Dict, Set, Tuple, Optional
from ..models import DFAModel, TraceStep, TraceStepHighlights
from .unreachable import format_block, remove_unreachable_states


def pair_key(p: str, q: str) -> Tuple[str, str]:
    return (min(p, q), max(p, q))


def run_table_filling(dfa_input: DFAModel) -> Tuple[List[TraceStep], DFAModel, Dict[str, str], List[str], DFAModel]:
    pruned_dfa, unreachable_states, unreach_steps = remove_unreachable_states(dfa_input)

    states = sorted(pruned_dfa.states)
    alphabet = sorted(pruned_dfa.alphabet)
    accept_set = set(pruned_dfa.accept_states)

    # All unique unordered pairs (p, q) with p < q
    all_pairs: List[Tuple[str, str]] = []
    for i in range(len(states)):
        for j in range(i + 1, len(states)):
            all_pairs.append((states[i], states[j]))

    # Marked map: (p, q) -> info dict
    marked_map: Dict[Tuple[str, str], Dict[str, str]] = {}
    raw_steps: List[TraceStep] = []

    # Round 0: Base Case - One accepting, one non-accepting
    round_0_marked: List[Tuple[str, str]] = []
    for (p, q) in all_pairs:
        p_acc = p in accept_set
        q_acc = q in accept_set
        if p_acc != q_acc:
            round_0_marked.append((p, q))
            marked_map[(p, q)] = {
                "round": "0",
                "reason": f"Base case: '{p if p_acc else q}' is accepting while '{q if p_acc else p}' is non-accepting (distinguished by ε)."
            }

    marked_list_so_far = [list(k) for k in marked_map.keys()]

    # Initial partition based on round 0 (accept vs non-accept)
    F = sorted([s for s in states if s in accept_set])
    non_F = sorted([s for s in states if s not in accept_set])
    initial_p = []
    if non_F:
        initial_p.append(non_F)
    if F:
        initial_p.append(F)

    round_0_str = ", ".join([f"({p},{q})" for (p, q) in round_0_marked])
    raw_steps.append(
        TraceStep(
            step_id=1,
            total_steps=1,
            phase="initial_partition",
            title="Table-Filling: Base Case (Distinguish by ε)",
            description=f"Marked {len(round_0_marked)} pair(s) with an 'X' in the table because one state is accepting and the other is rejecting: {round_0_str}. "
                        "These pairs are immediately 0-distinguishable by the empty string ε.",
            notation=rf"\forall (p, q) \in (F \times (Q \setminus F)), \; \text{{Mark}}(p, q) = \text{{'X'}} \implies \varepsilon \in L(p) \triangle L(q)",
            highlights=TraceStepHighlights(
                active_states=states,
                marked_pairs=marked_list_so_far,
                splitter_block=F
            ),
            partition_state=initial_p
        )
    )

    # Inductive Rounds
    round_num = 1
    changed = True

    while changed:
        changed = False
        newly_marked_in_round: List[Tuple[str, str]] = []

        for (p, q) in all_pairs:
            if (p, q) in marked_map:
                continue

            # Test each alphabet symbol
            for sym in alphabet:
                p_next = pruned_dfa.transitions.get(p, {}).get(sym)
                q_next = pruned_dfa.transitions.get(q, {}).get(sym)

                if p_next and q_next and p_next != q_next:
                    target_k = pair_key(p_next, q_next)
                    if target_k in marked_map:
                        reason = (
                            f"On input '{sym}', state {p} moves to {p_next} and state {q} moves to {q_next}. "
                            f"The target pair ({target_k[0]}, {target_k[1]}) is already marked distinguished, "
                            f"so ({p}, {q}) is also distinguished!"
                        )
                        marked_map[(p, q)] = {
                            "round": str(round_num),
                            "reason": reason,
                            "symbol": sym,
                            "target": f"({target_k[0]}, {target_k[1]})"
                        }
                        newly_marked_in_round.append((p, q))
                        changed = True

                        current_marked = [list(k) for k in marked_map.keys()]

                        raw_steps.append(
                            TraceStep(
                                step_id=len(raw_steps) + 1,
                                total_steps=1,
                                phase="refinement",
                                title=f"Round {round_num}: Mark pair ({p}, {q}) on input '{sym}'",
                                description=reason,
                                notation=rf"\delta(({p}, {q}), '{sym}') = ({p_next}, {q_next}) \in \text{{Marked}} \implies ({p}, {q}) \in \text{{Marked}}",
                                highlights=TraceStepHighlights(
                                    active_states=[p, q, p_next, q_next],
                                    active_pair=[p, q],
                                    target_pair=[target_k[0], target_k[1]],
                                    marked_pairs=current_marked,
                                    mark_reason=reason
                                ),
                                partition_state=initial_p
                            )
                        )
                        break

        round_num += 1

    # Connected components of unmarked pairs
    parent = {s: s for s in states}

    def find(i: str) -> str:
        if parent[i] == i:
            return i
        parent[i] = find(parent[i])
        return parent[i]

    def union(i: str, j: str):
        root_i = find(i)
        root_j = find(j)
        if root_i != root_j:
            parent[root_i] = root_j

    unmarked_pairs = [pair for pair in all_pairs if pair not in marked_map]
    for (p, q) in unmarked_pairs:
        union(p, q)

    groups_dict: Dict[str, List[str]] = {}
    for s in states:
        root = find(s)
        groups_dict.setdefault(root, []).append(s)

    P_final = sorted([sorted(b) for b in groups_dict.values()], key=lambda b: (0 if pruned_dfa.start_state in b else 1, b[0]))

    state_mapping: Dict[str, str] = {}
    for block in P_final:
        label = format_block(block)
        for s in block:
            state_mapping[s] = label

    min_states = [format_block(b) for b in P_final]
    min_start = state_mapping[pruned_dfa.start_state]
    min_accept = sorted(list({state_mapping[s] for s in pruned_dfa.accept_states if s in state_mapping}))

    min_transitions: Dict[str, Dict[str, str]] = {}
    for block in P_final:
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

    # Step: Stability & Unmarked Pairs
    unmarked_str = ", ".join([f"({p},{q})" for (p, q) in unmarked_pairs]) if unmarked_pairs else "None (all pairs distinguished)"
    min_states_str = ", ".join(min_states)
    raw_steps.append(
        TraceStep(
            step_id=len(raw_steps) + 1,
            total_steps=1,
            phase="refinement",
            title="Table-Filling Complete: Identify Equivalent States",
            description=f"No additional pairs can be distinguished. The unmarked cells in the table define the equivalence relation: {unmarked_str}. "
                        f"States that remain unmarked merge together to form the minimal DFA states: {min_states_str}.",
            notation=rf"\text{{Unmarked Pairs: }} \{{{unmarked_str}\}} \implies Q_{{\min}} = \{{{min_states_str}\}}",
            highlights=TraceStepHighlights(
                active_states=states,
                marked_pairs=[list(k) for k in marked_map.keys()]
            ),
            partition_state=P_final
        )
    )

    # Step: Final minimal DFA
    final_states_str = ", ".join(min_states)
    raw_steps.append(
        TraceStep(
            step_id=len(raw_steps) + 1,
            total_steps=1,
            phase="done",
            title="Minimization Complete",
            description=f"Table-Filling minimization successfully synthesized the minimal DFA with {len(P_final)} states: {final_states_str}.",
            notation=rf"|Q_{{\min}}| = {len(P_final)}, \quad P_{{\text{{final}}}} = \{{{final_states_str}\}}",
            highlights=TraceStepHighlights(
                active_states=min_states
            ),
            partition_state=P_final
        )
    )

    all_steps = unreach_steps + raw_steps
    tot = len(all_steps)
    for idx, stp in enumerate(all_steps):
        stp.step_id = idx + 1
        stp.total_steps = tot

    return all_steps, minimal_dfa, state_mapping, unreachable_states, pruned_dfa
