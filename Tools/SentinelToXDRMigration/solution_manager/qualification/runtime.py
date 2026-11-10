from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor
import hashlib
import json
import re
import threading
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
from pathlib import Path
from typing import Any

import yaml

from solution_manager.core.artifacts import (
    existing_artifact_path,
    report_directory,
    portable_artifact,
    write_json_artifact,
)
from solution_manager.migration.converter import custom_detail_schema_errors, load_config, xdr_detection_files
from solution_manager.authoring.dependencies import dependency_identity, live_dependency_check
from solution_manager.core.content_paths import content_path
from solution_manager.qualification.graph_auth import (
    GRAPH_RESOURCE_DEFAULT_SCOPE,
    validate_delegated_graph_claims,
)
from solution_manager.core.onboarding import (
    AUTH_RECORD_NAME,
    CONFIG_NAME,
    GRAPH_SCOPE,
    TOKEN_CACHE_NAME,
    _load_auth_record,
    _read_json,
    _state_dir,
)
from solution_manager.qualification.graph_client_config import (
    azure_cli_credential,
    configured_azure_cli_profile,
    graph_auth_record_path,
    graph_token_cache_name,
    resolve_graph_client_id,
    verify_graph_auth_binding,
)
from solution_manager.reporting.report import write_runtime_validation_report
from solution_manager.qualification.runtime_consent import require_runtime_query_consent
from solution_manager.migration.source_runtime_waiver import SOURCE_PROVIDERS
from solution_manager.core.target_context import require_locked_target

ADVANCED_HUNTING_ENDPOINT = "https://graph.microsoft.com/v1.0/security/runHuntingQuery"
MAX_GRAPH_IN_FLIGHT_REQUESTS = 5
MAX_ADVANCED_HUNTING_WORKERS = 3
ADVANCED_HUNTING_MIN_INTERVAL_SECONDS = 1.5
MAX_ADVANCED_HUNTING_RETRIES = 3
ADVANCED_HUNTING_RETRY_BUDGET_SECONDS = 5 * 60
MAX_ADVANCED_HUNTING_SAMPLE_ROWS = 10
_GRAPH_REQUEST_SEMAPHORE = threading.BoundedSemaphore(MAX_GRAPH_IN_FLIGHT_REQUESTS)
PROVIDER_PLATFORMS = {
    "graph": "Microsoft Defender XDR Advanced Hunting",
    "triage-mcp": "Microsoft Sentinel Triage MCP",
    "log-analytics-cli": "Microsoft Sentinel Log Analytics",
    "azure-monitor-sdk": "Microsoft Sentinel Log Analytics (Azure Monitor Query SDK)",
}
PROVIDER_QUERY_SURFACES = {
    "graph": "defender-advanced-hunting",
    "triage-mcp": "microsoft-sentinel-triage",
    "log-analytics-cli": "log-analytics-workspace",
    "azure-monitor-sdk": "log-analytics-workspace",
}
SUPPORTED_EXTERNAL_PROVIDERS = frozenset(
    provider for provider in PROVIDER_PLATFORMS if provider != "graph"
)
PROVIDER_GAP_CODES = frozenset({
    "tool-unavailable",
    "authentication",
    "authorization",
    "timeout",
    "transient-provider-error",
    "batch-provider-failure",
})


def _detection_files(output: Path) -> list[Path]:
    return xdr_detection_files(output)


def _effective_sdk_target(
    solution: Path,
    supplied_target: dict[str, str],
) -> dict[str, str]:
    workflow_state = existing_artifact_path(solution, "workflow-state.json")
    if not workflow_state.is_file():
        return supplied_target
    locked = require_locked_target(solution, materialize_missing=False)
    fields = (
        "tenantId",
        "subscriptionId",
        "resourceGroup",
        "workspaceResourceId",
        "workspaceCustomerId",
    )
    mismatches = [
        field
        for field in fields
        if not isinstance(supplied_target.get(field), str)
        or supplied_target[field].strip().casefold()
        != str(locked[field]).strip().casefold()
    ]
    if mismatches:
        raise ValueError(
            "SDK target conflicts with the locked Qualification target: "
            + ", ".join(mismatches)
        )
    return {field: str(locked[field]) for field in fields}


def _workflow_profile(root: Path) -> str | None:
    workflow_state = existing_artifact_path(root, "workflow-state.json")
    if not workflow_state.is_file():
        return None
    try:
        state = json.loads(workflow_state.read_text(encoding="utf-8-sig"))
    except (OSError, json.JSONDecodeError):
        return "unknown"
    profile = (state.get("context") or {}).get("workflowProfile")
    return profile if isinstance(profile, str) else "unknown"


def _assert_graph_auth_tenant_scope(
    state_root: Path,
    *,
    locked_tenant_id: str,
    requested_tenant_id: str | None,
) -> dict[str, Any]:
    if (
        requested_tenant_id
        and requested_tenant_id.strip().casefold()
        != locked_tenant_id.casefold()
    ):
        raise ValueError("requested Graph tenant does not match the selected workflow tenant")
    graph_client_id = resolve_graph_client_id(state_root, "advancedHunting")
    record_path = graph_auth_record_path(
        state_root,
        "advancedHunting",
        graph_client_id,
        AUTH_RECORD_NAME,
    )
    record = _load_auth_record(record_path)
    record_tenant = getattr(record, "tenant_id", None) if record is not None else None
    config = _read_json(state_root / CONFIG_NAME)
    configured_tenant = config.get("tenantId")
    use_cli_fallback = (
        (not isinstance(record_tenant, str) or record_tenant.strip().casefold() != locked_tenant_id.casefold())
        and configured_azure_cli_profile(state_root) is not None
        and azure_cli_credential(tenant_id=locked_tenant_id, state_root=state_root) is not None
    )
    if not use_cli_fallback:
        if not isinstance(record_tenant, str) or not record_tenant.strip():
            raise ValueError(
                "Graph authentication record has no tenant identity for the selected workflow tenant"
            )
        if record_tenant.strip().casefold() != locked_tenant_id.casefold():
            raise ValueError(
                "Graph authentication record tenant does not match the selected workflow tenant"
            )
    if (
        configured_tenant
        and str(configured_tenant).strip().casefold() != locked_tenant_id.casefold()
    ):
        raise ValueError(
            "Graph authentication configuration tenant does not match the selected workflow tenant"
        )
    return config


def _assert_graph_auth_scope(
    state_root: Path,
    *,
    locked_target: dict[str, str],
    requested_tenant_id: str | None,
) -> None:
    config = _assert_graph_auth_tenant_scope(
        state_root,
        locked_tenant_id=locked_target["tenantId"],
        requested_tenant_id=requested_tenant_id,
    )
    expected_config = {
        "subscriptionId": locked_target["subscriptionId"],
        "workspaceResourceId": locked_target["workspaceResourceId"],
        "workspaceCustomerId": locked_target["workspaceCustomerId"],
    }
    for field, expected in expected_config.items():
        configured = config.get(field)
        if not configured:
            continue
        actual = str(configured).strip().rstrip("/")
        expected_value = str(expected).strip().rstrip("/")
        if actual.casefold() != expected_value.casefold():
            raise ValueError(
                f"Graph authentication configuration {field} does not match "
                "the locked Qualification target"
            )


