import json
import streamlit as st
import networkx as nx
import matplotlib.pyplot as plt
import pandas as pd

from automatalab.automata import DFA, product_bfs
from automatalab.lexer import reference_lexer, missing_le_mutant, mutation_experiment
from automatalab.loops import analyse_termination

st.set_page_config(page_title="AutomataLab | FLAT Toolkit", page_icon="🔁", layout="wide")
st.markdown("""
<style>
.block-container{padding-top:1.5rem;max-width:1440px}
[data-testid="stSidebar"]{border-right:1px solid rgba(128,128,128,.18)}
.hero{padding:1.5rem 1.7rem;border-radius:18px;background:linear-gradient(115deg,rgba(37,99,235,.18),rgba(14,165,233,.08));border:1px solid rgba(59,130,246,.25);margin-bottom:1.2rem}
.hero h1{margin:0 0 .35rem 0;font-size:2.1rem}.hero p{margin:0;opacity:.8}
div[data-testid="stMetric"]{padding:.8rem 1rem;border:1px solid rgba(128,128,128,.2);border-radius:14px}
div.stButton>button{border-radius:10px;font-weight:600}
</style>
<div class="hero"><h1>🔁 AutomataLab</h1><p>Interactive laboratory for finite automata, language equivalence, lexer mutation testing, and finite-state execution analysis.</p></div>
""", unsafe_allow_html=True)

def parse_dfa(raw):
    try:
        data = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise ValueError(f"Invalid JSON at line {exc.lineno}, column {exc.colno}: {exc.msg}") from exc
    required = {"states", "alphabet", "start", "accepting", "transitions"}
    if not isinstance(data, dict):
        raise ValueError("The DFA definition must be a JSON object.")
    missing = required - set(data)
    if missing:
        raise ValueError("Missing field(s): " + ", ".join(sorted(missing)))
    if not isinstance(data["transitions"], dict):
        raise ValueError("The transitions field must be a JSON object.")
    try:
        return DFA(tuple(data["states"]), tuple(data["alphabet"]), data["start"],
                   frozenset(data["accepting"]), data["transitions"])
    except (TypeError, KeyError) as exc:
        raise ValueError(f"Invalid DFA structure: {exc}") from exc

def trace_dfa(dfa, word):
    state = dfa.start
    rows = [{"Step": 0, "Read": "Start", "From": "—", "To": state,
             "State type": "Accepting" if state in dfa.accepting else "Non-accepting"}]
    for index, symbol in enumerate(word, 1):
        if symbol not in dfa.alphabet:
            raise ValueError(f"Unknown symbol '{symbol}' at position {index}. Allowed: {', '.join(dfa.alphabet)}")
        nxt = dfa.step(state, symbol)
        rows.append({"Step": index, "Read": symbol, "From": state, "To": nxt,
                     "State type": "Accepting" if nxt in dfa.accepting else "Non-accepting"})
        state = nxt
    return rows, state in dfa.accepting

def draw_dfa(dfa, title):
    graph = nx.DiGraph()
    graph.add_nodes_from(dfa.states)
    labels = {}
    for source, row in dfa.transitions.items():
        for symbol, target in row.items():
            graph.add_edge(source, target)
            labels.setdefault((source, target), []).append(symbol)
    positions = ({dfa.states[0]: (0, 0)} if len(dfa.states) == 1
                 else nx.spring_layout(graph, seed=17, k=1.25))
    fig, ax = plt.subplots(figsize=(10, 4.8))
    normal = [s for s in dfa.states if s not in dfa.accepting]
    accepting = [s for s in dfa.states if s in dfa.accepting]
    nx.draw_networkx_nodes(graph, positions, nodelist=normal, node_size=1700,
                           node_color="#dbeafe", edgecolors="#2563eb", linewidths=1.5, ax=ax)
    nx.draw_networkx_nodes(graph, positions, nodelist=accepting, node_size=1700,
                           node_color="#dcfce7", edgecolors="#16a34a", linewidths=2, ax=ax)
    nx.draw_networkx_labels(graph, positions, font_size=9, font_weight="bold", ax=ax)
    nx.draw_networkx_edges(graph, positions, arrows=True, arrowstyle="-|>", arrowsize=18,
                           connectionstyle="arc3,rad=0.12", ax=ax)
    nx.draw_networkx_edge_labels(graph, positions,
        edge_labels={edge: ", ".join(chars) for edge, chars in labels.items()},
        font_size=8, rotate=False, ax=ax)
    x, y = positions[dfa.start]
    ax.annotate("", xy=(x-.1, y), xytext=(x-.48, y),
                arrowprops={"arrowstyle": "-|>", "lw": 1.8, "color": "#f59e0b"})
    ax.set_title(title, fontsize=13, pad=14, fontweight="bold")
    ax.text(.01, .01, "Blue: non-accepting   Green: accepting   Gold arrow: start",
            transform=ax.transAxes, fontsize=8, alpha=.7)
    ax.axis("off")
    fig.tight_layout()
    st.pyplot(fig, use_container_width=True)
    plt.close(fig)

