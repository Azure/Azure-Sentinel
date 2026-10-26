from __future__ import annotations

from copy import deepcopy
import hashlib
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import yaml
from jsonschema import Draft202012Validator

from sentinel_xdr_migration.converter import (
    XDR_SCHEMA_PATH,
    build_xdr_document,
    convert_solution,
    validate_document,
)
from sentinel_xdr_migration.deployment import graph_detection_payload
from sentinel_xdr_migration.graph_readiness import graph_detection_payload_with_projection
from sentinel_xdr_migration.report_review import review_candidates, render_bulk_review
from sentinel_xdr_migration.solution_report import build_solution_report
from test_converter import RULE
from test_report_dashboard import report
from test_report_review import review_rule


class TacticPreservationTests(unittest.TestCase):
    def setUp(self) -> None:
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.solution = Path(self.directory.name) / "Example"
        self.source = self.solution / "Analytic Rules/Rule.yaml"
        self.source.parent.mkdir(parents=True)
        self.rule = yaml.safe_load(RULE)

    def build(self, tactics=None, techniques=None, override=None):
        self.rule["tactics"] = tactics if tactics is not None else ["Persistence", "CommandAndControl", "Discovery"]
        self.rule["relevantTechniques"] = techniques if techniques is not None else ["T1505.003", "T1071", "T1087"]
        self.source.write_text(yaml.safe_dump(self.rule, sort_keys=False))
        return build_xdr_document(
            self.source, self.solution, {"ruleOverrides": {self.rule["id"]: override or {}}},
        )

    @staticmethod
    def tactics(document):
        return document["properties"]["detectionAction"]["alertTemplate"].get("tactics", [])

    def test_three_tactics_preserve_order_compatible_techniques_and_provenance(self):
        document = self.build()
        self.assertEqual(self.tactics(document), [
            {"tactic": "Persistence", "techniques": [{"technique": "T1505", "subTechniques": ["T1505.003"]}]},
            {"tactic": "CommandAndControl", "techniques": [{"technique": "T1071"}]},
            {"tactic": "Discovery", "techniques": [{"technique": "T1087"}]},
        ])
        conversion = document["contentProvenance"]["conversion"]
        self.assertEqual(conversion["originalTactics"], self.rule["tactics"])
        self.assertEqual(conversion["originalTechniques"], self.rule["relevantTechniques"])
        self.assertFalse(conversion["reviewRequired"])
        self.assertEqual(validate_document(document), [])
        schema = json.loads(XDR_SCHEMA_PATH.read_text())
        self.assertEqual(list(Draft202012Validator(schema).iter_errors(document)), [])
        self.assertEqual(document["properties"]["status"], "disabled")
        self.assertEqual(f"xdr-{self.rule['id']}", document["properties"]["id"])
        self.assertEqual(document["version"], "3.1.0")
        self.assertEqual(document["contentProvenance"]["source"]["version"], "1.0.0")
        self.assertEqual(
            document["contentProvenance"]["source"]["querySha256"],
            hashlib.sha256(self.rule["query"].encode()).hexdigest(),
        )

    def test_documented_shared_technique_only_goes_to_compatible_tactics(self):
        document = self.build(
            ["Discovery", "Persistence", "PrivilegeEscalation"],
            ["T1078.004", "T1087", "T1098"],
        )
        self.assertEqual(self.tactics(document)[0]["techniques"], [{"technique": "T1087"}])
        self.assertEqual(self.tactics(document)[1]["techniques"], self.tactics(document)[2]["techniques"])
        self.assertEqual(validate_document(document), [])

    def test_no_techniques_is_not_a_multi_tactic_review(self):
        document = self.build(["Discovery", "Persistence"], [])
        self.assertEqual(self.tactics(document), [{"tactic": "Discovery"}, {"tactic": "Persistence"}])
        self.assertFalse(document["contentProvenance"]["conversion"]["reviewRequired"])

    def test_legacy_override_does_not_narrow_or_reorder(self):
        document = self.build(override={"tactic": "CommandAndControl", "techniques": ["T1071.001"]})
        self.assertEqual([item["tactic"] for item in self.tactics(document)], self.rule["tactics"])
        self.assertEqual(self.tactics(document)[1]["techniques"], [{"technique": "T1071", "subTechniques": ["T1071.001"]}])
        self.assertEqual(self.tactics(document)[0]["techniques"], [{"technique": "T1505", "subTechniques": ["T1505.003"]}])
        conversion = document["contentProvenance"]["conversion"]
        self.assertEqual(conversion["originalTechniques"], ["T1505.003", "T1071", "T1087"])
        self.assertTrue(any("not narrowed or reordered" in value for value in conversion["warnings"]))
        self.assertFalse(conversion["reviewRequired"])

    def test_invalid_classification_and_override_remain_blocking(self):
        for tactics, techniques, override in (
            (["Discovery", "Invalid"], ["T1087"], {}),
            (["Discovery", "Persistence"], ["T9999"], {}),
            (["Discovery", "Persistence"], ["T1087.abc"], {}),
            (["Discovery", "Persistence"], ["T1071"], {}),
            (["Discovery", "Persistence"], ["T1087"], {"tactic": "Execution", "techniques": ["T1059"]}),
            (["Discovery", "Persistence"], ["T1087"], {"tactic": "Discovery", "techniques": ["T1071"]}),
            (["Discovery", "Persistence"], ["T1087"], {"tactic": "Discovery"}),
            ("Discovery", ["T1087"], {}),
        ):
            with self.subTest(tactics=tactics, techniques=techniques, override=override):
                document = self.build(tactics, techniques, override)
                conversion = document["contentProvenance"]["conversion"]
                self.assertEqual(conversion["status"], "needsReview")
                self.assertTrue(conversion["errors"])
                self.assertTrue(validate_document(document))
                if isinstance(tactics, list):
                    self.assertEqual([item["tactic"] for item in self.tactics(document)], tactics)

    def test_missing_catalog_fails_closed(self):
        with patch("sentinel_xdr_migration.converter.MITRE_CATALOG_PATH", self.solution / "absent"):
            document = self.build()
        self.assertEqual(document["contentProvenance"]["conversion"]["status"], "needsReview")
        self.assertTrue(validate_document(document))

    def test_authored_tactic_validation_still_rejects_invalid_nested_metadata(self):
        original = self.build()
        for change in (
            {"tactic": "Invalid"},
            {"tactic": "Discovery", "techniques": [{"technique": "T1071"}]},
            {"tactic": "Discovery", "techniques": [{"technique": "T1087", "subTechniques": ["T1071.001"]}]},
            {"tactic": "Discovery", "techniques": 1},
            {"tactic": "Discovery", "techniques": [{"technique": "T1087", "subTechniques": 1}]},
        ):
            document = deepcopy(original)
            self.tactics(document)[0] = change
            self.assertTrue(validate_document(document))

    def test_repeated_conversion_is_idempotent_source_untouched_not_graph_ready(self):
        self.build()
        before = self.source.read_bytes()
        first = convert_solution(self.solution)
        target = self.solution / "XDR Detections/Rule.yaml"
        draft = target.read_bytes()
        second = convert_solution(self.solution)
        self.assertEqual(first["converted"], 1)
        self.assertEqual(first["needsReview"], 0)
        self.assertEqual(first["deploymentReady"], 0)
        self.assertFalse(first["results"][0]["directGraphDeploymentReady"])
        self.assertEqual(second["conflicts"], 0)
        self.assertEqual(target.read_bytes(), draft)
        self.assertEqual(self.source.read_bytes(), before)
        solution_report = build_solution_report(self.solution)
        self.assertEqual(solution_report["summary"]["deploymentReady"], 0)
        self.assertEqual(solution_report["rules"][0]["customDetection"]["structuralStatus"], "passed")

    def test_graph_projects_multiple_tactics_without_mutating_authored_document(self):
        document = self.build()
        before = deepcopy(document)
        payload, projection = graph_detection_payload_with_projection(document)
        self.assertEqual(document, before)
        self.assertEqual(
            payload["detectionAction"]["alertTemplate"]["tactics"],
            before["properties"]["detectionAction"]["alertTemplate"]["tactics"][:1],
        )
        self.assertEqual(
            projection["projectedTactics"],
            ["Persistence"],
        )
        self.assertEqual(
            projection["omittedTactics"],
            ["CommandAndControl", "Discovery"],
        )
        self.assertEqual(projection["classificationParity"], "not-established")
        single = self.build(["Discovery"], ["T1087"])
        self.assertEqual(graph_detection_payload(single)["detectionAction"], single["properties"]["detectionAction"])

    def test_legacy_export_explains_authoring_preservation(self):
        item = review_rule("Legacy", "source", ["Discovery", "Persistence"], ["T1087", "T1505"])
        value = report(item)
        html = render_bulk_review(value, review_candidates(value))
        self.assertIn("multiple source tactics no longer require selection of one tactic", html)
        self.assertIn("do not narrow or reorder tactics", html)
        self.assertNotIn("Primary tactic for compatible selected rules", html)
        item["customDetection"]["reviewReasons"] = []
        self.assertEqual(review_candidates(value), [])
