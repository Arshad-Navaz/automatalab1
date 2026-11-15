import unittest

from automatalab.automata import DFA, product_bfs
from automatalab.lexer import reference_lexer, missing_le_mutant
from automatalab.loops import analyse_termination, step_budget


class AutomataLabTests(unittest.TestCase):
    def make_parity_dfa(self, even_state="even", odd_state="odd"):
        return DFA(
            states=(even_state, odd_state),
            alphabet=("a", "b"),
            start=even_state,
            accepting=frozenset({even_state}),
            transitions={
                even_state: {"a": odd_state, "b": even_state},
                odd_state: {"a": even_state, "b": odd_state},
            },
        )

    def test_equivalent_dfas_with_different_state_names(self):
        result = product_bfs(self.make_parity_dfa(), self.make_parity_dfa("p", "q"))
        self.assertTrue(result.equivalent)
        self.assertIsNone(result.counterexample)

    def test_shortest_counterexample_can_be_empty_string(self):
        a = DFA(("e", "o"), ("a",), "e", frozenset({"e"}),
                {"e": {"a": "o"}, "o": {"a": "e"}})
        b = DFA(("e", "o"), ("a",), "e", frozenset({"o"}),
                {"e": {"a": "o"}, "o": {"a": "e"}})
        result = product_bfs(a, b)
        self.assertFalse(result.equivalent)
        self.assertEqual(result.counterexample, "")

    def test_invalid_incomplete_dfa_is_rejected(self):
        with self.assertRaises(ValueError):
            DFA(("s",), ("a",), "s", frozenset(),
                {"s": {}})

    def test_reference_lexer_accepts_less_equal(self):
        self.assertTrue(reference_lexer().accepts("<="))

    def test_mutant_rejects_less_equal_and_bfs_finds_it(self):
        reference = reference_lexer()
        mutant = missing_le_mutant(reference)
        self.assertTrue(reference.accepts("<="))
        self.assertFalse(mutant.accepts("<="))
        result = product_bfs(reference, mutant)
        self.assertFalse(result.equivalent)
        self.assertEqual(result.counterexample, "<=")

    def test_loop_analyser_detects_reachable_cycle(self):
        result = analyse_termination(
            {"S0": "S1", "S1": "S2", "S2": "S3", "S3": "S2"},
            "S0", "HALT"
        )
        self.assertFalse(result["terminates"])
        self.assertEqual(result["cycle"], ["S2", "S3", "S2"])
        self.assertEqual(result["steps"], 4)

    def test_loop_analyser_detects_halt(self):
        result = analyse_termination({"S0": "S1", "S1": "HALT"}, "S0", "HALT")
        self.assertTrue(result["terminates"])
        self.assertIsNone(result["cycle"])
        self.assertEqual(result["steps"], 2)

    def test_missing_successor_is_rejected(self):
        with self.assertRaises(ValueError):
            analyse_termination({"S0": "S1"}, "S0", "HALT")

    def test_step_budget_is_a_bounded_check(self):
        result = step_budget({"S0": "S1", "S1": "HALT"}, "S0", "HALT", 2)
        self.assertTrue(result["terminates"])


if __name__ == "__main__":
    unittest.main()