def _same_execution_scope(
    dispatch_snapshot: dict[str, Any],
    current_consent: dict[str, Any],
) -> bool:
    family = dispatch_snapshot.get("family")
    if (
        dispatch_snapshot.get("status") != "approved"
        or family not in {"sentinelSourceQueryFamily", "defenderXdrQueryFamily"}
        or dispatch_snapshot.get("provider") != current_consent.get("provider")
        or family != current_consent.get("family")
    ):
        return False
    dispatch_binding = dispatch_snapshot.get("binding")
    current_binding = current_consent.get("binding")
    if not isinstance(dispatch_binding, dict) or not isinstance(current_binding, dict):
        return False
    identity_fields = (
        "solution",
        "workflowProfile",
        "runId",
        "targetFingerprintSha256",
    )
    if any(
        dispatch_binding.get(field) != current_binding.get(field)
        for field in identity_fields
    ):
        return False
    dispatch_families = dispatch_binding.get("families")
    current_families = current_binding.get("families")
    return (
        isinstance(dispatch_families, dict)
        and isinstance(current_families, dict)
        and dispatch_families.get(family) == current_families.get(family)
    )


def _runtime_consent_for_import(
    root: Path,
    *,
    provider: str,
    source_provider: str,
) -> dict[str, Any] | None:
    workflow_state = existing_artifact_path(root, "workflow-state.json")
    if workflow_state.is_file():
        state = json.loads(workflow_state.read_text(encoding="utf-8-sig"))
        if (state.get("context") or {}).get("workflowProfile") == "authoring":
            return None
    return require_runtime_query_consent(
        root,
        family="sentinelSourceQueryFamily",
        provider=provider,
        source_provider=source_provider,
        allow_legacy=True,
    )


def _write_runtime_artifacts(
    root: Path,
    provider: str,
    results: list[dict[str, Any]],
    *,
    table_availability: dict[str, Any] | None = None,
    provider_fallback: dict[str, Any] | None = None,
    provider_failure: dict[str, Any] | None = None,
    family_complete: bool | None = None,
    runtime_query_consent: dict[str, Any] | None = None,
    runtime_query_dispatch_snapshot: dict[str, Any] | None = None,
) -> dict[str, Any]:
    output = report_directory(root, create=True)
    summary = {
        "solution": str(root),
        "platform": PROVIDER_PLATFORMS[provider],
        "querySurface": PROVIDER_QUERY_SURFACES[provider],
        "provider": provider,
        "total": len(results),
        "valid": sum(item["status"] == "passed" for item in results),
        "invalid": sum(item["status"] == "failed" for item in results),
        "blocked": sum(item["status"] == "blocked" for item in results),
        "notRun": sum(item["status"] == "not-run" for item in results),
        "tableAvailability": table_availability or {},
        "providerFallback": provider_fallback,
        "runtimeQueryConsent": {
            "status": (
                "not-applicable-authoring"
                if runtime_query_consent is None
                and _workflow_profile(root) == "authoring"
                else "not-required-legacy-workflow"
                if runtime_query_consent is None
                else "approved"
            ),
            "family": runtime_query_consent.get("family")
            if runtime_query_consent
            else None,
            "provider": runtime_query_consent.get("provider")
            if runtime_query_consent
            else None,
            "workflowProfile": runtime_query_consent.get("workflowProfile")
            if runtime_query_consent
            else _workflow_profile(root),
            "planSha256": runtime_query_consent.get("planSha256")
            if runtime_query_consent
            else None,
            "consentScope": runtime_query_consent.get("consentScope")
            if runtime_query_consent
            else None,
            "labConsentSha256": runtime_query_consent.get("labConsentSha256")
            if runtime_query_consent
            else None,
            "authoringConsentSha256": runtime_query_consent.get(
                "authoringConsentSha256"
            )
            if runtime_query_consent
            else None,
            "queryHashesAreConsentBindings": (
                runtime_query_consent.get("consentScope")
                == "one-run-authoring-query-only"
                if runtime_query_consent
                else False
            ),
            "runSnapshotPath": runtime_query_consent.get("runSnapshotPath")
            if runtime_query_consent
            else None,
            "authenticationClassification": runtime_query_consent.get(
                "authenticationClassification"
            )
            if runtime_query_consent
            else None,
            "binding": runtime_query_consent.get("binding")
            if runtime_query_consent
            else None,
            "interactiveAuthenticationAuthorized": False,
            "environmentWritesAuthorized": False,
        },
        "runtimeQueryDispatchSnapshot": (
            runtime_query_dispatch_snapshot
            if runtime_query_dispatch_snapshot is not None
            else runtime_query_consent
        ),
        "results": results,
    }
    if family_complete is not None:
        summary["familyComplete"] = family_complete
    if provider_failure:
        summary["providerFailure"] = provider_failure
    if provider in SOURCE_PROVIDERS:
        from solution_manager.migration.source_runtime_waiver import missing_schema_whitelist_match

        detection_paths = {
            path.relative_to(root / "XDR Detections").as_posix(): path
            for path in _detection_files(root / "XDR Detections")
        }
        expected_query_hashes = {
            name: current_runtime_query_hash(root, path, provider=provider)
            for name, path in detection_paths.items()
        }
        classified = []
        hash_bound_names: set[str] = set()
        for item in results:
            if not isinstance(item, dict):
                continue
            name = str(item.get("detection") or "").replace("\\", "/")
            match = missing_schema_whitelist_match(item, provider=provider)
            if match:
                expected_hash = expected_query_hashes.get(name)
                hash_matches = (
                    expected_hash is not None
                    and item.get("querySha256") == expected_hash
                )
                assessment = {
                    "detection": item.get("detection"),
                    "querySha256": item.get("querySha256"),
                    **match,
                    "status": "candidate-blocked",
                    "applied": False,
                }
                if hash_matches:
                    hash_bound_names.add(name)
                else:
                    assessment["blockedReason"] = (
                        "The failed result query hash does not match the current "
                        "source query hash."
                    )
                classified.append(assessment)
        result_names = [
            str(item.get("detection") or "").replace("\\", "/")
            for item in results
            if isinstance(item, dict)
        ]
        inventory_matches = (
            len(result_names) == len(expected_query_hashes)
            and len(result_names) == len(set(result_names))
            and set(result_names) == set(expected_query_hashes)
        )
        family_can_apply = (
            bool(hash_bound_names)
            and provider_failure is None
            and provider_fallback is None
            and family_complete is True
            and inventory_matches
            and all(isinstance(item, dict) for item in results)
            and all(
                (
                    item.get("status") == "passed"
                    and item.get("querySha256")
                    == expected_query_hashes.get(
                        str(item.get("detection") or "").replace("\\", "/")
                    )
                )
                or (
                    item.get("status") == "failed"
                    and str(item.get("detection") or "").replace("\\", "/")
                    in hash_bound_names
                    and item.get("querySha256")
                    == expected_query_hashes.get(
                        str(item.get("detection") or "").replace("\\", "/")
                    )
                )
                for item in results
            )
        )
        for item in classified:
            name = str(item.get("detection") or "").replace("\\", "/")
            item["applied"] = family_can_apply and name in hash_bound_names
            if item["applied"]:
                item["status"] = "source-waived"
            elif "blockedReason" not in item:
                item["blockedReason"] = (
                    "The complete source family contains another failure or is not confirmed complete."
                )
        summary["sourceWhitelist"] = classified
    json_path = output / f"runtime-validation.{provider}.json"
    html_path = output / f"runtime-validation.{provider}.html"
    summary["jsonReport"] = str(json_path)
    summary["htmlReport"] = str(html_path)
    write_json_artifact(root, json_path, summary)
    write_runtime_validation_report(portable_artifact(root, summary), html_path)
    from solution_manager.core.workflow import invalidate_runtime_completion

    invalidate_runtime_completion(
        root,
        [],
        reason=(
            f"new {provider} provider evidence was recorded after offline Authoring completion."
        ),
    )
    return summary


def _query_sha256(query: str) -> str:
    return hashlib.sha256(query.encode("utf-8")).hexdigest()


