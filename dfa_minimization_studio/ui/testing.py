"""
Tab 5: Interactive DFA String Testing Module.
"""

import streamlit as st
from core.dfa import DFA
from algorithms.minimizer import run_minimization
from core.simulator import simulate_both, batch_simulate


def render_testing_tab():
    st.markdown("### 🧪 Interactive DFA Testing")
    st.markdown(
        "Enter input strings to trace their execution paths simultaneously on both the original DFA "
        "and the minimized DFA to verify that language acceptance is strictly preserved."
    )

    dfa: DFA = st.session_state["current_dfa"]
    algorithm: str = st.session_state.get("selected_algorithm", "hopcroft")

    if st.session_state.get("minimization_result") is None:
        st.session_state["minimization_result"] = run_minimization(dfa, algorithm)

    result = st.session_state["minimization_result"]
    minimal_dfa = result["minimal_dfa"]

    tab_single, tab_batch = st.tabs(["Interactive Single String", "Batch Test Suite"])

    # --- 1. SINGLE STRING SIMULATION ---
    with tab_single:
        col_in1, col_in2 = st.columns([3, 1])
        with col_in1:
            test_str = st.text_input(
                "Input String (leave blank or type ε for empty string):",
                value="010",
                key="input_test_single_str"
            )
        with col_in2:
            st.markdown("<div style='margin-top: 1.7rem;'></div>", unsafe_allow_html=True)
            run_btn = st.button("Run Simulation", use_container_width=True)

        clean_input = "" if test_str.strip() in ["", "ε"] else test_str.strip()

        # Validate characters
        invalid_chars = [ch for ch in clean_input if ch not in dfa.alphabet]
        if invalid_chars:
            st.error(f"Invalid character(s) '{', '.join(invalid_chars)}' not in alphabet {sorted(list(dfa.alphabet))}.")
        else:
            sim = simulate_both(dfa, minimal_dfa, clean_input)

            # Verification Banner
            if sim["agreement"]:
                verdict = "ACCEPTED" if sim["original_accepted"] else "REJECTED"
                st.markdown(f"""
                <div style="background-color: #D8EDE8; border-left: 5px solid #2A9D8F; border-radius: 8px; padding: 1rem; margin: 1rem 0;">
                    <strong style="color: #142B45; font-size: 1.05rem;">✓ Language Equivalence Confirmed!</strong><br>
                    <span style="color: #2C435F;">Both the original DFA and the minimized DFA <strong>{verdict}</strong> the string <code>"{sim['input_string']}"</code>.</span>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.error("⚠️ Discrepancy detected between original and minimal DFA.")

            # Parallel State Paths
            p_col1, p_col2 = st.columns(2)
            with p_col1:
                st.markdown(f"**Original DFA Traversed Path:**")
                st.markdown(f"`{' → '.join(sim['original_path'])}`")
                acc_label = "✅ ACCEPTED" if sim["original_accepted"] else "❌ REJECTED"
                st.markdown(f"**Final Status:** {acc_label}")

            with p_col2:
                st.markdown(f"**Minimized DFA Traversed Path:**")
                st.markdown(f"`{' → '.join(sim['minimal_path'])}`")
                acc_label_min = "✅ ACCEPTED" if sim["minimal_accepted"] else "❌ REJECTED"
                st.markdown(f"**Final Status:** {acc_label_min}")

            # Step Breakdown Table
            st.markdown("---")
            st.markdown("#### Step-by-Step Transition Sequence")
            st.table(sim["steps"])

    # --- 2. BATCH TEST SUITE ---
    with tab_batch:
        st.markdown("Enter multiple strings to execute in batch (one per line, use ε or leave blank for empty string):")
        default_batch = "ε\n0\n1\n00\n01\n10\n11\n010\n110\n1001"
        batch_text = st.text_area("Test Strings:", value=default_batch, height=140)

        if st.button("Run Batch Tests"):
            raw_lines = [line.strip() for line in batch_text.split("\n") if line.strip() != ""]
            test_list = ["" if line == "ε" else line for line in raw_lines]

            batch_res = batch_simulate(dfa, minimal_dfa, test_list)
            all_agree = all(r["agreement"] for r in batch_res)

            if all_agree:
                st.success(f"✓ All {len(batch_res)} test strings yielded 100% agreement!")
            else:
                st.error("Some strings produced diverging results!")

            # Results table
            display_rows = []
            for r in batch_res:
                display_rows.append({
                    "String": r["input_string"],
                    "Original Result": "ACCEPT" if r["original_accepted"] else "REJECT",
                    "Minimized Result": "ACCEPT" if r["minimal_accepted"] else "REJECT",
                    "Agreement": "✓ Yes" if r["agreement"] else "✗ Diverged",
                    "Original Path": " → ".join(r["original_path"])
                })
            st.table(display_rows)
