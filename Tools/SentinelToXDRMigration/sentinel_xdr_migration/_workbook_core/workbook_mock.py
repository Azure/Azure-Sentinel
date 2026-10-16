"""Generate and validate reviewed workbook mock bundles locally. No live actions."""
from __future__ import annotations

import argparse
from datetime import timezone
import hashlib
import json
from pathlib import Path
import re
import sys

from . import dataframes, workbook, workbook_fixtures, workbook_mock_recipes as recipes

VERSION = 1
DEFAULT_CLOCK = "2026-10-07T12:00:00Z"


class Blocked(ValueError):
    def __init__(self, blockers):
        self.blockers = blockers
        super().__init__("No reviewed mock contract for one or more workbook inputs.")


def json_bytes(value) -> bytes:
    return (json.dumps(value, indent=2, ensure_ascii=True, allow_nan=False) + "\n").encode("utf-8")


def digest(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def configuration(seed, clock, scale, recipe, run_id=None) -> dict:
    if type(seed) is not int or not 0 <= seed <= 2**32 - 1:
        raise ValueError("seed must be an integer in 0..4294967295")
    if type(scale) is not int or not 1 <= scale <= 10:
        raise ValueError("scale must be an integer in 1..10")
    if recipe not in recipes.RECIPES:
        raise ValueError("Unsupported recipe; use list-recipes to see reviewed recipes.")
    if not isinstance(clock, str) or not re.fullmatch(r"\d{4}-\d\d-\d\dT\d\d:\d\d:\d\dZ", clock):
        raise ValueError("clock must be a fixed UTC timestamp: YYYY-MM-DDTHH:MM:SSZ")
    parsed = recipes.instant(clock)
    if not 1971 <= parsed.year <= 9998:
        raise ValueError("clock year must be in 1971..9998")
    if run_id is not None and (not isinstance(run_id, str) or
                              not re.fullmatch(r"[a-z0-9][a-z0-9-]{0,47}", run_id)):
        raise ValueError("run-id must be 1..48 lowercase ASCII letters, digits or hyphens")
    return {"seed": seed, "clock": clock, "scale": scale, "recipe": recipe, "runId": run_id}


def inventory(source: dict, recipe_id: str = "syslog-operational-v1") -> list[dict]:
    if not isinstance(source, dict) or source.get("version") != "Notebook/1.0" \
            or not isinstance(source.get("items"), list):
        raise ValueError("Expected a Notebook/1.0 document with an items array.")
    entries, blockers = [], []
    recipe = recipes.RECIPES[recipe_id]
    nodes = dict(workbook.walk(source))
    for surface in workbook.query_surfaces(source):
        path, node = surface["path"], surface["node"]
        inherited_time = {}
        ancestor = path.rsplit("/", 1)[0]
        while True:
            for key in ("timeContextFromParameter", "timeContext"):
                if key in nodes.get(ancestor, {}):
                    inherited_time.setdefault(key, nodes[ancestor][key])
            if not ancestor:
                break
            ancestor = ancestor.rsplit("/", 1)[0]
        query = node["query"]
        sha = workbook.query_hash(query) if isinstance(query, str) else None
        contract = recipe.contracts.get(sha)
        reason = None
        if surface["queryType"] not in (0, None) or surface["resourceType"] not in (None, workbook.LA):
            reason = "Unsupported source provider; reviewed contracts require Sentinel Logs KQL."
        elif contract is None:
            reason = ("Unreviewed query/table/function. Register an exact query dependency and "
                      "oracle contract plus reviewed table adapters; no generic rows are generated.")
        elif any(table not in recipes.TABLE_ADAPTERS for table in contract.tables):
            reason = "Missing reviewed table generator."
        elif surface["parameter"] != contract.parameter:
            reason = "Reviewed query moved between panel and parameter contexts."
        elif inherited_time.get("timeContextFromParameter") != contract.time_parameter:
            reason = "External time-context binding differs from the reviewed query contract."
        elif inherited_time.get("timeContext", {}) not in ({}, {"durationMs": 0}):
            reason = "Unreviewed fixed time-context override."
        if reason:
            blockers.append({"path": path, "querySha256": sha, "reason": reason})
        else:
            entries.append({"sourcePath": path, "querySha256": sha, "kind": contract.kind,
                            "tables": list(contract.tables), "parameter": contract.parameter,
                            "timeParameter": contract.time_parameter})
    if not entries and not blockers:
        blockers.append({"path": "", "reason": "Workbook contains no reviewed query surfaces."})
    parameters = {node["name"]: node for path, node in workbook.walk(source)
                  if re.search(r"/parameters/\d+$", path) and node.get("name")}
    blockers.extend(recipe.parameter_blockers(parameters, entries))
    if blockers:
        raise Blocked(blockers)
    return entries


def validate_rows(table: str, schema: dict, rows: list[list]) -> None:
    """Strict destination-table validation; never pretend this is DCR validation."""
    for side in ("sentinel", "ah"):
        known = dataframes.schema_for(table, side)
        if known is None or schema != known:
            raise ValueError(f"Reviewed {table} schema differs from cached {side} schema.")
    if not isinstance(rows, list) or len(rows) < 2:
        raise ValueError(f"{table} recipe must produce multiple typed rows.")
    for index, row in enumerate(rows):
        if not isinstance(row, list) or len(row) != len(schema):
            raise ValueError(f"{table} row {index}: invalid shape")
        for (column, typ), value in zip(schema.items(), row):
            valid = False
            if typ == "string":
                valid = isinstance(value, str)
            elif typ in ("int", "long"):
                bits = 32 if typ == "int" else 64
                valid = value is None or (type(value) is int and -2**(bits-1) <= value < 2**(bits-1))
            elif typ == "datetime":
                if isinstance(value, str):
                    try:
                        parsed = recipes.instant(value)
                        valid = parsed.tzinfo is not None and parsed.utcoffset() == timezone.utc.utcoffset(parsed)
                    except ValueError:
                        pass
            else:
                raise ValueError(f"No reviewed type validator for {table}.{column}: {typ}")
            if not valid:
                raise ValueError(f"{table} row {index}: invalid {typ} in {column}")


def build(source_bytes: bytes, config: dict) -> dict[str, bytes]:
    config = configuration(config["seed"], config["clock"], config["scale"],
                           config["recipe"], config.get("runId"))
    recipe = recipes.RECIPES[config["recipe"]]
    source = json.loads(source_bytes)
    queries = inventory(source, config["recipe"])
    source_hash = digest(source_bytes)
    implementation = {p.name: digest(p.read_bytes()) for p in (
        Path(__file__), Path(recipes.__file__), Path(workbook_fixtures.__file__),
        Path(dataframes.__file__))}
    identity = {"sourceSha256": source_hash, "config": config,
                "implementation": implementation, "spec": recipe.spec}
    run_id = config["runId"] or "wb-" + digest(json_bytes(identity))[:16]
    tables, records_by_table = {}, {}
    for table in sorted({table for query in queries for table in query["tables"]}):
        adapter = recipes.TABLE_ADAPTERS[table]
        records = adapter.generate(config["seed"], config["clock"], config["scale"], run_id)
        if any(set(record) != set(adapter.schema) for record in records):
            raise ValueError(f"{table} adapter generated missing or undeclared fields.")
        rows = [[record[column] for column in adapter.schema] for record in records]
        validate_rows(table, adapter.schema, rows)
        tables[table] = {"schema": adapter.schema, "rows": rows}
        records_by_table[table] = records
    resolutions = {entry["sourcePath"]: {
        "querySha256": entry["querySha256"], "tables": entry["tables"],
        "evidence": f"reviewed workbook mock recipe {config['recipe']}, generator v{VERSION}",
    } for entry in queries}
    converted = workbook.convert_workbook(source, resolutions=resolutions)
    if converted["report"]["status"] == "blocked":
        raise Blocked(converted["report"]["issues"])
    outputs = {entry["sourcePath"]: entry for entry in converted["report"]["queries"]}
    output_surfaces = {s["path"]: s for s in workbook.query_surfaces(converted["workbook"])}
    choices = recipe.selections(records_by_table, config["clock"])
    cases = []
    for index, query in enumerate(queries):
        output_path = outputs[query["sourcePath"]]["outputPath"]
        output_query = output_surfaces[output_path]["node"]["query"]
        if workbook.query_hash(output_query) != query["querySha256"]:
            raise Blocked([{"path": output_path,
                            "reason": "AH rewrite lacks a reviewed fixture mapping/oracle."}])
        query["outputPath"] = output_path
        contract = recipe.contracts[query["querySha256"]]
        for selection in choices:
            case = {
                "id": f"q{index:02d}-{selection['id']}", "sourcePath": query["sourcePath"],
                "outputPath": output_path, "querySha256": query["querySha256"],
                "selection": selection, "substitutions": recipe.substitutions(selection),
                "expected": recipe.expected(contract, records_by_table, selection),
            }
            if contract.time_parameter:
                case["tableTimeRanges"] = {table: {
                    "column": contract.time_column, "start": selection["start"], "end": selection["end"]}
                    for table in contract.tables}
            cases.append(case)
    manifest = {
        "version": VERSION, "generator": "workbook_mock", "runId": run_id,
        "provenance": {"kind": "generated-synthetic-operational", "sourceSha256": source_hash,
                       "recipeSha256": digest(json_bytes(recipe.spec)),
                       "implementation": implementation},
        "config": config, "seed": config["seed"], "clock": config["clock"],
        "recipe": recipe.spec, "inventory": queries, "tables": tables, "cases": cases,
        "ingestion": {"status": "not-ingestible", "directLogsIngestionSupported": False,
                      "stream": None, "payload": None,
                      "reason": "No exact custom input stream and transform verified for "
                                + ", ".join(tables) + ". Destination table fixtures are not raw connector payloads."},
        "validation": {"schema": "passed", "harnessAssembly": "checked",
                       "oracle": "reviewed-python-reference", "kqlExecution": "not-run",
                       "engineParity": "not-run", "portalParameterSerialization": "unverified"},
        "limitations": [
            "Only exact reviewed query hashes and registered table adapters are supported.",
            "Time context is modeled as inclusive TimeGenerated bounds on the input table; "
            "this is not a verification of the portal provider's boundary behavior.",
            "Computer picker has no time binding and intentionally sees the complete fixture.",
            "Computer:lable is an upstream typo retained unchanged. Its fixture substitution "
            "is explicit, not proof that the portal resolves this token.",
            "Expanded-all and literal All/* are separate contracts. Events has no wildcard "
            "clause and returns zero for literal All/*; no source query is silently fixed.",
            "Severity tiles ignore Computer. Emergency timecharts include emerg, not panic; "
            "timecharts group exact timestamps, not hourly bins.",
            "Synthetic severity levels are operational test coverage, not attack evidence.",
        ],
    }
    harnesses = workbook_fixtures.harness_files(manifest, source, converted["workbook"])
    # A recipe-level diagnostic exercises hour-boundary bins independently of
    # the nine panels (which group raw timestamps). It is not a new workbook panel.
    diagnostic = recipe.diagnostic(records_by_table)
    stub = "\n".join(dataframes.datatable_stub(table, tables[table]["schema"],
                                               rows=tables[table]["rows"])
                     for table in diagnostic["tables"])
    files = {"manifest.json": json_bytes(manifest), "diagnostic.json": json_bytes(diagnostic)}
    for table, records in records_by_table.items():
        files[f"tables/{table}.json"] = json_bytes(records)
        files[f"tables/{table}.schema.json"] = json_bytes(tables[table]["schema"])
        # Adjacent guard is understood by the future Azure-Sentinel ingestion tool.
    files["tables/scenario.json"] = json_bytes({
        "generationStatus": "table-fixture-only", "runId": run_id,
        "ingestion": manifest["ingestion"],
        "validation": {"schemaValidation": "passed", "rawStreamValidation": "not-run"},
        "fixtures": {"tableRecords": sum(len(records) for records in records_by_table.values())},
    })
    for name, text in harnesses.items():
        files[f"harnesses/{name}"] = text.encode("utf-8")
    for side in ("sentinel", "ah"):
        files[f"harnesses/{diagnostic['id']}.{side}.kql"] = (
            "// FIXTURE DIAGNOSTIC ONLY; not a workbook panel.\n" + stub + "\n" +
            diagnostic["query"] + "\n").encode("utf-8")
    files["checksums.json"] = json_bytes({name: digest(content) for name, content in sorted(files.items())})
    return files


def generate(source: Path, out: Path, config: dict) -> dict:
    if out.exists() or out.is_symlink():
        raise ValueError("Output must be a new directory; existing evidence is never overwritten.")
    if out.resolve() == source.resolve() or source.resolve().is_relative_to(out.resolve()):
        raise ValueError("Output must not contain or replace the source.")
    before = source.read_bytes()
    files = build(before, config)
    if source.read_bytes() != before:
        raise ValueError("Source changed during generation; no output written.")
    out.mkdir(parents=True, exist_ok=False)
    for name, content in files.items():
        path = out / name
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("xb") as handle:
            handle.write(content)
    manifest = json.loads(files["manifest.json"])
    return {"status": "generated-local", "runId": manifest["runId"],
            "sourceSha256": manifest["provenance"]["sourceSha256"],
            "rows": sum(len(t["rows"]) for t in manifest["tables"].values()),
            "cases": len(manifest["cases"]), "harnesses": len(manifest["cases"]) * 2 + 2,
            "ingestion": "not-ingestible", "kqlExecution": "not-run"}


def validate(source: Path, bundle: Path) -> dict:
    manifest = json.loads((bundle / "manifest.json").read_bytes())
    expected = build(source.read_bytes(), manifest["config"])
    paths = {p.relative_to(bundle).as_posix() for p in bundle.rglob("*") if p.is_file()}
    if paths != expected.keys():
        raise ValueError("Bundle file inventory mismatch (missing or unexpected artifacts).")
    for name, content in expected.items():
        path = bundle / name
        if path.is_symlink() or path.read_bytes() != content:
            raise ValueError(f"Offline regeneration mismatch: {name}")
    return {"status": "offline-checks-passed", "files": len(expected),
            "checks": ["source/recipe/code hashes", "typed rows", "reference cells/aggregates/bins",
                       "parameter cases", "actual-row harness bindings", "artifact integrity"],
            "kqlExecution": "not-run", "engineParity": "not-run", "ingestion": "not-ingestible"}


def assert_captured(bundle: Path, results_path: Path, side: str) -> dict:
    manifest = json.loads((bundle / "manifest.json").read_bytes())
    captured = json.loads(results_path.read_bytes())
    expected = {case["id"]: case["expected"] for case in manifest["cases"]}
    diagnostic = json.loads((bundle / "diagnostic.json").read_bytes())
    expected[diagnostic["id"]] = diagnostic["expected"]
    if not isinstance(captured, dict) or captured.keys() != expected.keys():
        raise ValueError("Captured results must contain every case ID and fixture diagnostic, without extras.")
    for case_id, oracle in expected.items():
        try:
            workbook_fixtures.assert_result(oracle, captured[case_id])
        except (AssertionError, TypeError, KeyError) as exc:
            raise ValueError(
                f"Captured result assertion failed: {side}/{case_id}; "
                "column, cell, multiplicity or ordering mismatch (captured values omitted)."
            ) from exc
    return {"status": "captured-results-match", "side": side, "cases": len(expected),
            "execution": "external-capture-not-performed-by-this-tool"}
