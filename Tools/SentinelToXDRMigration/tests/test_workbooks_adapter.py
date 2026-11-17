from __future__ import annotations
import copy
from collections import Counter
from datetime import datetime, timedelta, timezone
import json
from pathlib import Path
import shutil
import subprocess
from uuid import uuid4
import pytest
from sentinel_xdr_migration._workbook_core import workbook, workbook_fixtures
from sentinel_xdr_migration._workbook_core import workbook_mock as mock, workbook_mock_recipes as recipes

FIXTURES = Path(__file__).parent / "fixtures/workbooks"

@pytest.fixture
def source():
    return json.loads((FIXTURES / "notebook.json").read_text())


@pytest.fixture
def scratch():
    # Repository-local scratch only; no system temp directories.
    path = Path.cwd() / f".workbook-test-{uuid4()}"
    path.mkdir()
    try:
        yield path
    finally:
        shutil.rmtree(path)


def converted(source):
    return workbook.convert_workbook(source, tables=["Syslog"])


def test_every_query_layout_templates_drilldown_and_idempotence(source):
    source["items"][1]["content"]["items"][0]["content"]["gridSettings"]["customMetadata"] = {
        "resourceType": workbook.LA, "resourceIds": ["literal-business-link"]}
    original = copy.deepcopy(source)
    result = converted(source)
    output = result["workbook"]
    assert source == original
    assert len(workbook.query_surfaces(output)) == 3
    assert {x["name"] for x in result["report"]["removedParameters"]} == {"Subscription", "Workspace"}
    assert output["items"][1]["content"]["items"][0]["customWidth"] == "50"
    assert output["items"][1]["content"]["items"][1]["conditionalVisibility"] == \
        source["items"][1]["content"]["items"][1]["conditionalVisibility"]
    assert output["styleSettings"] == source["styleSettings"]
    assert output["items"][1]["content"]["items"][0]["content"]["gridSettings"] == \
        source["items"][1]["content"]["items"][0]["content"]["gridSettings"]
    assert "ownerId" not in output["context"]
    assert "fallbackResourceIds" not in output
    for s, old in zip(workbook.query_surfaces(output), workbook.query_surfaces(source)):
        assert s["node"]["queryType"] == "advancedHunting"
        assert s["node"]["query"] == old["node"]["query"]
        assert not (workbook.SCOPE_KEYS & s["node"].keys())
        assert "resourceType" not in s["node"]
    assert result["report"]["queries"][0]["sourcePath"] == "/items/0/content/parameters/3/query"
    assert result["report"]["queries"][0]["outputPath"] == "/items/0/content/parameters/1/query"
    assert converted(output)["workbook"] == output
    assert result["report"]["status"] == "needs-validation"
    assert {g["code"] for g in result["report"]["gates"]} == {
        "ah-query-backed-parameters", "blank-ah-selection-table-visibility"}


def test_scope_helper_chain_and_business_resourcegroup(source):
    params = source["items"][0]["content"]["parameters"]
    params.extend([
        {"name": "DefaultWorkspace", "type": 5,
         "typeSettings": {"resourceTypeFilter": {workbook.LA: True}}},
        {"name": "ContextFree", "type": 1, "queryType": 8,
         "isHiddenWhenLocked": True, "query": '{"content":"{DefaultWorkspace}"}'},
        {"name": "Selection", "type": 1, "queryType": 1,
         "query": "where type == 'microsoft.operationalinsights/workspaces' | extend w='{DefaultWorkspace}'"},
        {"name": "Subscriptions", "type": 6, "queryType": 1,
         "query": "print sub='{Selection}'"},
        {"name": "Workspaces", "type": 5, "crossComponentResources": ["{Subscriptions}"]},
        {"name": "ResourceGroup", "type": 2, "queryType": 0,
         "query": "AzureActivity | summarize by ResourceGroup",
         "typeSettings": {"resourceTypeFilter": {"microsoft.resources/resourcegroups": True}}},
    ])
    source["fallbackResourceIds"] = ["{Workspaces}"]
    result = workbook.convert_workbook(source, tables=["Syslog", "AzureActivity"])
    removed = {p["name"] for p in result["report"]["removedParameters"]}
    assert removed == {"Subscription", "Workspace", "DefaultWorkspace", "ContextFree",
                       "Selection", "Subscriptions", "Workspaces"}
    assert "ResourceGroup" in {p["name"] for p in result["workbook"]["items"][0]["content"]["parameters"]}
    assert not result["report"]["issues"]


def test_exported_workspace_is_not_deleted(source):
    source["items"][1]["content"]["items"][0]["content"]["exportParameterName"] = "Workspace"
    result = converted(source)
    assert "Workspace" not in {p["name"] for p in result["report"]["removedParameters"]}
    assert any(i["code"] == "scope-used-by-content" for i in result["report"]["issues"])


