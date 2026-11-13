"""
Curated Sample DFAs for experimentations in DFA Minimization Studio.
"""

from core.dfa import DFA


def get_sample_dfas():
    return {
        "Textbook Example (Equivalent States)": DFA(
            states={"A", "B", "C", "D", "E", "F"},
            alphabet={"0", "1"},
            initial_state="A",
            final_states={"C", "D"},
            transitions={
                ("A", "0"): "B", ("A", "1"): "C",
                ("B", "0"): "A", ("B", "1"): "D",
                ("C", "0"): "E", ("C", "1"): "F",
                ("D", "0"): "E", ("D", "1"): "F",
                ("E", "0"): "E", ("E", "1"): "F",
                ("F", "0"): "F", ("F", "1"): "F",
            }
        ),
        "Already Minimal DFA (Ends in '01')": DFA(
            states={"q0", "q1", "q2"},
            alphabet={"0", "1"},
            initial_state="q0",
            final_states={"q2"},
            transitions={
                ("q0", "0"): "q1", ("q0", "1"): "q0",
                ("q1", "0"): "q1", ("q1", "1"): "q2",
                ("q2", "0"): "q1", ("q2", "1"): "q0",
            }
        ),
        "DFA with Unreachable States": DFA(
            states={"q0", "q1", "q2", "q3", "q4", "q5"},
            alphabet={"a", "b"},
            initial_state="q0",
            final_states={"q2", "q5"},
            transitions={
                ("q0", "a"): "q1", ("q0", "b"): "q2",
                ("q1", "a"): "q0", ("q1", "b"): "q3",
                ("q2", "a"): "q2", ("q2", "b"): "q2",
                ("q3", "a"): "q3", ("q3", "b"): "q3",
                ("q4", "a"): "q5", ("q4", "b"): "q4",
                ("q5", "a"): "q4", ("q5", "b"): "q5",
            }
        ),
        "Binary Divisible by 3 (Redundant)": DFA(
            states={"r0", "r1_a", "r1_b", "r2_a", "r2_b"},
            alphabet={"0", "1"},
            initial_state="r0",
            final_states={"r0"},
            transitions={
                ("r0", "0"): "r0", ("r0", "1"): "r1_a",
                ("r1_a", "0"): "r2_a", ("r1_a", "1"): "r0",
                ("r1_b", "0"): "r2_b", ("r1_b", "1"): "r0",
                ("r2_a", "0"): "r1_b", ("r2_a", "1"): "r2_a",
                ("r2_b", "0"): "r1_a", ("r2_b", "1"): "r2_b",
            }
        ),
        "Total Merge (Universal Language)": DFA(
            states={"q0", "q1", "q2", "q3"},
            alphabet={"0", "1"},
            initial_state="q0",
            final_states={"q0", "q1", "q2", "q3"},
            transitions={
                ("q0", "0"): "q1", ("q0", "1"): "q2",
                ("q1", "0"): "q2", ("q1", "1"): "q3",
                ("q2", "0"): "q3", ("q2", "1"): "q0",
                ("q3", "0"): "q0", ("q3", "1"): "q1",
            }
        ),
        "8-State Complex Benchmark": DFA(
            states={"s0", "s1", "s2", "s3", "s4", "s5", "s6", "s7"},
            alphabet={"a", "b"},
            initial_state="s0",
            final_states={"s2", "s5", "s7"},
            transitions={
                ("s0", "a"): "s1", ("s0", "b"): "s3",
                ("s1", "a"): "s2", ("s1", "b"): "s4",
                ("s2", "a"): "s1", ("s2", "b"): "s4",
                ("s3", "a"): "s4", ("s3", "b"): "s5",
                ("s4", "a"): "s4", ("s4", "b"): "s4",
                ("s5", "a"): "s5", ("s5", "b"): "s5",
                ("s6", "a"): "s7", ("s6", "b"): "s4",
                ("s7", "a"): "s6", ("s7", "b"): "s4",
            }
        )
    }
