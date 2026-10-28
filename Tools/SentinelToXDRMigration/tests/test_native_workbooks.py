from __future__ import annotations

from copy import deepcopy
import importlib.util
import json
from pathlib import Path
import shutil
import subprocess
import sys
from uuid import uuid4
import zipfile

import pytest

from sentinel_xdr_migration import cli, native_workbooks as native, workbooks
from sentinel_xdr_migration._workbook_core import workbook

ROOT = Path(__file__).resolve().parents[3]
SOURCE = "Workbook Sources/Native/native.json"


@pytest.fixture
def solution():
    workspace = Path.cwd() / f".native-workbook-test-{uuid4()}"
    root = workspace / "Solutions" / "Sample"
    (root / "Data").mkdir(parents=True)
    (root / "Workbook Sources" / "Native").mkdir(parents=True)
    (root / "Data" / "Solution_Sample.json").write_text(json.dumps({
        "Name": "Sample", "Author": "Synthetic - test@example.invalid",
        "Version": "3.2.2", "Metadata": "SolutionMetadata.json",
        "Description": "Synthetic native workbook import regression.", "XDR Workbooks": [],
    }), encoding="utf-8")
    (root / "SolutionMetadata.json").write_text(json.dumps({
        "name": "Sample", "version": "3.2.2", "trackingId": "pid-native-regression",
        "support": {"name": "Synthetic", "email": "test@example.invalid", "tier": "Community"},
        "categories": {"domains": [], "verticals": []},
    }), encoding="utf-8")
    (root / SOURCE).write_text(json.dumps({
        "version": "Notebook/1.0", "isLocked": False, "fallbackResourceIds": [],
        "$schema": "https://github.com/Microsoft/Application-Insights-Workbooks/blob/master/schema/workbook.json",
        "items": [
            {"type": 1, "content": {"json": "Notice: an ISOC workspace is required for incident visuals."}},
            {"type": 3, "content": {
                "queryType": "advancedHunting",
                "query": "// Preserve CRLF, spacing and Unicode: café\r\nEmailEvents | take  1\r\n",
            }},
            {"type": 9, "content": {"parameters": [{
                "name": "Fixture", "queryType": "advancedHunting",
                "query": 'datatable(Value:string)["literal"]',
            }]}},
        ],
    }, ensure_ascii=False), encoding="utf-8")
    try:
        yield root
    finally:
        shutil.rmtree(workspace)


def reviewed(solution):
    plan = native.plan_native_workbook(solution, SOURCE)
    plan.update(actor="fixture reviewer", reference="offline fixture review")
    for query in plan["queries"]:
        query.update(decision="accept", evidence="Read exact fixture KQL and complete input tables.")
    return plan


def imported(solution):
    return native.import_native_workbook(solution, SOURCE, reviewed(solution))


def candidate(solution):
    return solution / "XDR Workbooks" / "native.json"


def write_source_query(solution, query):
    document = json.loads((solution / SOURCE).read_bytes())
    document["items"][1]["content"]["query"] = query
    (solution / SOURCE).write_text(json.dumps(document), encoding="utf-8")


def test_native_import_preserves_notebook_and_stable_identity(solution):
    original = (solution / SOURCE).read_bytes()
    first = imported(solution)
    raw = candidate(solution).read_bytes()
    document = json.loads(raw)
    assert document["contentProvenance"]["origin"] == "native-xdr"
    assert "conversion" not in document["contentProvenance"]
    payload = {k: v for k, v in document.items() if k not in ("xdrMetadata", "contentProvenance")}
    assert payload == json.loads(original)
    assert (solution / SOURCE).read_bytes() == original
    assert not (solution / "Workbooks").exists()
    assert first["validation"]["invalid"] == 0
    assert imported(solution)["contentId"] == first["contentId"]
    assert candidate(solution).read_bytes() == raw
    other = solution.parent.parent / "relocated" / "Sample"
    shutil.copytree(solution, other)
    assert native.identities(other, SOURCE) == (first["contentId"], first["instanceId"])
    # Identity is source-path based, not query-, file-hash- or release-based.
    write_source_query(solution, "EmailEvents | take 2")
    assert native.identities(solution, SOURCE) == (first["contentId"], first["instanceId"])
    assert workbooks.validate_workbooks(solution, selected_only=True)["invalid"] == 0
    (solution / SOURCE).unlink()
    assert workbooks.validate_workbooks(solution, selected_only=True)["invalid"] == 0
    document = json.loads(candidate(solution).read_bytes())
    document["items"][1]["content"]["query"] += " | take 2"
    candidate(solution).write_text(json.dumps(document), encoding="utf-8")
    assert workbooks.validate_workbooks(solution, selected_only=True)["invalid"] == 1


