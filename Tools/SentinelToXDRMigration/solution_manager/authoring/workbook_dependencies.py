"""Frozen, offline workbook gap proposals and explicit reviewer decisions.

Metadata is imported, never executed. Review writes only run-local config and
receipts, not source content, candidates, workflow state or cloud resources.
"""
from __future__ import annotations

from copy import deepcopy
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import os
import re

from solution_manager.authoring.dependencies import dependency_plan, dependency_validation_errors, TABLE_WORKLOADS, telemetry_data_types
from solution_manager.migration._workbook_core import workbook, mapping_catalog, migrator, rewrite
from solution_manager.migration.workbooks import _root, _path, _document, _solution_data, _sha, _write, inventory_workbooks
from solution_manager.authoring.workbook_functions import candidates, validate_functions, function_definition


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":"),
                                    ensure_ascii=True).encode()).hexdigest()


def _load(path):
    path = Path(path).expanduser()
    if any(p.is_symlink() for p in (path, *path.parents)):
        raise ValueError("Review inputs must not use symlinks.")
    def unique(pairs):
        value = {}
        for key, item in pairs:
            if key in value:
                raise ValueError(f"Duplicate JSON key: {key}")
            value[key] = item
        return value
    return json.loads(path.read_text("utf-8"), object_pairs_hook=unique)


def _connectors(root, data):
    alternatives = []
    references = data.get("Data Connectors", [])
    if not isinstance(references, list):
        raise ValueError("Solution Data Connectors must be an array.")
    for relative in references:
        prefix = f"Solutions/{root.name}/"
        if (isinstance(relative, str) and root.parent.name == "Solutions"
                and relative.startswith(prefix)):
            relative = relative[len(prefix):]
        path = _path(root, relative)
        if not relative.startswith("Data Connectors/") or not path.is_file():
            raise ValueError("Connector references must identify existing Data Connectors content.")
        value = json.loads(path.read_bytes())
        if not isinstance(value, dict):
            raise ValueError("Connector content must be a JSON object.")
        nested = value.get("properties") or value
        connector_id = value.get("id") or nested.get("id")
        types = nested.get("dataTypes", [])
        if isinstance(types, dict):
            types = list(types)
        names = sorted({entry.get("name") if isinstance(entry, dict) else entry for entry in types
                        if isinstance(entry, str) or isinstance(entry, dict) and isinstance(entry.get("name"), str)})
        alternatives.append({
            "sourcePath": path.relative_to(root).as_posix(), "sourceSha256": _sha(path.read_bytes()),
            "connectorId": connector_id, "dataTypes": telemetry_data_types(names),
            **({"referenceInputs": ["Watchlist"]} if "Watchlist" in names else {}),
            "title": value.get("title") or (nested.get("connectorUiConfig") or {}).get("title"),
            "recommendation": None,
        })
    return alternatives


def _binding(raw, entry):
    tokens = {match.group(0)[1:-1] for match in workbook.TOKEN.finditer(raw)}
    bindings = entry.get("bindings", {})
    if (not isinstance(bindings, dict) or set(bindings) != tokens
            or any(not isinstance(value, str) or not value for value in bindings.values())):
        raise ValueError("Metadata needs exact bindings for every raw workbook placeholder.")
    rendered = workbook.TOKEN.sub(lambda match: bindings[match.group(0)[1:-1]], raw)
    if workbook.TOKEN.search(rendered):
        raise ValueError("Imported metadata has unresolved rendered-query placeholders.")
    if entry.get("renderedQuery") != rendered or entry.get("renderedQuerySha256") != workbook.query_hash(rendered):
        raise ValueError("Metadata rendered query/hash does not match exact template bindings.")
    time_range = entry.get("timeRange")
    if not isinstance(time_range, dict) or set(time_range) != {"start", "end"}:
        raise ValueError("Metadata requires an explicit timeRange start/end.")
    try:
        start, end = [datetime.fromisoformat(time_range[key].replace("Z", "+00:00"))
                      for key in ("start", "end")]
        if start.tzinfo is None or end.tzinfo is None or start >= end:
            raise ValueError()
    except (ValueError, TypeError, AttributeError):
        raise ValueError("Metadata timeRange must be ordered timezone-aware ISO timestamps.") from None
    for key, expected in (("start", start), ("end", end)):
        for token, value in bindings.items():
            if token.endswith(":" + key):
                match = re.fullmatch(r"\s*datetime\(\s*(['\"]?)(.*?)\1\s*\)\s*", value)
                try:
                    actual = datetime.fromisoformat(match.group(2).replace("Z", "+00:00")) if match else None
                except ValueError:
                    actual = None
                if actual != expected:
                    raise ValueError("Metadata time bindings must match the exact declared timeRange.")
    return rendered


