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

PICKER = ("Syslog\r\n| summarize syslogEventsCount = count() by Computer\r\n"
          "| sort by syslogEventsCount desc\r\n| project Computer\r\n")


@pytest.fixture
def scratch():
    path = Path.cwd() / f".workbook-mock-test-{uuid4()}"
    path.mkdir()
    try:
        yield path
    finally:
        shutil.rmtree(path)


@pytest.fixture
def config():
    return mock.configuration(42, mock.DEFAULT_CLOCK, 1, "syslog-operational-v1")


@pytest.fixture
def source(scratch):
    path = scratch / "source.json"
    path.write_bytes(mock.json_bytes({
        "version": "Notebook/1.0", "items": [{"type": 9, "content": {
            "parameters": [{"name": "Computer", "query": PICKER, "queryType": 0}]
        }}],
    }))
    return path


@pytest.fixture
def real_source():
    return FIXTURES / "sources/Syslog/Workbooks/LinuxMachines.json"


def test_deterministic_generation_actual_rows_and_source_unchanged(source, scratch, config):
    before = source.read_bytes()
    first, second = scratch / "one", scratch / "two"
    report = mock.generate(source, first, config)
    mock.generate(source, second, config)
    assert report["rows"] == 240
    assert report["cases"] == 10
    assert report["harnesses"] == 22
    assert source.read_bytes() == before
    one = {p.relative_to(first): p.read_bytes() for p in first.rglob("*") if p.is_file()}
    two = {p.relative_to(second): p.read_bytes() for p in second.rglob("*") if p.is_file()}
    assert one == two
    assert mock.validate(source, first)["status"] == "offline-checks-passed"
    manifest = json.loads(one[Path("manifest.json")])
    table = manifest["tables"]["Syslog"]
    records = json.loads(one[Path("tables/Syslog.json")])
    assert records == [dict(zip(table["schema"], row)) for row in table["rows"]]
    stub = mock.dataframes.datatable_stub("Syslog", table["schema"], rows=table["rows"])
    for case in manifest["cases"]:
        for side in ("sentinel", "ah"):
            text = one[Path(f"harnesses/{case['id']}.{side}.kql")].decode()
            assert stub in text
            assert PICKER in text
            assert not case.get("tableTimeRanges")
    assert manifest["ingestion"]["payload"] is None
    assert not manifest["ingestion"]["directLogsIngestionSupported"]
    guard = json.loads(one[Path("tables/scenario.json")])
    assert guard["generationStatus"] == "table-fixture-only"
    assert not any(name.name in {"mock.json", "malicious.json", "benign.json"} for name in one)


def test_seed_scale_clock_and_shared_correlations(config):
    rows = recipes.syslog_rows(42, config["clock"], 1, "unit")
    assert rows == recipes.syslog_rows(42, config["clock"], 1, "unit")
    assert rows != recipes.syslog_rows(43, config["clock"], 1, "unit")
    assert len(recipes.syslog_rows(42, config["clock"], 2, "unit")) == 438
    shifted = recipes.syslog_rows(42, "2026-10-08T12:00:00Z", 1, "unit")
    for a, b in zip(rows, shifted):
        assert recipes.instant(b["TimeGenerated"]) - recipes.instant(a["TimeGenerated"]) == timedelta(days=1)
        assert a["EventTime"] == a["TimeGenerated"]
    assert Counter(row["Computer"] for row in rows) == {
        "mock-unit-1": 40, "mock-unit-2": 80, "mock-unit-3": 120}
    for host in {row["Computer"] for row in rows}:
        group = [row for row in rows if row["Computer"] == host]
        assert len({(row["HostIP"], row["_ResourceId"], row["HostName"]) for row in group}) == 1
        for process in {row["ProcessName"] for row in group}:
            assert len({row["ProcessID"] for row in group if row["ProcessName"] == process}) == 1
    assert {row["SeverityLevel"] for row in rows} == set(recipes.SEVERITIES)
    assert {row["Facility"] for row in rows} == {"cron", "daemon", "authpriv", "kern"}