@pytest.mark.parametrize("mutation", [
    "missing-query", "duplicate-query", "stale-query", "stale-source", "empty-evidence",
    "stale-payload", "defer", "missing-actor", "wrong-tables", "wrong-workload", "connectors",
])
def test_review_is_complete_current_and_explicit(solution, mutation):
    plan = reviewed(solution)
    if mutation == "missing-query":
        plan["queries"].pop()
    elif mutation == "duplicate-query":
        plan["queries"][1] = deepcopy(plan["queries"][0])
    elif mutation == "stale-query":
        plan["queries"][0]["querySha256"] = "0" * 64
    elif mutation == "stale-source":
        plan["source"]["sha256"] = "0" * 64
    elif mutation == "stale-payload":
        plan["canonicalPayloadSha256"] = "0" * 64
    elif mutation == "empty-evidence":
        plan["queries"][0]["evidence"] = " "
    elif mutation == "defer":
        plan["queries"][0]["decision"] = "defer"
    elif mutation == "missing-actor":
        plan["actor"] = ""
    elif mutation == "wrong-tables":
        plan["queries"][0]["tables"] = []
    elif mutation == "wrong-workload":
        plan["requiredWorkloads"][0]["workload"] = "mde"
    else:
        plan["requiredDataConnectors"] = [{"connectorId": "invented", "dataTypes": ["EmailEvents"]}]
    before = (solution / "Data" / "Solution_Sample.json").read_bytes()
    with pytest.raises(ValueError):
        native.import_native_workbook(solution, SOURCE, plan)
    assert not candidate(solution).exists()
    assert (solution / "Data" / "Solution_Sample.json").read_bytes() == before


@pytest.mark.parametrize("query", [
    "UnknownTable | take 1", "UnknownFunction() | take 1",
    "EmailEvents | join (UnknownTable | take 1) on NetworkMessageId",
    "EmailEvents | extend value=UnknownFunction(1)",
    "union EmailEvents, UnknownTable",
    "EmailEvents | join (SecurityIncident | take 1) on Title",
    "let f=(){UnknownTable | take 1}; f()",
    "table('EmailEvents') | take 1", "table({Table}) | take 1",
    "print x=1", "range n from 1 to toscalar(UnknownFunction()) step 1",
    'datatable(x:string)["literal"] | join (UnknownTable) on x',
    "workspace('other').EmailEvents | take 1",
    "_CustomFunction() | take 1", "_CustomSource | take 1",
    "_Im_Test | take 1", "_ASim_Test() | take 1",
    "ASimAuthentication() | take 1",
    "_Im_Authentication | extend x=_CustomFunction()",
    "_Im_Authentication | join (UnknownFunction()) on EventType",
    "_Im_Authentication | union SecurityEvent",
    "_Im_Authentication | extend x=['_CustomFunction']()",
    "union _Im_Authentication, _CustomSource",
    "_ASim_Authentication() | union externaldata(x:string)['https://example.invalid/data']",
    "_Im_Authentication | union cluster('other').database('db').EmailEvents",
    'print x="_Im_Authentication"',
    "print _Im_Authentication=1",
    "// _Im_Authentication\nprint x=1",
])
def test_unknown_functions_tables_and_unproven_empty_lineage_block(solution, query):
    write_source_query(solution, query)
    plan = reviewed(solution)
    assert plan["queries"][0]["blockers"]
    # Removing blockers/claiming empty tables cannot override current discovery.
    plan["queries"][0]["blockers"] = []
    with pytest.raises(ValueError):
        native.import_native_workbook(solution, SOURCE, plan)