def _source_query(root: Path, detection: dict[str, Any]) -> str:
    source = ((detection.get("contentProvenance") or {}).get("source") or {})
    source_reference = source.get("path")
    if not isinstance(source_reference, str) or not source_reference:
        raise ValueError("Custom Detection provenance must identify its source Analytic Rule")
    source_path = content_path(root, source_reference)
    with source_path.open(encoding="utf-8-sig") as handle:
        document = yaml.safe_load(handle) or {}
    if not isinstance(document, dict) or not isinstance(document.get("query"), str):
        raise ValueError(f"source Analytic Rule has no query: {source_reference}")
    return document["query"]


def current_runtime_query_hash(
    root: Path,
    detection_path: Path,
    *,
    provider: str,
) -> str:
    with detection_path.open(encoding="utf-8-sig") as handle:
        document = yaml.safe_load(handle) or {}
    if provider == "graph":
        query = (((document.get("properties") or {}).get("queryCondition") or {}).get("queryText"))
        if not isinstance(query, str):
            raise ValueError("Custom Detection has no Advanced Hunting query")
        return _query_sha256(query)
    return _query_sha256(_source_query(root, document))


def current_runtime_evidence(solution: str | Path) -> dict[str, Any]:
    """Require complete, exact-query evidence for both sides of the validation family."""
    root = Path(solution).expanduser().resolve()
    output = root / "XDR Detections"
    paths = {
        path.relative_to(output).as_posix(): path
        for path in _detection_files(output)
    }
    if not paths:
        return {"passed": False, "issues": ["no converted detections are available for runtime validation"]}

    issues: list[str] = []
    current_query_failures: list[str] = []
    graph_hashes = {
        name: current_runtime_query_hash(root, path, provider="graph")
        for name, path in paths.items()
    }
    source_reports = []
    for provider in ("triage-mcp", "azure-monitor-sdk", "log-analytics-cli"):
        report_path = report_directory(root) / f"runtime-validation.{provider}.json"
        if report_path.is_file():
            source_reports.append((provider, report_path))
    graph_path = report_directory(root) / "runtime-validation.graph.json"

    def inspect_family(
        provider: str,
        report_path: Path,
        expected_hashes: dict[str, str],
        *,
        require_actual_schema: bool = False,
    ) -> tuple[bool, list[str], bool, list[dict[str, Any]]]:
        if not report_path.is_file():
            return False, [f"{provider} runtime report is missing"], False, []
        try:
            report = json.loads(report_path.read_text(encoding="utf-8-sig"))
        except (OSError, json.JSONDecodeError):
            return False, [f"{provider} runtime report is invalid"], False, []
        if not isinstance(report, dict) or report.get("provider") != provider:
            return False, [f"{provider} runtime report provider does not match"], False, []
        entries = report.get("results")
        if not isinstance(entries, list):
            return False, [f"{provider} runtime report has no results list"], False, []
        from solution_manager.migration.source_runtime_waiver import missing_schema_whitelist_match

        def candidate_assessments() -> list[dict[str, Any]]:
            if provider not in SOURCE_PROVIDERS:
                return []
            candidates = []
            for candidate in entries:
                if not isinstance(candidate, dict):
                    continue
                candidate_name = str(candidate.get("detection") or "").replace("\\", "/")
                expected_hash = expected_hashes.get(candidate_name)
                if expected_hash is None:
                    continue
                match = missing_schema_whitelist_match(
                    candidate,
                    provider=provider,
                    expected_query_sha256=expected_hash,
                )
                if match:
                    candidates.append({
                        "detection": candidate_name,
                        "querySha256": expected_hash,
                        **match,
                        "status": "candidate-blocked",
                        "applied": False,
                        "blockedReason": (
                            "The source report has a provider, surface, family-completion, "
                            "fallback, or inventory failure."
                        ),
                    })
            return candidates

        if (
            report.get("querySurface") not in (
                None,
                PROVIDER_QUERY_SURFACES.get(provider),
            )
            or report.get("providerFailure")
            or report.get("familyComplete") is False
        ):
            return False, [
                f"{provider} runtime report has a provider, surface, or family-completion failure"
            ], False, candidate_assessments()
        by_name: dict[str, dict[str, Any]] = {}
        for entry in entries:
            if not isinstance(entry, dict):
                continue
            name = str(entry.get("detection") or "").replace("\\", "/")
            if name in by_name:
                return False, [f"{provider} runtime report has duplicate results for {name}"], False, candidate_assessments()
            by_name[name] = entry
        if set(by_name) != set(expected_hashes):
            return False, [
                f"{provider} runtime report is not a complete detection family "
                f"(missing={sorted(set(expected_hashes) - set(by_name))}, "
                f"unknown={sorted(set(by_name) - set(expected_hashes))})"
            ], False, candidate_assessments()
        source_whitelist: list[dict[str, Any]] = []

        failures = []
        for name, expected_hash in expected_hashes.items():
            entry = by_name[name]
            hash_matches = entry.get("querySha256") == expected_hash
            if provider in SOURCE_PROVIDERS and entry.get("status") == "passed":
                current_document = yaml.safe_load(paths[name].read_text(encoding="utf-8-sig"))
                if entry.get("dependencyProvenanceSha256") != dependency_identity(current_document):
                    failures.append(f"{provider} dependency provenance for {name} is stale or unbound")
            source_match = (
                missing_schema_whitelist_match(
                    entry,
                    provider=provider,
                    expected_query_sha256=expected_hash,
                )
                if provider in SOURCE_PROVIDERS
                and not report.get("providerFallback")
                else None
            )
            if source_match:
                source_whitelist.append({
                    "detection": name,
                    "querySha256": expected_hash,
                    **source_match,
                })
            if (
                provider == "graph"
                and require_actual_schema
                and entry.get("status") == "passed"
                and hash_matches
            ):
                schema = entry.get("schema")
                if not isinstance(schema, list):
                    failures.append(
                        "graph output schema is missing for "
                        f"{name}; schemaColumnCount is not sufficient evidence"
                    )
                else:
                    schema_columns = []
                    malformed_schema = False
                    seen_schema_names: set[str] = set()
                    for column in schema:
                        if not isinstance(column, dict):
                            malformed_schema = True
                            break
                        column_name = column.get("name", column.get("Name"))
                        column_type = column.get("type", column.get("Type"))
                        if (
                            not isinstance(column_name, str)
                            or not column_name.strip()
                            or not isinstance(column_type, str)
                            or not column_type.strip()
                            or column_name.casefold() in seen_schema_names
                        ):
                            malformed_schema = True
                            break
                        seen_schema_names.add(column_name.casefold())
                        schema_columns.append(column)
                    if not schema_columns or malformed_schema:
                        failures.append(
                            "graph output schema for "
                            f"{name} must contain usable, uniquely named columns with types"
                        )
                        continue
                    try:
                        document = yaml.safe_load(
                            paths[name].read_text(encoding="utf-8-sig")
                        ) or {}
                    except (OSError, yaml.YAMLError) as exc:
                        failures.append(
                            f"cannot verify current XDR output bindings for {name}: {exc}"
                        )
                    else:
                        binding_errors = custom_detail_schema_errors(document, schema)
                        failures.extend(
                            f"graph output schema for {name}: {error}"
                            for error in binding_errors
                        )
            if entry.get("status") == "failed" and hash_matches:
                if source_match:
                    continue
                current_query_failures.append(
                    f"{provider} query validation failed for {name}: "
                    f"{entry.get('error') or 'provider reported a KQL/runtime failure'}"
                )
            if entry.get("status") != "passed":
                failures.append(f"{provider} validation for {name} is {entry.get('status')!r}")
            if not hash_matches:
                failures.append(
                    f"{provider} validation for {name} is stale or unbound to the exact current query"
                )
        waived_failure = bool(source_whitelist) and not failures
        for item in source_whitelist:
            item["applied"] = waived_failure
            if not waived_failure:
                item["status"] = "candidate-blocked"
                item["blockedReason"] = (
                    "The complete source query family has another failed, blocked, "
                    "not-run, stale, or incomplete result."
                )
        return not failures and not waived_failure, failures, waived_failure, source_whitelist

    source_passed = False
    source_waiver_only_blocker = False
    source_whitelist: list[dict[str, Any]] = []
    source_provider_used = None
    source_issues: list[str] = []
    available_source_reports = [
        (provider, report_path)
        for provider, report_path in source_reports
        if report_path.is_file()
    ]
    for index, (provider, report_path) in enumerate(available_source_reports):
        try:
            selected_report = json.loads(report_path.read_text(encoding="utf-8-sig"))
        except (OSError, UnicodeError, json.JSONDecodeError):
            break
        unverified_fallback_claim = (
            index == 0
            and isinstance(selected_report, dict)
            and bool(selected_report.get("providerFallback"))
        )
        if index:
            previous_provider, previous_path = available_source_reports[0]
            try:
                previous_report = json.loads(previous_path.read_text(encoding="utf-8-sig"))
            except (OSError, UnicodeError, json.JSONDecodeError):
                break
            if (
                previous_provider != "triage-mcp"
                or not isinstance(previous_report, dict)
                or not isinstance(previous_report.get("providerFailure"), dict)
            ):
                break
            proof = selected_report.get("providerFallback") if isinstance(selected_report, dict) else None
            if (
                not isinstance(proof, dict)
                or proof.get("mcpProvider") != "triage-mcp"
                or proof.get("fallbackProvider") != provider
                or proof.get("batchComplete") is not True
                or proof.get("permissionsVerified") is not True
                or proof.get("kqlError") is not False
            ):
                continue
        current_failures_before = len(current_query_failures)
        passed, family_issues, waiver_only, current_whitelist = inspect_family(
            provider,
            report_path,
            {
                name: current_runtime_query_hash(root, path, provider=provider)
                for name, path in paths.items()
            },
        )
        if passed and not unverified_fallback_claim:
            source_passed = True
            source_provider_used = provider
            source_whitelist = current_whitelist
            break
        if unverified_fallback_claim:
            source_issues.extend(family_issues)
            source_issues.append(
                f"{provider} runtime report claims an unverified provider fallback"
            )
            if len(current_query_failures) > current_failures_before:
                break
            break
        if waiver_only:
            source_whitelist = current_whitelist
            source_waiver_only_blocker = True
            source_provider_used = provider
            break
        if current_whitelist:
            source_whitelist = current_whitelist
        source_issues.extend(family_issues)
        if len(current_query_failures) > current_failures_before:
            break
        try:
            report = json.loads(report_path.read_text(encoding="utf-8-sig"))
        except (OSError, UnicodeError, json.JSONDecodeError):
            break
        if (
            provider != "triage-mcp"
            or not isinstance(report, dict)
            or not isinstance(report.get("providerFailure"), dict)
        ):
            break
    if not source_passed and not source_waiver_only_blocker:
        issues.extend(source_issues or ["no Sentinel runtime validation report is available"])

    graph_passed, graph_issues, _, _ = inspect_family(
        "graph",
        graph_path,
        graph_hashes,
        require_actual_schema=bool(source_whitelist),
    )
    if not graph_passed:
        issues.extend(graph_issues)
    source_waived = source_waiver_only_blocker
    source_waiver_only_blocker = source_waiver_only_blocker and graph_passed
    if source_waiver_only_blocker:
        issues.append(
            "Sentinel source IdentityInfo query remains failed in raw evidence; "
            "the built-in source table whitelist is not runtime success"
        )
    return {
        "passed": source_passed and graph_passed,
        "sentinelProvider": source_provider_used,
        "sourceStatus": (
            "source-waived"
            if source_waived
            else "passed"
            if source_passed
            else "blocked"
        ),
        "sourceWhitelist": source_whitelist,
        "sourceWaiverOnlyBlocker": source_waiver_only_blocker,
        "currentQueryFailures": current_query_failures,
        "issues": issues,
        "sentinelReport": (
            str(report_directory(root) / f"runtime-validation.{source_provider_used}.json")
            if source_provider_used else None
        ),
        "graphReport": str(graph_path) if graph_passed else None,
    }


