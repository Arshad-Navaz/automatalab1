import json
import streamlit as st
import networkx as nx
import matplotlib.pyplot as plt
from automatalab.automata import DFA, product_bfs
from automatalab.lexer import reference_lexer, missing_le_mutant
from automatalab.loops import analyse_termination

st.set_page_config(page_title="AutomataLab", page_icon="🔁", layout="wide")
st.title("🔁 AutomataLab")
st.caption("Interactive finite automata, lexer verification and finite-state loop analysis")

def parse_dfa(raw):
    d=json.loads(raw)
    return DFA(tuple(d["states"]),tuple(d["alphabet"]),d["start"],frozenset(d["accepting"]),d["transitions"])

def draw_dfa(dfa,title):
    g=nx.DiGraph(); g.add_nodes_from(dfa.states); labels={}
    for s,row in dfa.transitions.items():
        for symbol,t in row.items():
            labels[(s,t)]=(labels.get((s,t),"") + (", " if (s,t) in labels else "") + symbol)
    g.add_edges_from(labels); pos=nx.spring_layout(g,seed=12)
    fig,ax=plt.subplots(figsize=(8,4))
    nx.draw_networkx_nodes(g,pos,nodelist=[s for s in dfa.states if s not in dfa.accepting],node_color="#dbeafe",node_size=1500,ax=ax)
    nx.draw_networkx_nodes(g,pos,nodelist=list(dfa.accepting),node_color="#bbf7d0",node_size=1500,ax=ax)
    nx.draw_networkx_labels(g,pos,ax=ax,font_size=9)
    nx.draw_networkx_edges(g,pos,ax=ax,arrows=True,arrowstyle="-|>",arrowsize=18)
    nx.draw_networkx_edge_labels(g,pos,edge_labels=labels,ax=ax,font_size=8)
    ax.set_title(title); ax.axis("off"); st.pyplot(fig); plt.close(fig)

page=st.sidebar.radio("Workspace",["Overview","DFA Playground","Equivalence Checker","Lexer Bug Lab","Loop Analyzer"])
st.sidebar.caption("Guarantees apply to the finite models entered, not arbitrary unrestricted programs.")

if page=="Overview":
    st.subheader("Explore AutomataLab")
    a,b,c=st.columns(3); a.metric("Workspaces","4"); b.metric("Core algorithm","Product BFS"); c.metric("Language","Python")
    st.markdown("""
    - **DFA Playground:** edit a DFA as JSON, view its state diagram and test input strings.
    - **Equivalence Checker:** compare two DFAs and find a shortest distinguishing string.
    - **Lexer Bug Lab:** inspect a reference lexer and a deliberately mutated lexer.
    - **Loop Analyzer:** detect a reachable repeated state before a halt state.
    """)
    st.info("Choose a workspace from the sidebar to begin.")

elif page=="DFA Playground":
    st.subheader("Build and test a DFA")
    sample={"states":["even","odd"],"alphabet":["a","b"],"start":"even","accepting":["even"],"transitions":{"even":{"a":"odd","b":"even"},"odd":{"a":"even","b":"odd"}}}
    raw=st.text_area("DFA JSON",json.dumps(sample,indent=2),height=300)
    try:
        d=parse_dfa(raw); st.success(f"Valid DFA: {len(d.states)} states")
        draw_dfa(d,"Your DFA")
        word=st.text_input("Input string","abba")
        if st.button("Test string",type="primary"):
            ok=d.accepts(word); (st.success if ok else st.error)(f"{'ACCEPTED' if ok else 'REJECTED'}: {word or 'ε'}")
        st.download_button("Download DFA JSON",raw,"my_dfa.json","application/json")
    except Exception as e: st.error(f"Invalid DFA: {e}")

elif page=="Equivalence Checker":
    st.subheader("Compare two DFA languages")
    a0={"states":["even","odd"],"alphabet":["a","b"],"start":"even","accepting":["even"],"transitions":{"even":{"a":"odd","b":"even"},"odd":{"a":"even","b":"odd"}}}
    b0={"states":["p","q"],"alphabet":["a","b"],"start":"p","accepting":["p"],"transitions":{"p":{"a":"q","b":"p"},"q":{"a":"p","b":"q"}}}
    c1,c2=st.columns(2)
    with c1: ar=st.text_area("DFA A",json.dumps(a0,indent=2),height=280)
    with c2: br=st.text_area("DFA B",json.dumps(b0,indent=2),height=280)
    if st.button("Compare",type="primary"):
        try:
            x,y=parse_dfa(ar),parse_dfa(br); r=product_bfs(x,y)
            st.metric("Language result","Equivalent" if r.equivalent else "Not equivalent")
            st.write(f"State pairs explored: {r.explored_pairs}")
            if r.equivalent: st.success("Both DFAs accept the same language.")
            else:
                w=r.counterexample or ""
                st.error(f"Shortest counterexample: {w if w else 'ε (empty string)'}")
                st.write(f"DFA A: {'accepts' if x.accepts(w) else 'rejects'} · DFA B: {'accepts' if y.accepts(w) else 'rejects'}")
        except Exception as e: st.error(str(e))

elif page=="Lexer Bug Lab":
    st.subheader("Find a lexer defect")
    ref=reference_lexer()
    st.write("Abstract input alphabet: a = letter, d = digit; operators =, ==, <, <=")
    mutant=missing_le_mutant(ref)
    r=product_bfs(ref,mutant)
    st.error(f"Exact DFA comparison finds a defect. Shortest counterexample: {r.counterexample}")
    word=st.text_input("Test a token","<=")
    try:
        st.write(f"Reference lexer: {'accept' if ref.accepts(word) else 'reject'}")
        st.caption("The mutant intentionally breaks the transition that recognises <=.")
    except Exception as e: st.error(str(e))
    with st.expander("Reference lexer state diagram"):
        draw_dfa(ref,"Reference lexer DFA")

elif page=="Loop Analyzer":
    st.subheader("Analyze a finite-state execution")
    st.write("Enter comma-separated transitions in source:target format.")
    edges=st.text_input("Transitions","S0:S1,S1:S2,S2:S3,S3:S2")
    c1,c2=st.columns(2)
    with c1: start=st.text_input("Start state","S0")
    with c2: halt=st.text_input("Halt state","HALT")
    if st.button("Analyze",type="primary"):
        try:
            trans=dict(part.strip().split(":",1) for part in edges.split(",") if part.strip())
            r=analyse_termination(trans,start,halt)
            if r["terminates"]: st.success("Execution reaches the halt state.")
            else: st.error("Reachable cycle: "+" → ".join(r["cycle"]))
            st.write("Execution path: "+" → ".join(r["path"]))
            st.write(f"Transitions before halt/repetition: {r['steps']}")
        except Exception as e: st.error(str(e))

st.divider()
st.caption("AutomataLab · Educational prototype · Finite deterministic models only")
