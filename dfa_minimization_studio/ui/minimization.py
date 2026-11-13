"""
Tab 4: Minimization Mode Module (Final Answer & Step-by-Step Interactive Visualization).
"""

import streamlit as st
import time
from core.dfa import DFA
from core.validator import validate_dfa, make_complete_with_dead_state
from algorithms.minimizer import run_minimization
from visualization.graph_visualizer import generate_dfa_dot, get_partition_color_map


def render_minimization_tab():
    st.markdown("### 🔍 Minimization Mode")

    dfa: DFA = st.session_state["current_dfa"]
    algorithm: str = st.session_state.get("selected_algorithm", "hopcroft")

    # Validation
    val = validate_dfa(dfa)
    if not val.is_valid:
        st.error("Cannot minimize: Please resolve the errors in the 'DFA Designer' tab first.")
        for err in val.errors:
            st.error(f"• {err}")
        return

    if not val.is_complete:
        st.warning(f"DFA is incomplete: {len(val.missing_transitions)} transition(s) are missing.")
        if st.button("Complete DFA with Dead State"):
            st.session_state["current_dfa"] = make_complete_with_dead_state(dfa)
            st.rerun()
        return

    # Mode Selector
    col_hdr1, col_hdr2 = st.columns([2, 1])
    with col_hdr1:
        st.markdown(
            f"Using **{algorithm.capitalize()}'s Algorithm** on automaton with **{len(dfa.states)} states**."
        )
    with col_hdr2:
        mode = st.radio(
            "Viewing Mode:",
            ["Mode A: Final Answer Only", "Mode B: Step-by-Step Explanation"],
            index=0 if st.session_state.get("view_mode") == "A" else 1,
            horizontal=True,
            key="radio_view_mode"
        )
        st.session_state["view_mode"] = "A" if "Final Answer" in mode else "B"

    # Compute or retrieve cached result
    if st.session_state.get("minimization_result") is None:
        with st.spinner("Computing theoretical minimization trace..."):
            st.session_state["minimization_result"] = run_minimization(dfa, algorithm)

    result = st.session_state["minimization_result"]
    minimal_dfa = result["minimal_dfa"]
    steps = result["steps"]

    # =========================================================================
    # MODE A: FINAL ANSWER ONLY
    # =========================================================================
    if st.session_state["view_mode"] == "A":
        st.markdown("---")
        # Summary metrics
        m1, m2, m3, m4 = st.columns(4)
        with m1:
            st.markdown(f"""
            <div class="metric-box">
                <div class="metric-value">{result['original_state_count']}</div>
                <div class="metric-label">Original States</div>
            </div>
            """, unsafe_allow_html=True)
        with m2:
            st.markdown(f"""
            <div class="metric-box">
                <div class="metric-value">{result['minimized_state_count']}</div>
                <div class="metric-label">Minimized States</div>
            </div>
            """, unsafe_allow_html=True)
        with m3:
            st.markdown(f"""
            <div class="metric-box">
                <div class="metric-value">{result['states_removed']}</div>
                <div class="metric-label">States Reduced</div>
            </div>
            """, unsafe_allow_html=True)
        with m4:
            st.markdown(f"""
            <div class="metric-box">
                <div class="metric-value">{len(result['merged_states'])}</div>
                <div class="metric-label">Classes Merged</div>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("<div style='margin-top: 1.5rem;'></div>", unsafe_allow_html=True)

        # Side-by-side graphs
        col_g1, col_g2 = st.columns(2, gap="large")
        with col_g1:
            st.markdown("#### 1. Original DFA")
            dot_orig = generate_dfa_dot(dfa, title="Original DFA")
            st.graphviz_chart(dot_orig, use_container_width=True)

        with col_g2:
            st.markdown("#### 2. Minimized DFA")
            dot_min = generate_dfa_dot(minimal_dfa, title="Minimized DFA")
            st.graphviz_chart(dot_min, use_container_width=True)

        # Merged States & Partitions Details
        st.markdown("---")
        st.markdown("#### 📊 Equivalence Classes & State Mapping")

        col_p1, col_p2 = st.columns(2)
        with col_p1:
            st.markdown("**Final Equivalence Partitions:**")
            for grp in result["final_partitions"]:
                members = ", ".join(sorted(grp))
                st.markdown(f"- `<span class='partition-pill'>{{{members}}}</span>`", unsafe_allow_html=True)

        with col_p2:
            st.markdown("**Merged Composite States:**")
            if result["merged_states"]:
                for macro, members in result["merged_states"].items():
                    st.markdown(f"- State `{macro}` was formed by merging `{', '.join(members)}`")
            else:
                st.info("No states were merged. The automaton was already minimal!")

    # =========================================================================
    # MODE B: STEP-BY-STEP EXPLANATION
    # =========================================================================
    else:
        st.markdown("---")
        total_steps = len(steps)
        curr_idx = st.session_state.get("current_step_idx", 0)
        curr_idx = max(0, min(curr_idx, total_steps - 1))
        st.session_state["current_step_idx"] = curr_idx

        step = steps[curr_idx]

        # Step Navigation Controls
        ctrl1, ctrl2, ctrl3, ctrl4, ctrl5 = st.columns([1, 1, 1, 1, 2])

        with ctrl1:
            if st.button("⏮️ Restart"):
                st.session_state["current_step_idx"] = 0
                st.rerun()

        with ctrl2:
            if st.button("◀ Previous", disabled=(curr_idx == 0)):
                st.session_state["current_step_idx"] = curr_idx - 1
                st.rerun()

        with ctrl3:
            if st.button("Next ▶", disabled=(curr_idx >= total_steps - 1)):
                st.session_state["current_step_idx"] = curr_idx + 1
                st.rerun()

        with ctrl4:
            auto_play = st.button("▶️ Auto Play")
            if auto_play:
                for i in range(curr_idx, total_steps):
                    st.session_state["current_step_idx"] = i
                    time.sleep(1.0)
                    st.rerun()

        with ctrl5:
            st.markdown(
                f"<div style='text-align: right; padding-top: 0.5rem; font-weight: 700; color: #142B45;'>"
                f"Step {curr_idx + 1} of {total_steps}"
                f"</div>",
                unsafe_allow_html=True
            )

        # Scrubber slider
        new_idx = st.slider(
            "Scrub steps:",
            min_value=0,
            max_value=total_steps - 1,
            value=curr_idx,
            label_visibility="collapsed"
        )
        if new_idx != curr_idx:
            st.session_state["current_step_idx"] = new_idx
            st.rerun()

        st.markdown("<div style='margin-top: 1rem;'></div>", unsafe_allow_html=True)

        # Two Columns: Left = Graph with Step Highlights; Right = Step Details & Signatures/Splitters
        col_step_graph, col_step_info = st.columns([1.1, 0.9], gap="large")

        with col_step_graph:
            st.markdown("#### Automaton State at Current Step")

            # Color partitions
            color_map = get_partition_color_map(step.get("partition", []))
            highlighted = set(step.get("preimage", []))

            dfa_to_show = step.get("dfa_state", dfa)
            dot_step = generate_dfa_dot(
                dfa_to_show,
                highlighted_states=highlighted,
                partition_colors=color_map,
                title=f"Step {step['step_id']}: {step['operation']}"
            )
            st.graphviz_chart(dot_step, use_container_width=True)

        with col_step_info:
            # Explanation card
            st.markdown(f"""
            <div class="step-box">
                <div class="step-num">{step['operation']} &bull; Step {curr_idx + 1} of {total_steps}</div>
                <h3 style="color: #142B45; margin: 0.25rem 0 0.5rem 0; font-size: 1.15rem;">{step['title']}</h3>
                <div class="step-text">{step['explanation']}</div>
            </div>
            """, unsafe_allow_html=True)

            # Current partition blocks
            st.markdown("**Current Partition Blocks (P):**")
            p_blocks = step.get("partition", [])
            for idx, blk in enumerate(p_blocks):
                st.markdown(
                    f"<span class='partition-pill'>P{idx} = {{{', '.join(blk)}}}</span>",
                    unsafe_allow_html=True
                )

            # Algorithm-specific details
            if algorithm == "hopcroft":
                if "worklist" in step and step["worklist"]:
                    st.markdown("**Candidate Splitter Worklist (W):**")
                    for w in step["worklist"]:
                        st.markdown(f"- `{w}`")

                if step.get("active_splitter"):
                    st.markdown(
                        f"**Active Splitter:** `{step['active_splitter']}` on symbol `'{step['active_symbol']}'`"
                    )
                if step.get("preimage"):
                    st.markdown(f"**Pre-image $\\delta^{{-1}}(A, \\sigma)$:** `{{{', '.join(step['preimage'])}}}`")

            elif algorithm == "moore":
                if "k" in step:
                    st.markdown(f"**Equivalence Level:** `k = {step['k']}`")

                sigs = step.get("signatures", {})
                if sigs:
                    st.markdown("**State Transition Signatures:**")
                    sig_data = []
                    for st_name, s_map in sigs.items():
                        sig_str = "(" + ", ".join(f"{sym}→{dest}" for sym, dest in s_map.items()) + ")"
                        sig_data.append({"State": st_name, "Signature": sig_str})
                    st.table(sig_data)
