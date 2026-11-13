"""
Graph Visualization Engine for DFA Minimization Studio.
Generates styled Graphviz DOT representations using the screenshot theme:
  Primary Blue: #2563EB
  Light Blue: #EFF6FF
  Border: #3B82F6
  Amber Splitter Fill: #FEF3C7
  Amber Splitter Border: #D97706
  Slate text: #1E293B
"""

from typing import Dict, List, Set, Optional, Tuple
from core.dfa import DFA


def generate_dfa_dot(
    dfa: DFA,
    highlighted_states: Optional[Set[str]] = None,
    partition_colors: Optional[Dict[str, str]] = None,
    active_edge: Optional[Tuple[str, str, str]] = None,
    title: str = ""
) -> str:
    """
    Generates a polished Graphviz DOT specification string matching the UI screenshot.
    """
    if highlighted_states is None:
        highlighted_states = set()
    if partition_colors is None:
        partition_colors = {}

    dot_lines = [
        'digraph DFA {',
        '  rankdir=LR;',
        '  bgcolor="transparent";',
        '  splines=true;',
        '  node [fontname="Inter, -apple-system, sans-serif", fontsize=11, fontcolor="#1E40AF", style=filled, penwidth=2.2];',
        '  edge [fontname="Inter, -apple-system, sans-serif", fontsize=10, penwidth=1.8, color="#64748B", fontcolor="#1E293B", arrowsize=0.7];',
    ]

    # Start arrow into initial state
    if dfa.initial_state and dfa.initial_state in dfa.states:
        dot_lines.append('  __start [shape=none, label="", width=0, height=0];')
        dot_lines.append(
            f'  __start -> "{dfa.initial_state}" '
            f'[label="", color="#2563EB", penwidth=2.5, arrowsize=0.9];'
        )

    # Nodes (States)
    for s in sorted(list(dfa.states)):
        is_final = s in dfa.final_states
        is_highlighted = s in highlighted_states

        shape = "doublecircle" if is_final else "circle"

        if is_highlighted:
            fill = "#FEF3C7"  # Warm Amber Fill for splitter block
            stroke = "#D97706"  # Amber Border
            font_color = "#92400E"
            pen_width = "2.8"
        elif s in partition_colors:
            fill = partition_colors[s]
            stroke = "#3B82F6"
            font_color = "#1E40AF"
            pen_width = "2.0"
        else:
            fill = "#EFF6FF"  # Soft Blue Fill
            stroke = "#3B82F6"  # Blue Border
            font_color = "#1E40AF"
            pen_width = "2.0"

        dot_lines.append(
            f'  "{s}" [shape={shape}, fillcolor="{fill}", color="{stroke}", fontcolor="{font_color}", penwidth={pen_width}, width=0.55, fixedsize=true];'
        )

    # Group transitions by (u, v) so multiple inputs show as "0,1"
    grouped_transitions: Dict[Tuple[str, str], List[str]] = {}
    for (src, sym), tgt in sorted(dfa.transitions.items()):
        key = (src, tgt)
        if key not in grouped_transitions:
            grouped_transitions[key] = []
        grouped_transitions[key].append(sym)

    for (src, tgt), syms in grouped_transitions.items():
        label = ",".join(sorted(syms))
        edge_color = "#64748B"
        edge_width = "1.8"
        dot_lines.append(
            f'  "{src}" -> "{tgt}" [label=" {label} ", color="{edge_color}", penwidth={edge_width}];'
        )

    dot_lines.append('}')
    return "\n".join(dot_lines)
