from __future__ import annotations

from copy import deepcopy
import unittest

from sentinel_xdr_migration.report import render_transformation_report, render_runtime_validation_report
from sentinel_xdr_migration.report_review import render_bulk_review, review_candidates
from test_report_dashboard import report, rule


def review_rule(name: str, rule_id: str, tactics: list[str], techniques: list[str]) -> dict:
    item = rule(name)
    item["analyticRule"]["id"] = rule_id
    item["sourceSha256"] = "a" * 64
    item["customDetection"]["reviewReasons"] = ["Custom Detections support one tactic"]
    item["attackClassification"] = {"sourceTactics": tactics, "sourceTechniques": techniques}
    return item


class ReportReviewTests(unittest.TestCase):
    def test_eligibility_requires_unique_ids_source_choices_and_snapshot_hash(self) -> None:
        first = review_rule("First", "a", ["Execution", "Collection"], ["T1059", "T1005"])
        value = report(first)
        before = deepcopy(value)
        self.assertTrue(review_candidates(value)[0]["eligible"])
        self.assertEqual(value, before)
        self.assertFalse(review_candidates(report(first, deepcopy(first)))[0]["eligible"])
        first.pop("sourceSha256")
        self.assertIn("hash", review_candidates(report(first))[0]["reason"])
        first["sourceSha256"] = "a" * 64
        first["attackClassification"]["sourceTechniques"] = ["not-a-technique"]
        self.assertFalse(review_candidates(report(first))[0]["eligible"])

    def test_export_controls_are_only_for_explicit_tactic_review(self) -> None:
        item = rule()
        item["warnings"] = ["Unsupported mapping loses evidence", "Frequency mismatch"]
        item["customDetection"]["reviewReasons"] = ["Confirm account mapping"]
        self.assertEqual(review_candidates(report(item)), [])
        self.assertEqual(render_bulk_review(report(item), []), "")

    def test_payload_is_escaped_and_export_contract_is_explicit(self) -> None:
        payload = '</script><img src=x onerror="alert(1)">'
        item = review_rule(payload, payload, ["Execution"], ["T1059"])
        value = report(item)
        html = render_bulk_review(value, review_candidates(value))
        self.assertNotIn(payload, html)
        self.assertIn("&lt;/script&gt;", html)
        for text in ("Pending export decisions", "individual", "no local write service", "source-file SHA-256",
                     "does not validate this review manifest", "--config", "--overwrite", "do not"):
            self.assertIn(text.lower(), html.lower())
        self.assertNotIn("acceptReviewReasons", html)

    def test_transformation_information_is_separate_nonblocking_and_escaped(self) -> None:
        value = {
            "solution": "Example", "total": 1, "converted": 1, "needsReview": 0, "conflicts": 0,
            "results": [{"source": "rule.yaml", "output": "draft.yaml", "status": "converted",
                         "informational": ["<script>alert(1)</script>"], "warnings": [], "errors": []}],
        }
        before = deepcopy(value)
        html = render_transformation_report(value)
        self.assertEqual(value, before)
        self.assertIn("Information — nonblocking", html)
        self.assertIn("Rules with information<strong>1", html)
        self.assertIn("&lt;script&gt;alert(1)&lt;/script&gt;", html)
        self.assertIn("--cp-bg: #f7f4ef", html)
        self.assertNotIn("<script>alert(1)</script>", html)
        value["results"][0].pop("informational")
        self.assertIn("Rules with information<strong>0", render_transformation_report(value))

    def test_runtime_theme_preserves_results(self) -> None:
        html = render_runtime_validation_report({
            "platform": "Example", "solution": "Example", "provider": "local",
            "total": 1, "valid": 1, "invalid": 0, "blocked": 0,
            "results": [{"detection": "Rule", "status": "passed", "rowCount": 0, "schemaColumnCount": 1}],
        })
        self.assertIn("--cp-bg: #f7f4ef", html)
        self.assertIn("<td>0</td>", html)
