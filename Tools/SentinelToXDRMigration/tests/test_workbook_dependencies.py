from copy import deepcopy
import json
from importlib.resources import files

import pytest

from sentinel_xdr_migration import cli, workbooks
from sentinel_xdr_migration.dependencies import dependency_plan, workload_records
from sentinel_xdr_migration import workbook_dependencies as dependencies
from sentinel_xdr_migration.workbook_functions import candidates
from sentinel_xdr_migration._workbook_core import workbook, mapping_catalog, migrator, rewrite
from test_workbooks import solution, config, convert, authored

SOURCE = "Workbooks/nested/fixture.json"
POINTER = "/items/0/content/query"


def write_query(solution, query):
    path = solution / SOURCE
    value = json.loads(path.read_bytes())
    value["items"][0]["content"]["query"] = query
    path.write_text(json.dumps(value))


def function(solution, alias="ReviewedFunction"):
    path = solution / "Parsers/nested/function.yaml"
    path.parent.mkdir(parents=True)
    path.write_text(f"FunctionName: {alias}\nFunctionAlias: {alias}\nFunctionQuery: Syslog | count\n")
    data_path = solution / "Data/Solution_Fixture.json"
    data = json.loads(data_path.read_bytes())
    data["Parsers"] = ["Parsers/nested/function.yaml"]
    data_path.write_text(json.dumps(data))
    return {key: candidates(solution)[0][key] for key in ("functionAlias", "sourcePath", "sourceSha256")}


def decisions(plan, *, decision="accept", tables=None, functions=None):
    return {
        "planSha256": plan["planSha256"],
        "queries": [{"workbook": row["workbook"], "path": row["path"],
                     "querySha256": row["querySha256"], "decision": decision,
                     "tables": tables or ["DeviceEvents"],
                     "workspaceFunctions": [a for a in row["workspaceFunctions"]
                                            if a not in (tables or ["DeviceEvents"])]}
                    for row in plan["queries"]],
        "workbooks": [{"path": row["path"], "decision": decision,
                       "requiredWorkloads": [{"workload": "sentinel" if tables == ["Syslog"] else "mde",
                                             "dataTypes": tables or ["DeviceEvents"]}],
                       "requiredDataConnectors": ([{"connectorId": "ReviewedConnector", "dataTypes": tables}]
                                                 if tables == ["Syslog"] else []),
                       "requiredWorkspaceFunctions": functions or []}
                      for row in plan["inventory"]],
    }


def review(solution, plan, value, output="Logs/review-1"):
    folder = solution / "Logs/inputs"
    folder.mkdir(parents=True, exist_ok=True)
    plan_path, decisions_path = folder / "plan.json", folder / "decisions.json"
    plan_path.write_text(json.dumps(plan))
    decisions_path.write_text(json.dumps(value))
    return dependencies.review_workbook_dependencies(
        solution, plan_path=plan_path, decisions_path=decisions_path,
        expected_plan_sha256=plan["planSha256"], actor="test-reviewer",
        reference="approval-42", output_directory=solution / output)


def metadata(plan):
    return {"results": [
        {"workbook": row["workbook"], "path": row["path"], "workspaceId": "approved-workspace",
         "workbookSha256": row["workbookSha256"], "querySha256": row["querySha256"],
         "status": "passed", "statusCode": 200, "partial": False,
         "bindings": {}, "renderedQuery": row["queryKql"],
         "renderedQuerySha256": workbook.query_hash(row["queryKql"]),
         "timeRange": {"start": "2026-01-01T00:00:00Z", "end": "2026-01-02T00:00:00Z"},
         "dataSources": [{"tables": ["DeviceEvents"]}]}
        for row in plan["queries"]]}


def test_plan_is_offline_hash_bound_and_never_accepts_heuristics(solution):
    before = {str(path): path.read_bytes() for path in solution.rglob("*") if path.is_file()}
    plan = dependencies.plan_workbook_dependencies(solution)
    assert plan["queries"][0]["sourceKql"].startswith("DeviceEvents")
    assert plan["queries"][0]["proposal"]["dataTypes"] == ["DeviceEvents"]
    assert plan["queries"][0]["proposalAccepted"] is False
    assert plan["queries"][0]["staticConfidence"] == "heuristic-not-reviewed"
    assert plan["liveQueriesExecuted"] is False
    assert plan["planSha256"] == dependencies.digest({k: v for k, v in plan.items() if k != "planSha256"})
    assert before == {str(path): path.read_bytes() for path in solution.rglob("*") if path.is_file()}


def test_office_native_tables_have_documented_identity_mappings_and_mdo_workload():
    names = (
        "MessageEvents", "MessageUrlInfo", "MessagePostDeliveryEvents",
        "FileMaliciousContentInfo",
    )
    tables = mapping_catalog.load_mapping_catalog()["tables"]
    for name in names:
        assert tables[name]["ahTable"] == name
        assert tables[name]["tier"] == "1to1"
    schemas = json.loads(files("sentinel_xdr_migration._workbook_core")
                         .joinpath("data/ah_schema_catalog.json").read_text())
    assert not {"MessageEvents", "MessageUrlInfo", "MessagePostDeliveryEvents"} & set(schemas)
    records, unknown = workload_records(list(names))
    assert records == [{"workload": "mdo", "dataTypes": sorted(names)}]
    assert unknown == []


def test_granularity_scalar_parameter_is_not_a_source_but_table_parameters_are():
    scalar = (
        "let gran = {Granularity}; "
        "EmailEvents | make-series Total = count() on Timestamp step gran"
    )
    assert workbook.opaque_functions(scalar) == set()
    assert workbook.opaque_functions("let source = {TableName}; source | take 1") == {"{TableName}"}
    assert workbook.opaque_functions("{TableName} | take 1") == {"{TableName}"}


def test_static_datatable_review_converts_without_phantom_dependencies(solution):
    query = '''datatable(Index:int, Name:string, Value:int)
[
    1, "Defender for Office 365", 194,
    2, "Mimecast", 478
]
| project ["Email security solution"] = Name, ["Threats missed"] = Value
| order by ["Threats missed"] asc'''
    assert rewrite.is_source_free_literal_datatable(query)
    assert not rewrite.is_source_free_literal_datatable(
        'datatable(Index:int, Name:string)[1, "x"] | join DeviceEvents on Index'
    )
    assert not rewrite.is_source_free_literal_datatable(
        'datatable(Index:int)[1] | project MissingColumn'
    )
    assert migrator.convert(query, tables=[])["status"] == "converted"
    assert migrator.convert("print 1", tables=[])["status"] == "needs-review"
    assert dependency_plan(query, metadata=[{"tables": ["MessageEvents"]}])["dataTypes"] == []

    write_query(solution, query)
    plan = dependencies.plan_workbook_dependencies(solution)
    row = plan["queries"][0]
    assert row["workspaceFunctions"] == []
    assert row["proposal"]["dataTypes"] == []
    assert row["proposal"]["reviewRequired"] is False

    reviewed = decisions(plan)
    reviewed["queries"][0]["tables"] = []
    reviewed["workbooks"][0]["requiredWorkloads"] = []
    reviewed["workbooks"][0]["requiredDataConnectors"] = []
    review(solution, plan, reviewed)
    settings = json.loads((solution / "Logs/review-1/conversion-config.json").read_bytes())
    result = convert(solution, settings)
    assert result["converted"] == 1 and result["blocked"] == 0
    assert workbooks.validate_workbooks(solution)["valid"] == 1

    authored_document = json.loads(authored(solution).read_bytes())
    provenance = authored_document["contentProvenance"]
    assert provenance["requiredWorkloads"] == []
    assert provenance["requiredDataConnectors"] == []
    record = provenance["conversion"]["queries"][0]
    assert record["conversion"]["resolvedTables"] == []
    assert record["conversion"]["status"] == "converted"

    write_query(solution, "print 1")
    unsupported_plan = dependencies.plan_workbook_dependencies(solution)
    unsupported_decisions = decisions(unsupported_plan)
    unsupported_decisions["queries"][0]["tables"] = []
    unsupported_decisions["workbooks"][0]["requiredWorkloads"] = []
    unsupported_decisions["workbooks"][0]["requiredDataConnectors"] = []
    with pytest.raises(ValueError, match="requires explicit underlying source tables"):
        review(solution, unsupported_plan, unsupported_decisions, output="Logs/review-unsupported")


