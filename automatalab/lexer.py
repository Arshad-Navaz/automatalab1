import random
from .automata import DFA, product_bfs

def reference_lexer():
    states = ("q0", "qI", "qN", "q=", "q==", "q<", "q<=", "DEAD")
    alphabet = ("a", "d", "=", "<")
    dead = {c: "DEAD" for c in alphabet}
    transitions = {
        "q0": {"a": "qI", "d": "qN", "=": "q=", "<": "q<"},
        "qI": {"a": "qI", "d": "qI", "=": "DEAD", "<": "DEAD"},
        "qN": {"a": "DEAD", "d": "qN", "=": "DEAD", "<": "DEAD"},
        "q=": {"a": "DEAD", "d": "DEAD", "=": "q==", "<": "DEAD"},
        "q==": dict(dead),
        "q<": {"a": "DEAD", "d": "DEAD", "=": "q<=", "<": "DEAD"},
        "q<=": dict(dead), "DEAD": dict(dead)
    }
    return DFA(states, alphabet, "q0",
               frozenset({"qI", "qN", "q=", "q==", "q<", "q<="}), transitions)

def missing_le_mutant(reference=None):
    reference = reference or reference_lexer()
    transitions = {s: dict(reference.transitions[s]) for s in reference.states}
    transitions["q<"]["="] = "DEAD"
    return DFA(reference.states, reference.alphabet, reference.start,
               reference.accepting, transitions)

def random_differential(reference, mutant, n=100, seed=2026):
    rng = random.Random(seed)
    for _ in range(n):
        word = "".join(rng.choice(reference.alphabet) for _ in range(rng.randint(1, 5)))
        if reference.accepts(word) != mutant.accepts(word):
            return True
    return False

def mutation_experiment(mutants=100, tests=100, seed=2026):
    rng = random.Random(seed)
    reference = reference_lexer()
    detected = generated = 0
    while generated < mutants:
        transitions = {s: dict(reference.transitions[s]) for s in reference.states}
        state = rng.choice(reference.states)
        symbol = rng.choice(reference.alphabet)
        transitions[state][symbol] = rng.choice(
            [target for target in reference.states if target != transitions[state][symbol]])
        mutant = DFA(reference.states, reference.alphabet, reference.start,
                     reference.accepting, transitions)
        if product_bfs(reference, mutant).equivalent:
            continue
        generated += 1
        detected += random_differential(reference, mutant, tests, seed + generated)
    return {"mutants": generated, "exact_detected": generated,
            "random_detected": detected, "random_rate": detected / generated}
