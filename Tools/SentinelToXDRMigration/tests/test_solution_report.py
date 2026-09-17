from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

import yaml

from sentinel_xdr_migration.converter import convert_solution
from sentinel_xdr_migration.artifacts import report_directory
from sentinel_xdr_migration.solution_report import build_solution_report


class SolutionReportTests(unittest.TestCase):
    def test_report_contains_rule_status_and_entity_recommendation(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp) / "Example"
            rules = root / "Analytic Rules"
            rules.mkdir(parents=True)
            source = {
                "id": "11111111-1111-1111-1111-111111111111",
                "name": "Example rule",
                "description": "Example",
                "severity": "High",
                "queryFrequency": "1h",
                "queryPeriod": "1h",
                "query": "Example_CL | project User",
                "entityMappings": [
                    {
                        "entityType": "Account",
                        "fieldMappings": [
                            {"identifier": "Name", "columnName": "User"}
                        ],
                    }
                ],
            }
            (rules / "Rule.yaml").write_text(
                yaml.safe_dump(source, sort_keys=False), encoding="utf-8"
            )
            convert_solution(root)
            output = root / "XDR Detections"
            reports = report_directory(root, create=True)
            (reports / "runtime-validation.log-analytics-cli.json").write_text(
                json.dumps(
                    {
                        "platform": "Microsoft Sentinel Log Analytics",
                        "provider": "log-analytics-cli",
                        "results": [
                            {
                                "detection": "Rule.yaml",
                                "status": "passed",
                                "rowCount": 1,
                            }
                        ],
                    }
                ),
                encoding="utf-8",
            )
            (reports / "runtime-validation.graph.json").write_text(
                json.dumps(
                    {
                        "platform": "Microsoft Defender XDR Advanced Hunting",
                        "provider": "graph",
                        "results": [
                            {
                                "detection": "Rule.yaml",
                                "status": "blocked",
                                "rowCount": 0,
                                "error": "table unavailable",
                            }
                        ],
                    }
                ),
                encoding="utf-8",
            )
            (reports / "mock-query-parity.json").write_text(
                json.dumps(
                    {
                        "reportPath": str(reports / "mock-query-parity.json"),
                        "comparisons": [
                            {
                                "detection": "Rule.yaml",
                                "passed": True,
                                "matchKey": {"IPAddress": "192.0.2.1"},
                                "analyticRuleRows": 1,
                                "customDetectionRows": 1,
                            }
                        ],
                    }
                ),
                encoding="utf-8",
            )

            report = build_solution_report(root)

            self.assertEqual(report["solution"], "Example")
            self.assertEqual(report["summary"]["rules"], 1)
            self.assertEqual(
                report["rules"][0]["customDetection"]["conversionStatus"],
                "converted",
            )
            self.assertTrue(
                report["rules"][0]["customDetection"]["reviewRequired"]
            )
            self.assertIn("complete UPN", report["rules"][0]["entityRecommendation"])
            self.assertEqual(
                report["rules"][0]["analyticRule"]["runtime"][0]["status"], "passed"
            )
            self.assertEqual(
                report["rules"][0]["customDetection"]["runtime"][0]["status"],
                "blocked",
            )
            self.assertEqual(report["summary"]["analyticRuntimePassed"], 1)
            self.assertEqual(report["summary"]["customRuntimePassed"], 0)
            self.assertEqual(report["summary"]["queryParityPassed"], 1)
            self.assertEqual(report["rules"][0]["queryParity"]["status"], "passed")
            self.assertTrue(Path(report["jsonReport"]).exists())
            self.assertTrue(Path(report["htmlReport"]).exists())
            self.assertEqual(reports, Path(report["jsonReport"]).parent)
            self.assertEqual(
                ["Rule.yaml"],
                sorted(path.name for path in output.iterdir()),
            )
            html = Path(report["htmlReport"]).read_text(encoding="utf-8")
            self.assertIn("log-analytics-cli", html)
            self.assertIn("graph", html)
            self.assertIn("Query parity", html)


if __name__ == "__main__":
    unittest.main()
