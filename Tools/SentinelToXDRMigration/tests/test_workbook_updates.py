from copy import deepcopy
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
from uuid import uuid4

import pytest

from sentinel_xdr_migration import cli, workbook_updates as updates, workbooks
from sentinel_xdr_migration import workbook_publication as publication
from test_native_workbooks import (
    solution as native_solution, imported as native_imported, candidate as native_candidate,
)
from test_workbooks import solution as migrated_solution, config, convert, authored

ROOT = Path(__file__).resolve().parents[3]


def powershell_scan(root, path, resources=()):
    script = ROOT / "Tools" / "Create-Azure-Sentinel-Solution" / "common" / "defenderWorkbooks.ps1"
    def literal(value):
        return "'" + str(value).replace("'", "''") + "'"
    command = (
        "$ErrorActionPreference='Stop'; . " + literal(script.with_name("commonFunctions.ps1"))
        + "; . " + literal(script) + "; "
        "$doc=Get-Content -LiteralPath " + literal(path) + " -Raw | ConvertFrom-Json; "
        "$data=Get-Content -LiteralPath " + literal(next((root / "Data").glob("Solution_*.json")))
        + " -Raw | ConvertFrom-Json; $template=" + literal(json.dumps({"resources": list(resources)}))
        + " | ConvertFrom-Json; "
        "Get-DefenderWorkbookParserDependencies -Document $doc -ContentToImport $data "
        "-Template $template -SolutionRoot " + literal(root) + " -SolutionName " + literal(root.name))
    return subprocess.run(
        ["pwsh", "-NoLogo", "-NoProfile", "-NonInteractive", "-Command", command],
        capture_output=True, text=True, encoding="utf-8",
        env={**os.environ, "SENTINEL_XDR_PYTHON": sys.executable})


@pytest.fixture(params=["native", "migrated"])
def update_case(request):
    root = request.getfixturevalue(request.param + "_solution")
    if request.param == "native":
        native_imported(root)
        path, index = native_candidate(root), 1
    else:
        assert convert(root)["converted"] == 1
        path, index = authored(root), 0
    data_path = next((root / "Data").glob("Solution_*.json"))
    data = json.loads(data_path.read_bytes())
    data["XDR Workbooks"] = [path.relative_to(root).as_posix()]
    data_path.write_text(json.dumps(data), encoding="utf-8")
    baseline = root / "external-baseline.json"
    baseline.write_bytes(path.read_bytes())
    old = json.loads(path.read_bytes())
    document = deepcopy(old)
    document["items"][index]["content"]["query"] += " | take 3"
    document["isLocked"] = True
    document["xdrMetadata"]["version"] = "3.2.3"
    path.write_text(json.dumps(document), encoding="utf-8")
    return root, path, baseline, index, old


def accepted(case):
    root, path, baseline, _, _ = case
    plan = updates.plan_workbook_update(root, path.relative_to(root).as_posix(), baseline)
    plan.update(actor="reviewer-fixture", reference="Explicit offline fixture correction review", decision="accept")
    for query in plan["changedQueries"]:
        query.update(decision="accept", evidence="Read exact corrected KQL and current dependency inventory.")
    return plan


def apply(case):
    root, path, baseline, _, _ = case
    return updates.apply_workbook_update(root, path.relative_to(root).as_posix(), baseline, accepted(case))


def test_restores_historical_proof_without_changing_edited_notebook(update_case):
    root, path, baseline, _, old = update_case
    current = json.loads(path.read_bytes())
    if "conversion" in current["contentProvenance"]:
        query = current["contentProvenance"]["conversion"]["queries"][0]
        query["conversion"]["convertedKql"] = "invented manual replacement"
        query["targetSha256"] = "0" * 64
    else:
        current["contentProvenance"]["nativeReview"]["actor"] = "manual replacement"
    path.write_text(json.dumps(current), encoding="utf-8")
    assert workbooks.validate_workbooks(root, selected_only=True)["invalid"] == 1
    applied = apply(update_case)
    assert applied["runtimeQualified"] is False
    result = json.loads(path.read_bytes())
    receipt = json.loads(Path(applied["localReceipt"]).read_bytes())
    review = receipt["evidence"]["review"]
    historical = json.loads(receipt["evidence"]["baselineArtifact"])
    assert historical["contentProvenance"] == old["contentProvenance"]
    assert result["contentProvenance"] == publication.public_document(old)["contentProvenance"]
    assert result["items"] == current["items"]
    assert result["xdrMetadata"] == current["xdrMetadata"]
    assert len(review["changedQueries"]) == 1
    # No external baseline or native raw source is required after apply.
    baseline.unlink()
    for source in (root / "Workbook Sources").rglob("*.json"):
        source.unlink()
    assert workbooks.validate_workbooks(root, selected_only=True)["invalid"] == 0
    assert publication.publication_errors(root, result) == []