def _load_provider_fallback(
    path: str | Path | None,
    *,
    query_family: str,
    fallback_provider: str,
) -> dict[str, Any] | None:
    if path is None:
        return None
    evidence = json.loads(Path(path).expanduser().read_text(encoding="utf-8"))
    if not isinstance(evidence, dict):
        raise ValueError("provider-gap evidence must be a JSON object")
    if (
        evidence.get("mcpProvider") != "triage-mcp"
        or evidence.get("queryFamily") != query_family
        or evidence.get("fallbackProvider") != fallback_provider
        or evidence.get("reasonCode") not in PROVIDER_GAP_CODES
        or evidence.get("batchComplete") is not True
        or evidence.get("scopeVerified") is not True
        or evidence.get("permissionsVerified") is not True
        or evidence.get("kqlError") is not False
    ):
        raise ValueError(
            "provider-gap evidence must record an official Triage provider failure, "
            "the complete query-family fallback, exact scope and permissions, and no KQL error"
        )
    tool_name = evidence.get("advertisedTool")
    if not isinstance(tool_name, str) or not tool_name.strip():
        raise ValueError("provider-gap evidence requires the advertised Triage tool name or 'unavailable'")
    scope_reference = evidence.get("scopeReference")
    if not isinstance(scope_reference, str) or not scope_reference.strip() or len(scope_reference) > 500:
        raise ValueError("provider-gap evidence requires the exact scoped target reference")
    reason = evidence.get("reason")
    if not isinstance(reason, str) or not reason.strip() or len(reason) > 500:
        raise ValueError("provider-gap evidence requires a concise reason of at most 500 characters")
    return {
        "mcpProvider": "triage-mcp",
        "advertisedTool": tool_name.strip(),
        "queryFamily": query_family,
        "fallbackProvider": fallback_provider,
        "scopeReference": scope_reference.strip(),
        "reasonCode": evidence["reasonCode"],
        "reason": reason.strip(),
        "batchComplete": True,
        "scopeVerified": True,
        "permissionsVerified": True,
        "kqlError": False,
    }


def _advanced_hunting_token(
    state_root: Path,
    *,
    tenant_id: str | None = None,
) -> str:
    from azure.identity import DeviceCodeCredential, TokenCachePersistenceOptions

    client_id = resolve_graph_client_id(state_root, "advancedHunting")
    record_path = graph_auth_record_path(
        state_root, "advancedHunting", client_id, AUTH_RECORD_NAME
    )
    record = _load_auth_record(record_path)
    config = _read_json(state_root / CONFIG_NAME)
    configured_tenant = config.get("tenantId") or getattr(record, "tenant_id", None)
    effective_tenant = tenant_id or configured_tenant
    record_tenant = getattr(record, "tenant_id", None) if record is not None else None
    if (
        effective_tenant
        and (
            record is None
            or not isinstance(record_tenant, str)
            or record_tenant.strip().casefold() != str(effective_tenant).strip().casefold()
        )
        and configured_azure_cli_profile(state_root) is not None
    ):
        cli_cred = azure_cli_credential(tenant_id=str(effective_tenant), state_root=state_root)
        if cli_cred is not None:
            token = cli_cred.get_token(GRAPH_RESOURCE_DEFAULT_SCOPE).token
            from solution_manager.qualification.graph_readiness import _token_claims

            validate_delegated_graph_claims(
                _token_claims(token),
                tenant_id=str(effective_tenant),
                required_scopes=(GRAPH_SCOPE,),
                purpose="Advanced Hunting",
            )
            return token
    if record is None:
        raise RuntimeError(
            "Advanced Hunting authentication is missing; run "
            "`sentinel-xdr-migration setup` first"
        )
    try:
        verify_graph_auth_binding(
            record_path,
            record,
            purpose="advancedHunting",
            client_id=client_id,
            tenant_id=tenant_id or configured_tenant,
        )
    except ValueError as exc:
        raise RuntimeError(str(exc)) from exc
    if tenant_id and configured_tenant and tenant_id.lower() != configured_tenant.lower():
        raise RuntimeError(
            "Advanced Hunting authentication tenant does not match the locked target"
        )
    credential = DeviceCodeCredential(
        client_id=client_id,
        tenant_id=tenant_id or configured_tenant,
        authentication_record=record,
        cache_persistence_options=TokenCachePersistenceOptions(
            name=graph_token_cache_name(
                "advancedHunting", client_id, TOKEN_CACHE_NAME
            )
        ),
        disable_automatic_authentication=True,
    )
    token = credential.get_token(GRAPH_SCOPE).token
    from solution_manager.qualification.graph_readiness import _token_claims

    validate_delegated_graph_claims(
        _token_claims(token),
        tenant_id=tenant_id or configured_tenant or "",
        required_scopes=(GRAPH_SCOPE,),
        purpose="Advanced Hunting",
    )
    return token


