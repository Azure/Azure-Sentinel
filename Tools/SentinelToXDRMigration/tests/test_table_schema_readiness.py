from __future__ import annotations

import io
import json
from pathlib import Path
from typing import Any
from unittest.mock import patch
import urllib.error

from solution_manager.qualification import evaluate_qualification_promotion_gate
from solution_manager.qualification.pr_applicability import determine_pr_applicability
from solution_manager.qualification.pr_check_runner import (
    SUBSTITUTABLE_MANUAL_CHECK_MAP,
    run_pr_qualification_checks,
)
from solution_manager.qualification.runtime import (
    build_graph_hunting_schema_tables_url,
    build_graph_run_hunting_query_url,
    collect_live_table_schema_readiness_evidence,
    fetch_arm_table_schema,
    fetch_graph_hunting_schema,
    fetch_graph_hunting_schema_tables,
    run_workspace_hunting_query_get,
)
from solution_manager.qualification.table_schema_readiness import (
    discover_solution_tables,
    evaluate_qual_tbl_01,
    evaluate_qual_tbl_02,
    evaluate_qual_tbl_03,
    evaluate_val_tbl_01,
    evaluate_val_tbl_02,
    evaluate_val_tbl_03,
    is_meaningful_description,
    resolve_table_schema_blocking_mode,
)


def _write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def _build_minimal_solution(
    sol_root: Path,
    *,
    version: str = "3.2.2",
    data_connectors: list[str] | None = None,
) -> None:
    _write_json(
        sol_root / "SolutionMetadata.json",
        {
            "publisherId": "azuresentinel",
            "offerId": "sentinel-custom-table-sol",
            "version": version,
            "support": {
                "tier": "Microsoft",
                "name": "Microsoft Corporation",
                "link": "https://aka.ms/sentinel-support",
            },
        },
    )
    data_doc: dict[str, Any] = {
        "Name": sol_root.name,
        "Author": "Microsoft",
        "Logo": '<img src="https://aka.ms/sentinel-logo.svg" width="75px" height="75px">',
        "Description": "Custom table solution description with https://aka.ms/sentinel-docs link.",
        "Version": version,
    }
    if data_connectors is not None:
        data_doc["Data Connectors"] = data_connectors
    _write_json(sol_root / "Data" / "Solution_CustomTableSol.json", data_doc)
    (sol_root / "ReleaseNotes.md").write_text(
        f"| **Version** | **Date Modified (DD-MM-YYYY)** | **Change History** |\n"
        f"|---|---|---|\n"
        f"| {version} | 19-10-2026 | Release {version}. |\n",
        encoding="utf-8",
    )
    pkg_dir = sol_root / "Package"
    pkg_dir.mkdir(parents=True, exist_ok=True)
    (pkg_dir / f"{version}.zip").write_bytes(b"PK\x03\x04dummy-zip")
    _write_json(
        pkg_dir / "createUiDefinition.json",
        {
            "$schema": "https://schema.management.azure.com/schemas/0.1.2-preview/CreateUIDefinition.MultiVm.json#",
            "handler": "Microsoft.Azure.CreateUIDef",
            "version": "0.1.2-preview",
            "parameters": {
                "basics": [{"name": "workspace", "type": "Microsoft.Solutions.ArmApiControl"}],
                "steps": [{"name": "dataconnectors", "label": "Data Connectors", "elements": []}],
                "outputs": {},
            },
        },
    )


def test_is_meaningful_description_rejects_placeholders_and_self_names() -> None:
    ok, _ = is_meaningful_description(
        "Stores 1Password sign-in and item usage events ingested via CCP.",
        entity_name="OnePasswordEventLogs_CL",
    )
    assert ok is True

    # Short but distinct acronym descriptions are allowed
    ok_short, _ = is_meaningful_description("URL", entity_name="TargetEndpoint")
    assert ok_short is True

    # Placeholders are rejected
    for bad in ("", "   ", "TODO", "TBD", "N/A", "description", "[parameters('tableDesc')]"):
        valid, _ = is_meaningful_description(bad, entity_name="CustomCol")
        assert valid is False, f"Expected {bad!r} to be rejected"

    # Repeating the item name (or normalized tokens) is rejected
    valid_same, _ = is_meaningful_description("OnePasswordEventLogs_CL", entity_name="OnePasswordEventLogs_CL")
    assert valid_same is False
    valid_norm, _ = is_meaningful_description("one password event logs", entity_name="OnePasswordEventLogs_CL")
    assert valid_norm is False


def test_discover_solution_tables_supports_bare_root_and_nested_package_layouts(tmp_path: Path) -> None:
    sol = tmp_path / "OnePasswordLikeSol"
    _build_minimal_solution(sol, data_connectors=["Data Connectors/1Password_ccpv2/1Password_tables.json"])

    # 1. Bare root resource object (1Password_tables.json style)
    bare_table = {
        "name": "OnePasswordEventLogs_CL",
        "apiVersion": "2022-10-01",
        "type": "Microsoft.OperationalInsights/workspaces/tables",
        "properties": {
            "schema": {
                "name": "OnePasswordEventLogs_CL",
                "description": "1Password audit and sign-in events collected via the polling CCP connector.",
                "columns": [
                    {
                        "name": "TimeGenerated",
                        "type": "datetime",
                        "description": "The timestamp (UTC) when the 1Password event was generated.",
                    },
                    {
                        "name": "EventUuid",
                        "type": "string",
                        "description": "Unique identifier assigned to the 1Password event.",
                    },
                    {
                        "name": "TargetUserEmail",
                        "type": "string",
                        "description": "Email address of the user affected by the event.",
                    },
                ],
            }
        },
    }
    _write_json(sol / "Data Connectors" / "1Password_ccpv2" / "1Password_tables.json", bare_table)

    # 2. Packaged mainTemplate with nested contentTemplates -> properties.mainTemplate.resources[]
    _write_json(
        sol / "Package" / "mainTemplate.json",
        {
            "$schema": "https://schema.management.azure.com/schemas/2019-04-01/deploymentTemplate.json#",
            "contentVersion": "1.0.0.0",
            "resources": [
                {
                    "type": "Microsoft.OperationalInsights/workspaces/providers/contentTemplates",
                    "apiVersion": "2023-04-01-preview",
                    "name": "conn-template",
                    "properties": {
                        "mainTemplate": {
                            "resources": [bare_table],
                        }
                    },
                }
            ],
        },
    )

    inventory = discover_solution_tables(sol)
    assert inventory.has_any_custom_tables is True
    assert [t.table_name for t in inventory.source_tables] == ["OnePasswordEventLogs_CL"]
    assert len(inventory.source_tables) == 1
    assert len(inventory.packaged_tables) == 1

    # Strict evaluations should all pass
    s1, _ = evaluate_val_tbl_01(inventory, enforce_blocking=True)
    s2, _ = evaluate_val_tbl_02(inventory, enforce_blocking=True)
    s3, _ = evaluate_val_tbl_03(inventory, enforce_blocking=True)
    assert s1 == "PASS"
    assert s2 == "PASS"
    assert s3 == "PASS"