@pytest.mark.parametrize("mutation", [
    "query", "settings", "identity", "historical-proof", "baseline-hash", "delta",
    "query-inventory", "dependencies", "metadata", "baseline-raw-hash", "actor",
])
def test_future_tampering_and_staleness_fail(update_case, mutation):
    root, path, _, index, _ = update_case
    applied = apply(update_case)
    document = json.loads(path.read_bytes())
    provenance = document["contentProvenance"]
    receipt_path = Path(applied["localReceipt"])
    receipt = json.loads(receipt_path.read_bytes())
    review = receipt["evidence"]["review"]
    if mutation == "query":
        document["items"][index]["content"]["query"] += " | take 4"
    elif mutation == "settings":
        document["isLocked"] = False
    elif mutation == "identity":
        document["xdrMetadata"]["contentId"] = str(uuid4())
    elif mutation == "historical-proof":
        receipt["evidence"]["baselineArtifact"] += " "
    elif mutation == "baseline-hash":
        review["baseline"]["canonicalDocumentSha256"] = "0" * 64
    elif mutation == "delta":
        review["reversePayloadChanges"] = []
    elif mutation == "query-inventory":
        review["queries"].pop()
    elif mutation == "dependencies":
        provenance["requiredWorkloads"] = []
    elif mutation == "baseline-raw-hash":
        review["baseline"]["sha256"] = "0" * 64
    elif mutation == "actor":
        review["actor"] = "changed"
    else:
        document["xdrMetadata"]["displayName"] += " changed"
    path.write_text(json.dumps(document), encoding="utf-8")
    receipt_path.write_text(json.dumps(receipt), encoding="utf-8")
    assert publication.publication_errors(root, document)


@pytest.mark.parametrize("query", [
    "UnknownTable | take 1", "UnknownFunction() | take 1",
    "EmailEvents | union DeviceEvents", "workspace('other').EmailEvents",
    "EmailEvents | extend x=UnknownFunction(1)",
    "_Im_Authentication | union UnknownTable",
])
def test_unsupported_current_lineage_cannot_be_approved(update_case, query):
    root, path, baseline, index, _ = update_case
    document = json.loads(path.read_bytes())
    document["items"][index]["content"]["query"] = query
    path.write_text(json.dumps(document), encoding="utf-8")
    with pytest.raises(ValueError):
        updates.plan_workbook_update(root, path.relative_to(root).as_posix(), baseline)


@pytest.mark.parametrize("mutation", ["hash", "actor", "query-hash", "table", "evidence", "decision", "proof"])
def test_review_does_not_accept_self_asserted_or_stale_evidence(update_case, mutation):
    root, path, baseline, _, _ = update_case
    review = accepted(update_case)
    before = path.read_bytes()
    if mutation == "hash":
        review["canonicalDocumentSha256"] = "0" * 64
    elif mutation == "actor":
        review["actor"] = " "
    elif mutation == "query-hash":
        review["changedQueries"][0]["querySha256"] = "0" * 64
    elif mutation == "table":
        review["queries"][0]["tables"] = ["Invented"]
    elif mutation == "evidence":
        review["changedQueries"][0]["evidence"] = " "
    elif mutation == "decision":
        review["decision"] = None
    else:
        old = json.loads(baseline.read_bytes())
        old["contentProvenance"]["source"]["sha256"] = "0" * 64
        baseline.write_text(json.dumps(old), encoding="utf-8")
    with pytest.raises(ValueError):
        updates.apply_workbook_update(root, path.relative_to(root).as_posix(), baseline, review)
    assert path.read_bytes() == before