def _retry_after_seconds(value: str | None) -> float | None:
    if not value:
        return None
    value = value.strip()
    if value.isdigit():
        return float(value)
    try:
        retry_at = parsedate_to_datetime(value)
    except (TypeError, ValueError, OverflowError):
        return None
    if retry_at.tzinfo is None:
        retry_at = retry_at.replace(tzinfo=timezone.utc)
    now = datetime.fromtimestamp(time.time(), timezone.utc)
    return max(0.0, (retry_at - now).total_seconds())


def _http_retry_after(exc: urllib.error.HTTPError) -> float | None:
    headers = getattr(exc, "headers", None)
    value = headers.get("Retry-After") if headers is not None else None
    return _retry_after_seconds(value)


def _is_odata_annotation(key: Any) -> bool:
    """Graph adds per-row annotations such as ``count_@odata.type: "#Int64"``."""
    return isinstance(key, str) and key.endswith("@odata.type")


def _strip_odata_annotations(rows: list[Any], schema: Any) -> list[Any]:
    declared = {
        str(column.get("name", column.get("Name"))).casefold()
        for column in (schema if isinstance(schema, list) else [])
        if isinstance(column, dict)
    }
    return [
        {
            key: value
            for key, value in row.items()
            if not (_is_odata_annotation(key) and key.casefold() not in declared)
        }
        if isinstance(row, dict) else row
        for row in rows
    ]


def _hunting_query_response_error(body: Any) -> str | None:
    if not isinstance(body, dict):
        return "Graph Advanced Hunting returned a JSON value instead of an object"
    provider_error = body.get("error")
    if provider_error:
        if isinstance(provider_error, dict):
            message = provider_error.get("message")
            if isinstance(message, str) and message.strip():
                return f"Graph Advanced Hunting returned an error: {message[:2000]}"
        return "Graph Advanced Hunting returned an error object"
    schema = body.get("schema", body.get("Schema"))
    if not isinstance(schema, list) or not schema:
        return "Graph Advanced Hunting response is missing its non-empty output schema"
    seen_names: set[str] = set()
    for column in schema:
        if not isinstance(column, dict):
            return "Graph Advanced Hunting output schema contains a non-object column"
        name = column.get("name", column.get("Name"))
        column_type = column.get("type", column.get("Type"))
        if (
            not isinstance(name, str)
            or not name.strip()
            or not isinstance(column_type, str)
            or not column_type.strip()
        ):
            return "Graph Advanced Hunting output schema columns require actual names and types"
        if name.casefold() in seen_names:
            return "Graph Advanced Hunting output schema contains duplicate column names"
        seen_names.add(name.casefold())
    rows = body.get("results", body.get("Results"))
    if not isinstance(rows, list):
        return "Graph Advanced Hunting response is missing its results array"
    if any(not isinstance(row, dict) for row in rows):
        return "Graph Advanced Hunting results contain a non-object row"
    if any(
        not isinstance(name, str)
        or (name.casefold() not in seen_names and not _is_odata_annotation(name))
        for row in rows
        for name in row
    ):
        return "Graph Advanced Hunting result columns do not match its declared schema"
    return None


def run_advanced_hunting_query(
    query: str,
    *,
    state_dir: str | Path | None = None,
    timeout: int = 90,
    retries: int = 2,
    _token: str | None = None,
    capture_full_results: bool = False,
) -> dict[str, Any]:
    """Run one Graph Advanced Hunting read within this process's provider bounds.

    The in-process semaphore limits actual Graph requests to five at a time;
    imported Log Analytics/MCP results are external and are not governed here.
    Transient attempts share a five-minute wall-clock budget, including request
    durations and retry waits. The public retry default remains two.
    """
    if not isinstance(capture_full_results, bool):
        raise ValueError("capture_full_results must be a boolean")
    token = _token or _advanced_hunting_token(_state_dir(state_dir))
    request = urllib.request.Request(
        ADVANCED_HUNTING_ENDPOINT,
        data=json.dumps({"Query": query}).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        },
        method="POST",
    )
    result: dict[str, Any] = {}
    retry_limit = max(0, min(retries, MAX_ADVANCED_HUNTING_RETRIES))
    deadline = time.monotonic() + ADVANCED_HUNTING_RETRY_BUDGET_SECONDS
    for attempt in range(retry_limit + 1):
        remaining = deadline - time.monotonic()
        if remaining <= 0:
            break
        acquired = _GRAPH_REQUEST_SEMAPHORE.acquire(timeout=remaining)
        if not acquired:
            result = {
                "ok": False,
                "statusCode": 0,
                "rowCount": 0,
                "schema": [],
                "error": "Timed out waiting for an available Graph request slot",
                "errorDetails": "The Advanced Hunting retry budget expired while waiting for a request slot",
                "failureKind": "provider",
            }
            return result
        try:
            remaining = deadline - time.monotonic()
            if remaining <= 0:
                break
            with urllib.request.urlopen(request, timeout=min(timeout, remaining)) as response:
                status_code = response.status
                try:
                    response_text = response.read().decode("utf-8")
                except UnicodeDecodeError as exc:
                    return {
                        "ok": False,
                        "statusCode": status_code,
                        "rowCount": 0,
                        "schema": [],
                        "error": "Graph Advanced Hunting returned non-UTF-8 JSON",
                        "errorDetails": str(exc),
                        "failureKind": "provider",
                    }
            try:
                body = json.loads(response_text)
            except json.JSONDecodeError as exc:
                return {
                    "ok": False,
                    "statusCode": status_code,
                    "rowCount": 0,
                    "schema": [],
                    "error": "Graph Advanced Hunting returned invalid JSON",
                    "errorDetails": f"{exc}: {response_text[:8000]}",
                    "failureKind": "provider",
                }
            response_error = _hunting_query_response_error(body)
            if response_error:
                return {
                    "ok": False,
                    "statusCode": status_code,
                    "rowCount": 0,
                    "schema": [],
                    "error": response_error,
                    "errorDetails": response_text[:8000],
                    "failureKind": "provider",
                }
            rows = body.get("results", body.get("Results"))
            schema = body.get("schema", body.get("Schema"))
            rows = _strip_odata_annotations(rows, schema)
            return {
                "ok": True,
                "statusCode": status_code,
                "rowCount": len(rows),
                "schema": schema,
                "sampleRows": rows[:MAX_ADVANCED_HUNTING_SAMPLE_ROWS],
                "sampleRowsTruncated": len(rows) > MAX_ADVANCED_HUNTING_SAMPLE_ROWS,
                **({"results": rows} if capture_full_results else {}),
                "error": None,
                "errorDetails": None,
            }
        except urllib.error.HTTPError as exc:
            body = exc.read().decode("utf-8", errors="replace")
            try:
                parsed = json.loads(body)
                error = parsed.get("error") or {}
                message = error.get("message") or body
            except json.JSONDecodeError:
                message = body
            result = {
                "ok": False,
                "statusCode": exc.code,
                "rowCount": 0,
                "schema": [],
                "error": message[:2000],
                "errorDetails": body[:8000],
                "failureKind": "query" if exc.code == 400 else "provider",
            }
            if exc.code not in {429, 502, 503, 504} or attempt == retry_limit:
                return result
            retry_after = _http_retry_after(exc)
        except (TimeoutError, urllib.error.URLError) as exc:
            result = {
                "ok": False,
                "statusCode": 0,
                "rowCount": 0,
                "schema": [],
                "error": str(exc),
                "errorDetails": str(exc),
                "failureKind": "provider",
            }
            if attempt == retry_limit:
                return result
            retry_after = None
        finally:
            _GRAPH_REQUEST_SEMAPHORE.release()

        remaining = deadline - time.monotonic()
        delay = retry_after if retry_after is not None else 2 * (attempt + 1)
        if delay >= remaining:
            return result
        if delay:
            time.sleep(delay)
    if result:
        return result
    return {
        "ok": False,
        "statusCode": 0,
        "rowCount": 0,
        "schema": [],
        "error": "Advanced Hunting retry budget expired before a request could complete",
        "errorDetails": "The five-minute request and retry budget was exhausted",
        "failureKind": "provider",
    }


