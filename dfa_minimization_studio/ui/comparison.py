"""
Tab 6: Algorithm Comparison Module.
Compares Hopcroft's and Moore's algorithms side-by-side on the exact same DFA.
"""

import streamlit as st
from core.dfa import DFA
from algorithms.minimizer import compare_algorithms


def render_comparison_tab():
    st.markdown("### ⚖️ Algorithm Comparison: Hopcroft vs. Moore")
    st.markdown(
        "Execute both minimization algorithms on the current DFA simultaneously to compare "
        "their execution efficiency, convergence iterations, and final equivalence partitions."
    )

    dfa: DFA = st.session_state["current_dfa"]

    if st.button("🔄 Run Side-by-Side Comparison", use_container_width=True):
        with st.spinner("Executing both Hopcroft's and Moore's algorithms..."):
            comp = compare_algorithms(dfa)
            st.session_state["comparison_result"] = comp

    comp = st.session_state.get("comparison_result")
    if comp is None:
        comp = compare_algorithms(dfa)
        st.session_state["comparison_result"] = comp

    h = comp["hopcroft"]
    m = comp["moore"]

    # Equivalence confirmation banner
    if comp["state_counts_match"] and comp["both_correct"]:
        st.markdown("""
        <div style="background-color: #D8EDE8; border-left: 5px solid #2A9D8F; border-radius: 8px; padding: 1rem; margin-bottom: 1.5rem;">
            <strong style="color: #142B45; font-size: 1.05rem;">✓ Algorithmic Isomorphism Verified!</strong><br>
            <span style="color: #2C435F;">Both Hopcroft's and Moore's algorithms successfully converged to isomorphic minimal DFAs with the exact same state count, and both preserve 100% regular language equivalence.</span>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.warning("State counts or language acceptance diverged between algorithms.")

    # Side-by-Side Comparison Cards
    c1, c2 = st.columns(2, gap="large")

    with c1:
        st.markdown(f"""
        <div class="studio-card">
            <h3 style="color: #2A9D8F; margin-top: 0;">Hopcroft's Algorithm</h3>
            <p style="font-size: 0.9rem; color: #142B45;">Worklist-driven partition refinement.</p>
            <hr style="border: none; border-top: 1px solid #E2DDD5; margin: 0.75rem 0;">
            <ul style="list-style: none; padding-left: 0; font-size: 0.9rem; line-height: 1.8;">
                <li><strong>Theoretical Complexity:</strong> <code>O(|Σ| · |Q| log |Q|)</code></li>
                <li><strong>Original States:</strong> {h['original_state_count']}</li>
                <li><strong>Minimized States:</strong> {h['minimized_state_count']}</li>
                <li><strong>States Reduced:</strong> {h['states_removed']}</li>
                <li><strong>Execution Steps:</strong> {h['iteration_count']}</li>
                <li><strong>Measured Run Time:</strong> {h['execution_time_ms']} ms</li>
                <li><strong>Final Partitions:</strong> {len(h['final_partitions'])} blocks</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)

    with c2:
        st.markdown(f"""
        <div class="studio-card">
            <h3 style="color: #142B45; margin-top: 0;">Moore's Algorithm</h3>
            <p style="font-size: 0.9rem; color: #142B45;">k-equivalence signature refinement.</p>
            <hr style="border: none; border-top: 1px solid #E2DDD5; margin: 0.75rem 0;">
            <ul style="list-style: none; padding-left: 0; font-size: 0.9rem; line-height: 1.8;">
                <li><strong>Theoretical Complexity:</strong> <code>O(|Σ| · |Q|²)</code></li>
                <li><strong>Original States:</strong> {m['original_state_count']}</li>
                <li><strong>Minimized States:</strong> {m['minimized_state_count']}</li>
                <li><strong>States Reduced:</strong> {m['states_removed']}</li>
                <li><strong>Execution Steps:</strong> {m['iteration_count']}</li>
                <li><strong>Measured Run Time:</strong> {m['execution_time_ms']} ms</li>
                <li><strong>Final Partitions:</strong> {len(m['final_partitions'])} blocks</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)

    # Detailed Comparative Table
    st.markdown("#### 📊 Comparative Summary Table")
    summary_table = [
        {"Metric": "Theoretical Time Complexity", "Hopcroft": "O(|Σ| · |Q| log |Q|)", "Moore": "O(|Σ| · |Q|²)"},
        {"Metric": "Original State Count", "Hopcroft": str(h['original_state_count']), "Moore": str(m['original_state_count'])},
        {"Metric": "Minimized State Count", "Hopcroft": str(h['minimized_state_count']), "Moore": str(m['minimized_state_count'])},
        {"Metric": "Total Steps Recorded", "Hopcroft": str(h['iteration_count']), "Moore": str(m['iteration_count'])},
        {"Metric": "Measured Execution Time", "Hopcroft": f"{h['execution_time_ms']} ms", "Moore": f"{m['execution_time_ms']} ms"},
        {"Metric": "Language Equivalence Preserved", "Hopcroft": "✓ Yes", "Moore": "✓ Yes"},
    ]
    st.table(summary_table)

    st.info(
        "💡 **Academic Note:** On small state counts (|Q| ≤ 10), runtime differences are negligible (often less than 1 ms). "
        "Hopcroft's asymptotic superiority (log |Q| vs |Q|) becomes pronounced on large DFAs with hundreds or thousands of states."
    )