def test_strict_blocking_by_default_for_val_and_qual_tbl_checks(tmp_path: Path) -> None:
    sol = tmp_path / "UndocumentedTableSol"
    _build_minimal_solution(sol, data_connectors=["Data Connectors/Vendor_tables.json"])

    # Source table missing table description and missing 1 column description, and omitted from Package/mainTemplate.json
    undoc_table = {
        "name": "VendorAudit_CL",
        "type": "Microsoft.OperationalInsights/workspaces/tables",
        "apiVersion": "2022-10-01",
        "properties": {
            "schema": {
                "name": "VendorAudit_CL",
                "description": "",
                "columns": [
                    {"name": "TimeGenerated", "type": "datetime"},
                    {"name": "ActorName", "type": "string"},
                ],
            }
        },
    }
    _write_json(sol / "Data Connectors" / "Vendor_tables.json", undoc_table)
    _write_json(
        sol / "Package" / "mainTemplate.json",
        {
            "$schema": "https://schema.management.azure.com/schemas/2019-04-01/deploymentTemplate.json#",
            "contentVersion": "1.0.0.0",
            "resources": [
                {
                    "type": "Microsoft.OperationalInsights/workspaces/providers/contentPackages",
                    "apiVersion": "2023-04-01-preview",
                    "name": "pkg-meta",
                    "properties": {"version": "3.2.2", "contentId": "sentinel-custom-table-sol"},
                }
            ],
        },
    )

    # Default mode is strictly blocking (default_blocking=True) -> FAIL
    assert resolve_table_schema_blocking_mode(None, None) is True
    res_default = run_pr_qualification_checks(sol, run_qualification=False)
    for cid in ("VAL-TBL-01", "VAL-TBL-02", "VAL-TBL-03"):
        chk = res_default["checksById"][cid]
        assert chk["applicable"] is True
        assert chk["status"] == "FAIL"
    assert res_default["validationStatus"] == "Validation Failed"

    # Qualification checks QUAL-TBL-01..03 also strictly block by default when live evidence is missing
    res_qual_default = run_pr_qualification_checks(
        sol,
        run_qualification=True,
        qualification_evidence={"deployment": {"status": "passed"}},
    )
    for cid in ("QUAL-TBL-01", "QUAL-TBL-02", "QUAL-TBL-03"):
        chk = res_qual_default["checksById"][cid]
        assert chk["applicable"] is True
        assert chk["status"] == "FAIL"


def test_microsoft_standard_table_config_is_exempt_from_custom_table_gates(tmp_path: Path) -> None:
    sol = tmp_path / "StandardTableConfigOnlySol"
    _build_minimal_solution(sol, data_connectors=["Data Connectors/StandardTableRetention.json"])

    # Microsoft-standard table config setting only retention/plan without custom schema columns or _CL suffix
    std_table_config = {
        "type": "Microsoft.OperationalInsights/workspaces/tables",
        "apiVersion": "2022-10-01",
        "name": "[concat(parameters('workspace'), '/SecurityEvent')]",
        "properties": {
            "plan": "Analytics",
            "retentionInDays": 90,
            "totalRetentionInDays": 180,
        },
    }
    _write_json(sol / "Data Connectors" / "StandardTableRetention.json", std_table_config)
    _write_json(
        sol / "Package" / "mainTemplate.json",
        {
            "$schema": "https://schema.management.azure.com/schemas/2019-04-01/deploymentTemplate.json#",
            "contentVersion": "1.0.0.0",
            "resources": [std_table_config],
        },
    )

    inv = discover_solution_tables(sol)
    assert inv.has_any_custom_tables is False
    assert len(inv.standard_table_configs) == 2

    app = determine_pr_applicability(sol)
    for cid in ("VAL-TBL-01", "VAL-TBL-02", "VAL-TBL-03", "QUAL-TBL-01", "QUAL-TBL-02", "QUAL-TBL-03"):
        assert app["checksById"][cid]["applicable"] is False
        assert "Microsoft-standard table configuration" in app["checksById"][cid]["applicabilityReason"]


def test_preservation_drift_and_unresolved_arm_expressions_fail_val_tbl_03(tmp_path: Path) -> None:
    sol = tmp_path / "PreservationDriftSol"
    _build_minimal_solution(sol, data_connectors=["Data Connectors/Custom_tables.json"])

    src_table = {
        "name": "AcmeSecurity_CL",
        "type": "Microsoft.OperationalInsights/workspaces/tables",
        "apiVersion": "2022-10-01",
        "properties": {
            "schema": {
                "name": "AcmeSecurity_CL",
                "description": "Acme security telemetry events collected via REST API.",
                "columns": [
                    {"name": "TimeGenerated", "type": "datetime"},
                    {"name": "EventSeverity", "type": "string", "description": "Severity level assigned by Acme."},
                    {"name": "SourceHost", "type": "string", "description": "Hostname of the originating endpoint."},
                ],
            }
        },
    }
    # Packaged table has drifted table description, drifted column description, and dropped SourceHost column
    pkg_table_drifted = {
        "name": "AcmeSecurity_CL",
        "type": "Microsoft.OperationalInsights/workspaces/tables",
        "apiVersion": "2022-10-01",
        "properties": {
            "schema": {
                "name": "AcmeSecurity_CL",
                "description": "Different packaged table description after packaging drift.",
                "columns": [
                    {"name": "TimeGenerated", "type": "datetime"},
                    {"name": "EventSeverity", "type": "string", "description": "Drifted column description."},
                ],
            }
        },
    }
    _write_json(sol / "Data Connectors" / "Custom_tables.json", src_table)
    _write_json(
        sol / "Package" / "mainTemplate.json",
        {
            "$schema": "https://schema.management.azure.com/schemas/2019-04-01/deploymentTemplate.json#",
            "contentVersion": "1.0.0.0",
            "resources": [pkg_table_drifted],
        },
    )

    inv = discover_solution_tables(sol)
    s3, obs3 = evaluate_val_tbl_03(inv, enforce_blocking=True)
    assert s3 == "FAIL"
    assert "Table 'AcmeSecurity_CL' schema.description drift between" in obs3
    assert "Table 'AcmeSecurity_CL' column 'EventSeverity' description drift" in obs3
    assert "Table 'AcmeSecurity_CL' column 'SourceHost' missing from packaged" in obs3

    # Unresolved ARM expressions on both source and package must NOT be treated as a matching value
    unresolved_table = {
        "name": "AcmeSecurity_CL",
        "type": "Microsoft.OperationalInsights/workspaces/tables",
        "apiVersion": "2022-10-01",
        "properties": {
            "schema": {
                "name": "AcmeSecurity_CL",
                "description": "[concat(parameters('prefix'), ' description')]",
                "columns": [
                    {"name": "TimeGenerated", "type": "datetime"},
                    {
                        "name": "EventSeverity",
                        "type": "string",
                        "description": "[variables('missingVar')]",
                    },
                ],
            }
        },
    }
    _write_json(sol / "Data Connectors" / "Custom_tables.json", unresolved_table)
    _write_json(
        sol / "Package" / "mainTemplate.json",
        {
            "$schema": "https://schema.management.azure.com/schemas/2019-04-01/deploymentTemplate.json#",
            "contentVersion": "1.0.0.0",
            "resources": [unresolved_table],
        },
    )
    inv_unresolved = discover_solution_tables(sol)
    s1_u, obs1_u = evaluate_val_tbl_01(inv_unresolved, enforce_blocking=True)
    s2_u, obs2_u = evaluate_val_tbl_02(inv_unresolved, enforce_blocking=True)
    s3_u, obs3_u = evaluate_val_tbl_03(inv_unresolved, enforce_blocking=True)
    assert s1_u == "FAIL"
    assert "unresolved_arm_expression" in obs1_u
    assert s2_u == "FAIL"
    assert "unresolved_arm_expression" in obs2_u
    assert s3_u == "FAIL"
    assert "unresolved_arm_expression" in obs3_u


