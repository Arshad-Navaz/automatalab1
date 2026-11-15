from collections import deque
from dataclasses import dataclass
import json

@dataclass(frozen=True)
class DFA:
    states: tuple
    alphabet: tuple
    start: str
    accepting: frozenset
    transitions: dict

    def __post_init__(self):
        ss, aa = set(self.states), set(self.alphabet)
        if not ss or len(ss) != len(self.states) or not aa or len(aa) != len(self.alphabet):
            raise ValueError("States and alphabet must be non-empty and unique.")
        if self.start not in ss or not self.accepting <= ss:
            raise ValueError("Invalid start or accepting state.")
        for s in self.states:
            if s not in self.transitions or set(self.transitions[s]) != aa:
                raise ValueError(f"Incomplete transition row for {s}.")
            if not set(self.transitions[s].values()) <= ss:
                raise ValueError(f"Unknown transition target from {s}.")

    def step(self, state, symbol):
        if symbol not in self.alphabet:
            raise ValueError(f"Unknown symbol: {symbol}")
        return self.transitions[state][symbol]

    def accepts(self, word):
        state = self.start
        for c in word:
            state = self.step(state, c)
        return state in self.accepting

    @classmethod
    def load(cls, path):
        with open(path, encoding="utf8") as handle:
            d = json.load(handle)
        return cls(tuple(d["states"]), tuple(d["alphabet"]), d["start"],
                   frozenset(d["accepting"]), d["transitions"])

@dataclass(frozen=True)
class EquivalenceResult:
    equivalent: bool
    counterexample: str | None
    explored_pairs: int

def product_bfs(a: DFA, b: DFA):
    if set(a.alphabet) != set(b.alphabet):
        raise ValueError("DFA alphabets must match.")
    start = (a.start, b.start)
    queue = deque([start])
    parent = {start: None}
    via = {}
    while queue:
        p, q = queue.popleft()
        if (p in a.accepting) != (q in b.accepting):
            chars = []
            cur = (p, q)
            while parent[cur] is not None:
                chars.append(via[cur])
                cur = parent[cur]
            return EquivalenceResult(False, "".join(reversed(chars)), len(parent))
        for symbol in a.alphabet:
            nxt = (a.step(p, symbol), b.step(q, symbol))
            if nxt not in parent:
                parent[nxt] = (p, q)
                via[nxt] = symbol
                queue.append(nxt)
    return EquivalenceResult(True, None, len(parent))

class UnionFind:
    def __init__(self, items):
        self.parent = {x: x for x in items}
        self.rank = {x: 0 for x in items}
    def find(self, x):
        if self.parent[x] != x:
            self.parent[x] = self.find(self.parent[x])
        return self.parent[x]
    def union(self, x, y):
        x, y = self.find(x), self.find(y)
        if x == y:
            return
        if self.rank[x] < self.rank[y]:
            x, y = y, x
        self.parent[y] = x
        if self.rank[x] == self.rank[y]:
            self.rank[x] += 1

def hopcroft_karp_equivalent(a: DFA, b: DFA):
    if set(a.alphabet) != set(b.alphabet):
        raise ValueError("DFA alphabets must match.")
    left = {s: ("A", s) for s in a.states}
    right = {s: ("B", s) for s in b.states}
    uf = UnionFind(list(left.values()) + list(right.values()))
    stack = [(a.start, b.start)]
    seen = set()
    while stack:
        p, q = stack.pop()
        if (p, q) in seen:
            continue
        seen.add((p, q))
        if (p in a.accepting) != (q in b.accepting):
            return False
        uf.union(left[p], right[q])
        for symbol in a.alphabet:
            stack.append((a.step(p, symbol), b.step(q, symbol)))
    return True