@pytest.mark.parametrize("query,tables", [
    ("range n from 1 to 5 step 1", []),
    ('datatable(x:string)["EmailEvents"]', []),
    ("EmailEvents | take 1", ["EmailEvents"]),
    ("let x = EmailEvents | take 1; x | count", ["EmailEvents"]),
    ("EmailEvents | join kind=inner (EmailUrlInfo) on NetworkMessageId", ["EmailEvents", "EmailUrlInfo"]),
    ('let c=toscalar(EmailEvents | count); union withsource=Table (print x=c), (print x=c)', ["EmailEvents"]),
])
def test_strict_recognizers_and_native_source_shapes(solution, query, tables):
    write_source_query(solution, query)
    plan = reviewed(solution)
    assert plan["queries"][0]["tables"] == tables
    assert not plan["queries"][0]["blockers"]
    assert native.import_native_workbook(solution, SOURCE, plan)["validation"]["invalid"] == 0


def test_soc_health_uses_mtp_workload_and_live_schema(solution):
    write_source_query(solution, "SOCHealth | project ResourceId, AdditionalFields | take 1")

    plan = reviewed(solution)

    assert plan["queries"][0]["tables"] == ["SOCHealth"]
    assert plan["queries"][0]["blockers"] == []
    assert plan["requiredWorkloads"] == [{"workload": "mtp", "dataTypes": ["SOCHealth"]}]
    schemas = json.loads(
        (Path(__file__).parents[1]
         / "solution_manager/migration/_workbook_core/data/ah_schema_catalog.json").read_text()
    )
    assert schemas["SOCHealth"]["ResourceId"] == "string"
    assert schemas["SOCHealth"]["AdditionalFields"] == "dynamic"


@pytest.mark.parametrize("query,tables", [
    ("_Im_Authentication | take 1", []),
    ("_ASim_Authentication() | take 1", []),
    ("_ASim_NetworkSession | count", []),
    ("_ASim_NetworkSession(starttime=ago(1d)) | count", []),
    ("_im_Dns() | count", []),
    ("let events = _Im_Authentication; events | count", []),
    ("union _Im_Authentication, _ASim_NetworkSession()", []),
    ("['_ASim_Authentication']() | take 1", []),
    ("_Im_Authentication | union EmailEvents | count", ["EmailEvents"]),
])
def test_builtin_asim_roundtrip_does_not_invent_hidden_dependencies(solution, query, tables):
    write_source_query(solution, query)
    plan = reviewed(solution)
    assert plan["queries"][0]["tables"] == tables
    assert plan["queries"][0]["blockers"] == []
    assert plan["requiredWorkloads"] == (
        [{"workload": "mdo", "dataTypes": ["EmailEvents"]}] if tables else [])
    assert plan["requiredDataConnectors"] == []
    assert native.review_native_workbook(solution, SOURCE, plan) == plan
    result = native.import_native_workbook(solution, SOURCE, plan)
    assert result["runtimeQualified"] is False
    assert result["validation"]["invalid"] == 0
    document = json.loads(candidate(solution).read_bytes())
    assert document["items"][1]["content"]["query"] == query
    assert document["contentProvenance"]["requiredWorkloads"] == plan["requiredWorkloads"]
    (solution / SOURCE).unlink()
    assert workbooks.validate_workbooks(solution, selected_only=True)["invalid"] == 0


@pytest.mark.parametrize("mutation", ["stale-query", "invented-tables", "invented-workload"])
def test_builtin_asim_review_cannot_override_hash_or_dependencies(solution, mutation):
    write_source_query(solution, "_Im_Authentication | take 1")
    plan = reviewed(solution)
    if mutation == "stale-query":
        write_source_query(solution, "_ASim_Authentication() | take 1")
    elif mutation == "invented-tables":
        plan["queries"][0]["tables"] = ["IdentityLogonEvents"]
    else:
        plan["requiredWorkloads"] = [{"workload": "mdi", "dataTypes": ["IdentityLogonEvents"]}]
    with pytest.raises(ValueError):
        native.import_native_workbook(solution, SOURCE, plan)
    assert not candidate(solution).exists()


