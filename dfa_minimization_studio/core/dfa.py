"""
Core DFA (Deterministic Finite Automaton) Data Structure.
Formal definition M = (Q, Σ, δ, q0, F)
"""

from dataclasses import dataclass, field
from typing import Set, Dict, List, Tuple, Optional


@dataclass
class Transition:
    from_state: str
    symbol: str
    to_state: str

    def to_tuple(self) -> Tuple[str, str, str]:
        return (self.from_state, self.symbol, self.to_state)


@dataclass
class DFA:
    states: Set[str] = field(default_factory=set)
    alphabet: Set[str] = field(default_factory=set)
    transitions: Dict[Tuple[str, str], str] = field(default_factory=dict)  # (state, symbol) -> next_state
    initial_state: str = ""
    final_states: Set[str] = field(default_factory=set)

    def add_state(self, state: str, is_initial: bool = False, is_final: bool = False):
        self.states.add(state)
        if is_initial:
            self.initial_state = state
        if is_final:
            self.final_states.add(state)

    def add_symbol(self, symbol: str):
        self.alphabet.add(symbol)

    def add_transition(self, from_state: str, symbol: str, to_state: str):
        self.states.add(from_state)
        self.states.add(to_state)
        self.alphabet.add(symbol)
        self.transitions[(from_state, symbol)] = to_state

    def get_transition(self, state: str, symbol: str) -> Optional[str]:
        return self.transitions.get((state, symbol))

    def accepts(self, input_str: str) -> bool:
        """Determines if the DFA accepts the given input string."""
        curr = self.initial_state
        if not curr:
            return False
        for char in input_str:
            if char not in self.alphabet:
                return False
            dest = self.get_transition(curr, char)
            if not dest:
                return False
            curr = dest
        return curr in self.final_states

    def get_transition_table(self) -> Dict[str, Dict[str, str]]:
        """Returns {state: {symbol: to_state}} for easy tabular inspection."""
        table: Dict[str, Dict[str, str]] = {s: {} for s in sorted(self.states)}
        for s in self.states:
            for sym in self.alphabet:
                dest = self.transitions.get((s, sym), "")
                table[s][sym] = dest
        return table

    def clone(self) -> 'DFA':
        return DFA(
            states=set(self.states),
            alphabet=set(self.alphabet),
            transitions=dict(self.transitions),
            initial_state=self.initial_state,
            final_states=set(self.final_states)
        )

    def to_dict(self) -> dict:
        return {
            "states": sorted(list(self.states)),
            "alphabet": sorted(list(self.alphabet)),
            "initial_state": self.initial_state,
            "final_states": sorted(list(self.final_states)),
            "transitions": [
                {"from_state": s, "symbol": sym, "to_state": dest}
                for (s, sym), dest in sorted(self.transitions.items())
            ]
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'DFA':
        dfa = cls(
            states=set(data.get("states", [])),
            alphabet=set(data.get("alphabet", [])),
            initial_state=data.get("initial_state", ""),
            final_states=set(data.get("final_states", []))
        )
        for t in data.get("transitions", []):
            dfa.transitions[(t["from_state"], t["symbol"])] = t["to_state"]
        return dfa