@pytest.mark.parametrize("query", [
    "range x from 0 to 10 step 1",
    "range x from 0 to 20 step 1",
    "\n range Value_1 from -10 to 0 step 2 \r\n",
    "range x from 10 to -10 step -1",
    "range x from 0.0 to 1.0 step 0.25",
    "range x from -1e1 to 1e1 step 5e-1",
    "range DeviceEvents from 0 to 10 step 1",
    "range x from 1 to 1 step -1",
    "range x from -9223372036854775808 to 9223372036854775807 step 1",
])
def test_literal_numeric_range_conversion_is_identity_and_dependency_free(query):
    assert rewrite.is_source_free_literal_range(query)
    assert rewrite.is_source_free_literal_query(query)
    assert not rewrite.is_source_free_literal_datatable(query)
    for tables in ([], None):
        contract = migrator.convert(query, tables=tables)
        assert contract["status"] == "converted"
        assert contract["convertedKql"] == query
        assert contract["resolvedTables"] == []
        assert contract["unsupported"] == []
        assert contract["diff"] == []
    proposal = dependency_plan(query, metadata=[{"tables": ["MessageEvents"]}])
    assert proposal["dataTypes"] == []
    assert proposal["requiredWorkloads"] == []
    assert proposal["requiredDataConnectors"] == []
    assert proposal["reviewRequired"] is False


def test_sentinel_health_union_dependencies_are_health_only_and_connector_optional():
    source = "SentinelHealth | take 1"
    converted = migrator.convert(source, tables=["SentinelHealth"])

    proposal = dependency_plan(source, target_query=converted["convertedKql"])

    assert converted["targetTables"] == ["SOCHealth", "SentinelHealth"]
    assert proposal["requiredWorkloads"] == [
        {"workload": "mtp", "dataTypes": ["SOCHealth"]},
        {"workload": "sentinel", "dataTypes": ["SentinelHealth"]},
    ]
    assert proposal["requiredDataConnectors"] == []
    assert proposal["reviewRequired"] is False
    from sentinel_xdr_migration.dependencies import CONNECTOR_OPTIONAL_SENTINEL_TABLES
    assert CONNECTOR_OPTIONAL_SENTINEL_TABLES == frozenset({"SentinelHealth"})


@pytest.mark.parametrize("query", [
    "range(0, 10, 1)",
    "range x from 0 to Limit step 1",
    "range x from 0 to {Limit} step 1",
    "range x from 0 to toscalar(DeviceEvents | count) step 1",
    "range x from 0 to HiddenParser() step 1",
    "range x from 0 to 10+1 step 1",
    "range x from 0 to long(10) step 1",
    "range x from datetime(2026-01-01) to now() step 1d",
    "range x from 0 to 10 step 0",
    "range x from 0 to 10 step -1",
    "range x from 10 to 0 step 1",
    "range x from 0 to 10 step 0e1",
    "range x from 0 to 10 step 1e-999",
    "range x from 0 to 1e999 step 1",
    "range x from 0 to 9223372036854775808 step 1",
    "range x from -9223372036854775809 to 0 step 1",
    "range x from NaN to 10 step 1",
    "range x from 0 to 10 step 1;",
    "range x from 0 to 10 step 1 // comment",
    "// range x from 0 to 10 step 1",
    "'range x from 0 to 10 step 1'",
    "range x from 0 to 10 step 1 | project x",
    "range x from 0 to 10 step 1 | union DeviceEvents",
    "union (range x from 0 to 10 step 1), (HiddenParser())",
    "range x from 0 to 10 step 1; DeviceEvents | count",
    "let r = range x from 0 to 10 step 1; r",
    "RANGE x FROM 0 TO 10 STEP 1",
])
def test_nonliteral_or_composite_ranges_do_not_clear_empty_lineage_review(query):
    assert not rewrite.is_source_free_literal_range(query)
    assert not rewrite.is_source_free_literal_query(query)
    assert migrator.convert(query, tables=[])["status"] != "converted"
    assert migrator.convert(query)["status"] != "converted"
    proposal = dependency_plan(query)
    if proposal["dataTypes"]:
        assert proposal["dataTypes"] == ["DeviceEvents"]
        assert proposal["requiredWorkloads"] == [{"workload": "mde", "dataTypes": ["DeviceEvents"]}]
    else:
        assert proposal["reviewRequired"] is True


def test_range_review_preserves_both_hash_bound_parameter_dropdowns(solution):
    path = solution / SOURCE
    document = json.loads(path.read_bytes())
    queries = ["range x from 0 to 10 step 1", "range x from 0 to 20 step 1"]
    hashes = [
        "2ccdaa784725b2a65a8f381ed39f1d053eb36879948ab0bc52508acdc47dbfea",
        "e19eb4f4d503984f28cd04aba8a7975c0ff909046d9c3f980c2033c16aaf61d4",
    ]
    document["items"] = [{"type": 1, "content": {"json": "layout"}} for _ in range(4)]
    parameters = [{"name": f"Placeholder{i}", "type": 1} for i in range(6)]
    parameters.extend({"name": f"Range{i}", "type": 2, "query": query, "queryType": 0}
                      for i, query in enumerate(queries))
    document["items"].append({"type": 9, "content": {"parameters": parameters}})
    path.write_text(json.dumps(document))
    before = path.read_bytes()
    plan = dependencies.plan_workbook_dependencies(solution)
    assert [row["path"] for row in plan["queries"]] == [
        "/items/4/content/parameters/6/query", "/items/4/content/parameters/7/query"]
    assert [row["querySha256"] for row in plan["queries"]] == hashes
    assert all(not row["proposal"]["reviewRequired"] for row in plan["queries"])
    reviewed = decisions(plan)
    for row in reviewed["queries"]:
        row["tables"] = []
    reviewed["workbooks"][0]["requiredWorkloads"] = []
    receipt = review(solution, plan, reviewed)
    assert receipt["unresolved"] == []
    settings = json.loads((solution / "Logs/review-1/conversion-config.json").read_bytes())
    assert convert(solution, settings)["converted"] == 1
    assert workbooks.validate_workbooks(solution)["valid"] == 1
    assert path.read_bytes() == before
    target = json.loads(authored(solution).read_bytes())
    assert [row["node"]["query"] for row in workbook.query_surfaces(target)] == queries
    provenance = target["contentProvenance"]
    assert provenance["requiredWorkloads"] == []
    assert provenance["requiredDataConnectors"] == []
    assert provenance.get("requiredWorkspaceFunctions", []) == []
    assert all(row["conversion"]["resolvedTables"] == []
               for row in provenance["conversion"]["queries"])