def test_qual_tbl_evaluators_reject_simulated_wrong_workspace_incomplete_pagination_and_auth_errors(
    tmp_path: Path,
) -> None:
    sol = tmp_path / "QualLiveSol"
    _build_minimal_solution(sol, data_connectors=["Data Connectors/Acme_tables.json"])
    table_def = {
        "name": "AcmeEvents_CL",
        "type": "Microsoft.OperationalInsights/workspaces/tables",
        "apiVersion": "2022-10-01",
        "properties": {
            "schema": {
                "name": "AcmeEvents_CL",
                "description": "Acme security events ingested into Log Analytics.",
                "columns": [
                    {
                        "name": "TimeGenerated",
                        "type": "datetime",
                        "description": "The timestamp (UTC) when the Acme event was generated.",
                    },
                    {"name": "EventId", "type": "string", "description": "Unique event identifier."},
                    {"name": "ActorUpn", "type": "string", "description": "User principal name of the actor."},
                ],
            }
        },
    }
    _write_json(sol / "Data Connectors" / "Acme_tables.json", table_def)
    _write_json(
        sol / "Package" / "mainTemplate.json",
        {
            "$schema": "https://schema.management.azure.com/schemas/2019-04-01/deploymentTemplate.json#",
            "contentVersion": "1.0.0.0",
            "resources": [table_def],
        },
    )
    inv = discover_solution_tables(sol)
    ws_id = "8fb6e2d6-1b0a-4d0b-9d9f-9f3e2a5c7b21"
    ws_res_id = (
        "/subscriptions/00000000-0000-0000-0000-000000000001"
        "/resourceGroups/rg-test/providers/Microsoft.OperationalInsights/workspaces/la-test"
    )

    # 1. Positive case: complete live ARM, Graph hunting schema tables, and Graph hunting query receipts
    good_evidence: dict[str, Any] = {
        "target": {
            "workspaceId": ws_id,
            "workspaceResourceId": ws_res_id,
        },
        "tableSchemaReadiness": {
            "target": {
                "workspaceId": ws_id,
                "workspaceResourceId": ws_res_id,
            },
            "armTables": {
                "AcmeEvents_CL": {
                    "ok": True,
                    "httpStatus": 200,
                    "requestUrl": f"https://management.azure.com{ws_res_id}/tables/AcmeEvents_CL?api-version=2025-02-01",
                    "workspaceResourceId": ws_res_id,
                    "tableDescription": "Acme security events ingested into Log Analytics.",
                    "columns": [
                        {
                            "name": "TimeGenerated",
                            "type": "datetime",
                            "description": "The timestamp (UTC) when the Acme event was generated.",
                        },
                        {"name": "EventId", "type": "string", "description": "Unique event identifier."},
                        {"name": "ActorUpn", "type": "string", "description": "User principal name of the actor."},
                    ],
                }
            },
            "huntingSchemaTables": {
                "ok": True,
                "httpStatus": 200,
                "endpoint": f"https://graph.microsoft.com/beta/security/getHuntingSchemaTables(workspaceId={ws_id})",
                "workspaceId": ws_id,
                "workspaceIdUnquoted": True,
                "complete": True,
                "paginationComplete": True,
                "hasUnfetchedPages": False,
                "tables": [
                    {
                        "name": "AcmeEvents_CL",
                        "description": "Acme security events ingested into Log Analytics.",
                        "columns": [
                            {
                                "name": "TimeGenerated",
                                "description": "The timestamp (UTC) when the Acme event was generated.",
                            },
                            {"name": "EventId", "description": "Unique event identifier."},
                            {"name": "ActorUpn", "description": "User principal name of the actor."},
                        ],
                    }
                ],
            },
            "huntingQuery": {
                "AcmeEvents_CL": {
                    "ok": True,
                    "httpStatus": 200,
                    "requestUrl": f"https://graph.microsoft.com/beta/security/getRunHuntingQuery(query='AcmeEvents_CL%20%7C%20take%201',timespan='P1D',workspaceId={ws_id})",
                    "workspaceId": ws_id,
                    "workspaceIdUnquoted": True,
                    "query": "AcmeEvents_CL | take 1",
                    "schema": [
                        {"name": "TimeGenerated", "type": "DateTime"},
                        {"name": "EventId", "type": "String"},
                        {"name": "ActorUpn", "type": "String"},
                    ],
                }
            },
        },
    }
    q1, _ = evaluate_qual_tbl_01(inv, good_evidence, enforce_blocking=True)
    q2, _ = evaluate_qual_tbl_02(inv, good_evidence, enforce_blocking=True)
    q3, _ = evaluate_qual_tbl_03(inv, good_evidence, enforce_blocking=True)
    assert (q1, q2, q3) == ("PASS", "PASS", "PASS")

    # Verify per-check manual review substitution is recorded as eligible but NOT active until agreed
    full_res = run_pr_qualification_checks(sol, run_qualification=True, qualification_evidence=good_evidence)
    for cid in ("QUAL-TBL-01", "QUAL-TBL-02", "QUAL-TBL-03"):
        chk = full_res["checksById"][cid]
        assert chk["status"] == "PASS"
        sub = chk.get("manualReviewSubstitution")
        assert isinstance(sub, dict)
        assert sub["substituted"] is False
        assert sub["eligibleForPerCheckSubstitution"] is True
        assert sub["manualCheckId"] == SUBSTITUTABLE_MANUAL_CHECK_MAP[cid]["manualCheckId"]
    assert full_res["SatisfiedManualChecksByQualificationEvidence"] == []
    assert len(full_res["EligibleManualCheckSubstitutionsByQualificationEvidence"]) >= 3

    # 2. Simulated receipt -> rejected
    sim_evidence = json.loads(json.dumps(good_evidence))
    sim_evidence["tableSchemaReadiness"]["armTables"]["AcmeEvents_CL"]["simulated"] = True
    sim_evidence["tableSchemaReadiness"]["huntingSchemaTables"]["mode"] = "simulated"
    sim_evidence["tableSchemaReadiness"]["huntingQuery"]["AcmeEvents_CL"]["isSimulated"] = True
    s_q1, obs_q1 = evaluate_qual_tbl_01(inv, sim_evidence, enforce_blocking=True)
    s_q2, obs_q2 = evaluate_qual_tbl_02(inv, sim_evidence, enforce_blocking=True)
    s_q3, obs_q3 = evaluate_qual_tbl_03(inv, sim_evidence, enforce_blocking=True)
    assert (s_q1, s_q2, s_q3) == ("FAIL", "FAIL", "FAIL")
    assert "simulated/dry-run; simulated evidence cannot qualify as PASS" in obs_q1
    assert "simulated/dry-run; simulated evidence cannot qualify as PASS" in obs_q2
    assert "simulated/dry-run; simulated evidence cannot qualify as PASS" in obs_q3

    # 3. Wrong target workspace -> rejected
    wrong_ws_evidence = json.loads(json.dumps(good_evidence))
    wrong_ws_evidence["tableSchemaReadiness"]["armTables"]["AcmeEvents_CL"]["workspaceResourceId"] = (
        "/subscriptions/00000000-0000-0000-0000-000000000001"
        "/resourceGroups/rg-other/providers/Microsoft.OperationalInsights/workspaces/la-other"
    )
    wrong_ws_evidence["tableSchemaReadiness"]["huntingSchemaTables"]["workspaceId"] = (
        "11111111-2222-3333-4444-555555555555"
    )
    wrong_ws_evidence["tableSchemaReadiness"]["huntingQuery"]["AcmeEvents_CL"]["workspaceId"] = (
        "11111111-2222-3333-4444-555555555555"
    )
    w_q1, w_obs1 = evaluate_qual_tbl_01(inv, wrong_ws_evidence, enforce_blocking=True)
    w_q2, w_obs2 = evaluate_qual_tbl_02(inv, wrong_ws_evidence, enforce_blocking=True)
    w_q3, w_obs3 = evaluate_qual_tbl_03(inv, wrong_ws_evidence, enforce_blocking=True)
    assert (w_q1, w_q2, w_q3) == ("FAIL", "FAIL", "FAIL")
    assert "does not match approved target" in w_obs1
    assert "does not match approved target" in w_obs2
    assert "does not match approved target" in w_obs3

    # 4. Incomplete pagination -> rejected
    inc_page_evidence = json.loads(json.dumps(good_evidence))
    inc_page_evidence["tableSchemaReadiness"]["huntingSchemaTables"]["complete"] = False
    inc_page_evidence["tableSchemaReadiness"]["huntingSchemaTables"]["hasUnfetchedPages"] = True
    ip_q2, ip_obs2 = evaluate_qual_tbl_02(inv, inc_page_evidence, enforce_blocking=True)
    assert ip_q2 == "FAIL"
    assert "incomplete_hunting_schema_pagination" in ip_obs2

    # 5. Provider/authorization failures -> rejected
    auth_fail_evidence = json.loads(json.dumps(good_evidence))
    auth_fail_evidence["tableSchemaReadiness"]["armTables"]["AcmeEvents_CL"] = {
        "ok": False,
        "httpStatus": 403,
        "error": "AuthorizationFailed",
    }
    auth_fail_evidence["tableSchemaReadiness"]["huntingSchemaTables"] = {
        "ok": False,
        "httpStatus": 403,
        "error": "Authorization_RequestDenied",
    }
    auth_fail_evidence["tableSchemaReadiness"]["huntingQuery"]["AcmeEvents_CL"] = {
        "ok": False,
        "httpStatus": 401,
        "error": "InvalidAuthenticationToken",
    }
    a_q1, a_obs1 = evaluate_qual_tbl_01(inv, auth_fail_evidence, enforce_blocking=True)
    a_q2, a_obs2 = evaluate_qual_tbl_02(inv, auth_fail_evidence, enforce_blocking=True)
    a_q3, a_obs3 = evaluate_qual_tbl_03(inv, auth_fail_evidence, enforce_blocking=True)
    assert (a_q1, a_q2, a_q3) == ("FAIL", "FAIL", "FAIL")
    assert "authorization error" in a_obs1
    assert "authorization error" in a_obs2
    assert "authorization error" in a_obs3

    # 6. Wrong/missing table or column evidence (HTTP 200 alone without matching columns/descriptions) -> rejected
    missing_fields_evidence = json.loads(json.dumps(good_evidence))
    missing_fields_evidence["tableSchemaReadiness"]["armTables"]["AcmeEvents_CL"]["columns"] = [
        {
            "name": "TimeGenerated",
            "type": "datetime",
            "description": "The timestamp (UTC) when the Acme event was generated.",
        },
        {"name": "EventId", "type": "string", "description": "Unique event identifier."},
        # ActorUpn missing
    ]
    missing_fields_evidence["tableSchemaReadiness"]["huntingSchemaTables"]["tables"][0]["columns"] = [
        {
            "name": "TimeGenerated",
            "description": "The timestamp (UTC) when the Acme event was generated.",
        },
        {"name": "EventId", "description": "Unique event identifier."},
        {"name": "ActorUpn", "description": ""},  # empty description in AH schema
    ]
    missing_fields_evidence["tableSchemaReadiness"]["huntingQuery"]["AcmeEvents_CL"]["schema"] = [
        {"name": "TimeGenerated", "type": "DateTime"},
        {"name": "EventId", "type": "String"},
        # ActorUpn missing from query schema
    ]
    m_q1, m_obs1 = evaluate_qual_tbl_01(inv, missing_fields_evidence, enforce_blocking=True)
    m_q2, m_obs2 = evaluate_qual_tbl_02(inv, missing_fields_evidence, enforce_blocking=True)
    m_q3, m_obs3 = evaluate_qual_tbl_03(inv, missing_fields_evidence, enforce_blocking=True)
    assert (m_q1, m_q2, m_q3) == ("FAIL", "FAIL", "FAIL")
    assert "missing_in_live_arm_schema" in m_obs1
    assert "ActorUpn (empty)" in m_obs2
    assert "missing expected custom column(s): ActorUpn" in m_obs3


