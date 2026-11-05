from typing import List, Tuple
from collections import deque
from ..models import DFAModel, TraceStep, TraceStepHighlights


def format_block(block: List[str]) -> str:
    return "{" + ", ".join(sorted(block)) + "}"


def remove_unreachable_states(dfa: DFAModel) -> Tuple[DFAModel, List[str], List[TraceStep]]:
    visited = set()
    queue = deque([dfa.start_state])
    if dfa.start_state in dfa.states:
        visited.add(dfa.start_state)

    while queue:
        curr = queue.popleft()
        trans = dfa.transitions.get(curr, {})
        for sym in dfa.alphabet:
            nxt = trans.get(sym)
            if nxt and nxt in dfa.states and nxt not in visited:
                visited.add(nxt)
                queue.append(nxt)

    all_states = sorted(dfa.states)
    reachable_states = sorted(list(visited))
    unreachable_states = sorted([s for s in all_states if s not in visited])

    pruned_transitions = {}
    for s in reachable_states:
        pruned_transitions[s] = {}
        for sym in dfa.alphabet:
            pruned_transitions[s][sym] = dfa.transitions.get(s, {}).get(sym, s)

    pruned_accept = [s for s in dfa.accept_states if s in visited]

    pruned_dfa = DFAModel(
        states=reachable_states,
        alphabet=dfa.alphabet,
        start_state=dfa.start_state if dfa.start_state in visited else (reachable_states[0] if reachable_states else ""),
        accept_states=pruned_accept,
        transitions=pruned_transitions
    )

    steps = []
    if unreachable_states:
        unreach_str = ", ".join(unreachable_states)
        reach_str = ", ".join(reachable_states)
        steps.append(
            TraceStep(
                step_id=1,
                total_steps=1,
                phase="unreachable_removal",
                title=f"Remove unreachable states: {format_block(unreachable_states)}",
                description=f"BFS traversal from start state '{dfa.start_state}' reached states {format_block(reachable_states)}. "
                            f"States {format_block(unreachable_states)} have no directed path from the start state and cannot affect the recognized language.",
                notation=rf"Q_{{\text{{pruned}}}} = Q \setminus \{{{unreach_str}\}} = \{{{reach_str}\}}",
                highlights=TraceStepHighlights(
                    unreachable_states=unreachable_states,
                    active_states=reachable_states
                ),
                partition_state=[reachable_states]
            )
        )

    return pruned_dfa, unreachable_states, steps