@pytest.mark.parametrize("column,value", [
    ("ProcessID", True), ("ProcessID", "1"), ("ProcessID", 2**31),
    ("Computer", None), ("Computer", 9), ("TimeGenerated", "tomorrow"),
    ("TimeGenerated", "2026-01-01T12:00:00"), ("TimeGenerated", "2026-01-01T12:00:00+01:00"),
])
def test_strict_destination_types(column, value):
    schema = recipes.SYSLOG_SCHEMA
    record = recipes.syslog_rows(42, mock.DEFAULT_CLOCK, 1, "unit")[0]
    record[column] = value
    with pytest.raises(ValueError, match="invalid"):
        mock.validate_rows("Syslog", schema, [[record[c] for c in schema]] * 2)


def test_schema_drift_and_missing_schema_fail_closed(monkeypatch):
    monkeypatch.setattr(mock.dataframes, "schema_for", lambda *args: None)
    with pytest.raises(ValueError, match="schema"):
        mock.validate_rows("Syslog", recipes.SYSLOG_SCHEMA, [])


def test_precise_aggregates_cells_and_time_bins():
    rows = recipes.syslog_rows(42, mock.DEFAULT_CLOCK, 1, "unit")
    choices = {choice["id"]: choice for choice in recipes.selections(rows, mock.DEFAULT_CLOCK)}
    severity = recipes.expected_result(recipes.QueryContract("severity"), rows, choices["all-literal"])
    assert {row[0]: row[1] for row in severity["rows"]} == {
        "emerg": 36, "panic": 6, "alert": 12, "crit": 18, "err": 12, "error": 6,
        "warning": 24, "warn": 12, "notice": 30, "info": 48, "debug": 18, "unknown": 6,
    }
    boundary = recipes.expected_result(recipes.QueryContract("emerg"), rows, choices["end-boundary"])
    assert boundary["rows"] == [[f"mock-unit-{i}", mock.DEFAULT_CLOCK, i] for i in range(1, 4)]
    picker = recipes.expected_result(recipes.QueryContract("computers", parameter=True, time_parameter=None),
                                     rows, choices["empty-time"])
    assert picker["ordered"]
    assert picker["rows"] == [["mock-unit-3"], ["mock-unit-2"], ["mock-unit-1"]]
    empty = recipes.expected_result(recipes.QueryContract("events"), rows, choices["all-literal"])
    assert empty["rows"] == []
    events = recipes.expected_result(recipes.QueryContract("events"), rows, choices["end-boundary"])
    assert len(events["rows"]) == 6
    assert events["columns"][3] == {"name": "SeverityNumber", "type": "long"}
    assert [mock.DEFAULT_CLOCK, "mock-unit-1", "emerg", 0, "kern", "192.0.2.10", "kernel (-)"] in events["rows"]
    assert "/subscriptions/00000000-" in events["rows"][1][1]
    # Independent epoch-floor oracle, not the implementation's replace() binning.
    expected_bins = Counter()
    for row in rows:
        timestamp = datetime.fromisoformat(row["TimeGenerated"].replace("Z", "+00:00")).timestamp()
        hour = datetime.fromtimestamp((int(timestamp) // 3600) * 3600, timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        expected_bins[row["Computer"], hour] += 1
    actual_bins = recipes.hourly_result(rows)
    assert actual_bins["rows"] == [[*key, count] for key, count in sorted(expected_bins.items())]
    for i in range(1, 4):
        assert [f"mock-unit-{i}", "2026-10-07T05:00:00Z", i] in actual_bins["rows"]
        assert [f"mock-unit-{i}", "2026-10-07T12:00:00Z", i * 2] in actual_bins["rows"]
    wrong_bins = copy.deepcopy(actual_bins)
    wrong_bins["rows"][0][1] = "2026-10-07T04:00:00Z"
    with pytest.raises(AssertionError, match="time-bin"):
        workbook_fixtures.assert_result(actual_bins, wrong_bins)


def test_independent_multiple_selection_message_process_and_facility_aggregates():
    rows = recipes.syslog_rows(42, mock.DEFAULT_CLOCK, 1, "unit")
    selection = next(c for c in recipes.selections(rows, mock.DEFAULT_CLOCK) if c["id"] == "multiple")
    # Warning/Error records are generated strictly inside the six-hour window.
    filtered = [r for r in rows if r["Computer"] in ("mock-unit-1", "mock-unit-2")
                and r["SeverityLevel"] in ("warning", "warn", "error", "err")]
    assert len(filtered) == 27
    for kind, keys in (("messages", ("SyslogMessage",)), ("facilities", ("Facility", "SeverityLevel")),
                       ("processes", ("Facility", "ProcessName"))):
        counts = Counter(tuple(r[k] for k in keys) for r in filtered)
        expected = [[*key, count] for key, count in sorted(counts.items())]
        if kind == "processes":
            expected = [[f"{process} ({facility})", count] for facility, process, count in expected]
        actual = recipes.expected_result(recipes.QueryContract(kind), rows, selection)
        assert actual["rows"] == expected
        assert sum(row[-1] for row in actual["rows"]) == 27


def test_assertions_reject_same_shape_wrong_values_duplicates_and_sort():
    rows = recipes.syslog_rows(42, mock.DEFAULT_CLOCK, 1, "unit")
    selection = recipes.selections(rows, mock.DEFAULT_CLOCK)[1]
    expected = recipes.expected_result(recipes.QueryContract("severity"), rows, selection)
    reversed_rows = {"columns": expected["columns"], "rows": list(reversed(expected["rows"]))}
    with pytest.raises(AssertionError, match="sort-group"):
        workbook_fixtures.assert_result(expected, reversed_rows)
    actual = copy.deepcopy(expected)
    actual["rows"][0][1] += 1
    with pytest.raises(AssertionError, match="Cell"):
        workbook_fixtures.assert_result(expected, actual)
    actual = copy.deepcopy(expected)
    actual["rows"][0] = actual["rows"][1]
    with pytest.raises(AssertionError, match="Cell"):
        workbook_fixtures.assert_result(expected, actual)
    expected["rows"][0], expected["rows"][1] = expected["rows"][1], expected["rows"][0]
    workbook_fixtures.assert_result(expected, expected)  # ties may be permuted


@pytest.mark.parametrize("changed", [
    {"seed": -1}, {"seed": True}, {"seed": 2**32}, {"scale": 0}, {"scale": 11},
    {"clock": "now"}, {"clock": "2026-13-01T12:00:00Z"},
    {"clock": "2026-01-01T12:00:00+00:00"}, {"recipe": "generic"},
    {"runId": "../escape"}, {"runId": "x';take 1"},
])
def test_invalid_configuration(config, changed):
    config.update(changed)
    with pytest.raises(ValueError):
        mock.configuration(config["seed"], config["clock"], config["scale"], config["recipe"], config["runId"])


@pytest.mark.parametrize("query", [
    "UnknownTable | count", "Syslog | count", "SyslogConnectorsOverallStatus()",
    "Syslog | join (Heartbeat) on Computer", PICKER + " ",
])
def test_unsupported_queries_block_without_writes(source, scratch, config, query):
    doc = json.loads(source.read_bytes())
    doc["items"][0]["content"]["parameters"][0]["query"] = query
    source.write_bytes(mock.json_bytes(doc))
    with pytest.raises(mock.Blocked, match="reviewed mock contract"):
        mock.generate(source, scratch / "blocked", config)
    assert not (scratch / "blocked").exists()


def test_inherited_unreviewed_time_context_is_not_silently_ignored(source, config):
    doc = json.loads(source.read_bytes())
    doc["timeContextFromParameter"] = "UnreviewedInheritedWindow"
    with pytest.raises(mock.Blocked):
        mock.build(mock.json_bytes(doc), config)


def test_artifact_tampering_and_collision(source, scratch, config):
    out = scratch / "bundle"
    mock.generate(source, out, config)
    before = (out / "manifest.json").read_bytes()
    with pytest.raises(ValueError, match="new directory"):
        mock.generate(source, out, config)
    assert (out / "manifest.json").read_bytes() == before
    harness = next((out / "harnesses").glob("*.kql"))
    harness.write_text(harness.read_text().replace('datatable(', 'datatable(Bogus:string, ', 1))
    with pytest.raises(ValueError, match="regeneration mismatch"):
        mock.validate(source, out)


def test_source_and_oracle_drift_detected(source, scratch, config):
    out = scratch / "bundle"
    mock.generate(source, out, config)
    source.write_bytes(source.read_bytes() + b"\n")
    with pytest.raises(ValueError, match="regeneration mismatch"):
        mock.validate(source, out)
    source.write_bytes(source.read_bytes()[:-1])
    manifest_path = out / "manifest.json"
    manifest = json.loads(manifest_path.read_bytes())
    manifest["cases"][0]["expected"]["rows"][0][0] = "WRONG"
    manifest_path.write_bytes(mock.json_bytes(manifest))
    with pytest.raises(ValueError, match="regeneration mismatch"):
        mock.validate(source, out)


def test_real_linux_all_panels_and_all_selection_cases(real_source, scratch, config):
    before = real_source.read_bytes()
    out = scratch / "linux"
    report = mock.generate(real_source, out, config)
    assert report["cases"] == 100
    assert report["harnesses"] == 202
    assert mock.validate(real_source, out)["status"] == "offline-checks-passed"
    manifest = json.loads((out / "manifest.json").read_bytes())
    assert len(manifest["inventory"]) == 10
    assert sum(item["parameter"] for item in manifest["inventory"]) == 1
    for case in manifest["cases"]:
        if case["sourcePath"].endswith("/parameters/1/query"):
            assert len(case["expected"]["rows"]) == 3
            assert "tableTimeRanges" not in case
        else:
            text = (out / f"harnesses/{case['id']}.ah.kql").read_text()
            assert "| where TimeGenerated between (datetime(" in text
            assert text.index("| where TimeGenerated between") < text.index("\nSyslog")
            assert "{Computer" not in text and "{Severity}" not in text
        if case["sourcePath"] == "/items/6/content/query":
            if case["selection"]["id"] in ("all-literal", "empty-computers", "empty-severity", "empty-time"):
                assert case["expected"]["rows"] == []
            if case["selection"]["id"] == "all-expanded":
                assert len(case["expected"]["rows"]) == 222
            if case["selection"]["id"] == "end-boundary":
                assert len(case["expected"]["rows"]) == 6
    assert real_source.read_bytes() == before


def test_real_linux_unreviewed_context_blocked(real_source, config):
    source = json.loads(real_source.read_bytes())
    source["items"][3]["content"]["timeContextFromParameter"] = "OtherTime"
    with pytest.raises(mock.Blocked):
        mock.build(mock.json_bytes(source), config)
    source = json.loads(real_source.read_bytes())
    source["items"][3]["content"]["timeContext"] = {"start": "2020-01-01"}
    with pytest.raises(mock.Blocked):
        mock.build(mock.json_bytes(source), config)
    source = json.loads(real_source.read_bytes())
    source["items"][1]["content"]["parameters"][2]["jsonData"] = '["invented severity"]'
    with pytest.raises(mock.Blocked):
        mock.build(mock.json_bytes(source), config)
    source = json.loads(real_source.read_bytes())
    source["items"][1]["content"]["parameters"][1]["typeSettings"]["selectAllValue"] = "*"
    with pytest.raises(mock.Blocked):
        mock.build(mock.json_bytes(source), config)


def test_no_network_or_environment_writes(source, scratch, config, monkeypatch):
    import socket
    import urllib.request

    def forbidden(*args, **kwargs):
        raise AssertionError("Offline generator attempted a live operation")

    monkeypatch.setattr(socket, "socket", forbidden)
    monkeypatch.setattr(urllib.request, "urlopen", forbidden)
    monkeypatch.setattr(subprocess, "run", forbidden)
    env_files = list(scratch.rglob(".env"))
    before = {path: mock.digest(path.read_bytes()) for path in env_files}
    out = scratch / "offline"
    mock.generate(source, out, config)
    mock.validate(source, out)
    assert before == {path: mock.digest(path.read_bytes()) for path in env_files}


def test_missing_cases_and_unexpected_files_fail(source, scratch, config):
    out = scratch / "bundle"
    mock.generate(source, out, config)
    path = scratch / "capture.json"
    path.write_text("{}")
    with pytest.raises(ValueError, match="every case"):
        mock.assert_captured(out, path, "sentinel")
    (out / "unexpected.json").write_text("{}")
    with pytest.raises(ValueError, match="file inventory"):
        mock.validate(source, out)