def test_collect_live_table_schema_readiness_evidence_wires_arm_and_graph_endpoints(
    tmp_path: Path,
) -> None:
    sol = tmp_path / "LiveCollectorSol"
    _build_minimal_solution(sol, data_connectors=["Data Connectors/Acme_tables.json"])
    table_def = {
        "name": "AcmeEvents_CL",
        "type": "Microsoft.OperationalInsights/workspaces/tables",
        "apiVersion": "2022-10-01",
        "properties": {
            "schema": {
                "name": "AcmeEvents_CL",
                "description": "Acme security events ingested into Log Analytics.",
                "columns": [
                    {
                        "name": "TimeGenerated",
                        "type": "datetime",
                        "description": "The timestamp (UTC) when the Acme event was generated.",
                    },
                    {"name": "EventId", "type": "string", "description": "Unique event identifier."},
                ],
            }
        },
    }
    _write_json(sol / "Data Connectors" / "Acme_tables.json", table_def)
    _write_json(
        sol / "Package" / "mainTemplate.json",
        {
            "$schema": "https://schema.management.azure.com/schemas/2019-04-01/deploymentTemplate.json#",
            "contentVersion": "1.0.0.0",
            "resources": [table_def],
        },
    )

    ws_id = "8fb6e2d6-1b0a-4d0b-9d9f-9f3e2a5c7b21"
    ws_res_id = (
        "/subscriptions/00000000-0000-0000-0000-000000000001"
        "/resourceGroups/rg-test/providers/Microsoft.OperationalInsights/workspaces/la-test"
    )

    def fake_urlopen(req: Any, timeout: int = 60) -> _FakeHttpResponse:
        url = req.full_url
        if url.startswith("https://management.azure.com/"):
            return _FakeHttpResponse(
                {
                    "name": "AcmeEvents_CL",
                    "properties": {
                        "schema": {
                            "name": "AcmeEvents_CL",
                            "description": "Acme security events ingested into Log Analytics.",
                            "columns": [
                                {
                                    "name": "TimeGenerated",
                                    "type": "datetime",
                                    "description": "The timestamp (UTC) when the Acme event was generated.",
                                },
                                {"name": "EventId", "type": "string", "description": "Unique event identifier."},
                            ],
                        }
                    },
                }
            )
        if url.startswith("https://graph.microsoft.com/beta/security/getHuntingSchemaTables"):
            return _FakeHttpResponse(
                {
                    "value": [
                        {
                            "name": "AcmeEvents_CL",
                            "description": "Acme security events ingested into Log Analytics.",
                            "columns": [
                                {
                                    "name": "TimeGenerated",
                                    "description": "The timestamp (UTC) when the Acme event was generated.",
                                },
                                {"name": "EventId", "description": "Unique event identifier."},
                            ],
                        }
                    ]
                }
            )
        if url.startswith("https://graph.microsoft.com/beta/security/getRunHuntingQuery"):
            return _FakeHttpResponse(
                {
                    "schema": [
                        {"name": "TimeGenerated", "type": "DateTime"},
                        {"name": "EventId", "type": "String"},
                    ],
                    "results": [],
                }
            )
        return _FakeHttpResponse({"tables": [{"name": "AcmeEvents_CL"}]})

    with patch("urllib.request.urlopen", side_effect=fake_urlopen):
        receipt = collect_live_table_schema_readiness_evidence(
            sol,
            workspace_resource_id=ws_res_id,
            workspace_id=ws_id,
            arm_token="dummy-arm-token",
            graph_token="dummy-graph-token",
        )

    assert receipt["status"] == "passed"
    assert receipt["verified"] is True
    assert receipt["target"]["workspaceId"] == ws_id
    assert receipt["target"]["workspaceResourceId"] == ws_res_id
    assert receipt["armTableReadback"]["ok"] is True
    assert receipt["armTableReadback"]["tables"][0]["ok"] is True
    assert receipt["huntingSchema"]["ok"] is True
    assert receipt["huntingSchema"]["complete"] is True
    assert receipt["workspaceHuntingQuery"]["ok"] is True
    assert receipt["workspaceHuntingQuery"]["queries"][0]["ok"] is True