def parse_error(raw):
    try:
        return parse_dfa(raw)
    except Exception as exc:
        st.error(str(exc))
        return None

pages = ["🏠 Overview", "🧩 DFA Playground", "⚖️ Equivalence Checker", "🧪 Lexer Bug Lab", "🔄 Loop Analyzer"]
selected = st.sidebar.radio("WORKSPACES", pages)
st.sidebar.divider()
st.sidebar.caption("Formal Languages and Automata Theory")
st.sidebar.caption("Results are exact for the finite models entered, not arbitrary unrestricted programs.")

if selected == "🏠 Overview":
    st.subheader("Welcome to your automata workspace")
    st.caption("Choose a lab to experiment with a model and inspect how the algorithm reaches its result.")
    cols = st.columns(4)
    for col, value, label in zip(cols, ["04", "DFA", "BFS", "Python"],
                                 ["Interactive labs", "Finite models", "Equivalence engine", "Implementation"]):
        col.metric(label, value)
    st.markdown("### Explore the workspaces")
    descriptions = [
        ("🧩 DFA Playground", "Edit a DFA, view its state diagram, and trace an input symbol by symbol."),
        ("⚖️ Equivalence Checker", "Compare two DFA languages and find a shortest distinguishing string."),
        ("🧪 Lexer Bug Lab", "Compare a reference lexer with an intentionally faulty version."),
        ("🔄 Loop Analyzer", "Trace a deterministic state system and detect termination or a reachable cycle."),
    ]
    for i in range(0, 4, 2):
        a, b = st.columns(2)
        for col, item in zip((a, b), descriptions[i:i+2]):
            with col:
                with st.container(border=True):
                    st.markdown("#### " + item[0])
                    st.write(item[1])
    st.info("Suggested path: begin with the DFA Playground, then compare two machines in the Equivalence Checker.")