def _not_run_result(
    path: Path, output: Path, query: str, *, status_code: int = 0
) -> dict[str, Any]:
    return {
        "detection": path.relative_to(output).as_posix(),
        "status": "not-run",
        "valid": False,
        "querySha256": _query_sha256(query),
        "statusCode": status_code,
        "rowCount": 0,
        "schemaColumnCount": 0,
        "error": None,
        "errorDetails": None,
    }


def validate_advanced_hunting(
    solution: str | Path,
    *,
    state_dir: str | Path | None = None,
    tenant_id: str | None = None,
    provider_gap_evidence: str | Path | None = None,
    max_workers: int = MAX_ADVANCED_HUNTING_WORKERS,
    min_request_interval_seconds: float | None = None,
) -> dict[str, Any]:
    root = Path(solution).expanduser().resolve()
    workflow_state = existing_artifact_path(root, "workflow-state.json")
    profile = _workflow_profile(root)
    locked_target = None
    if workflow_state.is_file():
        if profile == "qualification":
            locked_target = require_locked_target(root, materialize_missing=False)
        elif profile == "authoring":
            try:
                state = json.loads(workflow_state.read_text(encoding="utf-8-sig"))
            except (OSError, json.JSONDecodeError) as exc:
                raise ValueError(
                    "selected Authoring workflow state is unavailable"
                ) from exc
            context = state.get("context") if isinstance(state, dict) else None
            configured_tenant = (
                context.get("tenantId") if isinstance(context, dict) else None
            )
            if not isinstance(configured_tenant, str) or not configured_tenant:
                raise ValueError(
                    "Authoring Advanced Hunting requires the explicit tenant in "
                    "the selected workflow run"
                )
            locked_target = {"tenantId": configured_tenant}
            if tenant_id and tenant_id.strip().casefold() != configured_tenant.casefold():
                raise ValueError(
                    "requested Graph tenant does not match the selected Authoring run"
                )
            tenant_id = configured_tenant
        else:
            raise ValueError(
                "Advanced Hunting requires a recognized selected workflow profile"
            )
    if (
        locked_target is not None
        and tenant_id
        and tenant_id.strip().casefold() != locked_target["tenantId"].casefold()
    ):
        raise ValueError("requested Graph tenant does not match the locked Qualification tenant")
    effective_state_dir = Path(_state_dir(state_dir)).expanduser().resolve()
    if locked_target is not None:
        if profile == "authoring":
            _assert_graph_auth_tenant_scope(
                effective_state_dir,
                locked_tenant_id=locked_target["tenantId"],
                requested_tenant_id=tenant_id,
            )
        else:
            _assert_graph_auth_scope(
                effective_state_dir,
                locked_target=locked_target,
                requested_tenant_id=tenant_id,
            )
    consent = require_runtime_query_consent(
        root,
        family="defenderXdrQueryFamily",
        provider="graph",
        allow_legacy=True,
    )
    provider_fallback = _load_provider_fallback(
        provider_gap_evidence,
        query_family="advanced-hunting",
        fallback_provider="graph",
    )
    output = root / "XDR Detections"
    token = _advanced_hunting_token(
        effective_state_dir,
        tenant_id=locked_target["tenantId"] if locked_target is not None else tenant_id,
    )
    detections: list[tuple[Path, dict[str, Any], str]] = []
    for path in _detection_files(output):
        with path.open(encoding="utf-8-sig") as handle:
            document = yaml.safe_load(handle) or {}
        query = document["properties"]["queryCondition"]["queryText"]
        detections.append((path, document, query))

    if min_request_interval_seconds is None:
        is_live_runner = getattr(run_advanced_hunting_query, "__module__", "") == __name__
        interval = ADVANCED_HUNTING_MIN_INTERVAL_SECONDS if is_live_runner else 0.0
    else:
        interval = max(0.0, float(min_request_interval_seconds))

    results: list[dict[str, Any] | None] = [None] * len(detections)
    provider_failure: dict[str, Any] | None = None
    state_lock = threading.Lock()
    rate_lock = threading.Lock()
    next_allowed_start = 0.0

    def _paced_query(query: str) -> dict[str, Any]:
        nonlocal next_allowed_start
        if interval > 0:
            with rate_lock:
                now = time.monotonic()
                wait_seconds = max(0.0, next_allowed_start - now)
                next_allowed_start = max(now, next_allowed_start) + interval
            if wait_seconds > 0:
                time.sleep(wait_seconds)
        return run_advanced_hunting_query(query, _token=token)

    def _run_index(index: int) -> None:
        nonlocal provider_failure
        path, document, query = detections[index]
        with state_lock:
            failed = provider_failure is not None
        if failed:
            results[index] = _not_run_result(path, output, query)
            return
        runtime = _paced_query(query)
        if runtime.get("failureKind") == "provider":
            with state_lock:
                if provider_failure is None:
                    provider_failure = {
                        "provider": "graph",
                        "statusCode": runtime["statusCode"],
                        "error": runtime["error"],
                        "errorDetails": runtime["errorDetails"],
                    }
            results[index] = _not_run_result(
                path, output, query, status_code=runtime["statusCode"]
            )
            return
        binding_errors = custom_detail_schema_errors(document, runtime["schema"]) if runtime["ok"] else []
        results[index] = {
            "detection": path.relative_to(output).as_posix(),
            "status": "passed" if runtime["ok"] and not binding_errors else "failed",
            "valid": runtime["ok"] and not binding_errors,
            "querySha256": _query_sha256(query),
            "statusCode": runtime["statusCode"],
            "rowCount": runtime["rowCount"],
            "schemaColumnCount": len(runtime["schema"]),
            "schema": runtime["schema"],
            "sampleRows": runtime.get("sampleRows", []),
            "sampleRowsTruncated": runtime.get("sampleRowsTruncated", False),
            "error": "; ".join(binding_errors) if binding_errors else runtime["error"],
            "errorDetails": runtime["errorDetails"],
        }

    if detections:
        _run_index(0)
        remaining_indices = list(range(1, len(detections)))
        if remaining_indices:
            if provider_failure is not None or max_workers <= 1:
                for idx in remaining_indices:
                    _run_index(idx)
            else:
                workers = max(1, min(max_workers, len(remaining_indices)))
                with ThreadPoolExecutor(max_workers=workers) as executor:
                    futures = [executor.submit(_run_index, idx) for idx in remaining_indices]
                    for future in futures:
                        future.result()

    final_results = [entry for entry in results if entry is not None]
    return _write_runtime_artifacts(
        root,
        "graph",
        final_results,
        provider_fallback=provider_fallback,
        provider_failure=provider_failure,
        runtime_query_consent=consent,
    )