@pytest.mark.parametrize("source", [
    "../native.json", "Workbook Sources/Native/../../escape.json",
    "Workbook Sources/Native/./native.json", "Workbook Sources/Native//native.json",
    "Workbooks/native.json", "Workbook Sources\\Native\\native.json",
    "Workbook Sources/Native/missing.json", "C:/outside.json",
])
def test_unsafe_or_missing_source_paths_fail(solution, source):
    with pytest.raises(ValueError):
        native.plan_native_workbook(solution, source)


def test_symlink_source_is_rejected(solution):
    link = solution / "Workbook Sources" / "Native" / "link.json"
    try:
        link.symlink_to(solution / SOURCE)
    except OSError as exc:
        pytest.skip(f"Symlink privilege unavailable: {exc}")
    with pytest.raises(ValueError, match="Symlink"):
        native.plan_native_workbook(solution, "Workbook Sources/Native/link.json")


def test_bad_selection_and_existing_identity_are_not_mutated_by_import(solution):
    data_file = solution / "Data" / "Solution_Sample.json"
    data = json.loads(data_file.read_bytes())
    data["XDR Workbooks"] = ["XDR Workbooks/missing.json"]
    data_file.write_text(json.dumps(data), encoding="utf-8")
    previous = data_file.read_bytes()
    with pytest.raises(ValueError, match="Missing workbook"):
        imported(solution)
    assert data_file.read_bytes() == previous
    assert not candidate(solution).exists()
    data["XDR Workbooks"] = []
    data_file.write_text(json.dumps(data), encoding="utf-8")
    imported(solution)
    duplicate = candidate(solution).parent / "duplicate.json"
    duplicate.write_bytes(candidate(solution).read_bytes())
    candidate(solution).unlink()
    data["XDR Workbooks"] = ["XDR Workbooks/duplicate.json"]
    data_file.write_text(json.dumps(data), encoding="utf-8")
    with pytest.raises(ValueError, match="Duplicate"):
        imported(solution)
    assert not candidate(solution).exists()


@pytest.mark.parametrize("provider", [0, "logAnalytics", ""])
def test_native_provider_is_not_converted(solution, provider):
    path = solution / SOURCE
    document = json.loads(path.read_bytes())
    document["items"][1]["content"]["queryType"] = provider
    path.write_text(json.dumps(document), encoding="utf-8")
    assert native.plan_native_workbook(solution, SOURCE)["queries"][0]["blockers"]
    with pytest.raises(ValueError, match="advancedHunting"):
        imported(solution)


@pytest.mark.parametrize("mutation", [
    "query", "notice", "hash", "identity", "duplicate", "migration-origin",
    "payload-hash", "dependency", "review", "review-hash",
])
def test_authored_tampering_fails_closed(solution, mutation):
    imported(solution)
    document = json.loads(candidate(solution).read_bytes())
    if mutation == "query":
        document["items"][1]["content"]["query"] += " | take 2"
    elif mutation == "notice":
        document["items"][0]["content"]["json"] = "changed"
    elif mutation == "hash":
        document["contentProvenance"]["source"]["sha256"] = "0" * 64
    elif mutation == "payload-hash":
        document["contentProvenance"]["canonicalPayloadSha256"] = "0" * 64
    elif mutation == "dependency":
        document["contentProvenance"]["requiredWorkloads"] = []
    elif mutation == "review":
        document["contentProvenance"]["nativeReview"]["queries"][0]["evidence"] = ""
    elif mutation == "review-hash":
        document["contentProvenance"]["nativeReview"]["canonicalPayloadSha256"] = "0" * 64
    elif mutation == "identity":
        document["xdrMetadata"]["contentId"] = str(uuid4())
    elif mutation == "migration-origin":
        document["contentProvenance"].pop("origin")
    else:
        (candidate(solution).parent / "duplicate.json").write_bytes(candidate(solution).read_bytes())
    candidate(solution).write_text(json.dumps(document), encoding="utf-8")
    assert workbooks.validate_workbooks(solution)["invalid"] > 0