def plan_workbook_dependencies(solution, *, results_path=None, workspace_id=None,
                               imported_results=None):
    root = _root(solution)
    inventory = inventory_workbooks(root)
    data = _solution_data(root)
    connectors = _connectors(root, data)
    definitions = candidates(root)
    imported = _load(results_path) if results_path is not None else deepcopy(imported_results)
    if imported is None and workspace_id is not None:
        raise ValueError("Workspace ID is only accepted for explicitly approved metadata import.")
    entries = {}
    if imported is not None:
        if not isinstance(workspace_id, str) or not workspace_id.strip():
            raise ValueError("Metadata import requires the explicitly approved workspace ID.")
        if not isinstance(imported, dict) or set(imported) != {"results"} or not isinstance(imported["results"], list):
            raise ValueError("Metadata import must contain a results array.")
        for entry in imported["results"]:
            if not isinstance(entry, dict) or not isinstance(entry.get("workbook"), str) or not isinstance(entry.get("path"), str):
                raise ValueError("Metadata must identify each workbook/query path.")
            if set(entry) - {"workbook", "path", "workspaceId", "workbookSha256", "querySha256",
                             "status", "statusCode", "partial", "error", "errorDetails", "failureKind",
                             "bindings", "renderedQuery", "renderedQuerySha256", "timeRange", "dataSources"}:
                raise ValueError("Unknown workbook metadata import fields.")
            key = (entry["workbook"], entry["path"])
            if key in entries:
                raise ValueError("Duplicate workbook query metadata.")
            entries[key] = entry
        expected = {(row["path"], query["path"]) for row in inventory for query in row["queries"]}
        if set(entries) != expected:
            raise ValueError("Metadata must cover the complete current workbook/query inventory.")
    rows = []
    mappings = {name: value.get("ahTable") or name
                for name, value in mapping_catalog.load_mapping_catalog()["tables"].items()}
    for row in inventory:
        doc = _document(_path(root, row["path"]))
        helper_entries, removed, _ = workbook._scope_parameters(doc)
        removed_prefixes = [path + "/" for path, parameter in helper_entries if parameter["name"] in removed]
        for surface in workbook.query_surfaces(doc):
            template = surface["node"]["query"]
            blockers = []
            raw_valid = True
            try:
                raw = workbook._raw_query(template, surface["queryType"])
            except ValueError as exc:
                raw = template
                raw_valid = False
                blockers.append(str(exc))
            provider_supported = surface["queryType"] in (0, None, workbook.AH) and (
                surface["queryType"] == workbook.AH or
                (surface["resourceType"] or "").lower() in ("", workbook.LA))
            is_helper = any(surface["path"].startswith(prefix) for prefix in removed_prefixes)
            if not provider_supported and not is_helper:
                blockers.append("Unsupported provider requires a separately reviewed source migration.")
            code = "".join(text if kind == "code" else " " * len(text) for kind, text in rewrite._segments(raw))
            if re.search(r"\b(?:workspace|app|resource|cluster|database)\s*\(", code, re.I):
                blockers.append("Explicit cross-resource/scope function cannot be converted by dependency acceptance.")
            aliases = sorted(workbook.opaque_functions(raw)) if provider_supported else []
            entry = entries.get((row["path"], surface["path"]))
            metadata = None
            if entry is not None:
                if (entry.get("status") != "passed" or entry.get("partial", False) is not False
                        or any(entry.get(key) for key in ("error", "errorDetails", "failureKind"))
                        or entry.get("statusCode", 200) != 200
                        or entry.get("workspaceId") != workspace_id
                        or entry.get("querySha256") != workbook.query_hash(template)
                        or entry.get("workbookSha256") != row["sha256"]
                        or not provider_supported or not raw_valid):
                    raise ValueError("Metadata has failed/partial/stale/cross-workspace scope or unsupported provider.")
                _binding(raw, entry)
                metadata = entry.get("dataSources")
                if not isinstance(metadata, list):
                    raise ValueError("Metadata requires a dataSources array from Prefer: include-dataSources=true.")
                # Do not accept mixed-workspace input telemetry as target-workspace evidence.
                for source in metadata:
                    if isinstance(source, dict) and any(
                        source.get(key) not in (None, workspace_id)
                        for key in ("workspaceId", "workspace", "workspaceCustomerId")
                    ):
                        raise ValueError("Metadata dataSources contains cross-workspace input.")
            proposal = dependency_plan(raw, metadata=metadata, table_mappings=mappings)
            if aliases and metadata is None:
                proposal["reviewReasons"].append("Underlying function tables need distinct exact-query or manual evidence.")
                proposal["reviewRequired"] = True
            proposals = [record for record in definitions if record.get("functionAlias") in aliases]
            missing = sorted(set(aliases) - {record["functionAlias"] for record in proposals})
            reasons = list(proposal["reviewReasons"])
            if missing:
                reasons.append("No current local definition for: " + ", ".join(missing))
            rows.append({
                "workbook": row["path"], "workbookSha256": row["sha256"],
                "path": surface["path"], "querySha256": workbook.query_hash(template),
                "sourceKql": template, "queryKql": raw, "queryType": surface["queryType"],
                "resourceType": surface["resourceType"], "scopeHelper": is_helper,
                "proposal": proposal, "proposalAccepted": False,
                "staticConfidence": "heuristic-not-reviewed" if entry is None else "imported-not-reviewed",
                "workspaceFunctions": aliases, "functionPrerequisites": proposals,
                "externalSourceWarnings": (
                    ["Query uses externaldata; review exact external source binding and availability separately."]
                    if re.search(r"\bexternaldata\s*[\[(]", code) else []),
                "technicalBlockers": blockers, "gapExplanations": reasons,
                "labBindingRequirements": {
                    "placeholders": sorted({m.group(0)[1:-1] for m in workbook.TOKEN.finditer(raw)}),
                    "requiredFields": ["workspaceId", "workbookSha256", "querySha256", "bindings",
                                       "renderedQuery", "renderedQuerySha256", "timeRange", "dataSources"],
                    "prefer": "include-dataSources=true",
                },
                "recommendedActions": ["Review raw source inputs and their telemetry/platform-reference classification.",
                                       "Choose connector alternatives only for Sentinel telemetry; platform reference inputs require none.",
                                       "Preserve reviewed functions; request optional parser changes separately.",
                                       "Supply bound read-only metadata only after separate exact workspace approval."],
            })
    result = {
        "schemaVersion": "1.0.0", "kind": "workbook-dependency-plan", "solution": str(root),
        "inventory": inventory, "solutionDataSha256": digest(data),
        "workloadMap": deepcopy(TABLE_WORKLOADS), "connectorAlternatives": connectors,
        "workspaceFunctionCandidates": definitions, "queries": rows,
        "sourceRecommendationEvidence": {
            "text": data.get("Description"), "solutionDataSha256": digest(data),
            "reviewRequired": True, "titleHeuristicsUsed": False,
        },
        "metadataImport": imported, "workspaceId": workspace_id,
        "liveQueriesExecuted": False, "writesSource": False, "runtimeParityVerified": False,
    }
    return {**result, "planSha256": digest(result)}


