# AutomataLab

A practical Formal Language and Automata toolkit demonstrating three software-verification ideas:

1. **Finite-state loop detection** — detect a reachable repeated state in a deterministic finite transition system.
2. **Lexer bug detection** — model a small token recogniser as a DFA, mutate a transition, and find an input that exposes the defect.
3. **Program equivalence** — compare two DFAs using product-automaton breadth-first search and return a shortest distinguishing string.

## Requirements

- Python 3.10 or later
- No third-party packages required

## Setup

```bash
git clone https://github.com/Arshad-Navaz/automatalab1.git
cd automatalab1
python3 -m unittest discover -s tests -v
```

## Try the modules

```python
from automatalab.lexer import reference_lexer, find_mutant_counterexample
from automatalab.loops import analyse

lexer = reference_lexer()
print(lexer.run("a"))       # True: identifier-like token
print(lexer.run("<="))      # True: less-than-or-equal token
print(lexer.run("ad"))      # False: invalid mixed token

bug = find_mutant_counterexample()
print(bug.equivalent)       # False
print(bug.counterexample)   # <=

loop = analyse({"S0": "S1", "S1": "S2", "S2": "S1"}, "S0", "HALT")
print(loop["cycle"])        # ['S1', 'S2', 'S1']
```

## How it works

### DFA equivalence

The product-BFS algorithm explores state pairs from the two DFAs. If exactly one state in a pair is accepting, the input used to reach that pair distinguishes the languages. BFS guarantees that this counterexample is shortest. If no such pair is reachable, the DFAs are equivalent.

### Lexer bug detection

The lexer recognises abstract input classes: `a` for a letter, `d` for a digit, and literal `=` and `<` operator characters. The example mutant breaks the transition that recognises `<=`. Equivalence checking returns the shortest input that reveals the defect.

### Infinite-loop detection

A deterministic finite transition system has one next state per current state. During execution, revisiting a state before reaching the halt state proves that execution will repeat the same cycle indefinitely. This is exact for the finite-state model supplied.

## Important limitation

This project analyses **finite automata and finite-state models**. It does not solve the halting problem or prove semantic equivalence for arbitrary unrestricted programs; those general problems are undecidable.

## Project structure

```text
automatalab1/
├── automatalab/
│   ├── automata.py
│   ├── lexer.py
│   ├── loops.py
│   └── __init__.py
├── examples/
│   ├── even_a.json
│   └── odd_a.json
├── tests/
│   └── test_project.py
├── pyproject.toml
├── LICENSE
└── README.md
```

## Academic context

AutomataLab is the implementation companion to a Formal Language and Automata report on infinite-loop detection, compiler/lexer bug detection, and program equivalence checking. It is intended for learning, demonstrations, and controlled experiments.