@pytest.mark.parametrize("query", ["EmailEvents | take 1", "_Im_Authentication | take 1"])
def test_cli_roundtrip_and_duplicate_json_keys(solution, capsys, query):
    write_source_query(solution, query)
    assert cli.main(["native-workbook-plan", "--solution", str(solution), "--source", SOURCE]) == 0
    plan = json.loads(capsys.readouterr().out)
    plan.update(actor="CLI reviewer", reference="CLI regression")
    for query in plan["queries"]:
        query.update(decision="accept", evidence="Explicit current query review.")
    review = solution / "review.json"
    review.write_text(json.dumps(plan), encoding="utf-8")
    assert cli.main(["native-workbook-review", "--solution", str(solution), "--source", SOURCE,
                     "--review", str(review)]) == 0
    assert json.loads(capsys.readouterr().out) == plan
    assert cli.main(["native-workbook-import", "--solution", str(solution), "--source", SOURCE,
                     "--review", str(review)]) == 0
    capsys.readouterr()
    assert cli.main(["native-workbook-validate", "--solution", str(solution)]) == 0
    write_source_query(solution, "UnknownFunction()")
    assert cli.main(["native-workbook-validate", "--solution", str(solution)]) == 0
    document = json.loads(candidate(solution).read_bytes())
    document["items"][1]["content"]["query"] = "UnknownFunction()"
    candidate(solution).write_text(json.dumps(document), encoding="utf-8")
    assert cli.main(["native-workbook-validate", "--solution", str(solution)]) == 1
    review.write_text('{"queries": [], "queries": []}', encoding="utf-8")
    assert cli.main(["native-workbook-import", "--solution", str(solution), "--source", SOURCE,
                     "--review", str(review)]) == 2


@pytest.mark.skipif(not shutil.which("pwsh"), reason="PowerShell 7 required")
@pytest.mark.parametrize("query", [
    "EmailEvents | take 1", "_Im_Authentication | take 1", "_ASim_NetworkSession() | count",
])
def test_native_only_v31_package_requires_no_sentinel_parent(solution, monkeypatch, query):
    from sentinel_xdr_migration import workbook_publication as public
    monkeypatch.setenv("SENTINEL_XDR_PYTHON", sys.executable)
    content_root = solution.parent.parent
    subprocess.run(["git", "init", "--quiet", str(content_root)], check=True)
    (content_root / ".gitignore").write_text("Solutions/**/Logs/\n", encoding="utf-8")
    write_source_query(solution, query)
    imported(solution)
    rel = candidate(solution).relative_to(solution).as_posix()
    review = public.plan_publication(solution, rel)
    review.update(actor="fixture reviewer", reference="offline fixture publication", decision="accept")
    public.clean_publication(solution, rel, review["inputSha256"], review)
    (solution / SOURCE).unlink()
    result = subprocess.run([
        "pwsh", "-NoLogo", "-NoProfile", "-NonInteractive", "-File",
        str(ROOT / "Tools" / "Create-Azure-Sentinel-Solution" / "V3" / "createSolutionV3_1.ps1"),
        "-SolutionDataFolderPath", str(solution / "Data"), "-ToolkitRootPath", str(ROOT),
        "-VersionMode", "local", "-VersionBump", "none",
        "-ArmValidationMethod", "lab-deployment", "-SkipAttributionLookup",
    ], cwd=content_root, capture_output=True, text=True, encoding="utf-8")
    assert result.returncode == 0, result.stdout + result.stderr
    template = json.loads((solution / "Package" / "mainTemplate.json").read_bytes())
    assert not (solution / "Workbooks").exists()
    assert "DeployWorkbook" not in template["parameters"]
    assert len([r for r in template["resources"]
                if r.get("properties", {}).get("contentKind") == "DefenderWorkbook"]) == 1
    assert not [r for r in template["resources"]
                if r.get("properties", {}).get("contentKind") == "Workbook"]
    from sentinel_xdr_migration.packaging import _verify_workbook_package
    _verify_workbook_package(solution, workbooks.selected_workbook_files(solution), template,
                             next((solution / "Package").glob("*.zip")))


