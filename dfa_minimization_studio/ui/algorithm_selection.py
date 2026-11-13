"""
Tab 3: Algorithm Selection Module for DFA Minimization Studio.
"""

import streamlit as st


def render_algorithm_selection_tab():
    st.markdown("### ⚙️ Algorithm Selection")
    st.markdown(
        "Choose which minimization algorithm you want to study. "
        "Both algorithms produce an identical minimal DFA, but utilize fundamentally different partition refinement strategies."
    )

    current_algo = st.session_state.get("selected_algorithm", "hopcroft")

    col1, col2 = st.columns(2, gap="large")

    with col1:
        is_hopcroft_selected = current_algo == "hopcroft"
        border_color = "#2A9D8F" if is_hopcroft_selected else "#E2DDD5"
        bg_card = "#FFFFFF"

        st.markdown(f"""
        <div style="background-color: {bg_card}; border: 2.5px solid {border_color}; border-radius: 12px; padding: 1.5rem; height: 100%;">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.5rem;">
                <h3 style="color: #142B45; margin: 0; font-size: 1.35rem;">Hopcroft's Algorithm</h3>
                {'<span class="partition-pill">SELECTED</span>' if is_hopcroft_selected else ''}
            </div>
            <p style="color: #2C435F; font-size: 0.95rem; line-height: 1.5;">
                A worklist-driven partition refinement algorithm that maintains candidate splitter sets <code>A</code>.
            </p>
            <hr style="border: none; border-top: 1px solid #E2DDD5; margin: 1rem 0;">
            <p style="font-size: 0.9rem; color: #142B45;">
                <strong>Working Principle:</strong><br>
                Instead of examining all states simultaneously, Hopcroft takes a splitter block <code>A</code> from a worklist <code>W</code> and splits each block <code>Y ∈ P</code> into states that transition into <code>A</code> on symbol <code>σ</code> versus those that do not.
            </p>
            <p style="font-size: 0.9rem; color: #142B45;">
                <strong>Time Complexity:</strong><br>
                <code style="font-size: 1rem; color: #2A9D8F; font-weight: bold;">O(|Σ| · |Q| log |Q|)</code><br>
                <span style="font-size: 0.8rem; color: #2C435F;">Asymptotically the fastest known minimization algorithm.</span>
            </p>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("<div style='margin-top: 0.75rem;'></div>", unsafe_allow_html=True)
        if st.button("Select Hopcroft's Algorithm", key="btn_sel_hopcroft", use_container_width=True):
            st.session_state["selected_algorithm"] = "hopcroft"
            st.session_state["minimization_result"] = None
            st.session_state["current_step_idx"] = 0
            st.rerun()

    with col2:
        is_moore_selected = current_algo == "moore"
        border_color = "#2A9D8F" if is_moore_selected else "#E2DDD5"
        bg_card = "#FFFFFF"

        st.markdown(f"""
        <div style="background-color: {bg_card}; border: 2.5px solid {border_color}; border-radius: 12px; padding: 1.5rem; height: 100%;">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.5rem;">
                <h3 style="color: #142B45; margin: 0; font-size: 1.35rem;">Moore's Algorithm</h3>
                {'<span class="partition-pill">SELECTED</span>' if is_moore_selected else ''}
            </div>
            <p style="color: #2C435F; font-size: 0.95rem; line-height: 1.5;">
                An intuitive k-equivalence partition algorithm based on state transition signatures.
            </p>
            <hr style="border: none; border-top: 1px solid #E2DDD5; margin: 1rem 0;">
            <p style="font-size: 0.9rem; color: #142B45;">
                <strong>Working Principle:</strong><br>
                Iteratively computes <code>k</code>-equivalence partitions (starting at <code>k=0</code> for <code>F</code> vs <code>Q\F</code>). In round <code>k</code>, each state is assigned a signature vector of destination partitions. Blocks with divergent signatures split until convergence.
            </p>
            <p style="font-size: 0.9rem; color: #142B45;">
                <strong>Time Complexity:</strong><br>
                <code style="font-size: 1rem; color: #2A9D8F; font-weight: bold;">O(|Σ| · |Q|²)</code><br>
                <span style="font-size: 0.8rem; color: #2C435F;">Highly intuitive for human tracing and manual calculations.</span>
            </p>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("<div style='margin-top: 0.75rem;'></div>", unsafe_allow_html=True)
        if st.button("Select Moore's Algorithm", key="btn_sel_moore", use_container_width=True):
            st.session_state["selected_algorithm"] = "moore"
            st.session_state["minimization_result"] = None
            st.session_state["current_step_idx"] = 0
            st.rerun()

    st.markdown("---")
    st.markdown("<div style='text-align: center;'>", unsafe_allow_html=True)
    if st.button("Proceed to Minimization Mode →", use_container_width=True):
        st.session_state["active_nav_tab"] = "Minimization Mode"
        st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)
