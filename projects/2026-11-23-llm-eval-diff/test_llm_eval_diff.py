import unittest

from llm_eval_diff import compare, index_results


class LlmEvalDiffTests(unittest.TestCase):
    def test_finds_regressions_and_improvements(self):
        baseline = [
            {"id": "math", "passed": True, "latency_ms": 100},
            {"id": "style", "passed": False, "latency_ms": 120},
        ]
        candidate = [
            {"id": "math", "passed": False, "latency_ms": 110},
            {"id": "style", "passed": True, "latency_ms": 100},
            {"id": "new-case", "passed": True},
        ]
        report = compare(baseline, candidate)
        self.assertEqual(report["regressions"], ["math"])
        self.assertEqual(report["improvements"], ["style"])
        self.assertEqual(report["new_cases"], ["new-case"])
        self.assertEqual(report["median_latency_delta_ms"], -5.0)
        self.assertFalse(report["release_recommended"])

    def test_recommends_release_without_regressions(self):
        report = compare([{"id": "a", "passed": True}], [{"id": "a", "passed": True}])
        self.assertTrue(report["release_recommended"])
        self.assertEqual(report["candidate_pass_rate"], 1.0)

    def test_rejects_duplicate_ids(self):
        with self.assertRaises(ValueError):
            index_results([{"id": "a", "passed": True}, {"id": "a", "passed": False}])

    def test_rejects_missing_boolean_passed(self):
        with self.assertRaises(ValueError):
            index_results([{"id": "a"}])


if __name__ == "__main__":
    unittest.main()
