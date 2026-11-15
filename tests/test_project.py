import unittest
from automatalab.automata import DFA,equivalent
from automatalab.loops import analyse
from automatalab.lexer import reference_lexer,find_mutant_counterexample

class AutomataLabTests(unittest.TestCase):
 def test_equivalent_dfas(self):
  a=DFA(("e","o"),("a","b"),"e",frozenset({"e"}),{"e":{"a":"o","b":"e"},"o":{"a":"e","b":"o"}})
  b=DFA(("x","y"),("a","b"),"x",frozenset({"x"}),{"x":{"a":"y","b":"x"},"y":{"a":"x","b":"y"}})
  self.assertTrue(equivalent(a,b).equivalent)
 def test_shortest_counterexample(self):
  a=DFA(("e","o"),("a",),"e",frozenset({"e"}),{"e":{"a":"o"},"o":{"a":"e"}})
  b=DFA(("e","o"),("a",),"e",frozenset({"o"}),{"e":{"a":"o"},"o":{"a":"e"}})
  self.assertEqual(equivalent(a,b).counterexample,"")
 def test_cycle(self): self.assertEqual(analyse({"s":"a","a":"b","b":"a"},"s","halt")["cycle"],["a","b","a"])
 def test_terminates(self): self.assertTrue(analyse({"s":"a","a":"halt"},"s","halt")["terminates"])
 def test_lexer(self):
  d=reference_lexer(); self.assertTrue(d.run("a")); self.assertTrue(d.run("<=")); self.assertFalse(d.run("ad"))
 def test_lexer_bug(self): self.assertEqual(find_mutant_counterexample().counterexample,"<=")
if __name__=="__main__": unittest.main()
