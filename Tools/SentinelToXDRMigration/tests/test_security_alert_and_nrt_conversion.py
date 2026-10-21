from __future__ import annotations

import json
import shutil
import subprocess
from pathlib import Path

import pytest
import yaml

from solution_manager.migration._workbook_core import migrator, rewrite, workbook
from solution_manager.migration.converter import (
    build_xdr_document,
    convert_security_alert_incident_query,
    rewrite_cosmetic_nrt_summarize,
)
from solution_manager.migration.workbooks import convert_workbooks, validate_workbooks


def _write_minimal_solution(root: Path) -> Path:
    sol = root / "Solutions" / "TestSolution"
    (sol / "Analytic Rules").mkdir(parents=True, exist_ok=True)
    (sol / "Data").mkdir(parents=True, exist_ok=True)
    (sol / "SolutionMetadata.json").write_text(
        json.dumps(
            {
                "publisherId": "microsoftsentinel",
                "offerId": "test-solution",
                "firstPublishDate": "2024-01-01",
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
    (sol / "Data" / "Solution_TestSolution.json").write_text(
        json.dumps(
            {
                "Name": "TestSolution",
                "Author": "Microsoft",
                "Description": "Test solution",
                "Version": "3.1.0",
                "BasePath": str(sol),
                " Analtyic Rules": [],
            },
            indent=2,
        ),
        encoding="utf-8",
    )
    return sol


def _write_rule(sol: Path, filename: str, payload: dict) -> Path:
    rule_path = sol / "Analytic Rules" / filename
    rule_path.write_text(yaml.safe_dump(payload, sort_keys=False), encoding="utf-8")
    return rule_path


class TestSecurityAlertAndIncidentConversion:
    def test_security_alert_query_rewrites_columns_and_preserves_aliases(self) -> None:
        query = (
            "SecurityAlert\n"
            "| where TimeGenerated > ago(1d)\n"
            "| where AlertSeverity in ('High', 'Medium') and ProviderName == 'MDATP'\n"
            "| where ProductName has 'Defender' and AlertName has 'Suspicious'\n"
            "| project TimeGenerated, SystemAlertId, AlertName, DisplayName, AlertSeverity, "
            "ProviderName, ProductName, Tactics, Description"
        )
        converted, notes, renamed = convert_security_alert_incident_query(query)
        assert "security_alert_migrated_to_alert_info" in notes
        assert renamed == {"SecurityAlert": "AlertInfo"}
        assert converted.startswith("AlertInfo")
        assert "Timestamp > ago(1d)" in converted
        assert "Severity in ('High', 'Medium')" in converted
        assert "DetectionSource == 'MDATP'" in converted
        assert "ServiceSource has 'Defender'" in converted
        assert "Title has 'Suspicious'" in converted
        assert "| extend " in converted
        assert "SystemAlertId = AlertId" in converted
        assert "AlertName = Title" in converted
        assert "AlertSeverity = Severity" in converted
        assert "ProviderName = DetectionSource" in converted
        assert "ProductName = ServiceSource" in converted

    def test_security_alert_with_entities_joins_alert_evidence(self) -> None:
        query = (
            "SecurityAlert\n"
            "| where AlertSeverity == 'High'\n"
            "| extend ParsedEntities = parse_json(Entities)\n"
            "| project SystemAlertId, AlertName, Entities, AccountUpn, RemoteIp"
        )
        converted, notes, renamed = convert_security_alert_incident_query(query)
        assert "security_alert_migrated_to_alert_info_and_evidence" in notes
        assert renamed == {"SecurityAlert": "AlertInfo"}
        assert "AlertInfo\n| join kind=leftouter AlertEvidence on AlertId" in converted
        assert "Entities = AdditionalFields" in converted

    def test_security_alert_cross_surface_azure_resource_columns_emit_coalesce_aliases(self) -> None:
        query = (
            "SecurityAlert\n"
            "| where isnotempty(AzureResourceId) or isnotempty(ResourceID)\n"
            "| where AzureResourceType =~ 'microsoft.containerservice/managedclusters'\n"
            "| project TimeGenerated, SystemAlertId, AlertName, AzureResourceId, ResourceID, "
            "AzureResourceType, AzureSubscriptionId, CloudResource"
        )
        converted, notes, renamed = convert_security_alert_incident_query(query)
        assert "security_alert_migrated_to_alert_info_and_evidence" in notes
        assert renamed == {"SecurityAlert": "AlertInfo"}
        assert "AlertInfo\n| join kind=leftouter AlertEvidence on AlertId" in converted
        assert (
            'AzureResourceId = coalesce(tostring(column_ifexists("ResourceID", "")), '
            'tostring(column_ifexists("AzureResourceId", "")))'
        ) in converted
        assert (
            'ResourceID = coalesce(tostring(column_ifexists("ResourceID", "")), '
            'tostring(column_ifexists("AzureResourceId", "")))'
        ) in converted
        assert (
            'AzureResourceType = coalesce(tostring(column_ifexists("ResourceType", "")), '
            'tostring(column_ifexists("AzureResourceType", "")))'
        ) in converted
        assert (
            'AzureSubscriptionId = coalesce(tostring(column_ifexists("SubscriptionId", "")), '
            'tostring(column_ifexists("AzureSubscriptionId", "")))'
        ) in converted

    def test_security_incident_query_maps_to_alert_info_with_compatibility_projection(self) -> None:
        query = (
            "SecurityIncident\n"
            "| where Severity == 'High' and Status != 'Closed'\n"
            "| where IncidentName has 'Ransomware'\n"
            "| project IncidentNumber, IncidentName, Severity, Status, Title"
        )
        converted, notes, renamed = convert_security_alert_incident_query(query)
        assert "security_incident_migrated_to_alert_info" in notes
        assert renamed == {"SecurityIncident": "AlertInfo"}
        assert converted.startswith("AlertInfo")
        assert "Title has 'Ransomware'" in converted
        assert "IncidentName = Title" in converted
        assert "IncidentNumber = AlertId" in converted
        assert 'Status = column_ifexists("Status", "Active")' in converted

    def test_rule_conversion_for_security_alert_and_incident(self, tmp_path: Path) -> None:
        sol = _write_minimal_solution(tmp_path)
        alert_rule_path = _write_rule(
            sol,
            "AlertCorrelationRule.yaml",
            {
                "id": "11111111-2222-3333-4444-555555555555",
                "name": "High Severity Defender Alert Correlation",
                "description": "Correlates high severity alerts with evidence.",
                "severity": "High",
                "kind": "Scheduled",
                "queryFrequency": "1h",
                "queryPeriod": "1h",
                "triggerOperator": "gt",
                "triggerThreshold": 0,
                "tactics": ["CredentialAccess"],
                "relevantTechniques": ["T1003"],
                "query": (
                    "SecurityAlert\n"
                    "| where AlertSeverity == 'High' and ProductName has 'Defender'\n"
                    "| extend EntityData = Entities\n"
                    "| where isnotempty(AccountUpn)\n"
                    "| project TimeGenerated, SystemAlertId, AlertName, AlertSeverity, AccountUpn, DeviceId"
                ),
                "entityMappings": [
                    {
                        "entityType": "Account",
                        "fieldMappings": [
                            {"identifier": "FullName", "columnName": "AccountUpn"}
                        ],
                    }
                ],
            },
        )
        doc = build_xdr_document(alert_rule_path, sol, {})
        query_text = doc["properties"]["queryCondition"]["queryText"]
        conv = doc["contentProvenance"]["conversion"]
        assert "AlertInfo" in query_text
        assert "join kind=leftouter AlertEvidence on AlertId" in query_text
        assert any("security_alert_migrated_to_alert_info_and_evidence" in n for n in conv["notes"])
        assert conv["errors"] == []
        assert conv["status"] == "converted"

        incident_rule_path = _write_rule(
            sol,
            "IncidentCorrelationRule.yaml",
            {
                "id": "22222222-3333-4444-5555-666666666666",
                "name": "High Severity Incident Correlation",
                "description": "Correlates high severity incidents.",
                "severity": "High",
                "kind": "Scheduled",
                "queryFrequency": "1h",
                "queryPeriod": "1h",
                "triggerOperator": "gt",
                "triggerThreshold": 0,
                "tactics": ["Impact"],
                "relevantTechniques": ["T1486"],
                "query": (
                    "SecurityIncident\n"
                    "| where Severity == 'High' and IncidentName has 'Exfiltration'\n"
                    "| join kind=inner AlertEvidence on $left.IncidentNumber == $right.AlertId\n"
                    "| project IncidentNumber, IncidentName, Severity, Status, AccountUpn"
                ),
                "entityMappings": [
                    {
                        "entityType": "Account",
                        "fieldMappings": [
                            {"identifier": "FullName", "columnName": "AccountUpn"}
                        ],
                    }
                ],
            },
        )
        inc_doc = build_xdr_document(incident_rule_path, sol, {})
        inc_query = inc_doc["properties"]["queryCondition"]["queryText"]
        inc_conv = inc_doc["contentProvenance"]["conversion"]
        assert inc_query.startswith("AlertInfo")
        assert any("security_incident_migrated_to_alert_info" in n for n in inc_conv["notes"])
        assert inc_conv["errors"] == []
        assert inc_conv["status"] == "converted"

    def test_workbook_query_and_workbook_conversion_for_security_alert_and_incident(
        self, tmp_path: Path
    ) -> None:
        raw_alert_kql = (
            "SecurityAlert\n"
            "| where AlertSeverity == 'High'\n"
            "| summarize AlertCount = count() by AlertName, ProductName, ProviderName"
        )
        rw = rewrite.rewrite(raw_alert_kql, ["SecurityAlert"])
        assert rw["deterministic"] is True
        assert rw["renamedTables"] == {"SecurityAlert": "AlertInfo"}
        assert "AlertInfo" in rw["convertedKql"]
        assert "security_alert_migrated_to_alert_info" in rw["provenanceNotes"]

        contract = migrator.convert(raw_alert_kql, tables=["SecurityAlert"], artifact_type="workbook")
        assert contract["status"] == "converted"
        assert contract["renamedTables"] == {"SecurityAlert": "AlertInfo"}
        assert "security_alert_migrated_to_alert_info" in contract["provenanceNotes"]

        wb_doc = {
            "version": "Notebook/1.0",
            "items": [
                {
                    "type": 3,
                    "content": {
                        "version": "KqlItem/1.0",
                        "query": (
                            "SecurityAlert\n"
                            "| where AlertSeverity == 'High'\n"
                            "| extend ParsedEntities = Entities\n"
                            "| project SystemAlertId, AlertName, AlertSeverity, Entities"
                        ),
                        "queryType": 0,
                        "resourceType": "microsoft.operationalinsights/workspaces",
                    },
                },
                {
                    "type": 3,
                    "content": {
                        "version": "KqlItem/1.0",
                        "query": (
                            "SecurityIncident\n"
                            "| where Severity == 'High'\n"
                            "| project IncidentNumber, IncidentName, Severity, Status"
                        ),
                        "queryType": 0,
                        "resourceType": "microsoft.operationalinsights/workspaces",
                    },
                },
            ],
        }
        converted_wb = workbook.convert_workbook(wb_doc)
        assert converted_wb["report"]["status"] in ("converted", "needs-validation")
        assert converted_wb["report"]["issues"] == []
        assert "security_alert_migrated_to_alert_info_and_evidence" in converted_wb["report"]["provenanceNotes"]
        assert "security_incident_migrated_to_alert_info" in converted_wb["report"]["provenanceNotes"]

        q0 = converted_wb["workbook"]["items"][0]["content"]
        q1 = converted_wb["workbook"]["items"][1]["content"]
        assert q0["queryType"] == workbook.AH
        assert "AlertInfo\n| join kind=leftouter AlertEvidence on AlertId" in q0["query"]
        assert q1["queryType"] == workbook.AH
        assert q1["query"].startswith("AlertInfo")

        # Also verify solution-level convert_workbooks + validate_workbooks
        sol = _write_minimal_solution(tmp_path)
        (sol / "Workbooks").mkdir(parents=True, exist_ok=True)
        wb_path = sol / "Workbooks" / "AlertOverview.json"
        wb_path.write_text(json.dumps(wb_doc, indent=2), encoding="utf-8")
        sol_data_path = sol / "Data" / "Solution_TestSolution.json"
        sol_data = json.loads(sol_data_path.read_text(encoding="utf-8"))
        sol_data["Workbooks"] = ["Workbooks/AlertOverview.json"]
        sol_data_path.write_text(json.dumps(sol_data, indent=2), encoding="utf-8")
        summary = convert_workbooks(
            sol,
            config={"targetVersion": "3.2.2"},
            report_directory=tmp_path / "reports",
        )
        assert summary["converted"] == 1
        assert summary["blocked"] == 0
        validation = validate_workbooks(sol)
        assert validation["valid"] == 1
        assert validation["invalid"] == 0


class TestNrtSummarizeHandling:
    def test_rewrite_cosmetic_nrt_summarize_direct(self) -> None:
        query = (
            "DeviceProcessEvents\n"
            "| where FileName =~ 'cmd.exe'\n"
            "| summarize StartTime = min(TimeGenerated), EndTime = max(TimeGenerated), "
            "EventCount = count(), CommandLines = make_set(ProcessCommandLine), "
            "SampleFolder = take_any(FolderPath) by AccountName, DeviceName"
        )
        rewritten, changed, notes = rewrite_cosmetic_nrt_summarize(query)
        assert changed is True
        assert any("nrt_cosmetic_summarize_rewritten" in n for n in notes)
        assert "| summarize" not in rewritten.lower()
        assert "StartTime = TimeGenerated" in rewritten
        assert "EndTime = TimeGenerated" in rewritten
        assert "EventCount = 1" in rewritten
        assert "CommandLines = pack_array(ProcessCommandLine)" in rewritten
        assert "SampleFolder = FolderPath" in rewritten
        assert "| project StartTime, EndTime, EventCount, CommandLines, SampleFolder, AccountName, DeviceName" in rewritten

    def test_rewrite_cosmetic_nrt_summarize_arg_max_star(self) -> None:
        query = (
            "DeviceNetworkEvents\n"
            "| where RemotePort == 4444\n"
            "| summarize arg_max(TimeGenerated, *) by DeviceId, RemoteIP"
        )
        rewritten, changed, notes = rewrite_cosmetic_nrt_summarize(query)
        assert changed is True
        assert any("nrt_cosmetic_summarize_rewritten" in n for n in notes)
        assert "| summarize" not in rewritten.lower()

    def test_nrt_rule_with_cosmetic_summarize_preserves_pt0s(self, tmp_path: Path) -> None:
        sol = _write_minimal_solution(tmp_path)
        rule_path = _write_rule(
            sol,
            "NrtCosmeticRule.yaml",
            {
                "id": "33333333-4444-5555-6666-777777777777",
                "name": "NRT Cosmetic Summarize Detection",
                "description": "Detects suspicious process execution in near real time.",
                "severity": "High",
                "kind": "NRT",
                "tactics": ["Execution"],
                "relevantTechniques": ["T1059"],
                "query": (
                    "DeviceProcessEvents\n"
                    "| where FileName =~ 'powershell.exe' and ProcessCommandLine has '-enc'\n"
                    "| summarize StartTime = min(TimeGenerated), EndTime = max(TimeGenerated), "
                    "count(), Cmds = make_set(ProcessCommandLine) by DeviceId, AccountName, InitiatingProcessFileName"
                ),
                "entityMappings": [
                    {
                        "entityType": "Host",
                        "fieldMappings": [
                            {"identifier": "AzureID", "columnName": "DeviceId"}
                        ],
                    }
                ],
            },
        )
        doc = build_xdr_document(rule_path, sol, {})
        query_text = doc["properties"]["queryCondition"]["queryText"]
        conv = doc["contentProvenance"]["conversion"]
        assert doc["properties"]["schedule"]["frequency"] == "PT0S"
        assert "| summarize" not in query_text.lower()
        assert any("nrt_cosmetic_summarize_rewritten" in n for n in conv["notes"])
        assert conv["errors"] == []
        assert conv["status"] == "converted"

    def test_nrt_rule_with_behavioral_summarize_falls_back_to_pt1h(self, tmp_path: Path) -> None:
        sol = _write_minimal_solution(tmp_path)
        rule_path = _write_rule(
            sol,
            "NrtBehavioralRule.yaml",
            {
                "id": "44444444-5555-6666-7777-888888888888",
                "name": "NRT Behavioral Threshold Detection",
                "description": "Detects brute force bursts across multiple attempts.",
                "severity": "Medium",
                "kind": "NRT",
                "tactics": ["CredentialAccess"],
                "relevantTechniques": ["T1110"],
                "query": (
                    "DeviceLogonEvents\n"
                    "| where ActionType == 'LogonFailed'\n"
                    "| summarize StartTime = min(TimeGenerated), EndTime = max(TimeGenerated), "
                    "FailedCount = count() by AccountName, DeviceId, RemoteIP\n"
                    "| where FailedCount > 5"
                ),
                "entityMappings": [
                    {
                        "entityType": "Host",
                        "fieldMappings": [
                            {"identifier": "AzureID", "columnName": "DeviceId"}
                        ],
                    }
                ],
            },
        )
        rewritten, changed, notes = rewrite_cosmetic_nrt_summarize(
            "DeviceLogonEvents\n| summarize FailedCount = count() by AccountName\n| where FailedCount > 5"
        )
        assert changed is False
        assert notes == []

        doc = build_xdr_document(rule_path, sol, {})
        query_text = doc["properties"]["queryCondition"]["queryText"]
        conv = doc["contentProvenance"]["conversion"]
        assert doc["properties"]["schedule"] == {"frequency": "PT1H", "queryPeriod": "PT4H"}
        assert "| summarize" in query_text.lower()
        assert "| where FailedCount > 5" in query_text
        assert any("nrt_behavioral_summarize_fallback_pt1h" in n for n in conv["notes"])
        assert conv["errors"] == []
        assert conv["status"] == "converted"


class TestSampleDataCatalogValidator:
    def test_sample_data_validator_catalog_routing(self) -> None:
        node = shutil.which("node")
        if not node:
            pytest.skip("Node.js is not available")
        repo_root = Path(__file__).resolve().parents[3]
        checker_js = repo_root / ".script" / "utils" / "sampleDataCheckers" / "sampleDataCheckers.js"
        script = f"""
import assert from 'node:assert';
import * as checker from {json.dumps(checker_js.as_uri())};

// 1. Catalog path detection
assert.strictEqual(checker.isTableCatalogSampleDataPath('Sample Data/Tables/Syslog/base-event.json'), true);
assert.strictEqual(checker.isTableCatalogSampleDataPath('Sample Data/Tables/Syslog/metadata.json'), true);
assert.strictEqual(checker.isTableCatalogSampleDataPath('Sample Data/Syslog_Sample.json'), false);

// 2. Valid base-event.json (single JSON object + allowed example/sanitized emails)
const validBaseEvent = {{
  TimeGenerated: '2025-01-01T00:00:00Z',
  UserPrincipalName: 'user@example.com',
  AdminEmail: 'admin@contoso.com',
  SanitizedEmail: 'sanitized@sanitized.com'
}};
assert.strictEqual(
  checker.isValidTableCatalogSampleData(validBaseEvent, 'Sample Data/Tables/AuditLogs/base-event.json'),
  true
);

// 3. Valid metadata.json (catalog metadata structure)
const validMetadata = {{
  tableName: 'AuditLogs',
  columns: [{{ name: 'TimeGenerated', type: 'datetime' }}, {{ name: 'UserPrincipalName', type: 'string' }}],
  contact: 'user@example.org'
}};
assert.strictEqual(
  checker.isValidTableCatalogSampleData(validMetadata, 'Sample Data/Tables/AuditLogs/metadata.json'),
  true
);

// 4. Reject unsanitized private email in catalog file
const unsanitizedCatalog = {{
  TimeGenerated: '2025-01-01T00:00:00Z',
  UserPrincipalName: 'real.person@corp-internal.net'
}};
assert.throws(
  () => checker.isValidTableCatalogSampleData(unsanitizedCatalog, 'Sample Data/Tables/AuditLogs/base-event.json'),
  (err) => err && /email/i.test(err.message)
);

// 5. Reject array or empty object in catalog file
assert.throws(
  () => checker.isValidTableCatalogSampleData([], 'Sample Data/Tables/AuditLogs/base-event.json'),
  (err) => err && /non-empty JSON object/i.test(err.message)
);
assert.throws(
  () => checker.isValidTableCatalogSampleData({{}}, 'Sample Data/Tables/AuditLogs/base-event.json'),
  (err) => err && /non-empty JSON object/i.test(err.message)
);

// 6. Reject metadata.json missing required catalog metadata fields
assert.throws(
  () => checker.isValidTableCatalogSampleData({{ foo: 'bar' }}, 'Sample Data/Tables/AuditLogs/metadata.json'),
  (err) => err && /metadata\\.json/i.test(err.message)
);

// 7. Existing strict validation preserved for non-catalog Sample Data files
assert.doesNotThrow(() => checker.isValidSampleData([{{ email: 'sanitized@sanitized.com' }}]));
assert.throws(
  () => checker.isValidSampleData({{ email: 'sanitized@sanitized.com' }}),
  (err) => err && /array/i.test(err.message)
);
assert.throws(
  () => checker.isValidSampleData([{{ email: 'user@example.com' }}]),
  (err) => err && /sanitized@sanitized\\.com/i.test(err.message)
);
console.log('ALL_SAMPLE_DATA_CHECKS_PASSED');
"""
        proc = subprocess.run(
            [node, "--input-type=module", "-e", script],
            capture_output=True,
            text=True,
            check=False,
        )
        assert proc.returncode == 0, f"stderr: {proc.stderr}\nstdout: {proc.stdout}"
        assert "ALL_SAMPLE_DATA_CHECKS_PASSED" in proc.stdout
