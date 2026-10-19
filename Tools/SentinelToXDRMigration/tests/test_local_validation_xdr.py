# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See LICENSE in the repository root.
from __future__ import annotations

import copy
import hashlib
import importlib.util
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
from uuid import uuid4
import zipfile
import yaml

from sentinel_xdr_migration import workbooks
from sentinel_xdr_migration._workbook_core import workbook as wb_core
from sentinel_xdr_migration.arm_acceptance import _parse_build_validation_receipt
from sentinel_xdr_migration.arm_acceptance_support import _canonical_sha256
from sentinel_xdr_migration.converter import build_xdr_document
from sentinel_xdr_migration.packaging import (
    package_input_file_hashes,
    package_input_identity,
)


REPO_ROOT = Path(__file__).resolve().parents[3]
VALIDATE_XDR_SCRIPT = REPO_ROOT / ".script/local-validation/validate-xdr-content.py"
VALIDATE_JS = REPO_ROOT / ".script/local-validation/validate.js"
BUILD_AND_VALIDATE_PS1 = REPO_ROOT / ".script/local-validation/build-and-validate.ps1"
COMMON_FUNCTIONS_PS1 = (
    REPO_ROOT / "Tools/Create-Azure-Sentinel-Solution/common/commonFunctions.ps1"
)


def _load_validate_xdr_module():
    spec = importlib.util.spec_from_file_location("validate_xdr_content", VALIDATE_XDR_SCRIPT)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


VALIDATE_XDR = _load_validate_xdr_module()


SAMPLE_ANALYTIC_RULE = """id: 7f8c3a12-4b5e-4d9a-8c1e-2f3a4b5c6d7e
name: Sample Device Process Rule
description: Detects suspicious process execution on endpoints.
severity: Medium
requiredDataConnectors:
  - connectorId: MicrosoftThreatProtection
    dataTypes:
      - DeviceProcessEvents
queryFrequency: 1h
queryPeriod: 1h
triggerOperator: gt
triggerThreshold: 0
tactics:
  - Execution
relevantTechniques:
  - T1059
query: |
  DeviceProcessEvents
  | where TimeGenerated > ago(1h)
  | where FileName =~ "cmd.exe"
entityMappings:
  - entityType: Host
    fieldMappings:
      - identifier: HostName
        columnName: DeviceName
version: 1.0.0
kind: Scheduled
"""


SAMPLE_PARSER_YAML = """id: a1b2c3d4-e5f6-4a7b-8c9d-0e1f2a3b4c5d
Function:
  Title: HelperFunction parser
  Version: '1.0.0'
  LastUpdated: '2026-04-01'
Category: Microsoft Sentinel Parser
FunctionName: HelperFunction
FunctionAlias: HelperFunction
FunctionQuery: 'DeviceProcessEvents | where FileName =~ "cmd.exe"'
"""


