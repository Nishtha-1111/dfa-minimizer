import pytest
from backend.app.main import validate_endpoint, minimize_endpoint, simulate_endpoint, health_check
from backend.app.models import DFAModel, ValidationRequest, MinimizeRequest, SimulateRequest

TEXTBOOK_DFA = DFAModel(
    states=["A", "B", "C", "D", "E", "F"],
    alphabet=["0", "1"],
    start_state="A",
    accept_states=["C", "D"],
    transitions={
        "A": {"0": "B", "1": "C"},
        "B": {"0": "A", "1": "D"},
        "C": {"0": "E", "1": "E"},
        "D": {"0": "F", "1": "E"},
        "E": {"0": "E", "1": "F"},
        "F": {"0": "F", "1": "F"}
    }
)

ALREADY_MINIMAL_DFA = DFAModel(
    states=["q0", "q1"],
    alphabet=["0", "1"],
    start_state="q0",
    accept_states=["q1"],
    transitions={
        "q0": {"0": "q1", "1": "q0"},
        "q1": {"0": "q0", "1": "q1"}
    }
)

UNREACHABLE_DFA = DFAModel(
    states=["q0", "q1", "u1", "u2"],
    alphabet=["0", "1"],
    start_state="q0",
    accept_states=["q1", "u2"],
    transitions={
        "q0": {"0": "q1", "1": "q0"},
        "q1": {"0": "q1", "1": "q0"},
        "u1": {"0": "u2", "1": "q0"},
        "u2": {"0": "u1", "1": "u2"}
    }
)

SINGLE_STATE_DFA = DFAModel(
    states=["q0"],
    alphabet=["0", "1"],
    start_state="q0",
    accept_states=["q0"],
    transitions={
        "q0": {"0": "q0", "1": "q0"}
    }
)

ALL_ACCEPT_DFA = DFAModel(
    states=["s1", "s2", "s3"],
    alphabet=["a", "b"],
    start_state="s1",
    accept_states=["s1", "s2", "s3"],
    transitions={
        "s1": {"a": "s2", "b": "s3"},
        "s2": {"a": "s3", "b": "s1"},
        "s3": {"a": "s1", "b": "s2"}
    }
)

NO_ACCEPT_DFA = DFAModel(
    states=["r1", "r2"],
    alphabet=["0", "1"],
    start_state="r1",
    accept_states=[],
    transitions={
        "r1": {"0": "r2", "1": "r1"},
        "r2": {"0": "r1", "1": "r2"}
    }
)


def test_health():
    res = health_check()
    assert res["status"] == "ok"


def test_validation():
    # Valid DFA
    res = validate_endpoint(ValidationRequest(dfa=TEXTBOOK_DFA))
    assert res.is_valid is True
    assert res.is_complete is True
    assert len(res.missing_transitions) == 0

    # Incomplete DFA
    incomplete = DFAModel(
        states=TEXTBOOK_DFA.states,
        alphabet=TEXTBOOK_DFA.alphabet,
        start_state=TEXTBOOK_DFA.start_state,
        accept_states=TEXTBOOK_DFA.accept_states,
        transitions={"A": {"0": "B"}}
    )
    res_inc = validate_endpoint(ValidationRequest(dfa=incomplete))
    assert res_inc.is_complete is False
    assert len(res_inc.missing_transitions) > 0


def test_minimize_textbook_table_filling_and_moore():
    # Table-Filling (Myhill-Nerode)
    res_tf = minimize_endpoint(MinimizeRequest(dfa=TEXTBOOK_DFA, algorithm="table_filling"))
    assert len(res_tf.minimal_dfa.states) == 3
    assert res_tf.state_mapping["A"] == res_tf.state_mapping["B"]
    assert res_tf.state_mapping["C"] == res_tf.state_mapping["D"]
    assert res_tf.state_mapping["E"] == res_tf.state_mapping["F"]

    # Moore
    res_m = minimize_endpoint(MinimizeRequest(dfa=TEXTBOOK_DFA, algorithm="moore"))
    assert len(res_m.minimal_dfa.states) == 3
    assert res_m.state_mapping["A"] == res_m.state_mapping["B"]
    assert res_m.state_mapping["C"] == res_m.state_mapping["D"]
    assert res_m.state_mapping["E"] == res_m.state_mapping["F"]

    # Both Table-Filling and Moore produce identical minimal quotient state equivalence
    assert res_tf.minimal_dfa.states == res_m.minimal_dfa.states


def test_minimize_already_minimal():
    res = minimize_endpoint(MinimizeRequest(dfa=ALREADY_MINIMAL_DFA, algorithm="table_filling"))
    assert len(res.minimal_dfa.states) == 2
    assert res.is_already_minimal is True


def test_minimize_unreachable_removal():
    res = minimize_endpoint(MinimizeRequest(dfa=UNREACHABLE_DFA, algorithm="table_filling"))
    assert set(res.unreachable_states) == {"u1", "u2"}
    assert "u1" not in res.pruned_dfa.states
    assert "u2" not in res.pruned_dfa.states


def test_edge_cases():
    # Single-state DFA
    res_single = minimize_endpoint(MinimizeRequest(dfa=SINGLE_STATE_DFA, algorithm="table_filling"))
    assert len(res_single.minimal_dfa.states) == 1

    # All-accept DFA merges into 1
    res_all = minimize_endpoint(MinimizeRequest(dfa=ALL_ACCEPT_DFA, algorithm="moore"))
    assert len(res_all.minimal_dfa.states) == 1

    # No-accept DFA merges into 1
    res_none = minimize_endpoint(MinimizeRequest(dfa=NO_ACCEPT_DFA, algorithm="table_filling"))
    assert len(res_none.minimal_dfa.states) == 1


def test_simulate_endpoint():
    min_res = minimize_endpoint(MinimizeRequest(dfa=TEXTBOOK_DFA, algorithm="table_filling"))
    min_dfa = min_res.minimal_dfa

    # Valid string accepted: 01 (A -> B -> D)
    res = simulate_endpoint(SimulateRequest(
        original_dfa=TEXTBOOK_DFA,
        minimal_dfa=min_dfa,
        input_string="01"
    ))
    assert res.is_valid_alphabet is True
    assert res.original_result.accepted is True
    assert res.minimized_result.accepted is True
    assert res.agreement is True

    # Empty string (ε) test: A is not accept state
    res_empty = simulate_endpoint(SimulateRequest(
        original_dfa=TEXTBOOK_DFA,
        minimal_dfa=min_dfa,
        input_string=""
    ))
    assert res_empty.original_result.accepted is False
    assert res_empty.agreement is True

    # Invalid alphabet character (e.g. '2')
    res_invalid = simulate_endpoint(SimulateRequest(
        original_dfa=TEXTBOOK_DFA,
        minimal_dfa=min_dfa,
        input_string="0120"
    ))
    assert res_invalid.is_valid_alphabet is False
    assert "Invalid character" in res_invalid.alphabet_error
