"""Small lexer DFA and transition mutation experiment."""
from .automata import DFA, equivalent

def reference_lexer():
    # Abstract symbols: a=letter, d=digit, '=' and '<' are literal operators.
    states=("q0","ID","INT","EQ","EQUAL","LT","LE","DEAD")
    alphabet=("a","d","=","<"); dead={c:"DEAD" for c in alphabet}
    t={
      "q0":{"a":"ID","d":"INT","=":"EQ","<":"LT"},
      "ID":{"a":"ID","d":"ID","=":"DEAD","<":"DEAD"},
      "INT":{"a":"DEAD","d":"INT","=":"DEAD","<":"DEAD"},
      "EQ":{"a":"DEAD","d":"DEAD","=":"EQUAL","<":"DEAD"},
      "EQUAL":dict(dead), "LT":{"a":"DEAD","d":"DEAD","=":"LE","<":"DEAD"},
      "LE":dict(dead), "DEAD":dict(dead)}
    return DFA(states,alphabet,"q0",frozenset({"ID","INT","EQ","EQUAL","LT","LE"}),t)

def find_mutant_counterexample():
    ref=reference_lexer(); t={q:dict(row) for q,row in ref.transitions.items()}
    t["LT"]["="]="DEAD"
    mutant=DFA(ref.states,ref.alphabet,ref.start,ref.accepting,t)
    return equivalent(ref,mutant)