def test_recomputed_hashes_do_not_override_discovered_dependencies(update_case):
    root, path, _, index, old = update_case
    applied = apply(update_case)
    document = json.loads(path.read_bytes())
    receipt_path = Path(applied["localReceipt"])
    receipt = json.loads(receipt_path.read_bytes())
    document["items"][index]["content"]["query"] = "UnknownTable | take 1"
    receipt["canonicalDocumentSha256"] = publication.digest(document)
    receipt["evidence"]["publicDocument"] = document
    receipt.pop("receiptSha256")
    receipt["receiptSha256"] = publication.digest(receipt)
    new_receipt = publication._receipt_path(root, document)
    new_receipt.write_text(json.dumps(receipt), encoding="utf-8")
    path.write_text(json.dumps(document), encoding="utf-8")
    result = workbooks.validate_workbooks(root, selected_only=True)
    assert result["invalid"] == 1
    assert any("UnknownTable" in error for error in result["results"][0]["errors"])
    assert publication.publication_errors(root, document)


def test_replacement_conversion_receipt_cannot_be_used_as_original_baseline(migrated_solution):
    root = migrated_solution
    convert(root)
    path = authored(root)
    document = json.loads(path.read_bytes())
    query = document["contentProvenance"]["conversion"]["queries"][0]
    raw = document["items"][0]["content"]["query"] + " | take 3"
    document["items"][0]["content"]["query"] = raw
    query["targetSha256"] = updates.workbook.query_hash(raw)
    query["conversion"]["convertedKql"] = raw
    baseline = root / "fabricated-baseline.json"
    baseline.write_text(json.dumps(document), encoding="utf-8")
    path.write_text(json.dumps(document), encoding="utf-8")
    with pytest.raises(ValueError, match="deterministic conversion"):
        updates.plan_workbook_update(root, path.relative_to(root).as_posix(), baseline)


def test_builtin_asim_lineage_is_explicit_without_inventing_hidden_tables(update_case):
    root, path, _, index, _ = update_case
    document = json.loads(path.read_bytes())
    document["items"][index]["content"]["query"] = "_Im_Authentication | take 1"
    path.write_text(json.dumps(document), encoding="utf-8")
    review = accepted(update_case)
    assert review["queries"][0]["builtinAsimParsers"] == ["_Im_Authentication"]
    assert review["queries"][0]["tables"] == []
    apply(update_case)
    assert workbooks.validate_workbooks(root, selected_only=True)["invalid"] == 0


def test_added_and_removed_queries_and_second_review(update_case):
    root, path, baseline, _, old = update_case
    document = json.loads(path.read_bytes())
    document["items"].insert(0, {"type": 3, "content": {
        "queryType": "advancedHunting", "query": 'datatable(x:string)["reviewed literal"]'}})
    path.write_text(json.dumps(document), encoding="utf-8")
    review = accepted(update_case)
    assert any(q["baselineQuerySha256"] is None for q in review["changedQueries"])
    apply(update_case)
    assert workbooks.validate_workbooks(root, selected_only=True)["invalid"] == 0
    document = json.loads(path.read_bytes())
    document["items"] = [{"type": 1, "content": {"json": "All original query panels removed."}}]
    path.write_text(json.dumps(document), encoding="utf-8")
    review = accepted(update_case)
    assert len(review["changedQueries"]) == len(list(
        updates.workbook.query_surfaces(old)))
    assert all(q["querySha256"] is None for q in review["changedQueries"])
    apply(update_case)
    assert workbooks.validate_workbooks(root, selected_only=True)["invalid"] == 0


def test_cli_plan_review_apply(update_case, capsys):
    root, path, baseline, _, _ = update_case
    args = ["--solution", str(root), "--content", path.relative_to(root).as_posix(),
            "--baseline", str(baseline)]
    assert cli.main(["workbook-update-plan", *args]) == 0
    assert json.loads(capsys.readouterr().out)["decision"] is None
    review_file = root / "review.json"
    review_file.write_text(json.dumps(accepted(update_case)), encoding="utf-8")
    for operation in ("review", "apply"):
        assert cli.main(["workbook-update-" + operation, *args, "--review", str(review_file)]) == 0
        capsys.readouterr()
    assert workbooks.validate_workbooks(root, selected_only=True)["invalid"] == 0


