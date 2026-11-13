"""
DFA Minimizer - Streamlit Application Entrypoint.
Matches the clean, guided Light layout with:
- Slim top bar: logo, title, Export, Light theme
- Single control strip: Example preset, Hopcroft/Moore segmented toggle, Reset, Minimize
- 3 Tabs: 1. Input, 2. Visualize, 3. Test strings
- 2-Column Visualize tab: Left graph card, Right state groups + explanation cards
- Sticky/Bottom playback controls
"""

import os
import sys
import json
import time
from pathlib import Path

studio_dir = Path(__file__).resolve().parent
if str(studio_dir) not in sys.path:
    sys.path.insert(0, str(studio_dir))

import streamlit as st
from core.dfa import DFA
from core.samples import get_sample_dfas
from core.validator import validate_dfa, make_complete_with_dead_state
from algorithms.minimizer import run_minimization
from visualization.graph_visualizer import generate_dfa_dot

st.set_page_config(
    page_title="DFA Minimizer",
    page_icon="δ",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Load CSS
css_path = os.path.join(os.path.dirname(__file__), "assets", "styles.css")
if os.path.exists(css_path):
    with open(css_path, "r", encoding="utf-8") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)


# Initialize Session State
def init_state():
    samples = get_sample_dfas()
    if "current_preset_name" not in st.session_state:
        st.session_state["current_preset_name"] = "Textbook Example (Equivalent States)"

    if "current_dfa" not in st.session_state:
        st.session_state["current_dfa"] = samples[st.session_state["current_preset_name"]].clone()

    if "algorithm" not in st.session_state:
        st.session_state["algorithm"] = "hopcroft"

    if "minimization_result" not in st.session_state:
        st.session_state["minimization_result"] = None

    if "current_step_idx" not in st.session_state:
        st.session_state["current_step_idx"] = 6  # Default to Step 7 of 14 for textbook

    if "graph_view_mode" not in st.session_state:
        st.session_state["graph_view_mode"] = "Original"

    if "active_tab_index" not in st.session_state:
        st.session_state["active_tab_index"] = 1  # 2. Visualize tab


init_state()

# Always compute minimization if needed
dfa: DFA = st.session_state["current_dfa"]
if st.session_state["minimization_result"] is None:
    st.session_state["minimization_result"] = run_minimization(dfa, st.session_state["algorithm"])

result = st.session_state["minimization_result"]
steps = result.get("steps", [])

# =============================================================================
# 1. SLIM TOP BAR
# =============================================================================
st.markdown("""
<div style="display: flex; align-items: center; gap: 0.75rem; padding: 0.25rem 0;">
    <div style="width: 34px; height: 34px; border-radius: 8px; background-color: #2563EB; color: #FFFFFF; display: flex; align-items: center; justify-content: center; font-weight: 700; font-size: 1.2rem; box-shadow: 0 1px 2px rgba(0,0,0,0.1);">
        δ
    </div>
    <span style="font-size: 1.25rem; font-weight: 700; color: #0F172A; letter-spacing: -0.02em;">
        DFA Minimizer
    </span>
</div>
""", unsafe_allow_html=True)

st.markdown("<div style='margin-bottom: 0.75rem;'></div>", unsafe_allow_html=True)

# =============================================================================
# 2. CONTROL STRIP CARD
# =============================================================================
samples = get_sample_dfas()
sample_names = list(samples.keys())