def test_solution_without_custom_tables_marks_tbl_checks_not_applicable(tmp_path: Path) -> None:
    sol = tmp_path / "NoCustomTablesSol"
    _build_minimal_solution(sol)
    _write_json(
        sol / "Package" / "mainTemplate.json",
        {
            "$schema": "https://schema.management.azure.com/schemas/2019-04-01/deploymentTemplate.json#",
            "contentVersion": "1.0.0.0",
            "resources": [],
        },
    )
    app = determine_pr_applicability(sol)
    for cid in ("VAL-TBL-01", "VAL-TBL-02", "VAL-TBL-03", "QUAL-TBL-01", "QUAL-TBL-02", "QUAL-TBL-03"):
        assert app["checksById"][cid]["applicable"] is False


class _FakeHttpResponse:
    def __init__(self, payload: dict[str, Any], status: int = 200) -> None:
        self._bytes = json.dumps(payload).encode("utf-8")
        self.status = status

    def read(self) -> bytes:
        return self._bytes

    def __enter__(self) -> "_FakeHttpResponse":
        return self

    def __exit__(self, exc_type: Any, exc: Any, tb: Any) -> bool:
        return False


def test_graph_beta_odata_url_builders_and_helpers() -> None:
    ws_guid = "8fb6e2d6-1b0a-4d0b-9d9f-9f3e2a5c7b21"

    # workspaceId must be an unquoted Edm.Guid
    tables_url = build_graph_hunting_schema_tables_url(ws_guid)
    assert tables_url == (
        "https://graph.microsoft.com/beta/security/getHuntingSchemaTables"
        "(workspaceId=8fb6e2d6-1b0a-4d0b-9d9f-9f3e2a5c7b21)"
    )

    # Single quotes in KQL must be doubled first, then percent-encoded with %20 for spaces
    query_url = build_graph_run_hunting_query_url(
        "OnePasswordEventLogs_CL | where Action == 'signin' | take 1",
        workspace_id=ws_guid,
        timespan="P1D",
    )
    assert "workspaceId=8fb6e2d6-1b0a-4d0b-9d9f-9f3e2a5c7b21" in query_url
    assert "timespan='P1D'" in query_url
    assert "%27%27signin%27%27" in query_url
    assert "+" not in query_url

    with patch(
        "urllib.request.urlopen",
        return_value=_FakeHttpResponse({"tables": [{"name": "AlertInfo", "description": "Alerts table"}]}),
    ):
        schema_res = fetch_graph_hunting_schema("dummy-token")
    assert schema_res["ok"] is True
    assert len(schema_res["tables"]) == 1

    with patch(
        "urllib.request.urlopen",
        return_value=_FakeHttpResponse(
            {
                "value": [
                    {
                        "name": "OnePasswordEventLogs_CL",
                        "description": "1Password audit events.",
                        "columns": [{"name": "EventUuid", "description": "Unique event ID."}],
                    }
                ]
            }
        ),
    ):
        ws_tables_res = fetch_graph_hunting_schema_tables("dummy-token", workspace_id=ws_guid)
    assert ws_tables_res["ok"] is True
    assert len(ws_tables_res["tables"]) == 1

    with patch(
        "urllib.request.urlopen",
        return_value=_FakeHttpResponse(
            {
                "schema": [
                    {"name": "TimeGenerated", "type": "DateTime"},
                    {"name": "EventUuid", "type": "String"},
                ],
                "results": [{"TimeGenerated": "2026-10-19T00:00:00Z", "EventUuid": "abc-123"}],
            }
        ),
    ):
        query_res = run_workspace_hunting_query_get(
            "OnePasswordEventLogs_CL | take 1",
            "dummy-token",
            workspace_id=ws_guid,
        )
    assert query_res["ok"] is True
    assert query_res["rowCount"] == 1
    assert len(query_res["schema"]) == 2


