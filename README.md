# AutomataLab — Interactive Formal Verification Toolkit

AutomataLab is a learning and demonstration tool for three Formal Language and Automata applications: finite-state loop detection, lexer bug detection, and DFA language-equivalence checking.

## Features
- Interactive Streamlit dashboard with four workspaces.
- DFA JSON editor, state-diagram visualisation, and input-string testing.
- DFA equivalence using product-automaton breadth-first search (BFS).
- Shortest distinguishing string when two DFA languages differ.
- Reference lexer DFA and a deliberate mutation that breaks recognition of `<=`.
- Exact reachable-cycle detection for deterministic finite-state transition systems.
- Command-line demonstrations and automated unit tests.

> **Scope:** Results are exact for the finite models entered. This project does not solve termination or semantic equivalence for arbitrary unrestricted programs; those general problems are undecidable.

## Requirements
- Python 3.10+
- Streamlit, NetworkX and Matplotlib for the dashboard

## Run locally

### macOS / Linux
```bash
git clone https://github.com/Arshad-Navaz/automatalab1.git
cd automatalab1
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
streamlit run app.py
```

### Windows
```powershell
git clone https://github.com/Arshad-Navaz/automatalab1.git
cd automatalab1
py -m venv .venv
.venv\Scripts\activate
py -m pip install --upgrade pip
pip install -r requirements.txt
streamlit run app.py
```

Open the local URL printed by Streamlit (usually http://localhost:8501).

## Run tests and CLI
```bash
python -m unittest discover -s tests -v
python -m automatalab demo
```

## Project structure
```text
automatalab1/
├── app.py
├── automatalab/
│   ├── __init__.py
│   ├── automata.py
│   ├── lexer.py
│   ├── loops.py
│   └── __main__.py
├── examples/
├── tests/
├── requirements.txt
├── pyproject.toml
└── README.md
```

## Algorithms
### DFA equivalence
The product construction explores reachable pairs of states. A pair where exactly one component is accepting identifies a distinguishing input. BFS returns a shortest such string. If no such pair is reachable, the languages are equivalent.

### Lexer verification
The reference lexer recognises abstract identifiers, integers and simple operators over the alphabet `{a,d,=,<}`. A deliberately modified transition causes the `<=` token to be rejected. Equivalence checking detects the shortest counterexample.

### Loop detection
A deterministic finite execution either reaches its halt state or repeats a state. Repetition before halt proves that the model will cycle forever.

## Academic use
This software is intended for education, formal-language demonstrations, and controlled experiments. It is not a production compiler verifier.