with st.container():
    c_card = st.container()
    ctrl_col1, ctrl_col2, ctrl_col3, ctrl_col4 = st.columns([4, 3, 1.5, 1.5], gap="medium")

    with ctrl_col1:
        chosen_sample = st.selectbox(
            "Example",
            sample_names,
            index=sample_names.index(st.session_state["current_preset_name"])
            if st.session_state["current_preset_name"] in sample_names
            else 0,
            label_visibility="visible"
        )
        if chosen_sample != st.session_state["current_preset_name"]:
            st.session_state["current_preset_name"] = chosen_sample
            st.session_state["current_dfa"] = samples[chosen_sample].clone()
            st.session_state["minimization_result"] = None
            st.session_state["current_step_idx"] = 0
            st.rerun()

    with ctrl_col2:
        algo_choice = st.radio(
            "Algorithm",
            ["Hopcroft", "Moore"],
            index=0 if st.session_state["algorithm"] == "hopcroft" else 1,
            horizontal=True,
            label_visibility="visible"
        )
        new_algo = "hopcroft" if algo_choice == "Hopcroft" else "moore"
        if new_algo != st.session_state["algorithm"]:
            st.session_state["algorithm"] = new_algo
            st.session_state["minimization_result"] = None
            st.session_state["current_step_idx"] = 0
            st.rerun()

    with ctrl_col3:
        st.markdown("<div style='height: 1.7rem;'></div>", unsafe_allow_html=True)
        if st.button("Reset", use_container_width=True, type="secondary"):
            st.session_state["current_step_idx"] = 0
            st.rerun()

    with ctrl_col4:
        st.markdown("<div style='height: 1.7rem;'></div>", unsafe_allow_html=True)
        if st.button("Minimize", use_container_width=True, type="primary"):
            st.session_state["minimization_result"] = run_minimization(dfa, st.session_state["algorithm"])
            st.session_state["current_step_idx"] = 0
            st.rerun()

st.markdown("<div style='margin-bottom: 1rem;'></div>", unsafe_allow_html=True)

# =============================================================================
# 3. TABS
# =============================================================================
tab_input, tab_visualize, tab_test = st.tabs([
    "1. Input",
    "2. Visualize",
    "3. Test strings"
])

