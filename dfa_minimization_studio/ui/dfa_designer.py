"""
Tab 2: DFA Designer Module for DFA Minimization Studio.
Allows creating, editing, table input, sample loading, and real-time visualization.
"""

import streamlit as st
from core.dfa import DFA
from core.validator import validate_dfa, make_complete_with_dead_state
from core.samples import get_sample_dfas
from visualization.graph_visualizer import generate_dfa_dot


def render_dfa_designer_tab():
    st.markdown("### ✏️ DFA Designer")
    st.markdown(
        "Build a custom automaton, load a curated textbook sample, or configure transitions using the table below."
    )

    dfa: DFA = st.session_state["current_dfa"]

    # 1. Preset Loader Toolbar
    with st.expander("📚 Load a Preset Textbook DFA", expanded=False):
        sample_dict = get_sample_dfas()
        col_s1, col_s2 = st.columns([3, 1])
        with col_s1:
            chosen_sample = st.selectbox("Choose a sample:", list(sample_dict.keys()))
        with col_s2:
            st.markdown("<div style='margin-top: 1.7rem;'></div>", unsafe_allow_html=True)
            if st.button("Load Preset"):
                st.session_state["current_dfa"] = sample_dict[chosen_sample].clone()
                st.session_state["minimization_result"] = None
                st.session_state["current_step_idx"] = 0
                st.success(f"Loaded '{chosen_sample}'!")
                st.rerun()

    # 2. Main Layout: Two Columns (Left: Configuration Controls, Right: Visual Graph Preview)
    col_left, col_right = st.columns([1, 1], gap="large")

    with col_left:
        st.markdown("#### 1. States & Alphabet")

        # States management
        state_list = sorted(list(dfa.states))
        st.markdown(f"**Current States:** `[{', '.join(state_list)}]`")

        col_st1, col_st2 = st.columns([3, 1])
        with col_st1:
            new_state = st.text_input("Add State Name", placeholder="e.g. q3", key="input_new_state")
        with col_st2:
            st.markdown("<div style='margin-top: 1.7rem;'></div>", unsafe_allow_html=True)
            if st.button("Add State"):
                if new_state.strip():
                    dfa.add_state(new_state.strip())
                    if not dfa.initial_state:
                        dfa.initial_state = new_state.strip()
                    st.rerun()

        # Rename / Delete state
        if state_list:
            with st.expander("Manage Existing States (Rename or Delete)"):
                col_m1, col_m2 = st.columns(2)
                with col_m1:
                    target_state = st.selectbox("Select State", state_list, key="sel_state_del")
                    if st.button("Delete State"):
                        dfa.states.remove(target_state)
                        dfa.final_states.discard(target_state)
                        if dfa.initial_state == target_state:
                            dfa.initial_state = sorted(list(dfa.states))[0] if dfa.states else ""
                        dfa.transitions = {
                            k: v for k, v in dfa.transitions.items()
                            if k[0] != target_state and v != target_state
                        }
                        st.rerun()
                with col_m2:
                    rename_target = st.selectbox("State to Rename", state_list, key="sel_rename_st")
                    renamed_val = st.text_input("New Name", key="rename_val_st")
                    if st.button("Rename"):
                        if renamed_val.strip() and renamed_val.strip() not in dfa.states:
                            old = rename_target
                            new = renamed_val.strip()
                            dfa.states.remove(old)
                            dfa.states.add(new)
                            if dfa.initial_state == old:
                                dfa.initial_state = new
                            if old in dfa.final_states:
                                dfa.final_states.remove(old)
                                dfa.final_states.add(new)
                            new_trans = {}
                            for (s, sym), dest in dfa.transitions.items():
                                src = new if s == old else s
                                dst = new if dest == old else dest
                                new_trans[(src, sym)] = dst
                            dfa.transitions = new_trans
                            st.rerun()

        # Alphabet Management
        alphabet_list = sorted(list(dfa.alphabet))
        st.markdown(f"**Alphabet (Σ):** `[{', '.join(alphabet_list)}]`")

        col_sym1, col_sym2 = st.columns([3, 1])
        with col_sym1:
            new_sym = st.text_input("Add Input Symbol", placeholder="e.g. 0 or a", key="input_new_sym")
        with col_sym2:
            st.markdown("<div style='margin-top: 1.7rem;'></div>", unsafe_allow_html=True)
            if st.button("Add Symbol"):
                if new_sym.strip():
                    dfa.add_symbol(new_sym.strip())
                    st.rerun()

        if alphabet_list:
            with st.expander("Remove Alphabet Symbol"):
                del_sym = st.selectbox("Symbol to Delete", alphabet_list, key="sel_del_sym")
                if st.button("Delete Symbol"):
                    dfa.alphabet.remove(del_sym)
                    dfa.transitions = {k: v for k, v in dfa.transitions.items() if k[1] != del_sym}
                    st.rerun()

        st.markdown("---")
        st.markdown("#### 2. Initial & Final States")

        # Initial state dropdown
        if state_list:
            init_idx = state_list.index(dfa.initial_state) if dfa.initial_state in state_list else 0
            selected_init = st.selectbox("Initial State (q0)", state_list, index=init_idx)
            if selected_init != dfa.initial_state:
                dfa.initial_state = selected_init
                st.rerun()

            # Final states multiselect
            selected_finals = st.multiselect(
                "Final / Accepting States (F)",
                state_list,
                default=[s for s in dfa.final_states if s in state_list]
            )
            dfa.final_states = set(selected_finals)
        else:
            st.warning("Please add at least one state above.")

        st.markdown("---")
        st.markdown("#### 3. Transitions (Table Editor)")

        # Tabular transition editor
        if state_list and alphabet_list:
            st.markdown("Specify $\\delta(q, \\sigma)$ for each state and symbol:")
            for s in state_list:
                cols = st.columns([1] + [2 for _ in alphabet_list])
                cols[0].markdown(f"**{s}**")
                for idx, sym in enumerate(alphabet_list):
                    current_dest = dfa.get_transition(s, sym) or ""
                    options = [""] + state_list
                    default_idx = options.index(current_dest) if current_dest in options else 0
                    chosen_dest = cols[idx + 1].selectbox(
                        f"on '{sym}'",
                        options,
                        index=default_idx,
                        key=f"trans_{s}_{sym}",
                        label_visibility="collapsed"
                    )
                    if chosen_dest != current_dest:
                        if chosen_dest:
                            dfa.transitions[(s, sym)] = chosen_dest
                        else:
                            dfa.transitions.pop((s, sym), None)
                        st.rerun()
        else:
            st.info("Add states and alphabet symbols to configure transitions.")

    with col_right:
        st.markdown("#### 4. Visual DFA Preview")

        # Validation check
        val = validate_dfa(dfa)
        if val.is_valid and val.is_complete:
            st.success("Complete & Valid DFA ready for minimization.")
        elif not val.is_complete:
            st.warning(f"Incomplete DFA: Missing {len(val.missing_transitions)} transition(s).")
            if st.button("⚡ Add Dead / Trap State"):
                st.session_state["current_dfa"] = make_complete_with_dead_state(dfa)
                st.rerun()
        else:
            for err in val.errors:
                st.error(err)

        if val.unreachable_states:
            st.info(f"Unreachable states detected: {', '.join(val.unreachable_states)}. They will be removed in Phase 1.")

        # Graphviz graph rendering
        if dfa.states:
            dot_code = generate_dfa_dot(dfa)
            st.graphviz_chart(dot_code, use_container_width=True)
        else:
            st.markdown("""
            <div style="background-color: #FFFFFF; border: 2px dashed #E2DDD5; border-radius: 12px; padding: 3rem; text-align: center; color: #142B45;">
                No states created yet. Add a state or load a preset on the left!
            </div>
            """, unsafe_allow_html=True)

        st.markdown("<div style='margin-top: 1.5rem;'></div>", unsafe_allow_html=True)
        if st.button("Proceed to Algorithm Selection →", use_container_width=True):
            st.session_state["active_nav_tab"] = "Algorithm Selection"
            st.rerun()