def validate_sentinel_sdk(
    solution: str | Path,
    *,
    target: dict[str, str],
    request_timeout_seconds: int = 90,
    family_timeout_seconds: int = 30 * 60,
    provider_gap_evidence: str | Path | None = None,
    _credential_factory=None,
    _client_factory=None,
    _scope_verifier=None,
    _monotonic=None,
    _sleep=None,
) -> dict[str, Any]:
    """Run the complete current Sentinel source-query family with Azure Monitor SDK."""
    from solution_manager.core.content_paths import content_path
    from solution_manager.migration.converter import analytic_rule_files, solution_paths, xdr_detection_files
    from solution_manager.qualification.logs_query import (
        DEFAULT_FAMILY_TIMEOUT_SECONDS,
        DEFAULT_REQUEST_TIMEOUT_SECONDS,
        azure_cli_credential,
        execute_workspace_query,
        logs_query_client,
        query_family,
        verify_azure_cli_target,
    )

    root, analytic, output = solution_paths(solution)
    provider = "azure-monitor-sdk"
    effective_target = _effective_sdk_target(root, target)
    consent = require_runtime_query_consent(
        root,
        family="sentinelSourceQueryFamily",
        provider=provider,
        allow_legacy=True,
    )
    provider_fallback = _load_provider_fallback(
        provider_gap_evidence,
        query_family="sentinel",
        fallback_provider=provider,
    )
    sources = analytic_rule_files(root)
    if not sources:
        raise ValueError("complete Sentinel source-query inventory is empty; no SDK validation report was written")

    source_by_path: dict[str, tuple[Path, str, str]] = {}
    for source_path in sources:
        relative = source_path.relative_to(analytic).as_posix()
        with source_path.open(encoding="utf-8-sig") as handle:
            source = yaml.safe_load(handle)
        if not isinstance(source, dict) or not isinstance(source.get("query"), str) or not source["query"].strip():
            raise ValueError(f"source Analytic Rule has no non-empty query: {source_path}")
        query = source["query"]
        source_by_path[relative] = (source_path, query, _query_sha256(query))

    detections: dict[str, str] = {}
    for detection_path in xdr_detection_files(output):
        with detection_path.open(encoding="utf-8-sig") as handle:
            detection = yaml.safe_load(handle)
        source_ref = ((detection or {}).get("contentProvenance") or {}).get("source") or {}
        source_path_ref = source_ref.get("path")
        if not isinstance(source_path_ref, str):
            raise ValueError(f"Custom Detection provenance is missing its source path: {detection_path}")
        source_path = content_path(root, source_path_ref)
        if not source_path.is_file():
            raise ValueError(f"Custom Detection source Analytic Rule is missing: {source_path_ref}")
        relative = source_path.relative_to(analytic).as_posix()
        if relative not in source_by_path:
            raise ValueError(f"Custom Detection provenance is outside the complete source inventory: {source_path_ref}")
        if relative in detections.values():
            raise ValueError(f"multiple Custom Detections refer to the same source Analytic Rule: {source_path_ref}")
        current_hash = source_by_path[relative][2]
        if source_ref.get("querySha256") != current_hash:
            raise ValueError(f"Custom Detection provenance has a stale source-query hash: {source_path_ref}")
        detections[detection_path.relative_to(output).as_posix()] = relative

    if set(detections.values()) != set(source_by_path):
        raise ValueError(
            "SDK validation requires the complete source inventory to map one-to-one to "
            "generated detections "
            f"(missing={sorted(set(source_by_path) - set(detections.values()))}, "
            f"extra={sorted(set(detections.values()) - set(source_by_path))})"
        )
    queries = [
        {
            "detection": detection,
            "query": source_by_path[source_relative][1],
            "querySha256": source_by_path[source_relative][2],
        }
        for detection, source_relative in sorted(detections.items())
    ]

    results: list[dict[str, Any]]
    provider_failure = None
    scope_verifier = _scope_verifier or verify_azure_cli_target
    try:
        scope_verifier(effective_target)
        credential_factory = _credential_factory or azure_cli_credential
        client_factory = _client_factory or logs_query_client
        credential = credential_factory(effective_target)
        client = client_factory(credential, retry_total=0)
        try:
            results = query_family(
                client,
                effective_target["workspaceCustomerId"],
                queries,
                request_timeout_seconds=request_timeout_seconds,
                family_timeout_seconds=(
                    family_timeout_seconds
                    if family_timeout_seconds is not None
                    else DEFAULT_FAMILY_TIMEOUT_SECONDS
                ),
                monotonic=_monotonic or time.monotonic,
                sleep=_sleep or time.sleep,
            )
            provider_failure_result = next(
                (
                    item for item in results
                    if item.get("failureKind") not in {
                        None, "query", "partial-response",
                    }
                ),
                None,
            )
            if provider_failure_result:
                provider_failure = {
                    "failureKind": provider_failure_result.get("failureKind"),
                    "statusCode": provider_failure_result.get("statusCode", 0),
                    "error": provider_failure_result.get("error"),
                    "errorDetails": provider_failure_result.get("errorDetails"),
                }
        finally:
            close = getattr(client, "close", None)
            if callable(close):
                close()
    except Exception as exc:
        if isinstance(exc, (ValueError, TypeError)):
            raise
        failure_kind = getattr(exc, "failure_kind", "provider")
        provider_failure = {
            "failureKind": failure_kind,
            "statusCode": int(getattr(exc, "status_code", 0) or 0),
            "error": str(exc)[:2000],
            "errorDetails": str(getattr(exc, "error_details", exc))[:8000],
        }
        results = [
            {
                "detection": item["detection"],
                "status": "not-run",
                "valid": False,
                "querySha256": item["querySha256"],
                "statusCode": provider_failure["statusCode"],
                "rowCount": 0,
                "schema": [],
                "error": "query was not dispatched because provider initialization or target authentication failed",
                "errorDetails": provider_failure["error"],
            }
            for item in queries
        ]
    family_complete = len(results) == len(queries) and all(
        item.get("status") != "not-run" for item in results
    )
    report = record_runtime_validation(
        root,
        provider=provider,
        results_data=results,
        provider_gap_evidence=provider_gap_evidence,
        provider_failure=provider_failure,
        family_complete=family_complete,
        runtime_query_consent=consent,
    )
    return report