@pytest.mark.parametrize("query", [
    "range x from 0 to 10 step 1 | union DeviceEvents",
    "range x from 0 to HiddenParser() step 1",
    "range x from 0 to 10 step 0",
])
def test_range_review_rejects_empty_lineage_for_unsupported_branches(solution, query):
    write_query(solution, query)
    plan = dependencies.plan_workbook_dependencies(solution)
    reviewed = decisions(plan)
    reviewed["queries"][0]["tables"] = []
    reviewed["workbooks"][0]["requiredWorkloads"] = []
    with pytest.raises(ValueError, match="explicit underlying source tables|vetted prerequisites"):
        review(solution, plan, reviewed)
    assert not authored(solution).exists()
    assert not (solution / "Logs/review-1").exists()


def test_saved_function_lineage_static_proposal_remains_unresolved(solution):
    record = function(solution)
    write_query(solution, "let DeviceEvents = Syslog; ReviewedFunction() | count")
    plan = dependencies.plan_workbook_dependencies(solution)
    row = plan["queries"][0]
    assert row["workspaceFunctions"] == [record["functionAlias"]]
    assert row["proposalAccepted"] is False
    assert row["proposal"]["reviewRequired"] is True
    assert "Underlying function tables" in " ".join(row["proposal"]["reviewReasons"])
    assert row["functionPrerequisites"][0]["coverageWarning"]


@pytest.mark.parametrize("decision", ["accept", "change"])
def test_review_writes_supported_config_receipt_not_source_and_converts(solution, decision):
    before = (solution / SOURCE).read_bytes()
    plan = dependencies.plan_workbook_dependencies(solution)
    receipt = review(solution, plan, decisions(plan, decision=decision))
    settings = json.loads((solution / "Logs/review-1/conversion-config.json").read_bytes())
    assert receipt["dependencyReviewRequired"] is False
    assert convert(solution, settings)["converted"] == 1
    assert workbooks.validate_workbooks(solution)["valid"] == 1
    assert (solution / SOURCE).read_bytes() == before
    assert json.loads((solution / "Logs/review-1/workbook-review-receipt.json").read_bytes())["actor"] == "test-reviewer"


def test_defer_cannot_clear_dependency_review(solution):
    plan = dependencies.plan_workbook_dependencies(solution)
    receipt = review(solution, plan, decisions(plan, decision="defer"))
    settings = json.loads((solution / "Logs/review-1/conversion-config.json").read_bytes())
    assert receipt["dependencyReviewRequired"] is True
    assert settings["workbookDependencies"][SOURCE]["dependencyReviewRequired"] is True
    assert convert(solution, settings)["blocked"] == 1


@pytest.mark.parametrize("failure", ["hash", "query", "unknown", "incomplete", "stale-source", "stale-parser", "malformed", "unknown-key"])
def test_review_rejects_stale_malformed_incomplete_before_output_mutation(solution, failure):
    record = function(solution)
    plan = dependencies.plan_workbook_dependencies(solution)
    value = decisions(plan)
    if failure == "hash":
        value["planSha256"] = "0" * 64
    elif failure == "query":
        value["queries"][0]["querySha256"] = "0" * 64
    elif failure == "unknown":
        value["queries"][0]["path"] = "/unknown"
    elif failure == "incomplete":
        value["queries"] = []
    elif failure == "stale-source":
        write_query(solution, "DeviceEvents | take 1")
    elif failure == "stale-parser":
        with (solution / record["sourcePath"]).open("a") as handle:
            handle.write("# source changed\n")
    elif failure == "malformed":
        value["workbooks"][0]["requiredWorkloads"] = "mde"
    else:
        value["queries"][0]["typo"] = True
    with pytest.raises(ValueError):
        review(solution, plan, value)
    assert not (solution / "Logs/review-1").exists()
    assert not authored(solution).exists()


def test_technical_gaps_survive_reviewer_accept(solution):
    write_query(solution, "workspace('elsewhere').DeviceEvents | count")
    plan = dependencies.plan_workbook_dependencies(solution)
    receipt = review(solution, plan, decisions(plan))
    assert receipt["dependencyReviewRequired"] is True
    settings = json.loads((solution / "Logs/review-1/conversion-config.json").read_bytes())
    assert convert(solution, settings)["blocked"] == 1


def test_reviewed_workspace_function_preserves_calls_and_shared_contract(solution):
    record = function(solution)
    raw = "ReviewedFunction({TimeRange:start}, {TimeRange:end}) | count"
    write_query(solution, raw)
    assert convert(solution, config(solution, ["Syslog"]))["blocked"] == 1
    plan = dependencies.plan_workbook_dependencies(solution)
    review(solution, plan, decisions(plan, tables=["Syslog"], functions=[record]))
    settings = json.loads((solution / "Logs/review-1/conversion-config.json").read_bytes())
    assert convert(solution, settings, overwrite=True)["converted"] == 1
    document = json.loads(authored(solution).read_bytes())
    provenance = document["contentProvenance"]
    assert document["items"][0]["content"]["query"] == raw
    assert provenance["requiredWorkspaceFunctions"] == [record]
    assert provenance["conversion"]["queries"][0]["workspaceFunctions"] == ["ReviewedFunction"]
    assert provenance["conversion"]["queries"][0]["conversion"]["resolvedTables"] == ["Syslog"]
    assert workbooks.validate_workbooks(solution)["valid"] == 1
    # Omission cannot forge an ordinary table-only query.
    del provenance["requiredWorkspaceFunctions"]
    del provenance["conversion"]["queries"][0]["workspaceFunctions"]
    authored(solution).write_text(json.dumps(document))
    assert workbooks.validate_workbooks(solution)["invalid"] == 1


@pytest.mark.parametrize("failure", ["stale", "missing-selection", "alias", "extra", "unsafe", "malformed", "duplicate-selection"])
def test_function_prerequisite_failures_block_before_candidate_writes(solution, failure):
    record = function(solution)
    write_query(solution, "ReviewedFunction() | count")
    settings = config(solution, ["Syslog"])
    settings["workbookResolutions"][SOURCE][POINTER]["workspaceFunctions"] = ["ReviewedFunction"]
    settings["workbookDependencies"] = {SOURCE: {
        "requiredWorkspaceFunctions": [deepcopy(record)],
        "requiredWorkloads": [{"workload": "sentinel", "dataTypes": ["Syslog"]}],
        "requiredDataConnectors": []}}
    selected = settings["workbookDependencies"][SOURCE]["requiredWorkspaceFunctions"][0]
    if failure == "stale":
        selected["sourceSha256"] = "0" * 64
    elif failure == "alias":
        selected["functionAlias"] = "OtherFunction"
    elif failure in ("missing-selection", "duplicate-selection"):
        data_path = solution / "Data/Solution_Fixture.json"
        data = json.loads(data_path.read_bytes())
        data["Parsers"] = [] if failure == "missing-selection" else [record["sourcePath"]] * 2
        data_path.write_text(json.dumps(data))
    elif failure == "extra":
        settings["workbookResolutions"][SOURCE][POINTER]["workspaceFunctions"].append("Unexpected")
        assert convert(solution, settings)["blocked"] == 1
        return
    elif failure == "unsafe":
        selected["sourcePath"] = "Parsers/../Data/Solution_Fixture.json"
    else:
        selected["extra"] = True
    with pytest.raises(ValueError):
        convert(solution, settings)
    assert not authored(solution).exists()


