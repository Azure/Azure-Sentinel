# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See LICENSE in the repository root.
from __future__ import annotations

import json
from pathlib import Path
import shutil
import unittest
from uuid import uuid4
import yaml

from solution_manager.authoring.validator import (
    validate_kql_query_static,
    validate_xdr_artifacts_kql,
    validate_xdr_detection_kql,
    validate_xdr_workbook_kql,
)


REPO_ROOT = Path(__file__).resolve().parents[3]


class AuthoringKqlValidatorTests(unittest.TestCase):
    def setUp(self) -> None:
        self.root = REPO_ROOT / f"kql-val-test-{uuid4().hex[:8]}"
        self.root.mkdir(parents=True, exist_ok=True)
        self.solution = self.root / "Solutions" / "SampleSolution"
        (self.solution / "XDR Detections").mkdir(parents=True, exist_ok=True)
        (self.solution / "XDR Workbooks").mkdir(parents=True, exist_ok=True)

    def tearDown(self) -> None:
        shutil.rmtree(self.root, ignore_errors=True)

    def test_validate_kql_query_static_accepts_valid_advanced_hunting_query(self) -> None:
        query = """
        let lookback = 1h;
        DeviceProcessEvents
        | where Timestamp > ago(lookback)
        | where FileName =~ "cmd.exe"
        | project Timestamp, DeviceId, DeviceName, AccountName, ProcessCommandLine, ReportId
        """
        result = validate_kql_query_static(query, surface="advancedHunting")
        self.assertTrue(result["valid"], result["errors"])
        self.assertIn("DeviceProcessEvents", result["referencedTables"])

    def test_validate_kql_query_static_rejects_unbalanced_delimiters_and_unknown_operators(self) -> None:
        unbalanced = """
        DeviceProcessEvents
        | where (FileName =~ "cmd.exe"
        | project Timestamp, DeviceId
        """
        res1 = validate_kql_query_static(unbalanced, surface="advancedHunting")
        self.assertFalse(res1["valid"])
        self.assertTrue(any("Unclosed delimiter" in err for err in res1["errors"]))

        bad_op = """
        DeviceProcessEvents
        | frobnicate FileName =~ "cmd.exe"
        """
        res2 = validate_kql_query_static(bad_op, surface="advancedHunting")
        self.assertFalse(res2["valid"])
        self.assertTrue(any("Unknown KQL tabular operator 'frobnicate'" in err for err in res2["errors"]))

    def test_validate_kql_query_static_rejects_unknown_table_and_cross_workspace_on_ah(self) -> None:
        unknown_table = """
        CompletelyMadeUpTable_XYZ
        | where Timestamp > ago(1h)
        """
        res1 = validate_kql_query_static(unknown_table, surface="advancedHunting")
        self.assertFalse(res1["valid"])
        self.assertTrue(any("Unknown table or tabular identifier 'CompletelyMadeUpTable_XYZ'" in err for err in res1["errors"]))

        cross_ws = """
        workspace("other-ws").DeviceProcessEvents
        | where Timestamp > ago(1h)
        """
        res2 = validate_kql_query_static(cross_ws, surface="advancedHunting")
        self.assertFalse(res2["valid"])
        self.assertTrue(any("cross-workspace 'workspace(...)'" in err for err in res2["errors"]))

    def test_validate_xdr_artifacts_kql_checks_detections_and_workbooks(self) -> None:
        det_path = self.solution / "XDR Detections" / "ValidRule.yaml"
        det_doc = {
            "properties": {
                "displayName": "Valid Rule",
                "queryCondition": {
                    "queryText": "DeviceNetworkEvents\n| where Timestamp > ago(1h)\n| project Timestamp, DeviceId, ReportId\n"
                },
            }
        }
        det_path.write_text(yaml.safe_dump(det_doc, sort_keys=False), encoding="utf-8")

        wb_path = self.solution / "XDR Workbooks" / "ValidWorkbook.json"
        wb_doc = {
            "version": "Notebook/1.0",
            "items": [
                {
                    "type": 3,
                    "name": "ProcessSummary",
                    "content": {
                        "version": "KqlItem/1.0",
                        "queryType": "advancedHunting",
                        "query": json.dumps(
                            {
                                "__advancedHuntingSettings": True,
                                "query": "EmailEvents | where Timestamp > ago(1d) | summarize count() by EmailDirection",
                            }
                        ),
                    },
                }
            ],
        }
        wb_path.write_text(json.dumps(wb_doc, indent=2), encoding="utf-8")

        report = validate_xdr_artifacts_kql(self.solution)
        self.assertTrue(report["valid"], json.dumps(report, indent=2))
        self.assertEqual(len(report["detections"]), 1)
        self.assertEqual(len(report["workbooks"]), 1)
        self.assertEqual(len(report["errors"]), 0)

        # Now inject a broken query into the workbook and verify failure
        wb_doc["items"][0]["content"]["query"] = json.dumps(
            {
                "__advancedHuntingSettings": True,
                "query": "EmailEvents | where (Timestamp > ago(1d)",
            }
        )
        wb_res = validate_xdr_workbook_kql(wb_doc)
        self.assertFalse(wb_res["valid"])
        self.assertTrue(any("Unclosed delimiter" in err for err in wb_res["errors"]))

        det_res = validate_xdr_detection_kql(det_doc)
        self.assertTrue(det_res["valid"])


if __name__ == "__main__":
    unittest.main()