class LocalValidationXdrTests(unittest.TestCase):
    def setUp(self) -> None:
        self.scratch = tempfile.TemporaryDirectory(
            prefix="local-val-xdr-", dir=Path.cwd()
        )
        self.root = Path(self.scratch.name)
        self.solution = self.root / "Solutions" / "SampleSolution"
        (self.solution / "Analytic Rules").mkdir(parents=True)
        (self.solution / "Workbooks").mkdir(parents=True)
        (self.solution / "Parsers").mkdir(parents=True)
        (self.solution / "Data").mkdir(parents=True)
        (self.solution / "Package").mkdir(parents=True)

    def tearDown(self) -> None:
        self.scratch.cleanup()

    def _populate_valid_hybrid_solution(self, *, with_package: bool = True) -> dict[str, Path]:
        # 1. Source Analytic Rule + converted XDR Detection
        rule_path = self.solution / "Analytic Rules" / "SampleRule.yaml"
        rule_path.write_text(SAMPLE_ANALYTIC_RULE, encoding="utf-8")
        xdr_doc = build_xdr_document(rule_path, self.solution, {})
        xdr_det_dir = self.solution / "XDR Detections"
        xdr_det_dir.mkdir(exist_ok=True)
        xdr_det_path = xdr_det_dir / "SampleRule.yaml"
        xdr_det_path.write_text(
            yaml.safe_dump(xdr_doc, sort_keys=False), encoding="utf-8"
        )

        # 2. Source Parser + Source Workbook + converted XDR Workbook with requiredWorkspaceFunctions
        parser_path = self.solution / "Parsers" / "HelperFunction.yaml"
        parser_path.write_text(SAMPLE_PARSER_YAML, encoding="utf-8")

        wb_source = self.solution / "Workbooks" / "SampleWorkbook.json"
        wb_source_doc = {
            "version": "Notebook/1.0",
            "fromTemplateId": "sentinel-SampleWorkbook",
            "items": [
                {
                    "type": 3,
                    "content": {
                        "version": "KqlItem/1.0",
                        "query": "HelperFunction() | summarize count() by DeviceName",
                        "queryType": 0,
                        "resourceType": wb_core.LA,
                    },
                }
            ],
        }
        wb_source.write_text(json.dumps(wb_source_doc, indent=2), encoding="utf-8")

        data_file = self.solution / "Data" / "Solution_SampleSolution.json"
        data_doc = {
            "Name": "SampleSolution",
            "Author": "Microsoft - support@microsoft.com",
            "Description": "Sample hybrid Sentinel + Defender XDR solution.",
            "Version": "3.2.1",
            "BasePath": str(self.solution),
            "Metadata": "SolutionMetadata.json",
            "Analytic Rules": ["Analytic Rules/SampleRule.yaml"],
            "Workbooks": ["Workbooks/SampleWorkbook.json"],
            "Parsers": ["Parsers/HelperFunction.yaml"],
            "XDR Detections": ["XDR Detections/SampleRule.yaml"],
            "XDR Workbooks": ["XDR Workbooks/SampleWorkbook.json"],
        }
        data_file.write_text(json.dumps(data_doc, indent=2), encoding="utf-8")

        metadata_file = self.solution / "SolutionMetadata.json"
        metadata_file.write_text(
            json.dumps(
                {
                    "publisherId": "azuresentinel",
                    "offerId": "azure-sentinel-solution-samplesolution",
                    "firstPublishDate": "2025-01-01",
                    "providers": ["Microsoft"],
                    "categories": {"domains": ["Security - Threat Protection"]},
                    "support": {
                        "name": "Microsoft Corporation",
                        "email": "support@microsoft.com",
                        "tier": "Microsoft",
                        "link": "https://support.microsoft.com",
                    },
                },
                indent=2,
            ),
            encoding="utf-8",
        )

        query_text = wb_source_doc["items"][0]["content"]["query"]
        settings = {
            "workbookResolutions": {
                "Workbooks/SampleWorkbook.json": {
                    "/items/0/content/query": {
                        "querySha256": wb_core.query_hash(query_text),
                        "tables": ["DeviceProcessEvents"],
                        "workspaceFunctions": ["HelperFunction"],
                        "evidence": "Reviewed parser HelperFunction and table DeviceProcessEvents",
                    }
                }
            },
            "workbookDependencies": {
                "Workbooks/SampleWorkbook.json": {
                    "requiredWorkloads": [
                        {"workload": "mde", "dataTypes": ["DeviceProcessEvents"]}
                    ],
                    "requiredDataConnectors": [],
                    "requiredWorkspaceFunctions": [
                        {
                            "functionAlias": "HelperFunction",
                            "sourcePath": "Parsers/HelperFunction.yaml",
                            "sourceSha256": hashlib.sha256(parser_path.read_bytes()).hexdigest(),
                        }
                    ],
                }
            },
        }
        conv_result = workbooks.convert_workbooks(
            self.solution,
            config=settings,
            report_directory=self.solution / "Logs",
            overwrite=True,
        )
        self.assertEqual(conv_result["converted"], 1)
        shutil.rmtree(self.solution / "Logs", ignore_errors=True)
        xdr_wb_path = self.solution / "XDR Workbooks" / "SampleWorkbook.json"
        self.assertTrue(xdr_wb_path.is_file())

        if with_package:
            self._build_packaged_main_template(data_doc)

        return {
            "rule": rule_path,
            "xdr_detection": xdr_det_path,
            "parser": parser_path,
            "workbook": wb_source,
            "xdr_workbook": xdr_wb_path,
            "data": data_file,
            "main_template": self.solution / "Package" / "mainTemplate.json",
        }

    def _build_packaged_main_template(self, data_doc: dict) -> None:
        """Build a valid Package/mainTemplate.json containing CustomDetection, DefenderWorkbook-0, and savedSearches."""
        assert shutil.which("pwsh"), "pwsh is required to build packaged mainTemplate fixture"
        template = {
            "$schema": "https://schema.management.azure.com/schemas/2019-04-01/deploymentTemplate.json#",
            "contentVersion": "1.0.0.0",
            "parameters": {
                "workspace": {"type": "string", "defaultValue": "sample-ws"},
                "workspace-location": {"type": "string", "defaultValue": "eastus"},
            },
            "variables": {
                "solutionId": "azuresentinel.azure-sentinel-solution-samplesolution",
                "_solutionId": "[variables('solutionId')]",
                "_solutionVersion": "3.2.1",
                "workspaceResourceId": "[resourceId('microsoft.OperationalInsights/workspaces', parameters('workspace'))]",
                "uiuk": "sample-uiuk",
            },
            "resources": [
                {
                    "type": "Microsoft.OperationalInsights/workspaces/savedSearches",
                    "apiVersion": "2020-08-01",
                    "name": "[concat(parameters('workspace'), '/HelperFunction')]",
                    "properties": {
                        "category": "Microsoft Sentinel Parser",
                        "displayName": "HelperFunction parser",
                        "functionAlias": "HelperFunction",
                        "query": "DeviceProcessEvents | where FileName =~ \"cmd.exe\"",
                        "version": 2,
                    },
                },
                {
                    "type": "Microsoft.OperationalInsights/workspaces/providers/contentTemplates",
                    "apiVersion": "2023-04-01-preview",
                    "name": "[concat(parameters('workspace'),'/Microsoft.SecurityInsights/', concat('HelperFunction-Parser-', variables('_solutionVersion')))]",
                    "properties": {
                        "contentId": "a1b2c3d4-e5f6-4a7b-8c9d-0e1f2a3b4c5d",
                        "displayName": "HelperFunction parser",
                        "contentKind": "Function",
                        "contentProductId": "sample-function-product-id",
                        "contentSchemaVersion": "3.0.0",
                        "packageId": "[variables('_solutionId')]",
                        "packageVersion": "[variables('_solutionVersion')]",
                        "source": {"kind": "Solution", "name": "SampleSolution", "sourceId": "[variables('_solutionId')]"},
                        "author": {"name": "Microsoft"},
                        "support": {"name": "Microsoft Corporation", "tier": "Microsoft"},
                        "version": "1.0.0",
                        "mainTemplate": {
                            "$schema": "https://schema.management.azure.com/schemas/2019-04-01/deploymentTemplate.json#",
                            "contentVersion": "1.0.0.0",
                            "parameters": {},
                            "variables": {},
                            "resources": [
                                {
                                    "type": "Microsoft.OperationalInsights/workspaces/savedSearches",
                                    "apiVersion": "2020-08-01",
                                    "name": "[concat(parameters('workspace'), '/HelperFunction')]",
                                    "properties": {"functionAlias": "HelperFunction"},
                                },
                                {
                                    "type": "Microsoft.OperationalInsights/workspaces/providers/metadata",
                                    "apiVersion": "2022-01-01-preview",
                                    "name": "[concat(parameters('workspace'),'/Microsoft.SecurityInsights/Function-HelperFunction')]",
                                    "properties": {"kind": "Function", "parentId": "sample"},
                                },
                            ],
                        },
                    },
                },
                {
                    "type": "Microsoft.OperationalInsights/workspaces/providers/contentPackages",
                    "apiVersion": "2023-04-01-preview",
                    "location": "[parameters('workspace-location')]",
                    "name": "[concat(parameters('workspace'),'/Microsoft.SecurityInsights/', variables('_solutionId'))]",
                    "properties": {
                        "version": "3.2.1",
                        "contentId": "[variables('_solutionId')]",
                        "contentProductId": "sample-pkg",
                        "displayName": "SampleSolution",
                        "contentKind": "Solution",
                        "descriptionHtml": "<p>Sample</p>",
                        "icon": "",
                        "categories": {"domains": ["Security - Threat Protection"]},
                        "support": {
                            "name": "Microsoft Corporation",
                            "email": "support@microsoft.com",
                            "tier": "Microsoft",
                            "link": "https://support.microsoft.com",
                        },
                        "dependencies": {"criteria": []},
                    },
                },
                {
                    "type": "Microsoft.Resources/deployments",
                    "apiVersion": "2025-04-01",
                    "name": "CustomDetection-1",
                    "condition": "[parameters('DeployCustomDetection')]",
                    "dependsOn": [
                        "[extensionResourceId(resourceId('Microsoft.OperationalInsights/workspaces', parameters('workspace')), 'Microsoft.SecurityInsights/contentPackages', variables('_solutionId'))]"
                    ],
                    "properties": {
                        "mode": "Incremental",
                        "expressionEvaluationOptions": {"scope": "inner"},
                        "template": {
                            "$schema": "https://schema.management.azure.com/schemas/2019-04-01/deploymentTemplate.json#",
                            "languageVersion": "2.0",
                            "contentVersion": "1.0.0.0",
                            "imports": {
                                "MicrosoftSecurity": {
                                    "provider": "MicrosoftSecurity",
                                    "version": "1.0.0",
                                }
                            },
                            "resources": {
                                "detectionRule": {
                                    "import": "MicrosoftSecurity",
                                    "type": "Microsoft.Security/detectionRules@2026-03-01-beta",
                                    "properties": {
                                        "id": "xdr-7f8c3a12-4b5e-4d9a-8c1e-2f3a4b5c6d7e",
                                        "displayName": "Sample Device Process Rule",
                                        "status": "disabled",
                                    },
                                }
                            },
                        },
                    },
                },
                {
                    "type": "Microsoft.OperationalInsights/workspaces/providers/contentTemplates",
                    "apiVersion": "2023-04-01-preview",
                    "location": "[parameters('workspace-location')]",
                    "name": "[concat(parameters('workspace'),'/Microsoft.SecurityInsights/', concat('xdr-7f8c3a12-4b5e-4d9a-8c1e-2f3a4b5c6d7e-cd-', variables('_solutionVersion')))]",
                    "condition": "[parameters('DeployCustomDetection')]",
                    "dependsOn": [
                        "[resourceId('Microsoft.Resources/deployments', 'CustomDetection-1')]",
                        "[extensionResourceId(resourceId('Microsoft.OperationalInsights/workspaces', parameters('workspace')), 'Microsoft.SecurityInsights/contentPackages', variables('_solutionId'))]",
                    ],
                    "properties": {
                        "version": "1.0.0",
                        "contentId": "xdr-7f8c3a12-4b5e-4d9a-8c1e-2f3a4b5c6d7e",
                        "contentProductId": "sample-cd-product-id",
                        "contentSchemaVersion": "3.0.0",
                        "displayName": "Sample Device Process Rule",
                        "contentKind": "CustomDetection",
                        "packageId": "[variables('_solutionId')]",
                        "packageVersion": "[variables('_solutionVersion')]",
                        "mainTemplate": {
                            "$schema": "https://schema.management.azure.com/schemas/2019-04-01/deploymentTemplate.json#",
                            "contentVersion": "1.0.0.0",
                            "parameters": {},
                            "variables": {},
                            "resources": [],
                        },
                    },
                },
            ],
        }
        ui = {
            "parameters": {
                "outputs": {},
                "steps": [],
                "config": {
                    "basics": {
                        "description": "Sample description\n\n**Analytic Rules:** 1\n\n**Workbooks:** 1"
                    }
                },
            }
        }
        payload_path = self.root / "pkg-input.json"
        payload_path.write_text(
            json.dumps({"data": data_doc, "template": template, "ui": ui}),
            encoding="utf-8",
        )
        ps_cmd = (
            f". '{COMMON_FUNCTIONS_PS1}'; "
            f"$p = Get-Content -LiteralPath '{payload_path}' -Raw | ConvertFrom-Json -Depth 100; "
            f"$template = $p.template; $ui = $p.ui; "
            f"Register-SolutionRequiredResources -Resources @($template.resources[0], $template.resources[1]); "
            f"$wbCount = Add-XdrDefenderWorkbooksToSolution -SolutionName 'SampleSolution' -ContentToImport $p.data -Template $template -RepositoryRoot '{self.root}'; "
            f"Add-SolutionContentDeploymentParameters -Template $template -UiDefinition $ui; "
            f"$template | ConvertTo-Json -Depth 100 | Set-Content -LiteralPath '{self.solution / 'Package' / 'mainTemplate.json'}' -Encoding utf8"
        )
        proc = subprocess.run(
            ["pwsh", "-NoLogo", "-NoProfile", "-Command", ps_cmd],
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(proc.returncode, 0, proc.stderr or proc.stdout)
        payload_path.unlink(missing_ok=True)

    def test_solution_without_xdr_content_reports_visible_skips(self) -> None:
        # Solution with only native Sentinel rule and workbook
        (self.solution / "Analytic Rules" / "SampleRule.yaml").write_text(
            SAMPLE_ANALYTIC_RULE, encoding="utf-8"
        )
        (self.solution / "Data" / "Solution_SampleSolution.json").write_text(
            json.dumps(
                {
                    "Name": "SampleSolution",
                    "Version": "3.0.0",
                    "Analytic Rules": ["Analytic Rules/SampleRule.yaml"],
                }
            ),
            encoding="utf-8",
        )

        report = VALIDATE_XDR.run_validation(
            content_root=self.root,
            solution_paths=[self.solution],
            family="all",
        )
        self.assertEqual(report["summary"]["failed"], 0)
        self.assertEqual(report["summary"]["passed"], 0)
        self.assertEqual(report["summary"]["skipped"], 2)
        for item in report["results"]:
            self.assertTrue(item["skipped"])
            self.assertTrue(item["passed"])
            self.assertIn("No XDR", item["skipReason"])

    def test_valid_xdr_detections_and_defender_workbooks_pass_validation(self) -> None:
        self._populate_valid_hybrid_solution(with_package=True)
        report = VALIDATE_XDR.run_validation(
            content_root=self.root,
            solution_paths=[self.solution],
            family="all",
        )
        self.assertEqual(report["summary"]["failed"], 0, json.dumps(report, indent=2))
        self.assertEqual(report["summary"]["skipped"], 0)
        self.assertGreaterEqual(report["summary"]["passed"], 2)
        self.assertTrue(report["detections"][0]["applicable"])
        self.assertTrue(report["detections"][0]["liveKqlSkipped"])
        self.assertTrue(report["workbooks"][0]["applicable"])
        self.assertTrue(report["workbooks"][0]["liveKqlSkipped"])

    def test_xdr_detection_schema_and_provenance_failures_are_reported(self) -> None:
        paths = self._populate_valid_hybrid_solution(with_package=False)
        det_path = paths["xdr_detection"]
        original_doc = yaml.safe_load(det_path.read_text(encoding="utf-8"))

        # Case 1: dependencyReviewRequired = True + conversion.reviewRequired = True + stale source querySha256
        broken_doc = copy.deepcopy(original_doc)
        broken_doc["contentProvenance"]["dependencyReviewRequired"] = True
        broken_doc["contentProvenance"]["conversion"]["reviewRequired"] = True
        broken_doc["contentProvenance"]["conversion"]["status"] = "needs_review"
        broken_doc["contentProvenance"]["source"]["querySha256"] = "0" * 64
        broken_doc["contentProvenance"]["requiredWorkloads"] = [
            {"workload": "invalid-workload", "dataTypes": ["DeviceProcessEvents"]}
        ]
        det_path.write_text(yaml.safe_dump(broken_doc, sort_keys=False), encoding="utf-8")

        report = VALIDATE_XDR.run_validation(
            content_root=self.root,
            solution_paths=[self.solution],
            family="detections",
        )
        self.assertEqual(report["summary"]["failed"], 1)
        joined = "\n".join(r.get("error") or "" for r in report["results"])
        self.assertIn("dependencyReviewRequired", joined)
        self.assertIn("reviewRequired", joined)
        self.assertIn("needs_review", joined)
        self.assertIn("querySha256", joined)
        self.assertIn("invalid-workload", joined)

        # Case 2: Data/*.json missing explicit "XDR Detections" array when XDR Detections/ exists
        det_path.write_text(yaml.safe_dump(original_doc, sort_keys=False), encoding="utf-8")
        data_doc = json.loads(paths["data"].read_text(encoding="utf-8"))
        del data_doc["XDR Detections"]
        paths["data"].write_text(json.dumps(data_doc, indent=2), encoding="utf-8")

        report_missing_data = VALIDATE_XDR.run_validation(
            content_root=self.root,
            solution_paths=[self.solution],
            family="detections",
        )
        self.assertGreaterEqual(report_missing_data["summary"]["failed"], 1)
        all_msgs = [
            res.get("error") or ""
            for res in report_missing_data["results"]
            if not res.get("passed", True)
        ]
        self.assertTrue(
            any("missing an explicit XDR Detections array" in m for m in all_msgs),
            all_msgs,
        )

    def test_xdr_workbook_schema_provenance_and_packaged_depends_on_failures_are_reported(self) -> None:
        paths = self._populate_valid_hybrid_solution(with_package=True)
        wb_path = paths["xdr_workbook"]
        original_wb = json.loads(wb_path.read_text(encoding="utf-8"))

        # Case 1: Leaked deployment quartet + dependencyReviewRequired + broken requiredWorkspaceFunctions
        broken_wb = copy.deepcopy(original_wb)
        broken_wb["contentProvenance"]["packageId"] = "leaked.pkg"
        broken_wb["contentProvenance"]["dependencyReviewRequired"] = True
        broken_wb["contentProvenance"]["conversion"]["reviewRequired"] = True
        broken_wb["contentProvenance"]["requiredWorkspaceFunctions"] = [
            {
                "functionAlias": "HelperFunction",
                "sourcePath": "Parsers/MissingParser.yaml",
                "sourceSha256": "0" * 64,
            }
        ]
        wb_path.write_text(json.dumps(broken_wb, indent=2), encoding="utf-8")

        report = VALIDATE_XDR.run_validation(
            content_root=self.root,
            solution_paths=[self.solution],
            family="workbooks",
        )
        self.assertGreaterEqual(report["summary"]["failed"], 1)
        all_msgs = "\n".join(
            res.get("error") or ""
            for res in report["results"]
            if not res.get("passed", True)
        )
        self.assertIn("packageId", all_msgs)
        self.assertIn("dependencyReviewRequired", all_msgs)
        self.assertIn("reviewRequired", all_msgs)
        self.assertIn("MissingParser.yaml", all_msgs)

        # Case 2: Restore authored workbook, break packaged mainTemplate.json DefenderWorkbook dependsOn
        wb_path.write_text(json.dumps(original_wb, indent=2), encoding="utf-8")
        main_template_path = paths["main_template"]
        main_template = json.loads(main_template_path.read_text(encoding="utf-8"))
        for resource in main_template["resources"]:
            if (
                resource.get("type")
                == "Microsoft.OperationalInsights/workspaces/providers/contentTemplates"
                and resource.get("properties", {}).get("contentKind") == "DefenderWorkbook"
            ):
                # Corrupt dependsOn so contentPackages extensionResourceId is missing
                resource["dependsOn"] = [
                    "[resourceId('Microsoft.Resources/deployments', 'DefenderWorkbook-0')]"
                ]
        main_template_path.write_text(json.dumps(main_template, indent=2), encoding="utf-8")

        pkg_report = VALIDATE_XDR.run_validation(
            content_root=self.root,
            solution_paths=[self.solution],
            family="workbooks",
        )
        self.assertGreaterEqual(pkg_report["summary"]["failed"], 1)
        pkg_msgs = "\n".join(
            res.get("error") or ""
            for res in pkg_report["results"]
            if not res.get("passed", True)
        )
        self.assertIn("dependsOn", pkg_msgs)

        # Case 3: Standalone DefenderWorkbook-* in Package/mainTemplate.json without XDR Workbooks/ folder
        shutil.rmtree(self.solution / "XDR Workbooks")
        standalone_report = VALIDATE_XDR.run_validation(
            content_root=self.root,
            solution_paths=[self.solution],
            family="workbooks",
        )
        self.assertGreaterEqual(standalone_report["summary"]["failed"], 1)
        standalone_msgs = "\n".join(
            res.get("error") or ""
            for res in standalone_report["results"]
            if not res.get("passed", True)
        )
        self.assertIn("DefenderWorkbook", standalone_msgs)

    def test_validate_js_runs_xdr_validators_and_skips_legacy_workbook_template_on_xdr_workbooks(self) -> None:
        self._populate_valid_hybrid_solution(with_package=True)
        out_json = self.root / "validate-results.json"
        proc = subprocess.run(
            [
                "node",
                str(VALIDATE_JS),
                "--repository-root",
                str(self.root),
                "--path",
                "Solutions/SampleSolution",
                "--only",
                "workbook-template,xdr-detection,xdr-workbook",
                "--json-file",
                str(out_json),
            ],
            cwd=str(REPO_ROOT),
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(proc.returncode, 0, proc.stderr or proc.stdout)
        results = json.loads(out_json.read_text(encoding="utf-8"))
        self.assertEqual(results["summary"]["failed"], 0, json.dumps(results, indent=2))

        by_validator: dict[str, list[dict]] = {}
        for item in results["results"]:
            by_validator.setdefault(item["validator"], []).append(item)

        self.assertIn("XDR Detection", by_validator)
        self.assertIn("XDR Workbook", by_validator)
        self.assertTrue(all(r["passed"] and not r.get("skipped") for r in by_validator["XDR Detection"]))
        self.assertTrue(all(r["passed"] and not r.get("skipped") for r in by_validator["XDR Workbook"]))

        # Ensure XDR Workbooks/*.json was marked skipped by legacy Workbook Template validator
        wb_template_results = by_validator.get("Workbook Template", [])
        xdr_wb_entries = [
            r for r in wb_template_results if "XDR Workbooks/" in r["filePath"]
        ]
        self.assertEqual(len(xdr_wb_entries), 1)
        self.assertTrue(xdr_wb_entries[0].get("skipped"))
        self.assertIn("XDR Workbook validator", xdr_wb_entries[0].get("skipReason", ""))

    @unittest.skipUnless(shutil.which("pwsh"), "PowerShell 7 is required")
    def test_build_and_validate_ps1_surfaces_xdr_checks_and_visible_skipped_checks(self) -> None:
        self._populate_valid_hybrid_solution(with_package=True)
        subprocess.run(
            ["git", "init", "-q"],
            cwd=str(self.root),
            check=True,
        )

        package_dir = self.solution / "Package"
        (package_dir / "createUiDefinition.json").write_text(
            json.dumps(
                {
                    "$schema": "https://schema.management.azure.com/schemas/0.1.2-preview/CreateUIDefinition.MultiVm.json#",
                    "handler": "Microsoft.Azure.CreateUIDef",
                    "version": "0.1.2-preview",
                    "parameters": {
                        "config": {"isWizard": False, "basics": {"description": "Sample"}},
                        "basics": [],
                        "steps": [],
                        "outputs": {},
                    },
                },
                indent=2,
            ),
            encoding="utf-8",
        )
        (package_dir / "testParameters.json").write_text(
            json.dumps({"workspace": {"value": "ws"}}, indent=2),
            encoding="utf-8",
        )
        zip_path = package_dir / "3.2.1.zip"
        with zipfile.ZipFile(zip_path, "w") as archive:
            archive.write(package_dir / "mainTemplate.json", "mainTemplate.json")
            archive.write(package_dir / "createUiDefinition.json", "createUiDefinition.json")

        logs_dir = self.solution / "Logs"
        logs_dir.mkdir(exist_ok=True)
        pkg_paths = {
            "mainTemplate": "Package/mainTemplate.json",
            "createUiDefinition": "Package/createUiDefinition.json",
            "testParameters": "Package/testParameters.json",
            "zip": "Package/3.2.1.zip",
        }
        pkg_hashes = {
            name: hashlib.sha256((self.solution / rel).read_bytes()).hexdigest()
            for name, rel in pkg_paths.items()
        }
        identity = package_input_identity(self.solution)
        pkg_report = {
            "packager": "V3.1",
            "workflowRunId": "test-xdr-local-val-run",
            "packageAttemptId": "attempt-1",
            "version": "3.2.1",
            "armValidationMethod": "lab-deployment",
            "packageInputs": {
                "after": {**identity, "files": package_input_file_hashes(self.solution)}
            },
            "packageArtifactHashes": pkg_hashes,
            "packageArtifactsSha256": _canonical_sha256(pkg_hashes),
            **pkg_paths,
        }
        report_path = logs_dir / "packaging.v3_1.json"
        report_path.write_text(
            json.dumps(pkg_report, indent=2), encoding="utf-8"
        )
        package_files = sorted(
            (
                {
                    "path": path.relative_to(package_dir).as_posix(),
                    "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
                }
                for path in package_dir.rglob("*")
                if path.is_file()
            ),
            key=lambda item: item["path"],
        )
        package_identity = {
            "version": "3.2.1",
            "packageInputSha256": identity["sha256"],
            "packageContentSha256": _canonical_sha256(package_files),
            "packageReportSha256": hashlib.sha256(report_path.read_bytes()).hexdigest(),
            "packageAttemptId": "attempt-1",
            "workflowRunId": "test-xdr-local-val-run",
            "packageArtifactsSha256": pkg_report["packageArtifactsSha256"],
            "recordedPackageArtifactHashes": pkg_hashes,
        }

        proc = subprocess.run(
            [
                "pwsh",
                "-NoLogo",
                "-NoProfile",
                "-File",
                str(BUILD_AND_VALIDATE_PS1),
                "-SolutionName",
                "SampleSolution",
                "-ContentRoot",
                str(self.root),
                "-SkipPackaging",
                "-ArmValidationMethod",
                "lab-deployment",
                "-PackageReportPath",
                "Logs/packaging.v3_1.json",
            ],
            cwd=str(REPO_ROOT),
            capture_output=True,
            text=True,
            check=False,
        )
        output = proc.stdout
        evidence_dir: Path | None = None
        for line in output.splitlines():
            if line.startswith("Evidence: "):
                evidence_dir = Path(line.split("Evidence: ", 1)[1].strip())
                break
        try:
            self.assertEqual(proc.returncode, 0, proc.stderr or proc.stdout)
            self.assertIn("[REPORT_START]", output)
            self.assertIn("[REPORT_END]", output)
            self.assertIn("| TS | XDR Detection | PASS |", output)
            self.assertIn("| TS | XDR Workbook | PASS |", output)
            self.assertIn("| .NET | XDR KQL (Live / Advanced Hunting) | SKIP |", output)
            self.assertIn("Skipped / Unsupported Checks", output)
            self.assertIsNotNone(evidence_dir)

            # Verify that _parse_build_validation_receipt from arm_acceptance.py validates the report & binding receipt
            receipt = _parse_build_validation_receipt(
                self.solution,
                evidence_dir / "build-and-validate-report.md",
                package_report_path=report_path,
                package_identity=package_identity,
                arm_validation_method="lab-deployment",
            )
            self.assertEqual(receipt["validatorSummary"]["failed"], 0)
            self.assertGreater(receipt["validatorSummary"]["skipped"], 0)
            validators_by_name = {
                row["validator"]: row["status"] for row in receipt["validatorResults"]
            }
            self.assertEqual(validators_by_name.get("XDR Detection"), "PASS")
            self.assertEqual(validators_by_name.get("XDR Workbook"), "PASS")
            self.assertEqual(
                validators_by_name.get("XDR KQL (Live / Advanced Hunting)"), "SKIP"
            )
        finally:
            if evidence_dir and evidence_dir.exists():
                shutil.rmtree(evidence_dir, ignore_errors=True)
                try:
                    evidence_dir.parent.rmdir()
                except OSError:
                    pass
            subprocess.run(
                [
                    "git",
                    "checkout",
                    "--",
                    ".script/SolutionValidations",
                    ".script/utils",
                    ".script/contentValidator.js.map",
                    ".script/dataConnectorValidator.js.map",
                    ".script/documentsLinkValidator.js.map",
                    ".script/idChangeValidator.js.map",
                    ".script/logoValidator.js.map",
                    ".script/playbooksValidator.js.map",
                    ".script/workbooksTemplateValidator.js.map",
                    ".script/yamlFileValidator.js.map",
                ],
                cwd=str(REPO_ROOT),
                capture_output=True,
                check=False,
            )


if __name__ == "__main__":
    unittest.main()