def test_standard_builtin_asim_parsers_do_not_require_workspace_function_prerequisites(solution):
    write_query(
        solution,
        "_ASim_NetworkSession | union _Im_Dns(starttime=ago(1d)) | count",
    )
    plan = dependencies.plan_workbook_dependencies(solution)
    row = plan["queries"][0]
    assert row["workspaceFunctions"] == []
    assert row["functionPrerequisites"] == []
    assert not any(
        "Unresolved workspace functions" in reason
        for reason in row["proposal"]["reviewReasons"]
    )

    assert not (solution / "Logs").exists()


def test_optional_branch_removal_is_separate_requested_action_not_rewrite(solution):
    record = function(solution)
    write_query(solution, "ReviewedFunction()")
    plan = dependencies.plan_workbook_dependencies(solution)
    value = decisions(plan, tables=["Syslog"], functions=[record])
    value["queries"][0]["optionalBranches"] = [{**record, "branch": "Syslog | count", "decision": "remove-request"}]
    before = (solution / record["sourcePath"]).read_bytes()
    result = review(solution, plan, value)
    assert result["parserChangeActions"][0]["status"] == "requested-not-applied"
    assert result["dependencyReviewRequired"] is True
    assert (solution / record["sourcePath"]).read_bytes() == before


def test_import_exact_metadata_and_binding_requirements(solution):
    write_query(solution, "DeviceEvents | where Timestamp >= {TimeRange:start}")
    plan = dependencies.plan_workbook_dependencies(solution)
    imported = metadata(plan)
    entry = imported["results"][0]
    entry["bindings"] = {"TimeRange:start": "datetime(2026-01-01T00:00:00Z)"}
    entry["renderedQuery"] = plan["queries"][0]["queryKql"].replace("{TimeRange:start}", entry["bindings"]["TimeRange:start"])
    entry["renderedQuerySha256"] = workbook.query_hash(entry["renderedQuery"])
    current = dependencies.plan_workbook_dependencies(solution, workspace_id="approved-workspace", imported_results=imported)
    assert current["queries"][0]["proposal"]["method"] == "log-analytics"
    assert current["queries"][0]["proposalAccepted"] is False
    assert current["liveQueriesExecuted"] is False


@pytest.mark.parametrize("failure", ["workspace", "source", "query", "error", "partial", "status", "malformed",
                                    "incomplete", "cross-input", "binding", "rendered-hash", "time"])
def test_import_rejects_failed_stale_partial_cross_workspace_unbound_metadata(solution, failure):
    write_query(solution, "DeviceEvents | where Timestamp >= {TimeRange:start}")
    plan = dependencies.plan_workbook_dependencies(solution)
    imported = metadata(plan)
    entry = imported["results"][0]
    entry["bindings"] = {"TimeRange:start": "datetime(2026-01-01T00:00:00Z)"}
    entry["renderedQuery"] = entry["renderedQuery"].replace("{TimeRange:start}", entry["bindings"]["TimeRange:start"])
    entry["renderedQuerySha256"] = workbook.query_hash(entry["renderedQuery"])
    changes = {
        "workspace": ("workspaceId", "another-workspace"), "source": ("workbookSha256", "0" * 64),
        "query": ("querySha256", "0" * 64), "error": ("error", "failed"),
        "partial": ("partial", True), "status": ("statusCode", 403),
        "malformed": ("dataSources", "Syslog"), "binding": ("bindings", {}),
        "rendered-hash": ("renderedQuerySha256", "0" * 64),
        "time": ("timeRange", {"start": "2026-01-03", "end": "2026-01-01"}),
    }
    if failure == "incomplete":
        imported["results"] = []
    elif failure == "cross-input":
        entry["dataSources"][0]["workspaceId"] = "another-workspace"
    else:
        key, value = changes[failure]
        entry[key] = value
    with pytest.raises(ValueError):
        dependencies.plan_workbook_dependencies(solution, workspace_id="approved-workspace", imported_results=imported)
    assert not (solution / "Logs").exists()


def test_cli_pure_json_plan_and_review(solution, capsys):
    assert cli.main(["workbook-dependency-plan", "--solution", str(solution)]) == 0
    plan = json.loads(capsys.readouterr().out)
    assert not (solution / "Logs").exists()
    folder = solution / "Logs/inputs"
    folder.mkdir(parents=True)
    (folder / "plan.json").write_text(json.dumps(plan))
    (folder / "decisions.json").write_text(json.dumps(decisions(plan)))
    assert cli.main([
        "workbook-review", "--solution", str(solution), "--plan", str(folder / "plan.json"),
        "--decisions", str(folder / "decisions.json"), "--plan-sha256", plan["planSha256"],
        "--actor", "reviewer", "--reference", "ticket", "--output-dir", str(solution / "Logs/review"),
    ]) == 0
    assert json.loads(capsys.readouterr().out)["configPath"].endswith("conversion-config.json")


def test_review_symlink_output_and_existing_receipts_are_protected(solution):
    plan = dependencies.plan_workbook_dependencies(solution)
    target = solution / "linked"
    target.symlink_to(solution / "Data", target_is_directory=True)
    with pytest.raises(ValueError, match="symlink"):
        review(solution, plan, decisions(plan), output="linked/review")
    review(solution, plan, decisions(plan))
    before = (solution / "Logs/review-1/workbook-review-receipt.json").read_bytes()
    with pytest.raises(ValueError, match="already exist"):
        review(solution, plan, decisions(plan))
    assert (solution / "Logs/review-1/workbook-review-receipt.json").read_bytes() == before


@pytest.mark.parametrize("query", ["_GetWatchlist('fixture') | count",
                                  "Syslog | invoke _GetWatchlist('fixture')"])
def test_watchlist_is_builtin_not_workspace_installation_prerequisite(solution, query):
    write_query(solution, query)
    plan = dependencies.plan_workbook_dependencies(solution)
    assert plan["queries"][0]["workspaceFunctions"] == []
    assert not any("No current local definition" in text for text in plan["queries"][0]["gapExplanations"])
    settings = config(solution, ["Syslog"])
    settings["workbookDependencies"] = {SOURCE: {
        "requiredWorkloads": [{"workload": "sentinel", "dataTypes": ["Syslog"]}],
        "requiredDataConnectors": []}}
    assert convert(solution, settings)["converted"] == 1
    assert json.loads(authored(solution).read_bytes())["items"][0]["content"]["query"] == query


def test_watchlist_inside_saved_definition_is_not_missing_function(solution):
    record = function(solution)
    path = solution / record["sourcePath"]
    path.write_text("FunctionName: ReviewedFunction\nFunctionQuery: _GetWatchlist('fixture') | count\n")
    assert candidates(solution)[0]["nestedFunctions"] == []


@pytest.mark.parametrize("query,aliases", [
    ("union ReviewedFunction('x','y'), OtherFunction() | count", {"ReviewedFunction", "OtherFunction"}),
    ("union kind=outer (ReviewedFunction()), (OtherFunction()) | count", {"ReviewedFunction", "OtherFunction"}),
    ("DeviceEvents | join (ReviewedFunction()) on Computer", {"ReviewedFunction"}),
    ("let local=(){ReviewedFunction()}; local()", {"ReviewedFunction"}),
    ("let ids=dynamic([1,2]); DeviceEvents | summarize max(tolong(EventCount))", set()),
    ("print x='FakeFunction()' // FakeFunction()\n", set()),
])
def test_alias_inventory_is_tabular_comment_safe_and_complete(query, aliases):
    assert workbook.opaque_functions(query) == aliases