@pytest.mark.parametrize("function_query", [False, True])
def test_migrated_sentinel_tables_and_workspace_functions_remain_supported(migrated_solution, function_query):
    from test_workbook_dependencies import (
        function, write_query, decisions, review, dependencies,
    )
    root = migrated_solution
    if function_query:
        record = function(root)
        write_query(root, "ReviewedFunction() | count")
        plan = dependencies.plan_workbook_dependencies(root)
        review(root, plan, decisions(plan, tables=["Syslog"], functions=[record]))
        settings = json.loads((root / "Logs/review-1/conversion-config.json").read_bytes())
        expected_tables, expected_functions = [], ["ReviewedFunction"]
    else:
        write_query(root, "SecurityIncident | take 1")
        settings = config(root, ["SecurityIncident"])
        settings["workbookDependencies"] = {"Workbooks/nested/fixture.json": {
            "requiredWorkloads": [{"workload": "sentinel", "dataTypes": ["SecurityIncident"]}],
            "requiredDataConnectors": [{"connectorId": "ReviewedSentinel", "dataTypes": ["SecurityIncident"]}],
        }}
        expected_tables, expected_functions = ["SecurityIncident"], []
    assert convert(root, settings)["converted"] == 1
    path = authored(root)
    old = json.loads(path.read_bytes())
    baseline = root / "baseline.json"
    baseline.write_bytes(path.read_bytes())
    document = deepcopy(old)
    document["items"][0]["content"]["query"] += " | take 2"
    path.write_text(json.dumps(document), encoding="utf-8")
    case = root, path, baseline, 0, old
    plan = accepted(case)
    assert plan["queries"][0]["tables"] == expected_tables
    assert plan["queries"][0]["workspaceFunctions"] == expected_functions
    apply(case)
    assert workbooks.validate_workbooks(root)["invalid"] == 0
    if shutil.which("pwsh"):
        resources = ([{
            "type": "Microsoft.OperationalInsights/workspaces/savedSearches",
            "name": "workspace/ReviewedFunction",
            "properties": {"functionAlias": "ReviewedFunction", "query": "Syslog | count",
                           "functionParameters": ""},
        }] if function_query else [])
        result = powershell_scan(root, path, resources)
        assert result.returncode == 0, result.stdout + result.stderr
        if function_query:
            missing = powershell_scan(root, path)
            assert missing.returncode != 0
            normalized_stderr = " ".join(
                re.sub(r"\x1b\[[0-9;]*m", "", missing.stderr).replace("|", " ").split()
            )
            assert "requires exactly one emitted top-level savedSearch" in normalized_stderr
    if function_query:
        with (root / record["sourcePath"]).open("a", encoding="utf-8") as handle:
            handle.write("\n# changed dependency")
        assert workbooks.validate_workbooks(root)["invalid"] == 1


@pytest.mark.skipif(not shutil.which("pwsh"), reason="PowerShell 7 required")
def test_powershell_assert_and_dependency_scan_use_current_review(update_case):
    root, path, _, index, _ = update_case
    apply(update_case)
    result = powershell_scan(root, path)
    assert result.returncode == 0, result.stdout + result.stderr
    document = json.loads(path.read_bytes())
    document["items"][index]["content"]["query"] += " | take 8"
    path.write_text(json.dumps(document), encoding="utf-8")
    result = powershell_scan(root, path)
    assert result.returncode != 0