def _decision(value):
    if not isinstance(value, dict) or value.get("decision") not in ("accept", "change", "defer"):
        raise ValueError("Every review decision must be explicit accept, change or defer.")
    return value["decision"]


def _strings(value, field):
    if (not isinstance(value, list) or any(not isinstance(item, str) or not item.strip() for item in value)
            or len(value) != len(set(value))):
        raise ValueError(f"{field} must be an array of unique nonempty strings.")
    return value


def review_workbook_dependencies(solution, *, plan_path, decisions_path, expected_plan_sha256,
                                 actor, reference, output_directory):
    root = _root(solution)
    plan, decisions = _load(plan_path), _load(decisions_path)
    if not isinstance(actor, str) or not actor.strip() or not isinstance(reference, str) or not reference.strip():
        raise ValueError("Review requires an explicit actor and reference.")
    if not isinstance(plan, dict) or plan.get("planSha256") != expected_plan_sha256:
        raise ValueError("Review must bind the exact frozen plan hash.")
    current = plan_workbook_dependencies(root, workspace_id=plan.get("workspaceId"),
                                         imported_results=plan.get("metadataImport"))
    if plan != current:
        raise ValueError("Frozen workbook plan is malformed or stale; regenerate and review.")
    if (not isinstance(decisions, dict) or set(decisions) != {"planSha256", "queries", "workbooks"}
            or decisions["planSha256"] != expected_plan_sha256
            or not isinstance(decisions["queries"], list) or not isinstance(decisions["workbooks"], list)):
        raise ValueError("Decisions require exact planSha256, queries and workbooks arrays.")
    query_decisions = {}
    for decision in decisions["queries"]:
        _decision(decision)
        if set(decision) - {"workbook", "path", "querySha256", "decision", "tables", "workspaceFunctions", "optionalBranches"}:
            raise ValueError("Unknown query review decision fields.")
        if any(not isinstance(decision.get(key), str) for key in ("workbook", "path", "querySha256")):
            raise ValueError("Query review identities and hashes must be strings.")
        for field in ("tables", "workspaceFunctions"):
            if field in decision:
                _strings(decision[field], field)
        if "optionalBranches" in decision:
            branches = decision["optionalBranches"]
            if not isinstance(branches, list) or any(
                not isinstance(branch, dict) or set(branch) != {
                    "functionAlias", "sourcePath", "sourceSha256", "branch", "decision"}
                or any(not isinstance(value, str) or not value.strip() for value in branch.values())
                or branch["decision"] not in ("keep", "remove-request", "defer")
                for branch in branches
            ):
                raise ValueError("Malformed optional branch decisions.")
        key = (decision.get("workbook"), decision.get("path"))
        if key in query_decisions:
            raise ValueError("Duplicate query review decision.")
        query_decisions[key] = decision
    expected_queries = {(row["workbook"], row["path"]) for row in plan["queries"]}
    if set(query_decisions) != expected_queries:
        raise ValueError("Decisions must cover every query exactly once.")
    dependency_decisions = {}
    for decision in decisions["workbooks"]:
        _decision(decision)
        if set(decision) - {"path", "decision", "requiredWorkloads", "requiredDataConnectors", "requiredWorkspaceFunctions"}:
            raise ValueError("Unknown workbook dependency decision fields.")
        key = decision.get("path")
        if not isinstance(key, str):
            raise ValueError("Workbook review path must be a string.")
        errors = dependency_validation_errors({"contentProvenance": {
            field: decision.get(field, []) for field in ("requiredWorkloads", "requiredDataConnectors")}})
        if errors:
            raise ValueError("; ".join(errors))
        if "requiredWorkspaceFunctions" in decision:
            validate_functions(root, decision["requiredWorkspaceFunctions"])
        if key in dependency_decisions:
            raise ValueError("Duplicate workbook dependency decision.")
        dependency_decisions[key] = decision
    if set(dependency_decisions) != {row["path"] for row in plan["inventory"]}:
        raise ValueError("Decisions must cover every workbook exactly once.")
    config = {"workbookResolutions": {}, "workbookDependencies": {}}
    unresolved, parser_actions = [], []
    for path, decision in dependency_decisions.items():
        if decision["decision"] == "defer":
            unresolved.append({"workbook": path, "reason": "Dependency review deferred."})
            settings = {"dependencyReviewRequired": True}
        else:
            if not {"requiredWorkloads", "requiredDataConnectors", "requiredWorkspaceFunctions"} <= set(decision):
                raise ValueError("Accepted/changed dependencies require explicit workloads, connectors and functions.")
            settings = {key: deepcopy(decision[key]) for key in (
                "requiredWorkloads", "requiredDataConnectors", "requiredWorkspaceFunctions")}
            errors = dependency_validation_errors({"contentProvenance": settings})
            if errors:
                raise ValueError("; ".join(errors))
            validate_functions(root, settings["requiredWorkspaceFunctions"])
        config["workbookDependencies"][path] = settings
    for row in plan["queries"]:
        decision = query_decisions[(row["workbook"], row["path"])]
        if decision.get("querySha256") != row["querySha256"]:
            raise ValueError("Query decision must bind the exact current source template hash.")
        path = row["workbook"]
        settings = config["workbookDependencies"][path]
        if decision["decision"] == "defer":
            settings["dependencyReviewRequired"] = True
            unresolved.append({"workbook": path, "path": row["path"], "reason": "Query review deferred."})
            continue
        tables = _strings(decision.get("tables"), "tables")
        aliases = _strings(decision.get("workspaceFunctions", []), "workspaceFunctions")
        declared_aliases = {item["functionAlias"] for item in settings.get("requiredWorkspaceFunctions", [])}
        explicit_calls = workbook.opaque_functions(row["queryKql"], include_bare=False)
        expected_aliases = set(row["workspaceFunctions"]) - (set(tables) - explicit_calls - declared_aliases)
        if set(aliases) != expected_aliases:
            raise ValueError("Reviewed workspaceFunctions must match exact source aliases.")
        if not set(aliases) <= declared_aliases or set(aliases) & set(tables):
            raise ValueError("Function aliases need vetted prerequisites and separate underlying tables.")
        source_free_literal = rewrite.is_source_free_literal_query(row["queryKql"])
        if not tables and not row["scopeHelper"] and not source_free_literal:
            raise ValueError("Accepted query requires explicit underlying source tables.")
        resolution = {"querySha256": row["querySha256"], "tables": tables,
                      "evidence": {"actor": actor, "reference": reference, "planSha256": expected_plan_sha256,
                                   "decision": decision["decision"], "querySha256": row["querySha256"]}}
        if aliases:
            resolution["workspaceFunctions"] = aliases
        config["workbookResolutions"].setdefault(path, {})[row["path"]] = resolution
        blockers = list(row["technicalBlockers"])
        contract = migrator.convert(row["queryKql"], tables=tables, source_id=row["path"],
                                    artifact_type="workbook", resolve=False)
        if not row["scopeHelper"] and (contract["status"] != "converted" or contract["unsupported"]):
            blockers.append(contract["blockedReason"] or "Shared conversion requires technical review.")
        if aliases and contract["convertedKql"] != row["queryKql"]:
            blockers.append("Shared conversion would modify preserved function KQL.")
        branches = decision.get("optionalBranches", [])
        if not isinstance(branches, list):
            raise ValueError("optionalBranches must be an array.")
        for branch in branches:
            if (not isinstance(branch, dict) or set(branch) != {
                    "functionAlias", "sourcePath", "sourceSha256", "branch", "decision"}
                    or branch["decision"] not in ("keep", "remove-request", "defer")
                    or not isinstance(branch["branch"], str) or not branch["branch"].strip()
                    or {key: branch[key] for key in ("functionAlias", "sourcePath", "sourceSha256")}
                    not in settings.get("requiredWorkspaceFunctions", [])):
                raise ValueError("Optional branch decisions must bind a current exact reviewed function prerequisite.")
            if branch["decision"] == "remove-request":
                _, definition = function_definition(root, branch["sourcePath"])
                if definition["FunctionQuery"].count(branch["branch"]) != 1:
                    raise ValueError("Parser-change requests require an exact unambiguous current source branch.")
                parser_actions.append({**branch, "actor": actor, "reference": reference,
                                       "branchSha256": workbook.query_hash(branch["branch"]),
                                       "status": "requested-not-applied", "planSha256": expected_plan_sha256})
                blockers.append("Optional parser change requested, not applied or verified in current source.")
            elif branch["decision"] == "defer":
                blockers.append("Optional parser branch review deferred.")
        for reason in blockers:
            unresolved.append({"workbook": path, "path": row["path"], "reason": reason})
        if blockers:
            settings["dependencyReviewRequired"] = True
    catalog = mapping_catalog.load_mapping_catalog()["tables"]
    for path, settings in config["workbookDependencies"].items():
        sources = {table for row in config["workbookResolutions"].get(path, {}).values() for table in row["tables"]}
        targets = {catalog.get(table, {}).get("ahTable") or table for table in telemetry_data_types(sources)}
        declared = {table for record in settings.get("requiredWorkloads", []) for table in record["dataTypes"]}
        if not targets <= declared:
            settings["dependencyReviewRequired"] = True
            unresolved.append({"workbook": path, "reason": "Reviewed workloads do not cover all output tables."})
        if any(table not in sources for record in settings.get("requiredDataConnectors", []) for table in record["dataTypes"]):
            raise ValueError("Reviewed connector references tables outside reviewed query sources.")
        used = {alias for row in config["workbookResolutions"].get(path, {}).values()
                for alias in row.get("workspaceFunctions", [])}
        declared_aliases = {record["functionAlias"] for record in settings.get("requiredWorkspaceFunctions", [])}
        if used != declared_aliases:
            settings["dependencyReviewRequired"] = True
            unresolved.append({"workbook": path, "reason": "Function prerequisite coverage is incomplete."})
    reviewed_aliases = {record["functionAlias"] for settings in config["workbookDependencies"].values()
                        for record in settings.get("requiredWorkspaceFunctions", [])}
    reviewed_definitions = [record for record in plan["workspaceFunctionCandidates"]
                            if record.get("functionAlias") in reviewed_aliases]
    receipt = {
        "schemaVersion": "1.0.0", "planSha256": expected_plan_sha256,
        "actor": actor, "reference": reference, "reviewedAt": datetime.now(timezone.utc).isoformat(),
        "decisions": decisions, "configSha256": digest(config), "unresolved": unresolved,
        "sourceInventory": plan["inventory"], "metadataWorkspaceId": plan["workspaceId"],
        "parserChangeActions": parser_actions,
        "coverageWarnings": [record["coverageWarning"] for record in reviewed_definitions
                             if "coverageWarning" in record],
        "functionDependencyCoverage": [{
            key: record[key] for key in (
                "functionAlias", "sourcePath", "sourceSha256", "nestedFunctions",
                "unresolvedBranchCandidates", "nestedDiscoveryExhaustive", "externalSourceWarnings")
        } for record in reviewed_definitions],
        "runtimeParityVerified": False, "writesSource": False,
        "dependencyReviewRequired": bool(unresolved),
    }
    output = Path(output_directory).expanduser()
    if any(p.is_symlink() for p in (output, *output.parents)):
        raise ValueError("Review output must not use symlinks.")
    output = output.resolve()
    if (not output.is_relative_to(root) or output == root
            or output.parts[len(root.parts)].casefold() in {
                "workbooks", "xdr workbooks", "data", "parsers", "workspace functions",
                "xdr detections", "analytic rules", "package", "data connectors", "hunting queries", "playbooks"}):
        raise ValueError("Review output must be run-local and outside solution content directories.")
    files = [(output / "conversion-config.json", config), (output / "workbook-review-receipt.json", receipt)]
    if any(path.exists() or path.is_symlink() for path, _ in files):
        raise ValueError("Review outputs already exist; choose a new run-local review directory.")
    output.mkdir(parents=True, exist_ok=True)
    created = []
    try:
        for path, value in files:
            # Atomic publication uses the existing safe compare-and-replace writer.
            staged = path.with_name("." + path.name + ".staged")
            if staged.exists() or staged.is_symlink():
                raise ValueError("Review staging file already exists.")
            _write(staged, (json.dumps(value, indent=2, ensure_ascii=False) + "\n").encode(), None)
            try:
                if path.exists() or path.is_symlink():
                    raise ValueError("Review output changed before publication.")
                if any(parent.is_symlink() for parent in (output, *output.parents)):
                    raise ValueError("Review output changed to a symlink before publication.")
                # Hard-link publication is atomic and refuses an existing target.
                os.link(staged, path, follow_symlinks=False)
            finally:
                if staged.exists() and not staged.is_symlink():
                    staged.unlink()
            created.append(path)
    except Exception:
        for path in created:
            path.unlink()
        raise
    return {"planSha256": expected_plan_sha256, "configPath": str(files[0][0]),
            "receiptPath": str(files[1][0]), "dependencyReviewRequired": bool(unresolved),
            "unresolved": unresolved, "parserChangeActions": parser_actions}