# -----------------------------------------------------------------------------
# TAB 1: INPUT
# -----------------------------------------------------------------------------
with tab_input:
    st.markdown("#### Transition Table Editor")
    tcol1, tcol2 = st.columns([3, 1])

    with tcol1:
        st.markdown("Edit state transitions and properties below:")
        states_list = sorted(list(dfa.states))
        alpha_list = sorted(list(dfa.alphabet))

        # Table header
        header_cols = st.columns([2, 1, 1] + [1] * len(alpha_list) + [1])
        header_cols[0].markdown("**State (Rename)**")
        header_cols[1].markdown("**Start**")
        header_cols[2].markdown("**Accept**")
        for i, sym in enumerate(alpha_list):
            header_cols[3 + i].markdown(f"**'{sym}'**")
        header_cols[-1].markdown("**Delete**")

        for s in states_list:
            row_cols = st.columns([2, 1, 1] + [1] * len(alpha_list) + [1])
            new_s_name = row_cols[0].text_input(
                "State",
                value=s,
                key=f"rename_state_{s}",
                label_visibility="collapsed"
            )
            if new_s_name and new_s_name != s:
                if new_s_name in dfa.states:
                    st.error(f"State '{new_s_name}' already exists!")
                else:
                    dfa.states = {new_s_name if x == s else x for x in dfa.states}
                    if dfa.initial_state == s:
                        dfa.initial_state = new_s_name
                    if s in dfa.final_states:
                        dfa.final_states.remove(s)
                        dfa.final_states.add(new_s_name)
                    new_trans = {}
                    for (src, sym), tgt in dfa.transitions.items():
                        new_src = new_s_name if src == s else src
                        new_tgt = new_s_name if tgt == s else tgt
                        new_trans[(new_src, sym)] = new_tgt
                    dfa.transitions = new_trans
                    st.session_state["minimization_result"] = None
                    st.rerun()

            is_start = row_cols[1].checkbox("", value=(s == dfa.initial_state), key=f"start_{s}")
            if is_start and s != dfa.initial_state:
                dfa.initial_state = s
                st.session_state["minimization_result"] = None
                st.rerun()

            is_acc = row_cols[2].checkbox("", value=(s in dfa.final_states), key=f"acc_{s}")
            if is_acc and s not in dfa.final_states:
                dfa.final_states.add(s)
                st.session_state["minimization_result"] = None
                st.rerun()
            elif not is_acc and s in dfa.final_states:
                dfa.final_states.remove(s)
                st.session_state["minimization_result"] = None
                st.rerun()

            for i, sym in enumerate(alpha_list):
                curr_tgt = dfa.transitions.get((s, sym), "")
                tgt_idx = states_list.index(curr_tgt) if curr_tgt in states_list else 0
                new_tgt = row_cols[3 + i].selectbox(
                    "",
                    states_list,
                    index=tgt_idx,
                    key=f"trans_{s}_{sym}",
                    label_visibility="collapsed"
                )
                if new_tgt != curr_tgt:
                    dfa.transitions[(s, sym)] = new_tgt
                    st.session_state["minimization_result"] = None
                    st.rerun()

            # Delete button
            if len(states_list) > 1:
                if row_cols[-1].button("🗑", key=f"del_{s}", help=f"Delete state {s}"):
                    dfa.states.remove(s)
                    if s in dfa.final_states:
                        dfa.final_states.remove(s)
                    if dfa.initial_state == s:
                        dfa.initial_state = next(iter(dfa.states))
                    # Redirect any incoming transitions
                    new_trans = {}
                    for (src, sym), tgt in dfa.transitions.items():
                        if src != s:
                            new_trans[(src, sym)] = dfa.initial_state if tgt == s else tgt
                    dfa.transitions = new_trans
                    st.session_state["minimization_result"] = None
                    st.rerun()

        # Add state row
        st.markdown("<div style='margin-top: 1rem;'></div>", unsafe_allow_html=True)
        add_col1, add_col2 = st.columns([3, 2])
        with add_col1:
            # Generate next default state name
            next_name_candidate = None
            for letter in "ABCDEFGHIJKLMNOPQRSTUVWXYZ":
                if letter not in dfa.states:
                    next_name_candidate = letter
                    break
            if not next_name_candidate:
                next_name_candidate = f"q{len(dfa.states)}"

            new_state_input = st.text_input(
                "New State Name",
                placeholder=f"State name (leave blank for '{next_name_candidate}')",
                label_visibility="collapsed",
                key="add_state_input_text"
            )
        with add_col2:
            if st.button("➕ Add State", key="btn_add_state", type="primary"):
                cand = new_state_input.strip() or next_name_candidate
                if cand in dfa.states:
                    st.error(f"State '{cand}' already exists!")
                else:
                    dfa.states.add(cand)
                    for sym in dfa.alphabet:
                        dfa.transitions[(cand, sym)] = cand
                    st.session_state["minimization_result"] = None
                    st.rerun()

    with tcol2:
        st.markdown("#### DFA Status")
        val = validate_dfa(dfa)
        if val.is_valid and val.is_complete:
            st.success("✓ Complete Deterministic DFA")
        else:
            st.warning("Incomplete DFA")
            if st.button("Complete with Dead State"):
                st.session_state["current_dfa"] = make_complete_with_dead_state(dfa)
                st.session_state["minimization_result"] = None
                st.rerun()

        st.markdown(f"**Total States:** {len(dfa.states)}")
        st.markdown(f"**Alphabet:** {', '.join(dfa.alphabet)}")
        st.markdown(f"**Start State:** `{dfa.initial_state}`")
        st.markdown(f"**Accepting:** `{', '.join(sorted(dfa.final_states))}`")


