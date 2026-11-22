from __future__ import annotations

import io
import json
from pathlib import Path
from typing import Any
from unittest.mock import patch
import urllib.error

from solution_manager.qualification.pr_applicability import determine_pr_applicability
from solution_manager.qualification.pr_check_runner import run_pr_qualification_checks
from solution_manager.qualification.runtime import (
    build_graph_hunting_schema_tables_url,
    build_graph_run_hunting_query_url,
    fetch_arm_table_schema,
    fetch_graph_hunting_schema,
    fetch_graph_hunting_schema_tables,
    run_workspace_hunting_query_get,
)
from solution_manager.qualification.table_schema_readiness import (
    discover_solution_tables,
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
                    {"name": "TimeGenerated", "type": "datetime"},
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


def test_minimum_blocking_vs_strict_blocking_for_val_tbl_checks(tmp_path: Path) -> None:
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

    # Default rollout mode: minimum blocking (default_blocking=False) -> PASS with [Advisory: adoption mode]
    assert resolve_table_schema_blocking_mode(None, None) is False
    res_advisory = run_pr_qualification_checks(sol, run_qualification=False)
    for cid in ("VAL-TBL-01", "VAL-TBL-02", "VAL-TBL-03"):
        chk = res_advisory["checksById"][cid]
        assert chk["applicable"] is True
        assert chk["status"] == "PASS"
        assert "[Advisory: adoption mode]" in chk["whatWeObserved"]
    assert res_advisory["validationStatus"] == "Validated"

    # Strict mode via qualification_evidence["enforceTableSchemaDescriptions"] = True -> FAIL
    res_strict = run_pr_qualification_checks(
        sol,
        run_qualification=False,
        qualification_evidence={"enforceTableSchemaDescriptions": True},
    )
    for cid in ("VAL-TBL-01", "VAL-TBL-02", "VAL-TBL-03"):
        chk = res_strict["checksById"][cid]
        assert chk["applicable"] is True
        assert chk["status"] == "FAIL"
    assert res_strict["validationStatus"] == "Validation Failed"

    # Qualification checks QUAL-TBL-01..03 also honor minimum blocking by default vs strict mode
    res_qual_advisory = run_pr_qualification_checks(
        sol,
        run_qualification=True,
        qualification_evidence={"deployment": {"status": "passed"}},
    )
    for cid in ("QUAL-TBL-01", "QUAL-TBL-02", "QUAL-TBL-03"):
        chk = res_qual_advisory["checksById"][cid]
        assert chk["applicable"] is True
        assert chk["status"] == "PASS"
        assert "[Advisory: adoption mode]" in chk["whatWeObserved"]

    res_qual_strict = run_pr_qualification_checks(
        sol,
        run_qualification=True,
        qualification_evidence={"deployment": {"status": "passed"}, "enforceTableSchemaDescriptions": True},
    )
    for cid in ("QUAL-TBL-01", "QUAL-TBL-02", "QUAL-TBL-03"):
        chk = res_qual_strict["checksById"][cid]
        assert chk["applicable"] is True
        assert chk["status"] == "FAIL"


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