@pytest.mark.skipif(not shutil.which("pwsh"), reason="PowerShell 7 required")
@pytest.mark.parametrize("reviewed_updates", [False, True])
def test_real_v31_mixed_package_and_static_validator(solution, monkeypatch, reviewed_updates):
    from sentinel_xdr_migration import workbook_publication as public
    monkeypatch.setenv("SENTINEL_XDR_PYTHON", sys.executable)
    subprocess.run(["git", "init", "--quiet", str(solution.parent.parent)], check=True)
    (solution.parent.parent / ".gitignore").write_text("Solutions/**/Logs/\n", encoding="utf-8")
    sentinel = solution / "Workbooks" / "sentinel.json"
    sentinel.parent.mkdir()
    source = {"version": "Notebook/1.0", "fromTemplateId": str(uuid4()), "items": [
        {"type": 3, "content": {"queryType": 0, "resourceType": workbook.LA,
                               "query": "DeviceEvents | take 1"}},
    ]}
    sentinel.write_text(json.dumps(source), encoding="utf-8")
    metadata_dir = solution.parent.parent / "Workbooks"
    metadata_dir.mkdir()
    (metadata_dir / "WorkbooksMetadata.json").write_text(json.dumps([{
        "templateRelativePath": "sentinel.json", "workbookKey": source["fromTemplateId"],
        "title": "Sentinel fixture", "description": "Synthetic Sentinel workbook",
        "version": "3.2.0", "dataTypesDependencies": ["DeviceEvents"],
        "dataConnectorsDependencies": [],
    }]), encoding="utf-8")
    conversion = workbooks.convert_workbooks(solution, report_directory=solution / "Logs",
        config={"workbookResolutions": {"Workbooks/sentinel.json": {
            "/items/0/content/query": {
                "querySha256": workbook.query_hash(source["items"][0]["content"]["query"]),
                "tables": ["DeviceEvents"], "evidence": "Reviewed synthetic source",
            }}}})
    assert conversion["converted"] == 1
    data_file = solution / "Data" / "Solution_Sample.json"
    data = json.loads(data_file.read_bytes())
    data.update({"Workbooks": ["Workbooks/sentinel.json"],
                 "XDR Workbooks": ["XDR Workbooks/sentinel.json"]})
    data["Metadata"] = data.pop("Metadata")
    data_file.write_text(json.dumps(data), encoding="utf-8")
    migrated = (solution / "XDR Workbooks" / "sentinel.json").read_bytes()
    imported(solution)
    assert (solution / "XDR Workbooks" / "sentinel.json").read_bytes() == migrated
    if reviewed_updates:
        from sentinel_xdr_migration.workbook_updates import plan_workbook_update, apply_workbook_update
        for path in workbooks.selected_workbook_files(solution):
            baseline = solution / ("baseline-" + path.name)
            baseline.write_bytes(path.read_bytes())
            document = json.loads(path.read_bytes())
            for surface in workbook.query_surfaces(document):
                if not surface["node"]["query"].startswith("datatable("):
                    surface["node"]["query"] += " | take 2"
            document["isLocked"] = True
            path.write_text(json.dumps(document), encoding="utf-8")
            relative = path.relative_to(solution).as_posix()
            review = plan_workbook_update(solution, relative, baseline)
            review.update(actor="fixture reviewer", reference="Reviewed post-import fixes", decision="accept")
            for query in review["changedQueries"]:
                query.update(decision="accept", evidence="Read exact fixture correction and lineage.")
            apply_workbook_update(solution, relative, baseline, review)
            baseline.unlink()
    else:
        for path in workbooks.selected_workbook_files(solution):
            relative = path.relative_to(solution).as_posix()
            review = public.plan_publication(solution, relative)
            review.update(actor="fixture reviewer", reference="offline fixture publication", decision="accept")
            public.clean_publication(solution, relative, review["inputSha256"], review)
    (solution / SOURCE).unlink()
    assert workbooks.validate_workbooks(solution)["invalid"] == 0
    arguments = [
               str(ROOT / "Tools" / "Create-Azure-Sentinel-Solution" / "V3" / "createSolutionV3_1.ps1"),
               "-SolutionDataFolderPath", str(solution / "Data"), "-ToolkitRootPath", str(ROOT),
               "-VersionMode", "local", "-VersionBump", "none",
               "-ArmValidationMethod", "lab-deployment", "-SkipAttributionLookup"]
    def literal(value):
        return "'" + value.replace("'", "''") + "'"
    invocation = "& " + literal(arguments[0]) + " " + " ".join(
        arg if arg.startswith("-") else literal(arg) for arg in arguments[1:])
    command = ["pwsh", "-NoLogo", "-NoProfile", "-NonInteractive", "-Command",
               "try { " + invocation + " } catch { Write-Output $_.ScriptStackTrace; throw }"]
    result = subprocess.run(command, cwd=solution.parent.parent, capture_output=True, text=True, encoding="utf-8")
    assert result.returncode == 0, result.stdout + result.stderr
    template = json.loads((solution / "Package" / "mainTemplate.json").read_bytes())
    resources = template["resources"]
    installs = [r for r in resources if r["type"] == "Microsoft.Resources/deployments"
                and r["name"].startswith("DefenderWorkbook-")]
    registrations = [r for r in resources if r.get("properties", {}).get("contentKind") == "DefenderWorkbook"]
    assert len(installs) == len(registrations) == 2
    sentinel_registrations = [r for r in resources if r.get("properties", {}).get("contentKind") == "Workbook"]
    assert len(sentinel_registrations) == 1
    assert len([r for r in sentinel_registrations[0]["properties"]["mainTemplate"]["resources"]
                if r["type"] == "Microsoft.Insights/workbooks"]) == 1
    document = json.loads(candidate(solution).read_bytes())
    install = next(r for r in installs if
        r["properties"]["template"]["resources"]["workbook"]["properties"]["id"] == document["xdrMetadata"]["instanceId"])
    notebook = install["properties"]["template"]["resources"]["workbook"]["properties"]["content"]
    assert notebook["items"] == document["items"]
    assert "xdrMetadata" not in notebook
    assert set(notebook["contentProvenance"]) == {"packageId", "packageVersion", "contentId", "contentVersion"}
    assert template["parameters"]["DeployDefenderWorkbook"]["defaultValue"] is False
    assert json.loads(data_file.read_bytes())["Version"] == "3.2.2"
    from sentinel_xdr_migration.packaging import _verify_workbook_package
    zip_path = next((solution / "Package").glob("*.zip"))
    _verify_workbook_package(solution, workbooks.selected_workbook_files(solution), template, zip_path)
    with zipfile.ZipFile(zip_path) as archive:
        assert any(name.endswith("mainTemplate.json") for name in archive.namelist())
    spec = importlib.util.spec_from_file_location(
        "native_static_adapter", ROOT / ".script" / "local-validation" / "validate-xdr-content.py")
    adapter = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(adapter)
    static = adapter.validate_solution_xdr_workbooks(solution, solution.parent.parent, ROOT)
    assert all(row["passed"] for row in static["results"]), static
    # The same V3.1 entry point must reject a tampered native query, not merely
    # rely on the caller having run validation previously.
    document["items"][1]["content"]["query"] += " | take 2"
    candidate(solution).write_text(json.dumps(document), encoding="utf-8")
    failed = subprocess.run(command, cwd=solution.parent.parent, capture_output=True, text=True, encoding="utf-8")
    assert failed.returncode != 0
    assert "Native Defender Workbook validation failed" in failed.stdout + failed.stderr