def test_later_union_operand_cannot_be_forged_away(solution):
    record = function(solution)
    write_query(solution, "union ReviewedFunction(), UnreviewedFunction() | count")
    settings = config(solution, ["Syslog"])
    settings["workbookResolutions"][SOURCE][POINTER]["workspaceFunctions"] = ["ReviewedFunction"]
    settings["workbookDependencies"] = {SOURCE: {
        "requiredWorkspaceFunctions": [record],
        "requiredWorkloads": [{"workload": "sentinel", "dataTypes": ["Syslog"]}],
        "requiredDataConnectors": []}}
    assert convert(solution, settings)["blocked"] == 1


@pytest.mark.parametrize("query", ["ReviewedFunction() | count", "_GetWatchlist('fixture') | count"])
def test_explicit_reviewed_watchlist_lineage_is_passthrough_without_catalog_mutation(solution, query):
    record = function(solution) if query.startswith("ReviewedFunction") else None
    write_query(solution, query)
    plan = dependencies.plan_workbook_dependencies(solution)
    from sentinel_xdr_migration._workbook_core import mapping_catalog
    catalog_before = deepcopy(mapping_catalog.load_mapping_catalog())
    value = decisions(plan, tables=["Syslog"], functions=[record] if record else [])
    value["queries"][0]["tables"] = ["Syslog", "Watchlist"]
    value["workbooks"][0]["requiredWorkloads"][0]["dataTypes"] = ["Syslog"]
    result = review(solution, plan, value)
    assert result["dependencyReviewRequired"] is False
    settings = json.loads((solution / "Logs/review-1/conversion-config.json").read_bytes())
    conversion = convert(solution, settings)
    assert conversion["converted"] == 1
    document = json.loads(authored(solution).read_bytes())
    contract = document["contentProvenance"]["conversion"]["queries"][0]["conversion"]
    assert contract["resolvedTables"] == ["Syslog", "Watchlist"]
    assert document["contentProvenance"]["conversion"]["queries"][0]["referenceInputs"] == ["Watchlist"]
    assert document["items"][0]["content"]["query"] == query
    assert workbooks.validate_workbooks(solution)["valid"] == 1
    assert "blank-ah-selection-table-visibility" in {
        gate["code"] for gate in conversion["results"][0]["gates"]}
    assert catalog_before == mapping_catalog.load_mapping_catalog()


@pytest.mark.parametrize("mapping", [{"DeviceEvents": "DeviceEvents"}, {"Watchlist": "Syslog"},
                                    {"Unknown": "Unknown"}, ["Watchlist"]])
def test_reviewed_mapping_cannot_override_catalog_or_source_scope(solution, mapping):
    plan = dependencies.plan_workbook_dependencies(solution)
    value = decisions(plan)
    value["queries"][0]["tableMappings"] = mapping
    with pytest.raises(ValueError):
        review(solution, plan, value)
    assert not (solution / "Logs/review-1").exists()


def test_raw_watchlist_metadata_is_lineage_not_telemetry_prerequisite(solution):
    from sentinel_xdr_migration.dependencies import dependency_plan, workload_records
    raw = [{"tables": ["Syslog", "Watchlist"]}]
    proposal = dependency_plan("Syslog | join _GetWatchlist('fixture') on Computer", metadata=raw)
    assert proposal["returnedDataTypes"] == ["Syslog", "Watchlist"]
    assert proposal["sourceDataTypes"] == ["Syslog", "Watchlist"]
    assert proposal["referenceInputs"] == ["Watchlist"]
    assert proposal["dataTypes"] == proposal["targetDataTypes"] == ["Syslog"]
    assert proposal["requiredWorkloads"] == [{"workload": "sentinel", "dataTypes": ["Syslog"]}]
    assert workload_records(["Watchlist", "UnknownSource"]) == ([], ["UnknownSource"])


def test_watchlist_only_query_requires_no_telemetry_workload_or_connector(solution):
    write_query(solution, "_GetWatchlist('fixture') | count")
    plan = dependencies.plan_workbook_dependencies(solution)
    proposal = plan["queries"][0]["proposal"]
    assert proposal["referenceInputs"] == ["Watchlist"]
    assert proposal["dataTypes"] == proposal["targetDataTypes"] == []
    assert proposal["requiredWorkloads"] == proposal["requiredDataConnectors"] == []
    value = decisions(plan, tables=["Watchlist"])
    value["workbooks"][0]["requiredWorkloads"] = []
    result = review(solution, plan, value)
    assert result["dependencyReviewRequired"] is False
    settings = json.loads((solution / "Logs/review-1/conversion-config.json").read_bytes())
    assert convert(solution, settings)["converted"] == 1
    assert workbooks.validate_workbooks(solution)["valid"] == 1
    provenance = json.loads(authored(solution).read_bytes())["contentProvenance"]
    assert provenance["requiredWorkloads"] == provenance["requiredDataConnectors"] == []
    assert "requiredWorkspaceFunctions" not in provenance


@pytest.mark.parametrize("field", ["requiredWorkloads", "requiredDataConnectors"])
def test_watchlist_cannot_be_declared_as_connector_telemetry(solution, field):
    plan = dependencies.plan_workbook_dependencies(solution)
    value = decisions(plan)
    record = ({"workload": "sentinel", "dataTypes": ["Watchlist"]}
              if field == "requiredWorkloads" else {"connectorId": "Watchlist", "dataTypes": ["Watchlist"]})
    value["workbooks"][0][field] = [record]
    with pytest.raises(ValueError, match="platform reference"):
        review(solution, plan, value)
    assert not (solution / "Logs/review-1").exists()


def test_other_unknown_tables_are_not_hidden_by_platform_reference_classification(solution):
    write_query(solution, "UnknownSource | count")
    plan = dependencies.plan_workbook_dependencies(solution)
    value = decisions(plan, tables=["UnknownSource"])
    value["workbooks"][0]["requiredWorkloads"] = [{"workload": "sentinel", "dataTypes": ["UnknownSource"]}]
    result = review(solution, plan, value)
    assert result["dependencyReviewRequired"] is True
    settings = json.loads((solution / "Logs/review-1/conversion-config.json").read_bytes())
    assert convert(solution, settings)["blocked"] == 1


def test_metadata_time_binding_cannot_misstate_declared_range(solution):
    write_query(solution, "DeviceEvents | where Timestamp >= {TimeRange:start}")
    plan = dependencies.plan_workbook_dependencies(solution)
    imported = metadata(plan)
    entry = imported["results"][0]
    entry["bindings"] = {"TimeRange:start": "datetime(2025-01-01T00:00:00Z)"}
    entry["renderedQuery"] = entry["renderedQuery"].replace("{TimeRange:start}", entry["bindings"]["TimeRange:start"])
    entry["renderedQuerySha256"] = workbook.query_hash(entry["renderedQuery"])
    with pytest.raises(ValueError, match="time bindings"):
        dependencies.plan_workbook_dependencies(solution, workspace_id="approved-workspace", imported_results=imported)