def test_fetch_arm_table_schema_falls_back_to_2022_10_01_and_extracts_descriptions() -> None:
    ws_resource_id = (
        "/subscriptions/00000000-0000-0000-0000-000000000001"
        "/resourceGroups/rg-test/providers/Microsoft.OperationalInsights/workspaces/la-test"
    )
    calls: list[str] = []

    def fake_urlopen(req: Any, timeout: int = 60) -> _FakeHttpResponse:
        url = req.full_url
        calls.append(url)
        if "api-version=2025-02-01" in url:
            raise urllib.error.HTTPError(
                url=url,
                code=400,
                msg="Bad Request",
                hdrs=None,  # type: ignore[arg-type]
                fp=io.BytesIO(b'{"error":{"code":"InvalidApiVersionParameter"}}'),
            )
        return _FakeHttpResponse(
            {
                "name": "OnePasswordEventLogs_CL",
                "properties": {
                    "schema": {
                        "name": "OnePasswordEventLogs_CL",
                        "description": "1Password audit events.",
                        "columns": [
                            {"name": "TimeGenerated", "type": "datetime"},
                            {"name": "EventUuid", "type": "string", "description": "Unique event ID."},
                        ],
                    }
                },
            }
        )

    with patch("urllib.request.urlopen", side_effect=fake_urlopen):
        res = fetch_arm_table_schema(ws_resource_id, "OnePasswordEventLogs_CL", "dummy-arm-token")

    assert len(calls) == 2
    assert res["ok"] is True
    assert res["apiVersion"] == "2022-10-01"
    assert res["tableDescription"] == "1Password audit events."
    assert "raw" not in res
    assert any(c["name"] == "EventUuid" and c["description"] == "Unique event ID." for c in res["columns"])


def test_security_validations_on_graph_and_arm_helpers() -> None:
    ws_guid = "8fb6e2d6-1b0a-4d0b-9d9f-9f3e2a5c7b21"

    # Reject non-GUID workspace_id injection attempts
    try:
        build_graph_hunting_schema_tables_url("not-a-guid)?$filter=1")
        assert False, "Expected ValueError for invalid workspace_id"
    except ValueError:
        pass

    # Reject untrusted @odata.nextLink host to prevent bearer token exfiltration
    with patch(
        "urllib.request.urlopen",
        return_value=_FakeHttpResponse(
            {
                "value": [{"name": "OnePasswordEventLogs_CL", "description": "1Password audit events."}],
                "@odata.nextLink": "https://evil.example.com/beta/security/getHuntingSchemaTables?$skiptoken=123",
            }
        ),
    ):
        res = fetch_graph_hunting_schema_tables("dummy-token", workspace_id=ws_guid)
    assert res["ok"] is False
    assert "Untrusted @odata.nextLink" in str(res["error"])

    # Reject invalid ARM workspace_resource_id or traversal
    try:
        fetch_arm_table_schema("/subscriptions/not-a-valid-arm-id", "MyTable_CL", "dummy-arm-token")
        assert False, "Expected ValueError for invalid workspace_resource_id"
    except ValueError:
        pass


