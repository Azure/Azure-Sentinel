from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path


TOOLS = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(TOOLS))

import clean_xdr_detection_outputs as cleanup


DETECTION = """\
id: 11111111-1111-1111-1111-111111111111
name: Example detection
query: |
  DeviceEvents
  | where ActionType == "Example"
"""

RICH_DETECTION = """\
schemaVersion: 1.0.0
kind: CustomDetection
resourceType: Microsoft.Security/detectionRules
properties:
  id: xdr-example
  displayName: Example rich detection
  queryCondition:
    queryText: |
      DeviceEvents
      | where ActionType == "Example"
"""


class XdrDetectionCleanupTests(unittest.TestCase):
    def test_preserves_detection_yaml_and_moves_reports_and_config(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            xdr = root / "Solutions" / "Example" / "XDR Detections"
            xdr.mkdir(parents=True)
            (xdr / "ExampleDetection.yaml").write_text(DETECTION, encoding="utf-8")
            (xdr / "RichDetection.yaml").write_text(
                RICH_DETECTION, encoding="utf-8"
            )
            (xdr / "migration-config.yaml").write_text("version: 1\n", encoding="utf-8")
            (xdr / "migration-report.json").write_text("{}", encoding="utf-8")
            (xdr / "runtime-validation.html").write_text("<html></html>", encoding="utf-8")

            plan = cleanup.plan_cleanup(root)
            result = cleanup.apply_cleanup(plan, root / "Reports")

            self.assertEqual(3, result["movedCount"])
            self.assertTrue((xdr / "ExampleDetection.yaml").is_file())
            self.assertEqual(
                ["ExampleDetection.yaml", "RichDetection.yaml"],
                sorted(path.name for path in xdr.iterdir()),
            )
            report_root = (
                root
                / "Reports"
                / "Example"
                / "sentinel-xdr-migration"
            )
            self.assertTrue((report_root / "migration-config.yaml").is_file())
            self.assertTrue((report_root / "migration-report.json").is_file())
            self.assertTrue((report_root / "runtime-validation.html").is_file())

    def test_dry_run_plan_does_not_modify_files(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            xdr = root / "Solutions" / "Example" / "XDR Detections"
            xdr.mkdir(parents=True)
            report = xdr / "workflow-state.json"
            report.write_text(json.dumps({"status": "pending"}), encoding="utf-8")

            plan = cleanup.plan_cleanup(root)

            self.assertEqual(1, len(plan))
            self.assertTrue(report.is_file())


if __name__ == "__main__":
    unittest.main()