@pytest.mark.parametrize("query", [
    "workspace('example').Syslog | count",
    "let f=(){workspace('example').Syslog}; f()",
    "cluster('example').database('example').Syslog",
    "SyslogConnectorsOverallStatus({TimeRange:start}, {TimeRange:end})",
])
def test_explicit_scope_blocks_without_dropping_panel(source, query):
    node = source["items"][1]["content"]["items"][0]["content"]
    node["query"] = query
    result = converted(source)
    assert result["report"]["status"] == "blocked"
    assert result["workbook"]["items"][1]["content"]["items"][0]["content"] == node
    assert len(result["workbook"]["items"]) == len(source["items"])


def test_ah_wrapper_and_unknown_settings(source):
    node = source["items"][1]["content"]["items"][0]["content"]
    query = node["query"]
    node.update(queryType="advancedHunting", query=json.dumps({
        "__advancedHuntingSettings": True, "query": query, "selectedWorkspaceIds": ["synthetic-guid"]
    }))
    result = converted(source)
    assert result["workbook"]["items"][1]["content"]["items"][0]["content"]["query"] == query
    assert "selectedWorkspaceIds" not in json.dumps(result["workbook"])
    node["query"] = '{"__advancedHuntingSettings":true,"query":"Syslog","unknown":1}'
    assert any(i["code"] == "query-format" for i in converted(source)["report"]["issues"])


def test_unresolved_unknown_provider_and_unknown_mapping_preserved(source):
    result = workbook.convert_workbook(source)
    assert result["report"]["status"] == "blocked"
    assert result["workbook"]["items"][1] == source["items"][1]
    unknown = workbook.convert_workbook(source, tables=["UnknownCustomerTable"])
    assert unknown["report"]["status"] == "blocked"
    node = source["items"][1]["content"]["items"][0]["content"]
    node["queryType"] = 1
    assert any(i["code"] == "unsupported-provider" for i in converted(source)["report"]["issues"])


def test_hash_bound_resolution(source):
    resolutions = {
        s["path"]: {"querySha256": workbook.query_hash(s["node"]["query"]),
                    "tables": ["Syslog"], "evidence": "sanitized reviewed fixture"}
        for s in workbook.query_surfaces(source)
    }
    result = workbook.convert_workbook(source, resolutions=resolutions)
    assert result["report"]["status"] == "needs-validation"
    source["items"][1]["content"]["items"][0]["content"]["query"] += " | take 1"
    assert any(i["code"] == "stale-resolution" for i in
               workbook.convert_workbook(source, resolutions=resolutions)["report"]["issues"])


def test_real_rows_emitted_and_fixture_oracle(source, scratch):
    manifest = json.loads((FIXTURES / "manifest.json").read_text())
    result = workbook_fixtures.emit(manifest, source, converted(source)["workbook"], scratch)
    assert result["execution"] == "not-run"
    assert len(result["files"]) == 14
    text = (scratch / "all-computers-warning.ah.kql").read_text()
    assert '"alpha", "warning"' in text and "datetime(2026-01-02T09:59:00Z)" in text
    assert "{Computer}" not in text
    rows = manifest["tables"]["Syslog"]["rows"]
    # Independent fixture arithmetic verifies the oracle, not remote KQL execution.
    for case in manifest["cases"][:5]:
        counts = {}
        selected = case["substitutions"]
        start, end = [
            datetime.fromisoformat(selected[f"TimeRange:{key}"][9:-1].replace("Z", "+00:00"))
            for key in ("start", "end")
        ]
        for timestamp, computer, severity in rows:
            when = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
            if not start <= when <= end:
                continue
            if selected["Computer"] != "'*'" and repr(computer) not in selected["Computer"].split(","):
                continue
            if selected["Severity"] != "'*'" and selected["Severity"] != repr(severity):
                continue
            key = computer, when.replace(minute=0, second=0).isoformat().replace("+00:00", "Z")
            counts[key] = counts.get(key, 0) + 1
        actual = {"columns": case["expected"]["columns"],
                  "rows": [[*key, count] for key, count in sorted(counts.items())]}
        workbook_fixtures.assert_result(case["expected"], actual)


def test_exact_assertion_rejects_same_count_wrong_values():
    expected = {"columns": [{"name": "Events", "type": "long"}], "rows": [[3]]}
    with pytest.raises(AssertionError, match="Cell"):
        workbook_fixtures.assert_result(expected, {"columns": expected["columns"], "rows": [[9]]})
    with pytest.raises(AssertionError, match="Column"):
        workbook_fixtures.assert_result(expected, {"columns": [{"name": "Other", "type": "long"}], "rows": [[3]]})


def test_fixture_clock_and_json_literal_are_not_neutralized():
    query = 'print t=now ( ), x=dynamic({"key":1}), label="{Computer:label}"'
    result = workbook_fixtures.substitute(query, {"Computer:label": "alpha"},
                                          "2026-01-02T12:00:00Z")
    assert 'dynamic({"key":1})' in result
    assert "datetime(2026-01-02T12:00:00Z)" in result
    with pytest.raises(ValueError, match="relative time"):
        workbook_fixtures.substitute("print now(-1h)", {}, "2026-01-02T12:00:00Z")