def test_vendored_component_manifest_hashes_are_current():
    import hashlib
    from importlib.resources import files
    root = files("sentinel_xdr_migration._workbook_core")
    manifest = json.loads(root.joinpath("import-manifest.json").read_text())
    for item in manifest["components"]:
        contents = root.joinpath(item["component"]).read_bytes().replace(b"\r\n", b"\n")
        assert hashlib.sha256(contents).hexdigest() == item["sha256"]


@pytest.fixture
def connector_solution(solution):
    root = solution.parent / "Solutions" / "Microsoft Defender for Office 365"
    root.parent.mkdir()
    solution.rename(root)
    folder = root / "Data Connectors"
    folder.mkdir()
    (folder / "template_OfficeATP.json").write_text(json.dumps({
        "id": "ReviewedConnector", "dataTypes": [{"name": "Syslog"}]}))
    write_query(root, "Syslog | count")
    return root


@pytest.mark.parametrize("repository_relative", [False, True])
def test_connector_paths_are_canonical_read_only_and_review_hash_bound(connector_solution, repository_relative):
    root = connector_solution
    relative = "Data Connectors/template_OfficeATP.json"
    reference = f"Solutions/{root.name}/{relative}" if repository_relative else relative
    data_path = root / "Data/Solution_Fixture.json"
    data_path.write_text(json.dumps({"Version": "3.2.2", "Data Connectors": [reference]}))
    before = data_path.read_bytes()
    plan = dependencies.plan_workbook_dependencies(root)
    connector = plan["connectorAlternatives"][0]
    assert connector["sourcePath"] == relative
    assert connector["sourceSha256"] == workbooks._sha((root / relative).read_bytes())
    assert plan["solutionDataSha256"] == dependencies.digest(json.loads(before))
    assert review(root, plan, decisions(plan, tables=["Syslog"]))["dependencyReviewRequired"] is False
    assert data_path.read_bytes() == before

    altered = deepcopy(plan)
    altered["connectorAlternatives"][0]["sourcePath"] = f"Solutions/{root.name}/{relative}"
    altered["planSha256"] = dependencies.digest({k: v for k, v in altered.items() if k != "planSha256"})
    with pytest.raises(ValueError, match="malformed or stale"):
        review(root, altered, decisions(altered, tables=["Syslog"]), output="Logs/altered-review")
    (root / relative).write_text(json.dumps({"id": "Changed", "dataTypes": ["Syslog"]}))
    with pytest.raises(ValueError, match="malformed or stale"):
        review(root, plan, decisions(plan, tables=["Syslog"]), output="Logs/stale-review")
    assert not (root / "Logs/altered-review").exists()
    assert not (root / "Logs/stale-review").exists()


@pytest.mark.parametrize("reference", [
    "Solutions/Other/Data Connectors/template_OfficeATP.json",
    "Solutions/microsoft defender for office 365/Data Connectors/template_OfficeATP.json",
    "Solutions/Microsoft Defender for Office 365/../Data Connectors/template_OfficeATP.json",
    "Solutions/Microsoft Defender for Office 365/Workbooks/nested/fixture.json",
    "Solutions/Microsoft Defender for Office 365/Data Connectors/missing.json",
    "Data Connectors/../Data/Solution_Fixture.json",
    "Data Connectors/./template_OfficeATP.json",
    "Data Connectors//template_OfficeATP.json",
    "Data Connectors/",
    "/Data Connectors/template_OfficeATP.json",
    "C:/Data Connectors/template_OfficeATP.json",
    "C:Data Connectors/template_OfficeATP.json",
    "Data Connectors\\template_OfficeATP.json",
    "../Data Connectors/template_OfficeATP.json",
    None,
])
def test_connector_paths_reject_unsafe_or_non_connector_references(connector_solution, reference):
    data_path = connector_solution / "Data/Solution_Fixture.json"
    data_path.write_text(json.dumps({"Data Connectors": [reference]}))
    with pytest.raises(ValueError):
        dependencies.plan_workbook_dependencies(connector_solution)


def test_repository_relative_connector_requires_solutions_parent(solution):
    with pytest.raises(ValueError):
        dependencies._connectors(solution, {
            "Data Connectors": [f"Solutions/{solution.name}/Data Connectors/connector.json"]})


@pytest.mark.parametrize("repository_relative", [False, True])
@pytest.mark.parametrize("directory", [False, True])
def test_connector_paths_reject_symlinks(connector_solution, repository_relative, directory):
    root = connector_solution
    folder = root / "Data Connectors"
    if directory:
        target = root / "Actual Connectors"
        folder.rename(target)
        folder.symlink_to(target, target_is_directory=True)
        relative = "Data Connectors/template_OfficeATP.json"
    else:
        (folder / "linked.json").symlink_to(folder / "template_OfficeATP.json")
        relative = "Data Connectors/linked.json"
    reference = f"Solutions/{root.name}/{relative}" if repository_relative else relative
    with pytest.raises(ValueError, match="Symlink"):
        dependencies._connectors(root, {"Data Connectors": [reference]})


def test_connector_alternatives_are_not_cumulative_or_title_recommendations(solution):
    folder = solution / "Data Connectors"
    folder.mkdir()
    for identifier, title in (("Legacy", "Modern Agent"), ("Modern", "Older connector")):
        (folder / f"{identifier}.json").write_text(json.dumps({
            "id": identifier, "title": title, "dataTypes": [{"name": "Syslog"}]}))
    data_path = solution / "Data/Solution_Fixture.json"
    data = json.loads(data_path.read_bytes())
    data["Data Connectors"] = ["Data Connectors/Legacy.json", "Data Connectors/Modern.json"]
    data["Description"] = "Reviewed source recommendation: use Modern; legacy agent is deprecated."
    data_path.write_text(json.dumps(data))
    write_query(solution, "Syslog | count")
    plan = dependencies.plan_workbook_dependencies(solution)
    assert {record["connectorId"] for record in plan["connectorAlternatives"]} == {"Legacy", "Modern"}
    assert all(record["recommendation"] is None for record in plan["connectorAlternatives"])
    assert plan["sourceRecommendationEvidence"]["reviewRequired"] is True
    assert plan["sourceRecommendationEvidence"]["titleHeuristicsUsed"] is False
    value = decisions(plan, tables=["Syslog"])
    value["workbooks"][0]["requiredDataConnectors"] = [{"connectorId": "Modern", "dataTypes": ["Syslog"]}]
    result = review(solution, plan, value)
    assert result["dependencyReviewRequired"] is False
    settings = json.loads((solution / "Logs/review-1/conversion-config.json").read_bytes())
    assert settings["workbookDependencies"][SOURCE]["requiredDataConnectors"] == [
        {"connectorId": "Modern", "dataTypes": ["Syslog"]}]


@pytest.mark.parametrize("text", ["[]", "FunctionName: bad-name\nFunctionQuery: Syslog",
                                 "FunctionAlias: 42\nFunctionQuery: Syslog",
                                 "FunctionName: ValidName\nFunctionQuery: ''",
                                 "FunctionName: ValidName\nFunctionQuery: Syslog\nFunctionParams: malformed"])
def test_malformed_workspace_function_definition_is_not_approved(solution, text):
    record = function(solution)
    path = solution / record["sourcePath"]
    path.write_text(text)
    settings = config(solution)
    record["sourceSha256"] = workbooks._sha(path.read_bytes())
    settings["workbookDependencies"] = {SOURCE: {"requiredWorkspaceFunctions": [record]}}
    with pytest.raises(ValueError):
        convert(solution, settings)
    assert not (solution / "Logs").exists()
    assert not authored(solution).exists()


