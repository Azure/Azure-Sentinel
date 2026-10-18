"""Reviewed operational recipes, not a KQL constraint solver or attack generator.

Table adapters own correlations and typed rows. Query contracts separately own
source dependencies, external time context, parameter semantics and exact oracles.
Unknown hashes require review; a known table alone never authorizes fake rows.
"""
from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
from datetime import datetime, timedelta
import json
import random
from typing import Callable


def instant(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def stamp(value: datetime) -> str:
    return value.isoformat(timespec="seconds").replace("+00:00", "Z")


SEVERITIES = {
    "emerg": (0, "Emergency"), "panic": (0, "Emergency"),
    "alert": (1, "Alert"), "crit": (2, "Critical"),
    "err": (3, "Error"), "error": (3, "Error"),
    "warning": (4, "Warning"), "warn": (4, "Warning"),
    "notice": (5, "Notice"), "info": (6, "Informational"),
    "debug": (7, "Debug"), "unknown": (8, "Unknown"),
}
LABELS = list(dict.fromkeys(label for _, label in SEVERITIES.values() if label != "Unknown"))
SYSLOG_SCHEMA = {
    "CollectorHostName": "string", "Computer": "string", "EventTime": "datetime",
    "Facility": "string", "HostIP": "string", "HostName": "string", "MG": "string",
    "ProcessID": "int", "ProcessName": "string", "SeverityLevel": "string",
    "SourceSystem": "string", "SyslogMessage": "string", "TenantId": "string",
    "TimeGenerated": "datetime", "Type": "string", "_ResourceId": "string",
}
SYSLOG_SPEC = {
    "id": "syslog-operational-v1",
    "purpose": "Synthetic operational workbook mechanics; no malicious behavior or SOC-value claim.",
    "evidence": [
        "Syslog/Workbooks/LinuxMachines.json: ten exact reviewed source queries",
        "data/la_schema_catalog.json and data/ah_schema_catalog.json: Syslog types",
        "docs/Standard-table-mock-ingestion-onboarding.md: table rows are not a raw input contract",
    ],
    "hostWeights": [1, 2, 3],
    "severityWeights": dict(zip(SEVERITIES, [1, 1, 2, 3, 2, 1, 4, 2, 5, 8, 3, 1])),
    "processes": [["cron", "cron", 120], ["systemd", "daemon", 1],
                  ["sshd", "authpriv", 900], ["kernel", "kern", None]],
    "windowSeconds": 21600,
    "boundaryOffsetsSeconds": [-21601, -21600, -18001, -18000, -1, 0, 1],
    "correlations": ["Computer -> HostName, HostIP, _ResourceId",
                     "Computer + ProcessName -> ProcessID",
                     "ProcessName -> Facility, synthetic operational message"],
    "variation": "Seeded process choice and seconds within six hours; weighted hosts/severities, scale 1..10.",
}


def syslog_rows(seed: int, clock: str, scale: int, marker: str) -> list[dict]:
    rng = random.Random(seed)
    base = instant(clock)
    rows = []
    for host_index, weight in enumerate(SYSLOG_SPEC["hostWeights"]):
        host = f"mock-{marker}-{host_index + 1}"
        resource = (f"/subscriptions/00000000-0000-0000-0000-000000000000/"
                    f"resourceGroups/mock-only/providers/Microsoft.Compute/virtualMachines/{host}"
                    if host_index == 1 else "")

        def event(severity, offset, process_index):
            process, facility, pid = SYSLOG_SPEC["processes"][process_index]
            timestamp = stamp(base + timedelta(seconds=offset))
            return dict(zip(SYSLOG_SCHEMA, [
                "mock-collector", host, timestamp, facility, f"192.0.2.{10 + host_index}",
                host, "", None if pid is None else pid + host_index * 1000, process,
                severity, "Linux", f"MOCK {marker}: synthetic {process} operational test",
                "", timestamp, "Syslog", resource,
            ]))

        for severity, count in SYSLOG_SPEC["severityWeights"].items():
            for _ in range(count * weight * scale):
                rows.append(event(severity, -rng.randrange(1, 21600),
                                  rng.randrange(len(SYSLOG_SPEC["processes"]))))
        for offset in SYSLOG_SPEC["boundaryOffsetsSeconds"]:
            # Deliberate duplicates verify count(), not just distinct output shape.
            rows.extend([event("emerg", offset, 3)] * (host_index + 1))
    return rows


@dataclass(frozen=True)
class TableAdapter:
    table: str
    schema: dict[str, str]
    spec: dict
    generate: Callable


TABLE_ADAPTERS = {"Syslog": TableAdapter("Syslog", SYSLOG_SCHEMA, SYSLOG_SPEC, syslog_rows)}


@dataclass(frozen=True)
class QueryContract:
    kind: str
    tables: tuple[str, ...] = ("Syslog",)
    parameter: bool = False
    time_parameter: str | None = "TimeRange"
    time_column: str = "TimeGenerated"


# Exact UTF-8 hashes include whitespace and templates. No regex source guessing.
QUERY_CONTRACTS = {
    "7e4626fc678e25bfbb8010e213842a4db34ec565bf1d6b2f301d679539f0e658":
        QueryContract("computers", parameter=True, time_parameter=None),
    "24464f7e0e663896659523f152ad9566a9a33d479834cbc681932dcb8960f3ea":
        QueryContract("severity"),
    "206654d1ec09162aa64ff5d8ef0b72484cc4aea0eb58786714589e90c447ca7a":
        QueryContract("emerg"),
    "8661e28bd84bfe3a117cd6391d3d330aedc5d2af95534ffb8bae4cbf2371a28d":
        QueryContract("crit"),
    "71dad0100fcd2088e011ec965f7731eb4314df0419360377a874e24a0a319f54":
        QueryContract("alert"),
    "a569777af35afbe110ff64ced2df34f1d96a088fbba88e53372e56a5fc917d8a":
        QueryContract("events"),
    "43b873d68c1dfffa1fb72d48e3121abf844f31e98ce1982bad0af3844a344da9":
        QueryContract("messages"),
    "1eddbe8eae830de68f7a473ecf6e08e984430295d9436b3ca490fb1aa81eeced":
        QueryContract("processes"),
    "fb8370f59c577695bb940c54ca190a8d25ad09775e38b0e411996b63a996b761":
        QueryContract("facilities"),
    "335b9b05951ed2347c0d56c0a25bad137f6bca005500c80f4fef1f5d74d2eaed":
        QueryContract("facilities"),
}


def selections(rows: list[dict], clock: str) -> list[dict]:
    hosts = sorted({row["Computer"] for row in rows})
    base = instant(clock)
    result = []
    for name, computers, severity, start, end, label in [
        ("all-expanded", hosts, LABELS, -21600, 0, "All"),
        ("all-literal", ["All"], ["*"], -21600, 0, "All"),
        ("single", hosts[:1], LABELS, -21600, 0, hosts[0]),
        ("multiple", hosts[:2], ["Warning", "Error"], -21600, 0, "Multiple"),
        ("single-severity", hosts, ["Emergency"], -21600, 0, "All"),
        ("empty-computers", [], LABELS, -21600, 0, ""),
        ("empty-severity", hosts, [], -21600, 0, "All"),
        ("narrow-time", hosts, LABELS, -3600, 0, "All"),
        ("end-boundary", hosts, LABELS, 0, 0, "All"),
        ("empty-time", hosts, LABELS, 60, 120, "All"),
    ]:
        result.append({"id": name, "Computer": computers, "Severity": severity,
                       "computerLabel": label,
                       "start": stamp(base + timedelta(seconds=start)),
                       "end": stamp(base + timedelta(seconds=end))})
    return result


def literals(values: list[str]) -> str:
    # All values originate in reviewed recipes, but still quote as KQL data.
    return ",".join("'" + v.replace("\\", "\\\\").replace("'", "\\'") + "'"
                    for v in values) if values else "dynamic([])"


def substitutions(selection: dict) -> dict:
    return {"Computer": literals(selection["Computer"]),
            "Computer:lable": selection["computerLabel"],
            "Severity": literals(selection["Severity"])}


def scoped_rows(rows: list[dict], selection: dict, timed: bool) -> list[dict]:
    if not timed:
        return rows
    start, end = instant(selection["start"]), instant(selection["end"])
    return [row for row in rows if start <= instant(row["TimeGenerated"]) <= end]


def expected_result(contract: QueryContract, rows: list[dict], selection: dict) -> dict:
    """A finite reviewed relational oracle, deliberately not a general KQL evaluator."""
    kind = contract.kind
    records = scoped_rows(rows, selection, contract.time_parameter is not None)
    if kind == "computers":
        counts = Counter(row["Computer"] for row in records)
        ordered = len(set(counts.values())) == len(counts)
        return result([("Computer", "string")],
                      [[host] for host in sorted(counts, key=lambda h: (-counts[h], h))],
                      ordered=ordered)
    if kind != "severity":
        records = [row for row in records if row["Computer"] in selection["Computer"]
                   or (kind != "events" and selection["computerLabel"] == "All")]
    records = [row for row in records if SEVERITIES[row["SeverityLevel"]][1] in selection["Severity"]
               or (kind != "events" and "*" in selection["Severity"])]
    if kind == "severity":
        counts = Counter(row["SeverityLevel"] for row in records)
        return result([("SeverityLevel", "string"), ("count_", "long"), ("Severity", "string")],
                      [[level, count, SEVERITIES[level][1]] for level, count in
                       sorted(counts.items(), key=lambda item: (SEVERITIES[item[0]][0], item[0]))],
                      order_by_severity=True)
    if kind in ("emerg", "crit", "alert"):
        records = [row for row in records if row["SeverityLevel"] == kind]
        keys = ("Computer", "TimeGenerated")
        columns = [("Computer", "string"), ("TimeGenerated", "datetime"), ("count_", "long")]
    elif kind == "messages":
        keys, columns = ("SyslogMessage",), [("SyslogMessage", "string"), ("count_", "long")]
    elif kind == "processes":
        keys, columns = ("Facility", "ProcessName"), [("Process", "string"), ("Count", "long")]
    elif kind == "facilities":
        keys = ("Facility", "SeverityLevel")
        columns = [("Facility", "string"), ("SeverityLevel", "string"), ("count_", "long")]
    elif kind == "events":
        return result([
            ("TimeGenerated", "datetime"), ("Computer", "string"), ("SeverityLevel", "string"),
            ("SeverityNumber", "long"), ("Facility", "string"), ("HostIP", "string"),
            ("ProcessNameAndID", "string")],
            [[row["TimeGenerated"], row["_ResourceId"] or row["Computer"], row["SeverityLevel"],
              SEVERITIES[row["SeverityLevel"]][0], row["Facility"], row["HostIP"],
              f'{row["ProcessName"]} ({row["ProcessID"] if row["ProcessID"] is not None else "-"})']
             for row in records])
    else:
        raise ValueError(f"No reviewed oracle for {kind}")
    counts = Counter(tuple(row[key] for key in keys) for row in records)
    output = [[*key, count] for key, count in sorted(counts.items())]
    if kind == "processes":
        output = [[f"{process} ({facility})", count] for facility, process, count in output]
    return result(columns, output)


def result(columns, rows, *, ordered=False, order_by_severity=False):
    value = {"columns": [{"name": name, "type": typ} for name, typ in columns],
             "rows": rows, "ordered": ordered}
    if order_by_severity:
        # Aliases share ranks; KQL does not define tie ordering.
        value["sortGroups"] = {"column": "SeverityLevel",
                               "ranks": {key: rank for key, (rank, _) in SEVERITIES.items()}}
    return value


def hourly_result(rows: list[dict]) -> dict:
    counts = Counter((row["Computer"], stamp(instant(row["TimeGenerated"]).replace(
        minute=0, second=0, microsecond=0))) for row in rows)
    return result([("Computer", "string"), ("TimeGenerated", "datetime"), ("Events", "long")],
                  [[*key, value] for key, value in sorted(counts.items())])


def parameter_blockers(parameters: dict, inventory: list[dict]) -> list[dict]:
    blockers = []
    if any(not entry["parameter"] for entry in inventory):
        for name, typ, all_value in (("Computer", 5, "All"), ("Severity", 2, "*")):
            param = parameters.get(name, {})
            if (param.get("type") != typ or param.get("quote") != "'"
                    or param.get("delimiter") != "," or param.get("multiSelect") is not True
                    or param.get("typeSettings", {}).get("selectAllValue") != all_value):
                blockers.append({"path": name, "reason": "Unreviewed multiselect parameter contract."})
        if parameters.get("TimeRange", {}).get("type") != 4:
            blockers.append({"path": "TimeRange", "reason": "Missing reviewed time-range parameter."})
        try:
            severity_labels = json.loads(parameters.get("Severity", {}).get("jsonData", "null"))
        except (ValueError, TypeError):
            severity_labels = None
        if severity_labels != LABELS:
            blockers.append({"path": "Severity", "reason": "Unreviewed static severity values."})
    return blockers


@dataclass(frozen=True)
class WorkbookRecipe:
    spec: dict
    contracts: dict[str, QueryContract]
    selections: Callable
    substitutions: Callable
    expected: Callable
    diagnostic: Callable
    parameter_blockers: Callable


RECIPES = {
    SYSLOG_SPEC["id"]: WorkbookRecipe(
        spec=SYSLOG_SPEC, contracts=QUERY_CONTRACTS,
        parameter_blockers=parameter_blockers,
        selections=lambda tables, clock: selections(tables["Syslog"], clock),
        substitutions=substitutions,
        expected=lambda contract, tables, selection: expected_result(
            contract, tables["Syslog"], selection),
        diagnostic=lambda tables: {
            "id": "diagnostic-hourly", "tables": ["Syslog"],
            "purpose": "Fixture-only hourly distribution diagnostic; not a source workbook panel.",
            "query": "Syslog | summarize Events=count() by Computer, bin(TimeGenerated, 1h)",
            "expected": hourly_result(tables["Syslog"]),
        },
    ),
}