elif selected == "🧩 DFA Playground":
    st.subheader("DFA Playground")
    st.caption("Edit a deterministic finite automaton, validate it, and run an input string step by step.")
    examples = {
        "Even number of a's": {"states":["even","odd"],"alphabet":["a","b"],"start":"even","accepting":["even"],
            "transitions":{"even":{"a":"odd","b":"even"},"odd":{"a":"even","b":"odd"}}},
        "Binary strings ending in 1": {"states":["q0","q1"],"alphabet":["0","1"],"start":"q0","accepting":["q1"],
            "transitions":{"q0":{"0":"q0","1":"q1"},"q1":{"0":"q0","1":"q1"}}},
        "Even number of zeroes": {"states":["even0","odd0"],"alphabet":["0","1"],"start":"even0","accepting":["even0"],
            "transitions":{"even0":{"0":"odd0","1":"even0"},"odd0":{"0":"even0","1":"odd0"}}},
    }
    example = st.selectbox("Load a sample DFA", list(examples))
    raw = st.text_area("DFA definition (JSON)", json.dumps(examples[example], indent=2), height=270, key="dfa_json")
    dfa = parse_error(raw)
    if dfa:
        st.success(f"Valid DFA · {len(dfa.states)} states · {len(dfa.alphabet)} symbols")
        graph_tab, test_tab, info_tab = st.tabs(["State diagram", "Run input", "Model summary"])
        with graph_tab:
            draw_dfa(dfa, "DFA State Transition Diagram")
        with test_tab:
            word = st.text_input("Input string", "abba", key="dfa_word")
            if st.button("▶ Run DFA", type="primary"):
                try:
                    rows, accepted = trace_dfa(dfa, word)
                    st.success(("ACCEPTED" if accepted else "REJECTED") + " · " + (word or "ε (empty string)"))
                    st.dataframe(pd.DataFrame(rows), hide_index=True, use_container_width=True)
                    st.caption("The final state determines whether the input is accepted.")
                except ValueError as exc:
                    st.error(str(exc))
        with info_tab:
            a, b, c = st.columns(3)
            a.metric("States", len(dfa.states)); b.metric("Alphabet size", len(dfa.alphabet))
            c.metric("Accepting states", len(dfa.accepting))
            st.write("Start state:", dfa.start)
            st.write("Alphabet:", ", ".join(dfa.alphabet))
            st.write("Accepting states:", ", ".join(sorted(dfa.accepting)))
        st.download_button("⬇ Download validated DFA", json.dumps(json.loads(raw), indent=2),
                           "automatalab_dfa.json", "application/json")

elif selected == "⚖️ Equivalence Checker":
    st.subheader("DFA Equivalence Checker")
    st.caption("Product construction and breadth-first search determine whether two DFAs accept exactly the same language.")
    a0 = {"states":["even","odd"],"alphabet":["a","b"],"start":"even","accepting":["even"],
          "transitions":{"even":{"a":"odd","b":"even"},"odd":{"a":"even","b":"odd"}}}
    b0 = {"states":["p","q"],"alphabet":["a","b"],"start":"p","accepting":["p"],
          "transitions":{"p":{"a":"q","b":"p"},"q":{"a":"p","b":"q"}}}
    left, right = st.columns(2)
    with left:
        st.markdown("**DFA A**")
        raw_a = st.text_area("DFA A JSON", json.dumps(a0, indent=2), height=270, label_visibility="collapsed", key="eq_a")
    with right:
        st.markdown("**DFA B**")
        raw_b = st.text_area("DFA B JSON", json.dumps(b0, indent=2), height=270, label_visibility="collapsed", key="eq_b")
    if st.button("⚖ Compare languages", type="primary", use_container_width=True):
        a, b = parse_error(raw_a), parse_error(raw_b)
        if a and b:
            try:
                result = product_bfs(a, b)
                if result.equivalent:
                    st.success("Equivalent: both DFAs accept exactly the same language.")
                else:
                    witness = result.counterexample or ""
                    st.error("Not equivalent: a distinguishing string was found.")
                    st.markdown("### Shortest counterexample")
                    st.code(witness if witness else "ε (empty string)")
                    x, y = st.columns(2)
                    x.metric("DFA A", "ACCEPTS" if a.accepts(witness) else "REJECTS")
                    y.metric("DFA B", "ACCEPTS" if b.accepts(witness) else "REJECTS")
                    st.caption("BFS explores strings in increasing length, so this counterexample is shortest.")
                st.metric("Product-state pairs explored", result.explored_pairs)
            except ValueError as exc:
                st.error("Cannot compare these DFAs: " + str(exc))

