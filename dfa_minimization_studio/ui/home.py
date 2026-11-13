"""
Tab 1: Home / Introduction Module for DFA Minimization Studio.
"""

import streamlit as st


def render_home_tab():
    st.markdown("""
    <div style="text-align: center; margin-bottom: 2rem;">
        <h1 style="color: #142B45; font-size: 2.25rem; margin-bottom: 0.5rem;">
            DFA Minimization Studio
        </h1>
        <p style="color: #2C435F; font-size: 1.1rem; max-width: 700px; margin: 0 auto;">
            An interactive educational platform designed for students exploring Theory of Computation 
            and Formal Languages to master deterministic finite automaton minimization.
        </p>
    </div>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("""
        <div class="studio-card">
            <div class="card-title">📖 What is DFA Minimization?</div>
            <div class="card-desc">
                DFA minimization is the algorithmic process of transforming a given Deterministic Finite Automaton (DFA) 
                into an equivalent automaton that has the <strong>minimum possible number of states</strong>, 
                while recognizing the exact same regular language <code>L(M)</code>.
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("""
        <div class="studio-card">
            <div class="card-title">⚡ Why Minimize DFAs?</div>
            <div class="card-desc">
                <ul>
                    <li><strong>Hardware Efficiency:</strong> Minimizing states directly reduces the number of flip-flops (registers) required in digital sequential circuits.</li>
                    <li><strong>Compiler Optimizations:</strong> Lexical analyzers (like Lex/Flex) execute regular expressions faster using minimal state tables.</li>
                    <li><strong>Canonicity:</strong> By the Myhill-Nerode Theorem, the minimal DFA for any regular language is unique up to isomorphism.</li>
                </ul>
            </div>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown("""
        <div class="studio-card">
            <div class="card-title">🔬 Algorithms Implemented</div>
            <div class="card-desc">
                <p><strong>1. Hopcroft's Algorithm:</strong> The gold standard in computational theory. Uses partition refinement with a candidate splitter worklist <code>W</code> to achieve optimal <code>O(|Σ| · |Q| log |Q|)</code> time complexity.</p>
                <p><strong>2. Moore's Algorithm:</strong> Iterative k-equivalence partition refinement. Generates state transition signatures in <code>O(|Σ| · |Q|²)</code> time, providing clear intuition for step-by-step learning.</p>
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("""
        <div class="studio-card">
            <div class="card-title">🗺️ Simple Guided Workflow</div>
            <div class="card-desc">
                <ol>
                    <li><strong>Design:</strong> Build your DFA or pick a textbook sample in the <em>DFA Designer</em> tab.</li>
                    <li><strong>Select Algorithm:</strong> Choose Hopcroft or Moore in <em>Algorithm Selection</em>.</li>
                    <li><strong>Minimize:</strong> View the final reduced DFA or step through partition splits interactively.</li>
                    <li><strong>Verify:</strong> Test strings and compare both algorithms side-by-side.</li>
                </ol>
            </div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<div style='text-align: center; margin-top: 1.5rem;'>", unsafe_allow_html=True)
    if st.button("🚀 Start a DFA Minimization Session", use_container_width=True):
        st.session_state["active_nav_tab"] = "DFA Designer"
        st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)