def test_externaldata_is_source_operator_not_workspace_function(solution):
    record = function(solution)
    path = solution / record["sourcePath"]
    path.write_text("FunctionName: ReviewedFunction\nFunctionQuery: externaldata(value:string)['https://example.invalid/reviewed']\n")
    current = candidates(solution)[0]
    assert current["nestedFunctions"] == []
    assert current["externalSourceWarnings"]
    assert current["nestedDiscoveryExhaustive"] is False
    assert workbook.opaque_functions("externaldata(value:string)['https://example.invalid']") == set()


def test_static_nested_union_discovery_reports_unresolved_bare_branches_not_installed_claims(solution):
    record = function(solution)
    path = solution / record["sourcePath"]
    path.write_text("FunctionName: ReviewedFunction\nFunctionQuery: union isfuzzy=true CiscoISEEvent, OtherVendorParser, Syslog\n")
    current = candidates(solution)[0]
    assert current["nestedFunctions"] == []
    assert current["unresolvedBranchCandidates"] == ["CiscoISEEvent", "OtherVendorParser"]
    assert current["nestedDiscoveryExhaustive"] is False


@pytest.mark.parametrize("query", [
    "(ReviewedFunction()) | count",
    "let x = (ReviewedFunction()); x",
    "print toscalar(ReviewedFunction() | summarize count())",
    "print ReviewedFunction()",
    "print tostring(ReviewedFunction())",
    "Syslog | extend x = ReviewedFunction()",
    "Syslog | where Computer == ReviewedFunction()",
    "Syslog | where Computer in (ReviewedFunction())",
    "print (ReviewedFunction())",
    "Syslog | where Computer in ((ReviewedFunction() | project Computer))",
    "find in (ReviewedFunction()) where * has 'x'",
    "search in (ReviewedFunction()) 'x'",
    "find in (ReviewedFunction) where * has 'x'",
    "search in (ReviewedFunction) 'x'",
    "ReviewedFunction | count",
    "(ReviewedFunction) | count",
    "let x = ReviewedFunction; x",
    "let x = (ReviewedFunction); x",
    "let x = materialize(ReviewedFunction | take 1); x",
    "let x = materialize(ReviewedFunction); x",
    "Syslog | where Computer in (ReviewedFunction | project Computer)",
    "Syslog | where Computer in ((ReviewedFunction) | project Computer)",
    "Syslog | where Computer in ( ( ReviewedFunction ) | project Computer)",
    "['ReviewedFunction']() | count",
    '["ReviewedFunction"]() | count',
    "[\n'ReviewedFunction'\n]() | count",
    "print ['ReviewedFunction']()",
    "['ReviewedFunction'] | take 10",
    "union ['ReviewedFunction']",
    "union kind=outer ['ReviewedFunction']",
    "union isfuzzy=true ['ReviewedFunction']",
    "Syslog | invoke ['ReviewedFunction']()",
    "Syslog | invoke ['ReviewedFunction']",
    "table('ReviewedFunction') | take 10",
    "table('ReviewedFunction', 'all') | take 10",
    "table('ReviewedFunction', 'hotcache') | take 10",
    "table('ReviewedFunction', 'default') | take 10",
    "totable('ReviewedFunction') | take 10",
    "totable('ReviewedFunction', 'all') | take 10",
    "let local=(){ReviewedFunction()}; local()",
    "let local=(){ReviewedFunction}; local()",
    "let local=view(){ReviewedFunction}; local()",
    "view() { ReviewedFunction }",
    "Syslog | partition by Computer { ReviewedFunction }",
    "Syslog | fork (ReviewedFunction)",
    "Syslog | fork (['ReviewedFunction'])",
    "Syslog | where Computer has ['ReviewedFunction']()",
    "Syslog | where Computer !has ['ReviewedFunction']()",
    "Syslog | where Computer contains ['ReviewedFunction']()",
    "Syslog | where Computer !contains ['ReviewedFunction']()",
    "Syslog | where Computer startswith ['ReviewedFunction']()",
    "Syslog | where Computer endswith ['ReviewedFunction']()",
    "Syslog | where Computer has_cs ['ReviewedFunction']()",
    "Syslog | where Computer has['ReviewedFunction']()",
    "Syslog | where Computer !has['ReviewedFunction']()",
    "Syslog | where Computer has['ReviewedFunction'] ()",
    "Syslog | where Computer has['ReviewedFunction']\n()",
    "Syslog | where Computer contains['ReviewedFunction']()",
    "Syslog | where Computer !contains['ReviewedFunction']()",
    "Syslog | where Computer startswith['ReviewedFunction']()",
    "Syslog | where Computer endswith['ReviewedFunction']()",
    "Syslog | where Computer has_cs['ReviewedFunction']()",
    "Syslog | distinct ['ReviewedFunction']()",
    "Syslog | distinct['ReviewedFunction']()",
    "Syslog | mv-expand ['ReviewedFunction']()",
    "Syslog | mv-expand['ReviewedFunction']()",
    "print['ReviewedFunction']()",
    "union['ReviewedFunction']",
    "union kind=outer['ReviewedFunction']",
    "union isfuzzy=true['ReviewedFunction']",
    "Syslog | invoke['ReviewedFunction']()",
    "Syslog | invoke['ReviewedFunction']",
    "Syslog | join hint.strategy=broadcast (ReviewedFunction) on Computer",
    "Syslog | join kind=inner hint.strategy=broadcast (ReviewedFunction) on Computer",
    "Syslog | join hint.strategy=shuffle (['ReviewedFunction']) on Computer",
    "Syslog | lookup kind=leftouter hint.strategy=broadcast (ReviewedFunction) on Computer",
    "let local=(){Syslog | where Computer in (ReviewedFunction())}; local()",
    "DeviceEvents | lookup kind=leftouter (ReviewedFunction()) on DeviceId",
    "DeviceEvents | lookup kind=leftouter (ReviewedFunction) on DeviceId",
    "DeviceEvents | join kind = inner (ReviewedFunction) on DeviceId",
    "/* not a KQL comment */ ReviewedFunction() | count",
    "/* ReviewedFunction() */ | count",
])
def test_saved_function_scanner_catches_bypass_forms_and_enforces_review_and_validation(solution, query):
    assert workbook.opaque_functions(query) == {"ReviewedFunction"}
    record = function(solution)
    write_query(solution, query)
    plan = dependencies.plan_workbook_dependencies(solution)
    assert plan["queries"][0]["workspaceFunctions"] == ["ReviewedFunction"]
    bad_decisions = decisions(plan, tables=["Syslog", "DeviceEvents"], functions=[])
    bad_decisions["workbooks"][0]["requiredWorkspaceFunctions"] = []
    with pytest.raises(ValueError, match="Function aliases need vetted prerequisites"):
        review(solution, plan, bad_decisions)
    good_decisions = decisions(plan, tables=["Syslog", "DeviceEvents"], functions=["ReviewedFunction"])
    good_decisions["workbooks"][0]["requiredWorkspaceFunctions"] = [record]
    good_decisions["workbooks"][0]["requiredWorkloads"] = [
        {"workload": "sentinel", "dataTypes": ["Syslog"]},
        {"workload": "mde", "dataTypes": ["DeviceEvents"]},
    ]
    good_decisions["workbooks"][0]["requiredDataConnectors"] = [
        {"connectorId": "FixtureConnector", "dataTypes": ["Syslog", "DeviceEvents"]},
    ]
    review_result = review(solution, plan, good_decisions)
    assert review_result["dependencyReviewRequired"] is False
    settings = json.loads(sorted((solution / "Logs").glob("review-*/conversion-config.json"))[-1].read_bytes())
    assert convert(solution, settings)["converted"] == 1
    assert workbooks.validate_workbooks(solution)["valid"] == 1
    doc = json.loads(authored(solution).read_bytes())
    doc["contentProvenance"].pop("requiredWorkspaceFunctions", None)
    doc["contentProvenance"]["conversion"]["queries"][0].pop("workspaceFunctions", None)
    authored(solution).write_text(json.dumps(doc))
    validation = workbooks.validate_workbooks(solution)
    assert validation["valid"] == 0
    assert any("workspace function" in err.lower() for err in validation["results"][0]["errors"])