elif selected == "🧪 Lexer Bug Lab":
    st.subheader("Lexer Mutation Testing Lab")
    st.caption("Compare a correct token recognizer with a mutant containing one intentional transition defect.")
    reference = reference_lexer()
    mutant = missing_le_mutant(reference)
    result = product_bfs(reference, mutant)
    a, b, c = st.columns(3)
    a.metric("Reference states", len(reference.states))
    b.metric("Mutant states", len(mutant.states))
    c.metric("Shortest defect witness", result.counterexample or "None")
    st.warning("Intentional defect: the mutant sends the '<' followed by '=' transition to DEAD, so it fails to recognise the <= operator.")
    st.markdown("**Abstract alphabet**")
    st.write("The model uses a for a letter, d for a digit, and the literal symbols = and <. This is a simplified token recognizer, not a complete programming-language lexer.")
    token = st.text_input("Try a token or abstract input", "<=", key="lexer_token")
    if st.button("Test both lexers", type="primary"):
        try:
            ref_ok, mutant_ok = reference.accepts(token), mutant.accepts(token)
            x, y = st.columns(2)
            x.metric("Reference lexer", "ACCEPT" if ref_ok else "REJECT")
            y.metric("Mutant lexer", "ACCEPT" if mutant_ok else "REJECT")
            if ref_ok != mutant_ok:
                st.success("Defect reproduced: the two lexer models disagree on this input.")
            elif ref_ok:
                st.info("Both models accept this input.")
            else:
                st.info("Both models reject this input.")
        except ValueError as exc:
            st.error(str(exc))
    with st.expander("Inspect reference lexer state diagram"):
        draw_dfa(reference, "Reference Lexer DFA")
    st.markdown("### Random testing vs exact comparison")
    st.write("Run a reproducible experiment to compare random test detection with exact product-BFS detection.")
    if st.button("Run mutation experiment"):
        with st.spinner("Generating and checking finite-state mutants..."):
            stats = mutation_experiment(mutants=40, tests=40, seed=2026)
        x, y, z = st.columns(3)
        x.metric("Mutants generated", stats["mutants"])
        y.metric("Random tests detected", f"{stats['random_detected']} / {stats['mutants']}")
        z.metric("Exact BFS detected", f"{stats['exact_detected']} / {stats['mutants']}")
        st.caption(f"Random-test detection rate: {stats['random_rate']:.1%}. Exact equivalence checks each generated finite mutant.")

elif selected == "🔄 Loop Analyzer":
    st.subheader("Finite-State Loop Analyzer")
    st.caption("Follow a deterministic transition system. A repeated reachable state indicates a cycle unless the halt state is reached first.")
    a, b = st.columns(2)
    with a:
        start = st.text_input("Start state", "S0")
    with b:
        halt = st.text_input("Halt state", "HALT")
    edges = st.text_area("Transitions (one source:target pair per line)",
                         "S0:S1\nS1:S2\nS2:S3\nS3:S2", height=145,
                         help="Example: S0:S1 means the next state after S0 is S1.")
    if st.button("🔍 Analyze execution", type="primary", use_container_width=True):
        try:
            transitions = {}
            for line_no, line in enumerate(edges.splitlines(), 1):
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                if line.count(":") != 1:
                    raise ValueError(f"Line {line_no}: use exactly one colon in source:target.")
                source, target = (part.strip() for part in line.split(":", 1))
                if not source or not target:
                    raise ValueError(f"Line {line_no}: source and target cannot be empty.")
                if source in transitions:
                    raise ValueError(f"Line {line_no}: duplicate transition for state '{source}'.")
                transitions[source] = target
            start, halt = start.strip(), halt.strip()
            if not start or not halt:
                raise ValueError("Start state and halt state cannot be empty.")
            if start == halt:
                st.success("The system is already in the halt state. No transitions are required.")
                st.write("Execution path:", start)
            else:
                result = analyse_termination(transitions, start, halt)
                if result["terminates"]:
                    st.success("Termination detected: execution reaches the halt state.")
                else:
                    st.error("Non-termination detected: a reachable cycle was found.")
                    st.markdown("**Detected cycle**")
                    st.code(" → ".join(result["cycle"]))
                st.markdown("**Execution trace**")
                rows = []
                for i, state in enumerate(result["path"]):
                    event = "Halt" if state == halt else ("Repeated state" if state in result["path"][:i] else "Visit")
                    rows.append({"Step": i, "State": state, "Event": event})
                st.dataframe(pd.DataFrame(rows), hide_index=True, use_container_width=True)
                st.metric("Transitions before halt/repetition", result["steps"])
        except Exception as exc:
            st.error(str(exc))

st.divider()
st.caption("AutomataLab · Formal Languages and Automata Theory · Educational prototype")