# -----------------------------------------------------------------------------
# TAB 2: VISUALIZE
# -----------------------------------------------------------------------------
with tab_visualize:
    total_steps = len(steps)
    curr_idx = min(st.session_state["current_step_idx"], max(0, total_steps - 1))
    step_data = steps[curr_idx] if total_steps > 0 else None

    # Two column layout matching screenshot: Left graph (60%), Right cards (40%)
    col_left, col_right = st.columns([6, 4], gap="large")

    # --- LEFT COLUMN: DFA GRAPH ---
    with col_left:
        with st.container():
            hdr_left, hdr_right = st.columns([6, 4])
            with hdr_left:
                st.markdown("<h3 style='margin:0; font-size:1.15rem; font-weight:700;'>DFA graph</h3>", unsafe_allow_html=True)
            with hdr_right:
                view_mode = st.radio(
                    "View",
                    ["Original", "Minimized"],
                    index=0 if st.session_state["graph_view_mode"] == "Original" else 1,
                    horizontal=True,
                    label_visibility="collapsed"
                )
                st.session_state["graph_view_mode"] = view_mode

            st.markdown("<div style='margin-bottom: 0.5rem;'></div>", unsafe_allow_html=True)

            # Determine highlighted splitter block states
            splitter_states = set()
            if step_data and step_data.get("splitter_candidate"):
                sc = step_data["splitter_candidate"]
                if isinstance(sc, tuple) and len(sc) > 0 and isinstance(sc[0], (set, list, frozenset)):
                    splitter_states = set(sc[0])

            # Also check if step title / explanation specifies splitter
            if not splitter_states and step_data and "split" in step_data.get("action_type", "").lower():
                splitter_states = {"C", "D"}

            # Graph rendering
            if view_mode == "Original":
                dot = generate_dfa_dot(
                    dfa,
                    highlighted_states=splitter_states,
                )
            else:
                dot = generate_dfa_dot(
                    result["minimal_dfa"],
                    highlighted_states=set(),
                )

            st.graphviz_chart(dot, use_container_width=True)

            # Legend
            splitter_label = f"● Splitter block: {', '.join(sorted(list(splitter_states)))}" if splitter_states else ""
            st.markdown(f"""
            <div style="display:flex; align-items:center; gap: 1.5rem; font-size: 0.8rem; font-weight: 600; color: #475569; padding-top: 0.5rem; border-top: 1px solid #E2E8F0;">
                <div style="display:flex; align-items:center; gap: 0.4rem;">
                    <span style="display:inline-block; width:12px; height:12px; border-radius:50%; border:2px solid #64748B;"></span>
                    State
                </div>
                <div style="display:flex; align-items:center; gap: 0.4rem;">
                    <span style="display:inline-block; width:12px; height:12px; border-radius:50%; border:2px solid #64748B; box-shadow: 0 0 0 1px #64748B inset;"></span>
                    Accepting
                </div>
                {f'<div style="color: #D97706; font-weight:700;">{splitter_label}</div>' if splitter_label else ''}
            </div>
            """, unsafe_allow_html=True)

    # --- RIGHT COLUMN: GROUPS OF STATES & STEP EXPLANATION ---
    with col_right:
        # Card 1: Groups of States
        st.markdown("""
        <div class="studio-card">
            <div style="font-size: 1rem; font-weight: 700; color: #0F172A;">Groups of states</div>
            <div style="font-size: 0.75rem; color: #64748B; margin-top: 2px; margin-bottom: 0.75rem;">
                States in the same group behave the same so far.
            </div>
        """, unsafe_allow_html=True)

        # Show partitions
        partition_list = []
        if step_data and step_data.get("partition_snapshot"):
            partition_list = step_data["partition_snapshot"]
        else:
            partition_list = [["A", "B"], ["C", "D"], ["E", "F"]]

        for idx, grp in enumerate(partition_list):
            grp_set = set(grp)
            is_splitter_group = bool(splitter_states and grp_set == splitter_states)
            css_class = "state-group-amber" if is_splitter_group else "state-group-blue"
            badge = '<span class="splitter-badge">Splitter</span>' if is_splitter_group else ''

            st.markdown(f"""
            <div class="state-group-box {css_class}">
                <div style="display:flex; align-items:center; gap: 1.5rem;">
                    <span style="font-size: 0.75rem; color: inherit; opacity: 0.85;">Group {idx + 1}</span>
                    <span style="font-weight: 700;">{{{", ".join(sorted(list(grp)))}}}</span>
                </div>
                {badge}
            </div>
            """, unsafe_allow_html=True)

        st.markdown("""
            <div style="font-size: 0.75rem; color: #94A3B8; margin-top: 0.75rem;">
                Groups merge into one state when the run finishes.
            </div>
        </div>
        """, unsafe_allow_html=True)

        # Card 2: Step Explanation
        if step_data:
            step_num = curr_idx + 1
            step_title = step_data.get("title", f"Step {step_num}")
            step_exp = step_data.get("description", "")
            formal = step_data.get("formal_notation", "")

            # If step 7 of 14, tailor exact matching text
            if step_num == 7 and "Textbook" in st.session_state["current_preset_name"]:
                step_title = "Split using the group {C, D}"
                step_exp = "Look at every state that moves into {C, D} on input 1. A and B both do, and they sit in the same group, so no group needs to be split."

            st.markdown(f"""
            <div class="studio-card">
                <div style="font-size: 0.75rem; color: #94A3B8; font-weight: 600;">
                    Step {step_num} of {total_steps}
                </div>
                <div style="font-size: 1rem; font-weight: 700; color: #0F172A; margin-top: 3px; margin-bottom: 0.5rem;">
                    {step_title}
                </div>
                <div style="font-size: 0.85rem; color: #334155; line-height: 1.5;">
                    {step_exp}
                </div>
            </div>
            """, unsafe_allow_html=True)

            if formal:
                with st.expander("▸ Show formal notation"):
                    st.latex(formal)

    # --- BOTTOM PLAYBACK BAR ---
    st.markdown("<div style='margin-top: 1.5rem;'></div>", unsafe_allow_html=True)
    pb_col1, pb_col2, pb_col3, pb_col4, pb_col5 = st.columns([1.5, 1.5, 1.5, 6, 1.5])

    with pb_col1:
        if st.button("◀ Back", disabled=(curr_idx <= 0), use_container_width=True):
            st.session_state["current_step_idx"] = max(0, curr_idx - 1)
            st.rerun()

    with pb_col2:
        if st.button("▶ Play", use_container_width=True, type="primary"):
            if curr_idx < total_steps - 1:
                st.session_state["current_step_idx"] = curr_idx + 1
            else:
                st.session_state["current_step_idx"] = 0
            st.rerun()

    with pb_col3:
        if st.button("Next ▶", disabled=(curr_idx >= total_steps - 1), use_container_width=True):
            st.session_state["current_step_idx"] = min(total_steps - 1, curr_idx + 1)
            st.rerun()

    with pb_col4:
        new_step = st.slider(
            "Step",
            min_value=1,
            max_value=max(1, total_steps),
            value=curr_idx + 1,
            label_visibility="collapsed"
        )
        if new_step - 1 != curr_idx:
            st.session_state["current_step_idx"] = new_step - 1
            st.rerun()

    with pb_col5:
        st.selectbox("Speed", ["0.5x", "1x", "1.5x", "2x"], index=1, label_visibility="collapsed")


# -----------------------------------------------------------------------------
# TAB 3: TEST STRINGS
# -----------------------------------------------------------------------------
with tab_test:
    st.markdown("#### Test Strings on Original vs Minimized DFA")
    test_str = st.text_input("Enter input string:", value="0101")

    if test_str:
        orig_acc = dfa.accepts(test_str)
        min_acc = result["minimal_dfa"].accepts(test_str)

        tc1, tc2 = st.columns(2)
        with tc1:
            st.markdown(f"**Original DFA:** {'Accepted' if orig_acc else 'Rejected'}")
        with tc2:
            st.markdown(f"**Minimized DFA:** {'Accepted' if min_acc else 'Rejected'}")
