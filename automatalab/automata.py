"""Deterministic finite automata and language-equivalence checking."""
from collections import deque
from dataclasses import dataclass

@dataclass
class DFA:
    states: tuple
    alphabet: tuple
    start: str
    accepting: frozenset
    transitions: dict

    def __post_init__(self):
        if self.start not in self.states or not self.accepting <= set(self.states):
            raise ValueError("Invalid start or accepting state")
        for q in self.states:
            if set(self.transitions.get(q, {})) != set(self.alphabet):
                raise ValueError(f"Incomplete transition row: {q}")
            if any(t not in self.states for t in self.transitions[q].values()):
                raise ValueError(f"Unknown target from {q}")

    def run(self, word):
        q = self.start
        for c in word:
            if c not in self.alphabet: raise ValueError(f"Unknown symbol: {c}")
            q = self.transitions[q][c]
        return q in self.accepting

@dataclass
class EquivalenceResult:
    equivalent: bool
    counterexample: str | None
    explored_pairs: int

def equivalent(a: DFA, b: DFA) -> EquivalenceResult:
    """Product-automaton BFS; returns a shortest distinguishing word."""
    if set(a.alphabet) != set(b.alphabet): raise ValueError("Alphabets must match")
    alphabet = a.alphabet
    start = (a.start, b.start)
    queue = deque([start]); parent = {start: None}; via = {}
    while queue:
        p, q = queue.popleft()
        if (p in a.accepting) != (q in b.accepting):
            chars=[]; cur=(p,q)
            while parent[cur] is not None:
                chars.append(via[cur]); cur=parent[cur]
            return EquivalenceResult(False, "".join(reversed(chars)), len(parent))
        for c in alphabet:
            nxt=(a.transitions[p][c], b.transitions[q][c])
            if nxt not in parent:
                parent[nxt]=(p,q); via[nxt]=c; queue.append(nxt)
    return EquivalenceResult(True, None, len(parent))