@pytest.mark.parametrize("complete_dependencies", [False, True])
def test_migrated_hybrid_queries_preserve_historical_sentinel_lineage(migrated_solution, complete_dependencies):
    from test_workbook_dependencies import write_query
    root = migrated_solution
    raw = (
        'let alerts = SecurityAlert | project SystemAlertId; '
        'let incidents = materialize(SecurityIncident '
        '| join kind=inner (alerts) on $left.AlertId == $right.SystemAlertId); '
        'incidents | count'
    )
    write_query(root, raw)
    tables = ["SecurityAlert", "SecurityIncident"] if complete_dependencies else ["SecurityAlert"]
    settings = config(root, tables)
    settings["workbookDependencies"] = {"Workbooks/nested/fixture.json": {
        "requiredWorkloads": [{"workload": "sentinel", "dataTypes": tables}],
        "requiredDataConnectors": [{"connectorId": "MicrosoftThreatProtection", "dataTypes": tables}],
    }}
    assert convert(root, settings)["converted"] == 1
    path = authored(root)
    baseline = root / "baseline-hybrid.json"
    baseline.write_bytes(path.read_bytes())
    old = json.loads(path.read_bytes())
    current = deepcopy(old)
    current["items"][0]["content"]["query"] += " | take 2"
    path.write_text(json.dumps(current), encoding="utf-8")
    case = root, path, baseline, 0, old
    plan = accepted(case)
    assert plan["queries"][0]["tables"] == ["SecurityAlert", "SecurityIncident"]
    if not complete_dependencies:
        with pytest.raises(ValueError, match="Unknown or non-native"):
            apply(case)
        # Legacy historical exceptions stay in local proof. Publication needs
        # explicit complete public prerequisites, not an inherited waiver.
        legacy = deepcopy(current)
        legacy["contentProvenance"]["authoredReview"] = updates.review_workbook_update(
            root, path.relative_to(root).as_posix(), baseline, plan)
        assert updates.validate_updated_document(root, legacy) == []
        path.write_text(json.dumps(legacy), encoding="utf-8")
        clean_review = publication.plan_publication(root, path.relative_to(root).as_posix())
        clean_review.update(actor="fixture reviewer", reference="Explicit complete prerequisites", decision="accept")
        assert clean_review["dependencyErrors"]
        unchanged = path.read_bytes()
        with pytest.raises(ValueError, match="connector coverage"):
            publication.clean_publication(root, path.relative_to(root).as_posix(),
                                          clean_review["inputSha256"], clean_review)
        assert path.read_bytes() == unchanged
        clean_review["dependencies"]["requiredDataConnectors"][0]["dataTypes"].append("SecurityIncident")
        publication.clean_publication(root, path.relative_to(root).as_posix(),
                                      clean_review["inputSha256"], clean_review)
    else:
        apply(case)
    updated = json.loads(path.read_bytes())
    assert "authoredReview" not in updated["contentProvenance"]
    assert workbooks.validate_workbooks(root)["invalid"] == 0
    if shutil.which("pwsh"):
        result = powershell_scan(root, path)
        assert result.returncode == 0, result.stdout + result.stderr
    for replacement in (
        raw + " | union SecurityEvent",
        raw.replace("SecurityIncident", "SecurityEvent"),
    ):
        current["items"][0]["content"]["query"] = replacement
        path.write_text(json.dumps(current), encoding="utf-8")
        with pytest.raises(ValueError):
            accepted(case)
    if not complete_dependencies:
        current["items"][0]["content"]["query"] = raw
        current["items"].append(deepcopy(current["items"][0]))
        path.write_text(json.dumps(current), encoding="utf-8")
        with pytest.raises(ValueError):
            accepted(case)


def test_migrated_sentinel_query_requires_explicit_connector_coverage(migrated_solution):
    from test_workbook_dependencies import write_query
    root = migrated_solution
    write_query(root, "SecurityAlert | take 1")
    settings = config(root, ["SecurityAlert"])
    settings["workbookDependencies"] = {"Workbooks/nested/fixture.json": {
        "requiredWorkloads": [{"workload": "sentinel", "dataTypes": ["SecurityAlert"]}],
        "requiredDataConnectors": [],
    }}
    assert convert(root, settings)["converted"] == 1
    path = authored(root)
    baseline = root / "baseline-no-connector.json"
    baseline.write_bytes(path.read_bytes())
    with pytest.raises(ValueError, match="connector coverage"):
        updates.plan_workbook_update(root, path.relative_to(root).as_posix(), baseline)
