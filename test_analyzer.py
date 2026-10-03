import unittest
from analyzer import CommunicationGapAnalyzer

class TestCommunicationGapAnalyzer(unittest.TestCase):
    def setUp(self):
        self.analyzer = CommunicationGapAnalyzer()

    def test_no_communication_gap(self):
        text = """
Neha: What time is the meeting?
Ravi: The meeting is at 3 PM today.
Neha: Thanks, I will be there.
Soham: See you all at 3 PM.
"""
        res = self.analyzer.analyze(text)
        self.assertEqual(len(res["gaps"]), 0, f"Expected 0 gaps, got {len(res['gaps'])}: {res['gaps']}")
        self.assertEqual(res["summary"]["health_score"], 100)

    def test_unanswered_question(self):
        text = """
Neha: What time is the meeting?
Ravi: I am working on the report.
Soham: I'll send the dataset.
"""
        res = self.analyzer.analyze(text)
        gap_types = [g["type"] for g in res["gaps"]]
        self.assertIn("Unanswered Question", gap_types)
        neha_gap = next(g for g in res["gaps"] if g["type"] == "Unanswered Question")
        self.assertEqual(neha_gap["speaker"], "Neha")
        self.assertEqual(neha_gap["message"], "What time is the meeting?")
        self.assertIn("no direct response", neha_gap["evidence"].lower())

    def test_repeated_request(self):
        text = """
Ravi: Can you send the dataset?
Soham: Okay.
Ravi: Can you send the dataset?
"""
        res = self.analyzer.analyze(text)
        gap_types = [g["type"] for g in res["gaps"]]
        self.assertIn("Repeated Request", gap_types)
        gap = next(g for g in res["gaps"] if g["type"] == "Repeated Request")
        self.assertEqual(gap["speaker"], "Ravi")
        self.assertEqual(gap["message"], "Can you send the dataset?")
        self.assertIn("repeated", gap["evidence"].lower())

    def test_repeated_clarification(self):
        text = """
Neha: We need to update the entire core infrastructure today.
Ravi: What do you mean?
Neha: Just change the ports and auth keys.
Ravi: Can you clarify?
"""
        res = self.analyzer.analyze(text)
        gap_types = [g["type"] for g in res["gaps"]]
        self.assertIn("Repeated Clarification", gap_types)
        gap = next(g for g in res["gaps"] if g["type"] == "Repeated Clarification")
        self.assertEqual(gap["speaker"], "Ravi")

    def test_unresolved_topic(self):
        text = """
Neha: What about the budget for Q4?
Ravi: Let's focus on the client demo first.
Soham: Yes, the client demo is top priority.
"""
        res = self.analyzer.analyze(text)
        gap_types = [g["type"] for g in res["gaps"]]
        self.assertTrue("Unresolved Topic" in gap_types or "Unanswered Question" in gap_types)

    def test_multiple_gaps(self):
        text = """
Alice: What time is the release?
Bob: Please send the credentials.
Charlie: What do you mean?
Bob: Please send the credentials.
Charlie: Which one?
"""
        res = self.analyzer.analyze(text)
        gap_types = {g["type"] for g in res["gaps"]}
        self.assertIn("Unanswered Question", gap_types)
        self.assertIn("Repeated Request", gap_types)
        self.assertIn("Repeated Clarification", gap_types)

if __name__ == "__main__":
    unittest.main()