@pytest.mark.parametrize("query,token", [
    ("{Fn} | take 10", "{Fn}"),
    ("{Fn}() | take 10", "{Fn}"),
    ("({Fn} | project Computer)", "{Fn}"),
    ("Syslog | where Computer in ({Fn} | project Computer)", "{Fn}"),
    ("{Hidden Func}() | take 10", "{Hidden Func}"),
    ("({Hidden Func} | project Computer)", "{Hidden Func}"),
    ("let x = {Fn}; x | take 10", "{Fn}"),
    ("let x = materialize({Fn} | take 1); x", "{Fn}"),
    ("table({Fn}) | take 10", "{Fn}"),
    ("table(strcat('Le', 'ak')) | take 10", "{__unsupported_table_indirection__}"),
    ("totable(strcat('Le', 'ak')) | take 10", "{__unsupported_table_indirection__}"),
    ("Syslog | join ({Fn}) on Computer", "{Fn}"),
    ("print {Fn}()", "{Fn}"),
])
def test_parameter_built_sources_and_call_targets_fail_closed(solution, query, token):
    assert token in workbook.opaque_functions(query)
    write_query(solution, query)
    plan = dependencies.plan_workbook_dependencies(solution)
    assert token in plan["queries"][0]["workspaceFunctions"]
    bad_decisions = decisions(plan, tables=["Syslog"], functions=[])
    bad_decisions["workbooks"][0]["requiredWorkspaceFunctions"] = []
    with pytest.raises(ValueError):
        review(solution, plan, bad_decisions)
    res = workbook.convert_workbook(json.loads((solution / SOURCE).read_bytes()), tables=["Syslog"])
    assert res["report"]["status"] == "blocked"


@pytest.mark.parametrize("query", [
    "Evil_CL | take 1",
    "union Evil_CL",
    "table('Evil_CL') | take 1",
])
def test_cl_suffix_requires_explicit_reviewed_table_or_function_evidence(solution, query):
    assert workbook.opaque_functions(query) == set()
    write_query(solution, query)
    plan = dependencies.plan_workbook_dependencies(solution)
    assert plan["queries"][0]["workspaceFunctions"] == []
    res_reviewed_table = workbook.convert_workbook(json.loads((solution / SOURCE).read_bytes()), tables=["Evil_CL"])
    assert res_reviewed_table["report"]["queries"][0].get("workspaceFunctions", []) == []


def test_decoy_functions_cannot_satisfy_hint_flags_or_unsupported_table_indirection(solution):
    function(solution)
    decoys = ("hint", "broadcast", "__unsupported_table_indirection__", "__unsupported_escaped_call_context__")
    for alias in decoys:
        p = solution / "Parsers" / "nested" / f"{alias}.yaml"
        p.write_text(f"FunctionName: {alias}\nFunctionAlias: {alias}\nFunctionQuery: Syslog | take 1\n")
    data_file = solution / "Data" / "Solution_Fixture.json"
    data = json.loads(data_file.read_bytes())
    data["Parsers"] = ["Parsers/nested/function.yaml"] + [f"Parsers/nested/{a}.yaml" for a in decoys]
    data_file.write_text(json.dumps(data, indent=2))
    by_alias = {c["functionAlias"]: {k: c[k] for k in ("functionAlias", "sourcePath", "sourceSha256")}
                for c in candidates(solution)}
    decoy_records = [by_alias[a] for a in decoys]
    for query in (
        "Syslog | join hint.strategy=broadcast (ReviewedFunction) on Computer",
        "Syslog | join kind=inner hint.strategy=broadcast (ReviewedFunction) on Computer",
        "Syslog | join hint.strategy=shuffle (['ReviewedFunction']) on Computer",
        "table(strcat('Reviewed', 'Function')) | take 1",
        "print bag['ReviewedFunction']()",
        "Syslog | where isnotempty(todynamic(AdditionalFields)['ReviewedFunction']())",
    ):
        write_query(solution, query)
        plan = dependencies.plan_workbook_dependencies(solution)
        bad_decisions = decisions(plan, tables=["Syslog"], functions=list(decoys))
        for q_dec in bad_decisions["queries"]:
            q_dec["workspaceFunctions"] = list(decoys)
        bad_decisions["workbooks"][0]["requiredWorkspaceFunctions"] = decoy_records
        with pytest.raises(ValueError):
            review(solution, plan, bad_decisions)
        res = workbook.convert_workbook(
            json.loads((solution / SOURCE).read_bytes()),
            tables=["Syslog"],
            allowed_workspace_functions=list(decoys),
        )
        assert res["report"]["status"] == "blocked"


@pytest.mark.parametrize("query", [
    "print bag['Leak']",
    "Syslog | extend v = todynamic(AdditionalFields)['Leak'] | where isnotempty(AdditionalFields['Leak']) and tostring(AdditionalFields['Leak']['nested']) != ''",
    "Syslog | extend ['Activity Count'] = 1 | project ['Activity Count'], [\"ResolutionTime\"] = 2 | order by ['Activity Count'] desc",
    "let LocalView = view() { Syslog }; LocalView()",
    "Syslog | partition by Computer { Syslog | count }",
    "Syslog | fork (Syslog | count)",
    "table('Syslog') | take 1",
    "table('Syslog', 'all') | take 1",
    "totable('Syslog') | take 1",
])
def test_benign_member_indexing_and_catalog_table_controls(query):
    assert workbook.opaque_functions(query) == set()


@pytest.mark.parametrize("query", [
    "union withsource=Table \n (print X=1)",
    "union ISFUZZY=true WITHSOURCE = tAbLe\r\n (print X=1)",
    "union kind=outer withsource=ToTable\n(print X=1)",
])
def test_union_withsource_output_names_are_not_dynamic_table_calls(query):
    assert workbook._quoted_calls_and_table_sources(query) == (set(), set())
    assert workbook.opaque_functions(query) == set()


@pytest.mark.parametrize(("query", "calls", "bare"), [
    ("table(strcat('Device', 'Events'))", {"{__unsupported_table_indirection__}"}, set()),
    ("totable(strcat('Device', 'Events'))", {"{__unsupported_table_indirection__}"}, set()),
    ("table('DeviceEvents')", set(), {"DeviceEvents"}),
    ("totable('DeviceEvents')", set(), {"DeviceEvents"}),
])
def test_dynamic_and_literal_table_calls_keep_existing_scanner_behavior(query, calls, bare):
    assert workbook._quoted_calls_and_table_sources(query) == (calls, bare)