def record_runtime_validation(
    solution: str | Path,
    *,
    provider: str,
    results_path: str | Path | None = None,
    results_data: list[dict[str, Any]] | None = None,
    provider_gap_evidence: str | Path | None = None,
    provider_failure: dict[str, Any] | None = None,
    family_complete: bool | None = None,
    source_provider: str = "azure-monitor-sdk",
    runtime_query_consent: dict[str, Any] | None = None,
) -> dict[str, Any]:
    if provider not in SUPPORTED_EXTERNAL_PROVIDERS:
        raise ValueError(
            f"unsupported external runtime provider {provider!r}; "
            f"expected one of {sorted(SUPPORTED_EXTERNAL_PROVIDERS)}"
        )
    root = Path(solution).expanduser().resolve()
    consent = _runtime_consent_for_import(
        root,
        provider=provider,
        source_provider=source_provider,
    )
    if runtime_query_consent is not None and (
        consent is None
        or not _same_execution_scope(runtime_query_consent, consent)
    ):
        raise ValueError(
            "runtime-query dispatch snapshot no longer matches the current "
            "target, query inventory, provider route, or authentication scope"
        )
    dispatch_snapshot = runtime_query_consent or consent
    provider_fallback = _load_provider_fallback(
        provider_gap_evidence,
        query_family="sentinel",
        fallback_provider=provider,
    )
    if provider_fallback and provider != provider_fallback["fallbackProvider"]:
        raise ValueError("Sentinel MCP fallback results must be recorded under the approved fallback provider")
    output = root / "XDR Detections"
    detection_paths = {path.relative_to(output).as_posix(): path for path in _detection_files(output)}
    expected = set(detection_paths)
    if (results_path is None) == (results_data is None):
        raise ValueError("provide exactly one of results_path or results_data")
    raw = (
        json.loads(Path(results_path).expanduser().read_text(encoding="utf-8"))
        if results_path is not None else results_data
    )
    entries = raw.get("results") if isinstance(raw, dict) else raw
    if not isinstance(entries, list):
        raise ValueError("runtime results must be a JSON list or an object containing results")

    preflight_names = []
    for entry in entries:
        if not isinstance(entry, dict):
            raise ValueError("each runtime result must be a JSON object")
        detection = str(entry.get("detection") or "").strip().replace("\\", "/")
        if not detection:
            raise ValueError("each runtime result requires a detection filename")
        preflight_names.append(detection)
    if len(preflight_names) != len(set(preflight_names)):
        raise ValueError("duplicate runtime result for a detection")
    preflight_set = set(preflight_names)
    if preflight_set != expected:
        details = []
        missing = sorted(expected - preflight_set)
        unknown = sorted(preflight_set - expected)
        if missing:
            details.append(f"missing detections: {', '.join(missing)}")
        if unknown:
            details.append(f"unknown detections: {', '.join(unknown)}")
        raise ValueError("; ".join(details))

    expected_query_hashes = {
        name: current_runtime_query_hash(root, path, provider=provider)
        for name, path in detection_paths.items()
    }
    normalized: list[dict[str, Any]] = []
    names: set[str] = set()
    dependency_config = load_config(output)
    for entry in entries:
        if not isinstance(entry, dict):
            raise ValueError("each runtime result must be a JSON object")
        detection = str(entry.get("detection") or "").strip()
        if not detection:
            raise ValueError("each runtime result requires a detection filename")
        detection = detection.replace("\\", "/")
        if detection in names:
            raise ValueError(f"duplicate runtime result for {detection}")
        names.add(detection)
        status = str(entry.get("status") or "").strip().lower()
        if not status:
            status = "passed" if entry.get("valid") is True else "failed"
        if status not in {"passed", "failed", "blocked", "not-run"}:
            raise ValueError(f"invalid runtime status {status!r} for {detection}")
        error = entry.get("error")
        schema = entry.get("schema")
        dependency_validation = None
        query_hash = entry.get("querySha256")
        if status == "passed" and (
            entry.get("partial") is True or error or entry.get("failureKind")
        ):
            status = "failed"
            error = error or "source query returned a partial or failed result"
        if status == "passed" and detection in expected_query_hashes:
            if not isinstance(query_hash, str) or not re.fullmatch(r"[0-9a-f]{64}", query_hash):
                status = "blocked"
                error = (
                    "passed Sentinel validation must include the query hash (SHA-256) of the exact "
                    "source query that was executed"
                )
            elif query_hash != expected_query_hashes[detection]:
                status = "blocked"
                error = (
                    "Sentinel validation query hash is stale; rerun the complete Sentinel "
                    "query family against the current source queries"
                )
        if status == "passed" and detection in detection_paths:
            document = yaml.safe_load(detection_paths[detection].read_text(encoding="utf-8-sig"))
            source_path = content_path(root, document["contentProvenance"]["source"]["path"])
            source_document = yaml.safe_load(source_path.read_text(encoding="utf-8-sig"))
            try:
                dependency_validation = live_dependency_check(
                    document, source_document["query"], entry.get("dataSources"),
                    table_mappings=dependency_config.get("tableMappings"),
                    source_connectors=source_document.get("requiredDataConnectors"),
                )
            except ValueError as exc:
                dependency_validation = {"status": "failed", "errors": [str(exc)]}
            if dependency_validation["status"] != "passed":
                status = "failed"
                error = "; ".join(dependency_validation["errors"])
        if status == "passed" and provider == "graph" and detection in detection_paths:
            document = yaml.safe_load(detection_paths[detection].read_text(encoding="utf-8-sig")) or {}
            details = (
                ((document.get("properties") or {}).get("detectionAction") or {}).get("alertTemplate") or {}
            ).get("customDetails")
            if details:
                if not isinstance(schema, list):
                    status = "blocked"
                    error = "customDetails binding verification requires the returned target-query output schema, not just schemaColumnCount"
                else:
                    binding_errors = custom_detail_schema_errors(document, schema)
                    if binding_errors:
                        status = "failed"
                        error = "; ".join(binding_errors)
        normalized_entry = {
                "detection": detection,
                "status": status,
                "valid": status == "passed",
                "querySha256": query_hash,
                "statusCode": int(entry.get("statusCode") or 0),
                "rowCount": int(entry.get("rowCount") or 0),
                "schemaColumnCount": len(schema) if isinstance(schema, list) else int(entry.get("schemaColumnCount") or 0),
                "error": error,
                "errorDetails": entry.get("errorDetails"),
            }
        for field in (
            "tables",
            "partialError",
            "failureKind",
            "attempts",
            "durationMs",
            "schema",
            "dataSources",
        ):
            if field in entry:
                normalized_entry[field] = entry[field]
        if dependency_validation is not None:
            normalized_entry["dependencyValidation"] = dependency_validation
            normalized_entry["dependencyProvenanceSha256"] = dependency_identity(document)
        sample_rows = entry.get("sampleRows")
        if isinstance(sample_rows, list):
            normalized_entry["sampleRows"] = sample_rows[:MAX_ADVANCED_HUNTING_SAMPLE_ROWS]
            normalized_entry["sampleRowsTruncated"] = (
                entry.get("sampleRowsTruncated") is True
                or len(sample_rows) > MAX_ADVANCED_HUNTING_SAMPLE_ROWS
            )
        if entry.get("partial") is True:
            normalized_entry["partial"] = True
        normalized.append(normalized_entry)

    missing = sorted(expected - names)
    unknown = sorted(names - expected)
    if missing or unknown:
        details = []
        if missing:
            details.append(f"missing detections: {', '.join(missing)}")
        if unknown:
            details.append(f"unknown detections: {', '.join(unknown)}")
        raise ValueError("; ".join(details))

    fallback_rejection = None
    if provider_fallback:
        failed_results = [
            item for item in normalized if item["status"] != "passed"
        ]
        if failed_results or family_complete is False:
            reasons = [
                (
                    f"{item['detection']} is {item['status']}: "
                    f"{item.get('error') or item.get('errorDetails') or 'no query diagnostics returned'}"
                )
                for item in failed_results
            ]
            if family_complete is False:
                reasons.append("the query family is incomplete")
            fallback_rejection = (
                "provider fallback is not allowed unless every fallback query completed "
                "successfully; " + "; ".join(reasons)
            )

    report = _write_runtime_artifacts(
        root,
        provider,
        normalized,
        provider_fallback=provider_fallback,
        provider_failure=provider_failure,
        family_complete=family_complete,
        runtime_query_consent=consent,
        runtime_query_dispatch_snapshot=dispatch_snapshot,
    )
    if fallback_rejection:
        raise ValueError(
            f"{fallback_rejection}; attempt diagnostics were persisted to {report['jsonReport']}"
        )
    return report