def test_re_review_false_pass_regressions_bugs_1_through_5(tmp_path: Path) -> None:
    """Covers the 5 reproducible high-severity false-pass bugs reported in PR #15714 re-review."""
    sol = tmp_path / "ReReviewBugRegressionSol"
    _build_minimal_solution(sol, data_connectors=["Data Connectors/Vendor_tables.json"])

    # Bug 1: Declared system-named columns (TimeGenerated, Computer, RawData) in properties.schema.columns
    # with blank/missing descriptions must FAIL VAL-TBL-02, VAL-TBL-03, QUAL-TBL-01, and QUAL-TBL-02.
    sys_col_blank_src = {
        "name": "VendorAudit_CL",
        "type": "Microsoft.OperationalInsights/workspaces/tables",
        "apiVersion": "2022-10-01",
        "properties": {
            "schema": {
                "name": "VendorAudit_CL",
                "description": "Vendor audit events ingested via CCP.",
                "columns": [
                    {"name": "TimeGenerated", "type": "datetime", "description": ""},
                    {"name": "Computer", "type": "string"},
                    {"name": "RawData", "type": "string", "description": "   "},
                    {"name": "EventId", "type": "string", "description": "Unique event identifier."},
                ],
            }
        },
    }
    _write_json(sol / "Data Connectors" / "Vendor_tables.json", sys_col_blank_src)
    _write_json(
        sol / "Package" / "mainTemplate.json",
        {
            "$schema": "https://schema.management.azure.com/schemas/2019-04-01/deploymentTemplate.json#",
            "contentVersion": "1.0.0.0",
            "resources": [sys_col_blank_src],
        },
    )
    inv_bug1 = discover_solution_tables(sol)
    b1_s2, b1_obs2 = evaluate_val_tbl_02(inv_bug1, enforce_blocking=True)
    assert b1_s2 == "FAIL"
    assert "TimeGenerated" in b1_obs2
    assert "Computer" in b1_obs2
    assert "RawData" in b1_obs2

    # Now fix source descriptions for declared system-named columns, but drop TimeGenerated description in package
    valid_src = {
        "name": "VendorAudit_CL",
        "type": "Microsoft.OperationalInsights/workspaces/tables",
        "apiVersion": "2022-10-01",
        "properties": {
            "schema": {
                "name": "VendorAudit_CL",
                "description": "Vendor audit events ingested via CCP.",
                "columns": [
                    {
                        "name": "TimeGenerated",
                        "type": "datetime",
                        "description": "The timestamp (UTC) when the vendor audit event occurred.",
                    },
                    {"name": "EventId", "type": "string", "description": "Unique event identifier."},
                ],
            }
        },
    }
    pkg_dropped_sys_desc = json.loads(json.dumps(valid_src))
    pkg_dropped_sys_desc["properties"]["schema"]["columns"][0]["description"] = ""
    _write_json(sol / "Data Connectors" / "Vendor_tables.json", valid_src)
    _write_json(
        sol / "Package" / "mainTemplate.json",
        {
            "$schema": "https://schema.management.azure.com/schemas/2019-04-01/deploymentTemplate.json#",
            "contentVersion": "1.0.0.0",
            "resources": [pkg_dropped_sys_desc],
        },
    )
    inv_bug1_drift = discover_solution_tables(sol)
    b1_s3, b1_obs3 = evaluate_val_tbl_03(inv_bug1_drift, enforce_blocking=True)
    assert b1_s3 == "FAIL"
    assert "TimeGenerated" in b1_obs3

    # Restore valid package so static VAL-TBL-01..03 pass for live evaluator tests
    _write_json(
        sol / "Package" / "mainTemplate.json",
        {
            "$schema": "https://schema.management.azure.com/schemas/2019-04-01/deploymentTemplate.json#",
            "contentVersion": "1.0.0.0",
            "resources": [valid_src],
        },
    )
    inv_valid = discover_solution_tables(sol)
    ws_id = "8fb6e2d6-1b0a-4d0b-9d9f-9f3e2a5c7b21"
    ws_res_id = (
        "/subscriptions/00000000-0000-0000-0000-000000000001"
        "/resourceGroups/rg-test/providers/Microsoft.OperationalInsights/workspaces/la-test"
    )

    # Bug 2: qualification_evidence.checks PASS overrides must NOT bypass live evaluators for QUAL-TBL-01..03
    override_bypass_ev = {
        "target": {"workspaceId": ws_id, "workspaceResourceId": ws_res_id},
        "checks": {
            "QUAL-TBL-01": {"status": "PASS", "observation": "Spoofed override"},
            "QUAL-TBL-02": {"status": "PASS", "observation": "Spoofed override"},
            "QUAL-TBL-03": {"status": "PASS", "observation": "Spoofed override"},
        },
        "tableSchemaReadiness": {
            "target": {"workspaceId": ws_id, "workspaceResourceId": ws_res_id},
            "armTables": {"VendorAudit_CL": {"ok": False, "httpStatus": 403, "error": "Forbidden"}},
            "huntingSchemaTables": {"ok": False, "httpStatus": 403, "error": "Forbidden"},
            "huntingQuery": {"VendorAudit_CL": {"ok": False, "httpStatus": 403, "error": "Forbidden"}},
        },
    }
    res_bug2 = run_pr_qualification_checks(sol, run_qualification=True, qualification_evidence=override_bypass_ev)
    for cid in ("QUAL-TBL-01", "QUAL-TBL-02", "QUAL-TBL-03"):
        assert res_bug2["checksById"][cid]["status"] == "FAIL"

    # Bug 3: tableSchemaReadiness.target conflicting with workflow_state.target must fail closed (not override)
    other_ws_id = "11111111-2222-3333-4444-555555555555"
    other_ws_res_id = (
        "/subscriptions/00000000-0000-0000-0000-000000000001"
        "/resourceGroups/rg-other/providers/Microsoft.OperationalInsights/workspaces/la-other"
    )
    conflicting_target_ev = {
        "target": {"workspaceId": ws_id, "workspaceResourceId": ws_res_id},
        "tableSchemaReadiness": {
            "target": {"workspaceId": other_ws_id, "workspaceResourceId": other_ws_res_id},
            "armTables": {
                "VendorAudit_CL": {
                    "ok": True,
                    "httpStatus": 200,
                    "requestUrl": f"https://management.azure.com{other_ws_res_id}/tables/VendorAudit_CL?api-version=2025-02-01",
                    "workspaceResourceId": other_ws_res_id,
                    "tableDescription": "Vendor audit events ingested via CCP.",
                    "columns": valid_src["properties"]["schema"]["columns"],
                }
            },
            "huntingSchemaTables": {
                "ok": True,
                "httpStatus": 200,
                "endpoint": f"https://graph.microsoft.com/beta/security/getHuntingSchemaTables(workspaceId={other_ws_id})",
                "workspaceId": other_ws_id,
                "workspaceIdUnquoted": True,
                "complete": True,
                "paginationComplete": True,
                "tables": [
                    {
                        "name": "VendorAudit_CL",
                        "description": "Vendor audit events ingested via CCP.",
                        "columns": valid_src["properties"]["schema"]["columns"],
                    }
                ],
            },
            "huntingQuery": {
                "VendorAudit_CL": {
                    "ok": True,
                    "httpStatus": 200,
                    "requestUrl": f"https://graph.microsoft.com/beta/security/getRunHuntingQuery(query='VendorAudit_CL%20%7C%20take%201',timespan='P1D',workspaceId={other_ws_id})",
                    "workspaceId": other_ws_id,
                    "workspaceIdUnquoted": True,
                    "query": "VendorAudit_CL | take 1",
                    "schema": [
                        {"name": "TimeGenerated", "type": "DateTime"},
                        {"name": "EventId", "type": "String"},
                    ],
                }
            },
        },
    }
    res_bug3 = run_pr_qualification_checks(sol, run_qualification=True, qualification_evidence=conflicting_target_ev)
    for cid in ("QUAL-TBL-01", "QUAL-TBL-02", "QUAL-TBL-03"):
        assert res_bug3["checksById"][cid]["status"] == "FAIL"
        assert "does not match approved target" in res_bug3["checksById"][cid]["whatWeObserved"]

    # Bug 4: Missing execution metadata (omitted ok, httpStatus, requestUrl/endpoint, paginationComplete,
    # or conflicting per-table workspaceId in QUAL-TBL-02) must fail closed
    missing_meta_ev = {
        "target": {"workspaceId": ws_id, "workspaceResourceId": ws_res_id},
        "tableSchemaReadiness": {
            "target": {"workspaceId": ws_id, "workspaceResourceId": ws_res_id},
            "armTables": {
                "VendorAudit_CL": {
                    # Missing ok, httpStatus, requestUrl
                    "workspaceResourceId": ws_res_id,
                    "tableDescription": "Vendor audit events ingested via CCP.",
                    "columns": valid_src["properties"]["schema"]["columns"],
                }
            },
            "huntingSchemaTables": {
                "ok": True,
                "httpStatus": 200,
                "endpoint": f"https://graph.microsoft.com/beta/security/getHuntingSchemaTables(workspaceId={ws_id})",
                "workspaceId": ws_id,
                "workspaceIdUnquoted": True,
                # Missing complete / paginationComplete
                "tables": [
                    {
                        "name": "VendorAudit_CL",
                        "workspaceId": other_ws_id,  # Conflicting per-table workspaceId
                        "description": "Vendor audit events ingested via CCP.",
                        "columns": valid_src["properties"]["schema"]["columns"],
                    }
                ],
            },
            "huntingQuery": {
                "VendorAudit_CL": {
                    "ok": True,
                    "httpStatus": 200,
                    # Missing requestUrl / endpoint
                    "workspaceId": ws_id,
                    "workspaceIdUnquoted": True,
                    "query": "VendorAudit_CL | take 1",
                    "schema": [
                        {"name": "TimeGenerated", "type": "DateTime"},
                        {"name": "EventId", "type": "String"},
                    ],
                }
            },
        },
    }
    b4_q1, b4_obs1 = evaluate_qual_tbl_01(inv_valid, missing_meta_ev, enforce_blocking=True)
    b4_q2, b4_obs2 = evaluate_qual_tbl_02(inv_valid, missing_meta_ev, enforce_blocking=True)
    b4_q3, b4_obs3 = evaluate_qual_tbl_03(inv_valid, missing_meta_ev, enforce_blocking=True)
    assert (b4_q1, b4_q2, b4_q3) == ("FAIL", "FAIL", "FAIL")
    assert "missing required provider success metadata" in b4_obs1
    assert "incomplete_hunting_schema_pagination" in b4_obs2
    assert "missing required requestUrl/endpoint metadata" in b4_obs3

    # Also verify QUAL-TBL-01 fails when requestUrl/endpoint is omitted even if ok=True and httpStatus=200 are present
    arm_missing_url_ev = json.loads(json.dumps(missing_meta_ev))
    arm_missing_url_ev["tableSchemaReadiness"]["armTables"]["VendorAudit_CL"]["ok"] = True
    arm_missing_url_ev["tableSchemaReadiness"]["armTables"]["VendorAudit_CL"]["httpStatus"] = 200
    b4_q1_url, b4_obs1_url = evaluate_qual_tbl_01(inv_valid, arm_missing_url_ev, enforce_blocking=True)
    assert b4_q1_url == "FAIL"
    assert "missing required requestUrl/endpoint metadata" in b4_obs1_url

    # Also verify QUAL-TBL-02 and QUAL-TBL-03 reject URL fragment workspaceId spoofing (#<expected_ws_id>)
    frag_spoof_ev = json.loads(json.dumps(conflicting_target_ev))
    frag_spoof_ev["tableSchemaReadiness"]["target"] = {"workspaceId": ws_id, "workspaceResourceId": ws_res_id}
    frag_spoof_ev["tableSchemaReadiness"]["huntingSchemaTables"]["workspaceId"] = ws_id
    frag_spoof_ev["tableSchemaReadiness"]["huntingSchemaTables"]["endpoint"] = (
        f"https://graph.microsoft.com/beta/security/getHuntingSchemaTables(workspaceId={other_ws_id})#{ws_id}"
    )
    frag_spoof_ev["tableSchemaReadiness"]["huntingQuery"]["VendorAudit_CL"]["workspaceId"] = ws_id
    frag_spoof_ev["tableSchemaReadiness"]["huntingQuery"]["VendorAudit_CL"]["requestUrl"] = (
        f"https://graph.microsoft.com/beta/security/getRunHuntingQuery(query='VendorAudit_CL%20%7C%20take%201',timespan='P1D',workspaceId={other_ws_id})#{ws_id}"
    )
    f_q2, f_obs2 = evaluate_qual_tbl_02(inv_valid, frag_spoof_ev, enforce_blocking=True)
    f_q3, f_obs3 = evaluate_qual_tbl_03(inv_valid, frag_spoof_ev, enforce_blocking=True)
    assert (f_q2, f_q3) == ("FAIL", "FAIL")
    assert "does not target approved workspaceCustomerId" in f_obs2
    assert "does not match target workspaceId" in f_obs3

    # Also verify QUAL-TBL-02 rejects conflicting per-table workspaceId even when paginationComplete=True
    per_table_ws_conflict_ev = json.loads(json.dumps(missing_meta_ev))
    per_table_ws_conflict_ev["tableSchemaReadiness"]["huntingSchemaTables"]["complete"] = True
    per_table_ws_conflict_ev["tableSchemaReadiness"]["huntingSchemaTables"]["paginationComplete"] = True
    b4_q2_ws, b4_obs2_ws = evaluate_qual_tbl_02(inv_valid, per_table_ws_conflict_ev, enforce_blocking=True)
    assert b4_q2_ws == "FAIL"
    assert "does not match approved target" in b4_obs2_ws

    # Bug 5: Promotion gate must reject bare summary flags (tableSchemaQualificationVerified=True or
    # tableSchemaReadiness.verified=True with empty table receipts) when custom tables exist
    spoofed_promotion_state = {
        "solutionRoot": str(sol),
        "target": {"workspaceId": ws_id, "workspaceResourceId": ws_res_id},
        "expectedContentCounts": {
            "sentinelRulesCount": 1,
            "workbooksCount": 0,
            "customDetectionsCount": 1,
            "customTablesCount": 1,
        },
        "preflightPassed": True,
        "deploymentVerified": True,
        "mockIngestionVerified": True,
        "ruleParityVerified": True,
        "sanitizedEvidenceReady": True,
        "tableSchemaQualificationVerified": True,
        "tableSchemaReadiness": {
            "status": "passed",
            "verified": True,
            "armTableReadback": {"ok": True, "tables": []},
            "huntingSchema": {"ok": True, "complete": True, "tables": []},
            "workspaceHuntingQuery": {"ok": True, "queries": []},
        },
    }
    gate_spoofed = evaluate_qualification_promotion_gate(spoofed_promotion_state)
    assert gate_spoofed["passed"] is False
    assert gate_spoofed["tableSchemaQualificationVerified"] is False
    assert "tableSchemaQualificationVerified" in gate_spoofed["missingGates"]


