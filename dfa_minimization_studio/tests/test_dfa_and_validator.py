import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from core.dfa import DFA
from core.validator import validate_dfa, make_complete_with_dead_state, remove_unreachable_states
from core.samples import get_sample_dfas


def test_dfa_basic_operations():
    dfa = DFA()
    dfa.add_state("q0", is_initial=True)
    dfa.add_state("q1", is_final=True)
    dfa.add_symbol("0")
    dfa.add_transition("q0", "0", "q1")

    assert dfa.initial_state == "q0"
    assert "q1" in dfa.final_states
    assert dfa.get_transition("q0", "0") == "q1"


def test_validation_incomplete_and_dead_state():
    dfa = DFA(
        states={"q0", "q1"},
        alphabet={"a", "b"},
        initial_state="q0",
        final_states={"q1"},
        transitions={("q0", "a"): "q1"}
    )
    res = validate_dfa(dfa)
    assert res.is_valid
    assert not res.is_complete
    assert len(res.missing_transitions) == 3

    # Auto fix with dead state
    completed = make_complete_with_dead_state(dfa)
    c_res = validate_dfa(completed)
    assert c_res.is_valid
    assert c_res.is_complete


def test_remove_unreachable_states():
    samples = get_sample_dfas()
    unreach_dfa = samples["DFA with Unreachable States"]
    pruned, removed = remove_unreachable_states(unreach_dfa)

    assert removed == {"q4", "q5"}
    assert pruned.states == {"q0", "q1", "q2", "q3"}
