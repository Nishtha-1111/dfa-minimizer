import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from core.samples import get_sample_dfas
from algorithms.hopcroft import hopcroft_minimize
from algorithms.moore import moore_minimize
from core.simulator import batch_simulate


def test_hopcroft_textbook_sample():
    samples = get_sample_dfas()
    dfa = samples["Textbook Example (Equivalent States)"]
    min_dfa, steps, mapping = hopcroft_minimize(dfa)

    assert len(min_dfa.states) == 3
    assert len(steps) >= 3


def test_moore_textbook_sample():
    samples = get_sample_dfas()
    dfa = samples["Textbook Example (Equivalent States)"]
    min_dfa, steps, mapping = moore_minimize(dfa)

    assert len(min_dfa.states) == 3
    assert len(steps) >= 3


def test_both_algorithms_match_and_preserve_language():
    samples = get_sample_dfas()
    for name, dfa in samples.items():
        min_h, _, _ = hopcroft_minimize(dfa)
        min_m, _, _ = moore_minimize(dfa)

        # Both must produce identical state counts
        assert len(min_h.states) == len(min_m.states), f"State counts differ on {name}"

        # Both must accept exactly the same language
        test_strings = ["", "0", "1", "00", "01", "10", "11", "001", "110", "1001", "a", "b", "ab", "ba", "aba"]
        valid_strings = [s for s in test_strings if all(c in dfa.alphabet for c in s)]

        h_results = batch_simulate(dfa, min_h, valid_strings)
        m_results = batch_simulate(dfa, min_m, valid_strings)

        assert all(r["agreement"] for r in h_results), f"Hopcroft diverged on {name}"
        assert all(r["agreement"] for r in m_results), f"Moore diverged on {name}"
