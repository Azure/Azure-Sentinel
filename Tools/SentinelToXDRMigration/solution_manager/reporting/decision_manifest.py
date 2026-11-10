"""Sanitized, hash-bound decision manifest projection for Solution Manager flows."""

from __future__ import annotations

import hashlib
import json
import os
import re
import tempfile
from pathlib import Path
from typing import Any, Mapping, Optional

import yaml

from solution_manager.core.artifacts import (
    existing_artifact_path,
    existing_artifacts,
    report_directory,
)
from solution_manager.core.target_config import read_solution_target_config
from solution_manager.core.target_context import workspace_identity
from solution_manager.migration.converter import xdr_detection_files
from solution_manager.migration.source_runtime_waiver import missing_schema_whitelist_match
from solution_manager.packaging.packaging import solution_data_version

DECISION_MANIFEST_SCHEMA_VERSION = "decision-manifest-v1"
DEFAULT_DECISION_MANIFEST_FILENAME = "decision-manifest.json"

ALLOWED_DECISION_SCOPES = frozenset({
    "rule_review",
    "workbook_review",
    "connector_selection",
    "waiver",
    "exclusion",
    "arm_validation",
    "qualification_summary",
})

_SHA256_RE = re.compile(r"^[0-9a-f]{64}$", re.IGNORECASE)
_UUID_RE = re.compile(
    r"\b[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}\b",
    re.IGNORECASE,
)
_ARM_WORKSPACE_RE = re.compile(
    r"/subscriptions/[0-9a-fA-F-]+/resourceGroups/[^/\s\"']+/providers/"
    r"Microsoft\.OperationalInsights/workspaces/[^/\s\"']+",
    re.IGNORECASE,
)
_ARM_RESOURCE_GROUP_RE = re.compile(
    r"/subscriptions/[0-9a-fA-F-]+/resourceGroups/([^/\s\"']+)",
    re.IGNORECASE,
)
_ARM_SUBSCRIPTION_RE = re.compile(
    r"/subscriptions/([0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12})",
    re.IGNORECASE,
)
_LABELED_PRIVATE_GUID_RE = re.compile(
    r"(?P<label>\b(?:tenant(?:[_\s-]?id)?|subscription(?:[_\s-]?id)?|"
    r"workspace(?:[_\s-]?(?:customer[_\s-]?)?id)?|client(?:[_\s-]?id)?|"
    r"object(?:[_\s-]?id)?|detector(?:[_\s-]?id)?)\b"
    r"['\"]?\s*[:=]\s*['\"]?)"
    r"(?P<guid>[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12})"
    r"(?P<quote>['\"]?)",
    re.IGNORECASE,
)
_LABELED_RESOURCE_GROUP_RE = re.compile(
    r"(?P<label>\b(?:resource[_\s-]?group(?:[_\s-]?name)?)\b['\"]?\s*[:=]\s*['\"]?)"
    r"(?P<rg>[A-Za-z0-9_.()\-]{2,90})"
    r"(?P<quote>['\"]?)",
    re.IGNORECASE,
)
_EMAIL_RE = re.compile(
    r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b"
)
_LOCAL_FS_PATH_RE = re.compile(
    r"(?:"
    r"/(?:Users|home|private/var|var/folders|tmp|var/tmp|opt|etc)/[^\s\"',;)\]}]+"
    r"|[A-Za-z]:\\(?:Users|Windows|Temp|Program Files|home|var|tmp)\\[^\s\"',;)\]}]+"
    r")",
    re.IGNORECASE,
)
_SECRET_ASSIGNMENT_RE = re.compile(
    r"\b(?:Bearer\s+[A-Za-z0-9._~+/=-]{12,}|(?:password|passwd|secret|client_secret|access_token|api_key)\s*[:=]\s*[^\s\"',;)\]}]+)",
    re.IGNORECASE,
)


def _canonical_bytes(value: Any) -> bytes:
    return json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=False
    ).encode("utf-8")


def _sha256_hex(value: bytes | str) -> str:
    data = value.encode("utf-8") if isinstance(value, str) else value
    return hashlib.sha256(data).hexdigest()


def _sha256_canonical(value: Any) -> str:
    return _sha256_hex(_canonical_bytes(value))


def _normalize_sha256(value: Any, fallback_seed: str) -> str:
    if isinstance(value, str) and _SHA256_RE.fullmatch(value.strip()):
        return value.strip().lower()
    return _sha256_hex(fallback_seed)


def _read_json_safe(path: Path | None) -> dict[str, Any]:
    if path is None or not path.is_file() or path.is_symlink():
        return {}
    try:
        loaded = json.loads(path.read_text(encoding="utf-8-sig"))
        return loaded if isinstance(loaded, dict) else {}
    except (OSError, UnicodeError, json.JSONDecodeError):
        return {}


def _read_yaml_safe(path: Path | None) -> dict[str, Any]:
    if path is None or not path.is_file() or path.is_symlink():
        return {}
    try:
        loaded = yaml.safe_load(path.read_text(encoding="utf-8-sig"))
        return loaded if isinstance(loaded, dict) else {}
    except (OSError, UnicodeError, yaml.YAMLError):
        return {}


def _collect_private_identifiers(
    root: Path,
    state: Mapping[str, Any],
    run_dir: Path | None,
) -> dict[str, set[str]]:
    """Collect private tenant/subscription/workspace GUIDs, names, and local paths to redact and block."""
    guids: set[str] = set()
    names: set[str] = set()
    arm_ids: set[str] = set()
    paths: set[str] = {str(root), root.as_posix()}

    def _add_workspace_arm_id(raw_id: str) -> None:
        cleaned = raw_id.strip().rstrip("/")
        if not cleaned:
            return
        arm_ids.add(cleaned)
        try:
            ws = workspace_identity(cleaned)
            guids.add(ws["subscriptionId"].lower())
            if ws.get("resourceGroup"):
                names.add(ws["resourceGroup"])
            if ws.get("workspaceName"):
                names.add(ws["workspaceName"])
        except ValueError:
            for sub_match in _ARM_SUBSCRIPTION_RE.findall(cleaned):
                guids.add(sub_match.lower())
            for rg_match in _ARM_RESOURCE_GROUP_RE.findall(cleaned):
                names.add(rg_match)

    context = state.get("context")
    sources: list[Mapping[str, Any]] = [state]
    if isinstance(context, Mapping):
        sources.append(context)
    private_block = state.get("privateIdentifiers")
    if isinstance(private_block, Mapping):
        sources.append(private_block)

    try:
        env_cfg = read_solution_target_config(root)
        if isinstance(env_cfg, Mapping):
            sources.append(env_cfg)
    except ValueError:
        # Target config is optional during offline manifest projection.
        pass

    if run_dir is not None:
        target_doc = _read_json_safe(run_dir / "qualification-target.json")
        if target_doc:
            sources.append(target_doc)
        paths.add(str(run_dir))
        paths.add(run_dir.as_posix())

    for src in sources:
        for guid_key in (
            "tenantId",
            "subscriptionId",
            "workspaceCustomerId",
            "workspaceId",
            "clientId",
            "objectId",
        ):
            val = src.get(guid_key)
            if isinstance(val, str) and val.strip():
                for found in _UUID_RE.findall(val):
                    guids.add(found.lower())
        for name_key in ("resourceGroup", "resourceGroupName", "workspaceName"):
            val = src.get(name_key)
            if isinstance(val, str) and len(val.strip()) >= 3:
                names.add(val.strip())
        ws_arm = src.get("workspaceResourceId")
        if isinstance(ws_arm, str) and ws_arm.strip():
            _add_workspace_arm_id(ws_arm)

    return {
        "guids": guids,
        "names": names,
        "arm_ids": arm_ids,
        "paths": paths,
    }


def sanitize_decision_text(
    text: Any,
    *,
    private_identifiers: Optional[Mapping[str, set[str]]] = None,
    solution_root: Optional[Path] = None,
) -> str:
    """Sanitize a string field by stripping private identifiers, emails/UPNs, and local filesystem paths."""
    if text is None:
        return ""
    value = str(text).strip()
    if not value:
        return ""

    if solution_root is not None:
        for prefix in (str(solution_root) + os.sep, solution_root.as_posix() + "/", str(solution_root), solution_root.as_posix()):
            if prefix and prefix in value:
                value = value.replace(prefix, "")

    if private_identifiers:
        for arm_id in sorted(private_identifiers.get("arm_ids") or (), key=len, reverse=True):
            if arm_id:
                value = re.sub(re.escape(arm_id), "[REDACTED_WORKSPACE_ARM_ID]", value, flags=re.IGNORECASE)
        for p in sorted(private_identifiers.get("paths") or (), key=len, reverse=True):
            if p and len(p) > 1:
                value = value.replace(p + "/", "").replace(p + "\\", "").replace(p, "[REDACTED_PATH]")
        for guid in sorted(private_identifiers.get("guids") or (), key=len, reverse=True):
            if guid:
                value = re.sub(re.escape(guid), "[REDACTED_ID]", value, flags=re.IGNORECASE)
        for name in sorted(private_identifiers.get("names") or (), key=len, reverse=True):
            if name and len(name) >= 3:
                value = re.sub(rf"\b{re.escape(name)}\b", "[REDACTED_RESOURCE]", value, flags=re.IGNORECASE)

    # Redact structured ARM resource paths and labeled identifiers
    value = _ARM_WORKSPACE_RE.sub("[REDACTED_WORKSPACE_ARM_ID]", value)
    value = _ARM_RESOURCE_GROUP_RE.sub("/subscriptions/[REDACTED_ID]/resourceGroups/[REDACTED_RESOURCE]", value)
    value = _ARM_SUBSCRIPTION_RE.sub("/subscriptions/[REDACTED_ID]", value)
    value = _LABELED_PRIVATE_GUID_RE.sub(r"\g<label>[REDACTED_ID]\g<quote>", value)
    value = _LABELED_RESOURCE_GROUP_RE.sub(r"\g<label>[REDACTED_RESOURCE]\g<quote>", value)
    value = _EMAIL_RE.sub("[REDACTED_EMAIL]", value)
    value = _SECRET_ASSIGNMENT_RE.sub("[REDACTED_SECRET]", value)
    value = _LOCAL_FS_PATH_RE.sub("[REDACTED_PATH]", value)

    return value.strip() or "[REDACTED]"


def verify_sanitized_decision_manifest(
    manifest: Mapping[str, Any],
    *,
    private_identifiers: Optional[Mapping[str, set[str]]] = None,
    solution_root: Optional[Path] = None,
) -> None:
    """Fail-closed check that raises ValueError if any private identifier or local path remains."""
    serialized = json.dumps(manifest, sort_keys=True, ensure_ascii=False)

    if private_identifiers:
        for guid in sorted(private_identifiers.get("guids") or ()):
            if guid and guid.lower() in serialized.lower():
                raise ValueError(
                    "Unsafe content remained: unsanitized private identifier (GUID) detected in decision manifest"
                )
        for arm_id in sorted(private_identifiers.get("arm_ids") or ()):
            if arm_id and arm_id.lower() in serialized.lower():
                raise ValueError(
                    "Unsafe content remained: unsanitized workspace ARM resource ID detected in decision manifest"
                )
        for name in sorted(private_identifiers.get("names") or ()):
            if name and len(name) >= 3 and re.search(rf"\b{re.escape(name)}\b", serialized, re.IGNORECASE):
                raise ValueError(
                    "Unsafe content remained: unsanitized private resource/workspace name detected in decision manifest"
                )

    if solution_root is not None:
        root_posix = solution_root.as_posix()
        if len(root_posix) > 3 and root_posix in serialized:
            raise ValueError(
                "Unsafe content remained: unsanitized local solution filesystem path detected in decision manifest"
            )

    if _ARM_SUBSCRIPTION_RE.search(serialized) or _ARM_WORKSPACE_RE.search(serialized):
        raise ValueError(
            "Unsafe content remained: unsanitized Azure subscription or workspace ARM resource ID detected in decision manifest"
        )
    if _LABELED_PRIVATE_GUID_RE.search(serialized):
        raise ValueError(
            "Unsafe content remained: unsanitized labeled private tenant/subscription/workspace GUID detected in decision manifest"
        )
    if _EMAIL_RE.search(serialized):
        raise ValueError(
            "Unsafe content remained: unsanitized user email/UPN detected in decision manifest"
        )
    if _LOCAL_FS_PATH_RE.search(serialized):
        raise ValueError(
            "Unsafe content remained: unsanitized local filesystem path detected in decision manifest"
        )
    if _SECRET_ASSIGNMENT_RE.search(serialized):
        raise ValueError(
            "Unsafe content remained: unsanitized secret or bearer token detected in decision manifest"
        )

    overrides = manifest.get("overrides")
    if overrides is not None:
        if not isinstance(overrides, list):
            raise ValueError("Decision manifest 'overrides' must be a list when present.")
        for idx, ov in enumerate(overrides):
            if not isinstance(ov, Mapping):
                raise ValueError(f"Override at index {idx} must be a mapping.")
            for req_ov_key in ("itemId", "overrideType", "reason", "timestampUtc"):
                if req_ov_key not in ov:
                    raise ValueError(f"Override at index {idx} missing required key {req_ov_key!r}.")
            ov_type = str(ov.get("overrideType") or "")
            if ov_type not in {"waiver", "manual_edit", "rejection"}:
                raise ValueError(f"Invalid overrideType {ov_type!r} at index {idx}.")


def _contains_raw_private_data(
    raw_value: Any,
    private_identifiers: Mapping[str, set[str]],
    solution_root: Optional[Path] = None,
) -> bool:
    serialized = json.dumps(raw_value, sort_keys=True, ensure_ascii=False) if not isinstance(raw_value, str) else raw_value
    for guid in private_identifiers.get("guids") or ():
        if guid and guid.lower() in serialized.lower():
            return True
    for arm_id in private_identifiers.get("arm_ids") or ():
        if arm_id and arm_id.lower() in serialized.lower():
            return True
    for name in private_identifiers.get("names") or ():
        if name and len(name) >= 3 and re.search(rf"\b{re.escape(name)}\b", serialized, re.IGNORECASE):
            return True
    if solution_root is not None and solution_root.as_posix() in serialized:
        return True
    return bool(
        _ARM_SUBSCRIPTION_RE.search(serialized)
        or _ARM_WORKSPACE_RE.search(serialized)
        or _LABELED_PRIVATE_GUID_RE.search(serialized)
        or _EMAIL_RE.search(serialized)
        or _LOCAL_FS_PATH_RE.search(serialized)
        or _SECRET_ASSIGNMENT_RE.search(serialized)
    )


def _build_decision_record(
    *,
    scope: str,
    item_id: str,
    decision: str,
    rationale: str,
    source_sha256: Any,
    target_sha256: Any,
    private_identifiers: Mapping[str, set[str]],
    solution_root: Path,
    record_id: Optional[str] = None,
) -> dict[str, str]:
    if scope not in ALLOWED_DECISION_SCOPES:
        raise ValueError(f"unsupported decision scope: {scope!r}")

    clean_item_id = sanitize_decision_text(
        item_id,
        private_identifiers=private_identifiers,
        solution_root=solution_root,
    )
    clean_decision = sanitize_decision_text(
        decision,
        private_identifiers=private_identifiers,
        solution_root=solution_root,
    )
    clean_rationale = sanitize_decision_text(
        rationale,
        private_identifiers=private_identifiers,
        solution_root=solution_root,
    )
    norm_source_sha = _normalize_sha256(
        source_sha256,
        f"source:{scope}:{clean_item_id}",
    )
    norm_target_sha = _normalize_sha256(
        target_sha256,
        f"target:{scope}:{clean_item_id}:{clean_decision}",
    )
    decision_sha = _sha256_canonical({
        "scope": scope,
        "itemId": clean_item_id,
        "decision": clean_decision,
        "rationale": clean_rationale,
        "sourceSha256": norm_source_sha,
        "targetSha256": norm_target_sha,
    })
    clean_id = (
        sanitize_decision_text(
            record_id,
            private_identifiers=private_identifiers,
            solution_root=solution_root,
        )
        if record_id
        else f"{scope}:{clean_item_id}:{decision_sha[:12]}"
    )
    return {
        "id": clean_id,
        "scope": scope,
        "itemId": clean_item_id,
        "decision": clean_decision,
        "rationale": clean_rationale,
        "sourceSha256": norm_source_sha,
        "targetSha256": norm_target_sha,
        "decisionSha256": decision_sha,
    }


def _resolve_state_and_run_dir(
    root: Path,
    state_path: Optional[Path | str],
) -> tuple[dict[str, Any], Optional[Path]]:
    if state_path is not None:
        resolved = Path(state_path).expanduser().resolve()
        if not resolved.is_file():
            raise ValueError(f"workflow state file does not exist: {resolved}")
        loaded = json.loads(resolved.read_text(encoding="utf-8-sig"))
        if not isinstance(loaded, dict):
            raise ValueError(f"workflow state must be a JSON object: {resolved}")
        return loaded, resolved.parent

    direct_state = root / "workflow-state.json"
    try:
        art_state = existing_artifact_path(root, "workflow-state.json")
    except (OSError, ValueError):
        art_state = direct_state

    if art_state.is_file():
        return _read_json_safe(art_state), art_state.parent
    if direct_state.is_file():
        return _read_json_safe(direct_state), direct_state.parent
    dot_runs = root / ".sentinel-xdr-runs"
    if dot_runs.is_dir() and not dot_runs.is_symlink():
        latest_txt = dot_runs / "latest-run.txt"
        if latest_txt.is_file():
            run_name = latest_txt.read_text(encoding="utf-8", errors="ignore").strip()
            cand = dot_runs / run_name / "workflow-state.json"
            if cand.is_file():
                return _read_json_safe(cand), cand.parent
        for cand in sorted(dot_runs.glob("*/workflow-state.json")):
            if cand.is_file():
                return _read_json_safe(cand), cand.parent
    try:
        return {}, report_directory(root, create=False)
    except (OSError, ValueError):
        return {}, None


def _find_artifact_json(root: Path, run_dir: Optional[Path], filename: str) -> dict[str, Any]:
    candidates: list[Path] = []
    if run_dir is not None:
        candidates.append(run_dir / filename)
    try:
        candidates.append(existing_artifact_path(root, filename))
    except (OSError, ValueError):
        # Ignore missing or invalid artifact paths and fall back to local candidates.
        pass
    candidates.append(root / filename)
    candidates.append(root / "Reports" / filename)
    for cand in candidates:
        if cand.is_file() and not cand.is_symlink():
            doc = _read_json_safe(cand)
            if doc:
                return doc
    return {}


def _find_artifact_yaml(root: Path, run_dir: Optional[Path], filename: str) -> dict[str, Any]:
    candidates: list[Path] = []
    if run_dir is not None:
        candidates.append(run_dir / filename)
    try:
        candidates.append(existing_artifact_path(root, filename))
    except (OSError, ValueError):
        # Ignore missing or invalid artifact paths and fall back to local candidates.
        pass
    candidates.append(root / filename)
    candidates.append(root / "Reports" / filename)
    for cand in candidates:
        if cand.is_file() and not cand.is_symlink():
            doc = _read_yaml_safe(cand)
            if doc:
                return doc
    return {}


def _resolve_solution_version(root: Path, state: Mapping[str, Any]) -> str:
    if isinstance(state.get("solutionVersion"), str) and state["solutionVersion"].strip():
        return state["solutionVersion"].strip()
    context = state.get("context")
    if isinstance(context, Mapping):
        if isinstance(context.get("targetVersion"), str) and context["targetVersion"].strip():
            return context["targetVersion"].strip()
    packaging = state.get("packaging")
    if isinstance(packaging, Mapping):
        last_succ = packaging.get("lastSuccessful")
        if isinstance(last_succ, Mapping) and isinstance(last_succ.get("effectiveTargetVersion"), str):
            return last_succ["effectiveTargetVersion"].strip()
    try:
        ver_info = solution_data_version(root)
        if isinstance(ver_info, tuple) and ver_info:
            ver = ver_info[0]
            if isinstance(ver, str) and ver.strip():
                return ver.strip()
        elif isinstance(ver_info, str) and ver_info.strip():
            return ver_info.strip()
    except (OSError, ValueError, TypeError):
        # Fall back to SolutionMetadata.json or default version if Data file is unavailable.
        pass
    meta = _read_json_safe(root / "SolutionMetadata.json")
    if isinstance(meta.get("version"), str) and meta["version"].strip():
        return meta["version"].strip()
    return "3.1.0"


def build_sanitized_decision_manifest(
    solution_path: Path | str,
    state_path: Optional[Path | str] = None,
    *,
    strict_reject_private: bool = False,
) -> dict[str, Any]:
    """Build a deterministic, sanitized `decision-manifest-v1` document across all Solution Manager flows."""
    root = Path(solution_path).expanduser().resolve()
    if not root.is_dir():
        raise ValueError(f"solution folder does not exist: {root}")

    state, run_dir = _resolve_state_and_run_dir(root, state_path)
    private_ids = _collect_private_identifiers(root, state, run_dir)

    if strict_reject_private or state.get("failClosedOnPrivateIdentifiers") is True:
        containers_to_check = [state]
        if isinstance(state.get("context"), Mapping):
            containers_to_check.append(state["context"])
        for container in containers_to_check:
            for check_key in (
                "decisions",
                "decisionRecords",
                "ruleReviewDecisions",
                "workbookReviewDecisions",
                "connectorSelections",
                "waivers",
                "exclusions",
                "armValidation",
                "qualificationSummary",
            ):
                if check_key in container and _contains_raw_private_data(container[check_key], private_ids, root):
                    raise ValueError(
                        f"Unsafe content remained: unsanitized private identifier or local path in workflow state {check_key!r}"
                    )

    context = state.get("context") if isinstance(state.get("context"), Mapping) else {}
    raw_solution_name = (
        state.get("solutionName")
        or _read_json_safe(root / "SolutionMetadata.json").get("name")
        or root.name
    )
    solution_name = sanitize_decision_text(
        raw_solution_name,
        private_identifiers=private_ids,
        solution_root=root,
    )
    solution_version = sanitize_decision_text(
        _resolve_solution_version(root, state),
        private_identifiers=private_ids,
        solution_root=root,
    )
    workflow_profile = str(
        context.get("workflowProfile")
        or state.get("workflowProfile")
        or "authoring"
    ).strip()
    if workflow_profile not in {"authoring", "qualification"}:
        workflow_profile = "authoring"

    arm_validation_method = str(
        context.get("armValidationMethod")
        or state.get("armValidationMethod")
        or (((state.get("stages") or {}).get("packaging") or {}).get("artifacts") or {}).get("armValidationMethod")
        or "lab-deployment"
    ).strip()

    records_by_key: dict[tuple[str, str, str, str], dict[str, str]] = {}

    def add_record(
        *,
        scope: str,
        item_id: Any,
        decision: Any,
        rationale: Any,
        source_sha256: Any = None,
        target_sha256: Any = None,
        record_id: Optional[str] = None,
    ) -> None:
        item_str = str(item_id or "item")
        resolved_src_sha = source_sha256
        resolved_tgt_sha = target_sha256
        if not resolved_src_sha and item_str:
            candidate_src = root / item_str
            if candidate_src.is_file() and not candidate_src.is_symlink():
                try:
                    resolved_src_sha = _sha256_hex(candidate_src.read_bytes())
                except OSError:
                    # Leave hash empty if source file cannot be read.
                    pass
        if not resolved_tgt_sha and item_str:
            if scope == "rule_review":
                candidate_tgt = root / "XDR Detections" / Path(item_str).name
                if candidate_tgt.is_file() and not candidate_tgt.is_symlink():
                    try:
                        resolved_tgt_sha = _sha256_hex(candidate_tgt.read_bytes())
                    except OSError:
                        # Leave hash empty if target detection file cannot be read.
                        pass
            elif (root / item_str).is_file() and not (root / item_str).is_symlink():
                try:
                    resolved_tgt_sha = _sha256_hex((root / item_str).read_bytes())
                except OSError:
                    # Leave hash empty if target file cannot be read.
                    pass

        rec = _build_decision_record(
            scope=scope,
            item_id=item_str,
            decision=str(decision or "recorded"),
            rationale=str(rationale or "Recorded reviewer decision."),
            source_sha256=resolved_src_sha,
            target_sha256=resolved_tgt_sha,
            private_identifiers=private_ids,
            solution_root=root,
            record_id=record_id,
        )
        dedup_key = (rec["scope"], rec["itemId"], rec["decision"], rec["rationale"])
        records_by_key[dedup_key] = rec

    # 1. Explicit decisions list or per-scope lists/dicts in workflow-state.json (and state.context)
    state_sources: list[Mapping[str, Any]] = [state]
    if isinstance(context, Mapping) and context:
        state_sources.append(context)

    for src_container in state_sources:
        for list_attr in ("decisions", "decisionRecords"):
            for raw_dec in src_container.get(list_attr) or []:
                if not isinstance(raw_dec, Mapping):
                    continue
                raw_scope = str(raw_dec.get("scope") or "rule_review").strip()
                if raw_scope not in ALLOWED_DECISION_SCOPES:
                    continue
                add_record(
                    scope=raw_scope,
                    item_id=raw_dec.get("itemId") or raw_dec.get("targetId") or raw_dec.get("id") or "item",
                    decision=raw_dec.get("decision") or raw_dec.get("status") or "accepted",
                    rationale=raw_dec.get("rationale") or raw_dec.get("reason") or "Explicit workflow state decision.",
                    source_sha256=raw_dec.get("sourceSha256") or raw_dec.get("sourceDocumentSha256"),
                    target_sha256=raw_dec.get("targetSha256") or raw_dec.get("targetQuerySha256"),
                    record_id=raw_dec.get("id") if isinstance(raw_dec.get("id"), str) else None,
                )

    state_scope_lists: tuple[tuple[str, tuple[str, ...]], ...] = (
        ("rule_review", ("ruleReviewDecisions", "ruleDecisions", "reviewDecisions")),
        ("workbook_review", ("workbookReviewDecisions", "workbookDecisions")),
        ("connector_selection", ("connectorSelections", "connectorDecisions")),
        ("waiver", ("waivers", "sourceRuntimeWaivers")),
        ("exclusion", ("exclusions",)),
    )
    for src_container in state_sources:
        for scope_name, keys in state_scope_lists:
            for key_name in keys:
                raw_entries = src_container.get(key_name)
                if isinstance(raw_entries, Mapping):
                    entries: list[dict[str, Any]] = []
                    for map_key, map_val in sorted(raw_entries.items()):
                        if isinstance(map_val, Mapping):
                            merged = dict(map_val)
                            merged.setdefault("itemId", str(map_key))
                            entries.append(merged)
                        elif isinstance(map_val, str):
                            entries.append({"itemId": str(map_key), "decision": map_val})
                elif isinstance(raw_entries, list):
                    entries = [dict(e) for e in raw_entries if isinstance(e, Mapping)]
                else:
                    continue
                for entry in entries:
                    add_record(
                        scope=scope_name,
                        item_id=(
                            entry.get("itemId")
                            or entry.get("ruleId")
                            or entry.get("workbook")
                            or entry.get("connectorId")
                            or entry.get("table")
                            or entry.get("path")
                            or entry.get("id")
                            or scope_name
                        ),
                        decision=entry.get("decision") or entry.get("status") or "accepted",
                        rationale=entry.get("rationale") or entry.get("reason") or f"Recorded {scope_name} decision.",
                        source_sha256=entry.get("sourceSha256") or entry.get("sourceDocumentSha256") or entry.get("workbookSha256"),
                        target_sha256=entry.get("targetSha256") or entry.get("targetQuerySha256") or entry.get("querySha256"),
                        record_id=entry.get("id") if isinstance(entry.get("id"), str) else None,
                    )

    # 2. Rule review & connector/waiver/exclusion decisions from migration-config.yaml and XDR Detections
    migration_cfg = (
        _find_artifact_yaml(root, run_dir, "migration-config.yaml")
        or _find_artifact_json(root, run_dir, "migration-reviewed-overrides.json")
    )
    rule_overrides = migration_cfg.get("ruleOverrides") if isinstance(migration_cfg.get("ruleOverrides"), Mapping) else {}
    for rule_id, override in sorted(rule_overrides.items()):
        if not isinstance(override, Mapping):
            continue
        for rev_dec in override.get("reviewDecisions") or []:
            if not isinstance(rev_dec, Mapping):
                continue
            add_record(
                scope="rule_review",
                item_id=rule_id,
                decision=rev_dec.get("decision") or "accept",
                rationale=rev_dec.get("rationale") or rev_dec.get("reason") or "Rule review decision.",
                source_sha256=rev_dec.get("sourceDocumentSha256") or rev_dec.get("sourceSha256"),
                target_sha256=rev_dec.get("targetQuerySha256") or rev_dec.get("targetSha256"),
            )
        if isinstance(override.get("description"), str) and override["description"].strip():
            add_record(
                scope="rule_review",
                item_id=rule_id,
                decision="change",
                rationale="Reviewed concise alert description override.",
                source_sha256=override.get("sourceDocumentSha256"),
                target_sha256=override.get("targetQuerySha256"),
            )
        if isinstance(override.get("entityMappings"), Mapping):
            add_record(
                scope="rule_review",
                item_id=rule_id,
                decision="change",
                rationale="Reviewed entity mapping override.",
                source_sha256=override.get("sourceDocumentSha256"),
                target_sha256=override.get("targetQuerySha256"),
            )

    for conn_entry in migration_cfg.get("connectorSelections") or migration_cfg.get("selectedConnectors") or []:
        if isinstance(conn_entry, Mapping):
            add_record(
                scope="connector_selection",
                item_id=conn_entry.get("connectorId") or conn_entry.get("itemId") or conn_entry.get("id") or "connector",
                decision=conn_entry.get("decision") or "selected",
                rationale=conn_entry.get("rationale") or conn_entry.get("reason") or "Selected connector dependency.",
                source_sha256=conn_entry.get("sourceSha256"),
                target_sha256=conn_entry.get("targetSha256"),
            )
        elif isinstance(conn_entry, str) and conn_entry.strip():
            add_record(
                scope="connector_selection",
                item_id=conn_entry.strip(),
                decision="selected",
                rationale="Selected connector in migration configuration.",
            )

    for excl_entry in migration_cfg.get("excludedRules") or migration_cfg.get("exclusions") or []:
        if isinstance(excl_entry, Mapping):
            add_record(
                scope="exclusion",
                item_id=excl_entry.get("itemId") or excl_entry.get("ruleId") or excl_entry.get("path") or "excluded-item",
                decision="excluded",
                rationale=excl_entry.get("rationale") or excl_entry.get("reason") or "Excluded from migration scope.",
                source_sha256=excl_entry.get("sourceSha256"),
                target_sha256=excl_entry.get("targetSha256"),
            )
        elif isinstance(excl_entry, str) and excl_entry.strip():
            add_record(
                scope="exclusion",
                item_id=excl_entry.strip(),
                decision="excluded",
                rationale="Excluded rule in migration configuration.",
            )

    detections_dir = root / "XDR Detections"
    if detections_dir.is_dir():
        try:
            det_paths = xdr_detection_files(detections_dir)
        except (OSError, ValueError):
            det_paths = sorted(
                p for p in detections_dir.rglob("*")
                if p.is_file() and p.suffix.lower() in {".yaml", ".yml"}
            )
        for det_path in det_paths:
            raw_bytes = det_path.read_bytes()
            target_file_sha = _sha256_hex(raw_bytes)
            doc = _read_yaml_safe(det_path)
            if not doc:
                continue
            provenance = doc.get("contentProvenance") if isinstance(doc.get("contentProvenance"), Mapping) else {}
            source_meta = provenance.get("source") if isinstance(provenance.get("source"), Mapping) else {}
            conversion = provenance.get("conversion") if isinstance(provenance.get("conversion"), Mapping) else {}
            review_scope = conversion.get("reviewScope") if isinstance(conversion.get("reviewScope"), Mapping) else {}
            rule_id = str(source_meta.get("id") or det_path.stem)
            src_sha = (
                review_scope.get("sourceDocumentSha256")
                or source_meta.get("sha256")
                or source_meta.get("querySha256")
            )
            tgt_sha = review_scope.get("targetQuerySha256") or target_file_sha

            for rev_dec in conversion.get("reviewDecisions") or []:
                if not isinstance(rev_dec, Mapping):
                    continue
                add_record(
                    scope="rule_review",
                    item_id=rule_id,
                    decision=rev_dec.get("decision") or "accept",
                    rationale=rev_dec.get("rationale") or rev_dec.get("reason") or "Detection review decision.",
                    source_sha256=rev_dec.get("sourceDocumentSha256") or src_sha,
                    target_sha256=rev_dec.get("targetQuerySha256") or tgt_sha,
                )
            for acc_reason in conversion.get("acceptedReviewReasons") or []:
                if isinstance(acc_reason, str) and acc_reason.strip():
                    add_record(
                        scope="rule_review",
                        item_id=rule_id,
                        decision="accept",
                        rationale=acc_reason.strip(),
                        source_sha256=src_sha,
                        target_sha256=tgt_sha,
                    )
            event_tw = conversion.get("eventTimeWindow")
            if isinstance(event_tw, Mapping) and event_tw.get("defaultApplied"):
                add_record(
                    scope="rule_review",
                    item_id=rule_id,
                    decision="accept-default-timing",
                    rationale=(
                        f"Hourly frequency ({event_tw.get('sourceFrequency', 'PT1H')}) with "
                        f"native XDR lookback ({event_tw.get('targetLookback', 'PT4H')})."
                    ),
                    source_sha256=event_tw.get("sourceQuerySha256") or src_sha,
                    target_sha256=event_tw.get("targetQuerySha256") or tgt_sha,
                )
            schedule_freq = (((doc.get("properties") or {}).get("schedule") or {}).get("frequency"))
            if str(source_meta.get("kind") or "").upper() == "NRT" and schedule_freq == "PT0S":
                add_record(
                    scope="rule_review",
                    item_id=rule_id,
                    decision="nrt-continuous-pt0s",
                    rationale="Mapped eligible Sentinel NRT rule to Continuous (PT0S) Custom Detection.",
                    source_sha256=src_sha,
                    target_sha256=tgt_sha,
                )
            for conn in provenance.get("requiredConnectors") or []:
                if isinstance(conn, Mapping) and conn.get("connectorId"):
                    add_record(
                        scope="connector_selection",
                        item_id=str(conn["connectorId"]),
                        decision="selected",
                        rationale=f"Required connector for detection {rule_id}.",
                        source_sha256=src_sha,
                        target_sha256=tgt_sha,
                    )

    # 3. Workbook review & workbook exclusions
    wb_state = state.get("workbooks") if isinstance(state.get("workbooks"), Mapping) else {}
    wb_inv_sha = {
        str(item.get("path")): str(item.get("sha256") or "")
        for item in (wb_state.get("inventory") or [])
        if isinstance(item, Mapping) and item.get("path")
    }
    wb_selection = wb_state.get("selection") if isinstance(wb_state.get("selection"), Mapping) else {}
    for excl_wb in wb_selection.get("excluded") or []:
        if isinstance(excl_wb, Mapping) and excl_wb.get("path"):
            wb_path = str(excl_wb["path"])
            add_record(
                scope="exclusion",
                item_id=wb_path,
                decision="excluded",
                rationale=str(excl_wb.get("reason") or "Workbook excluded from migration selection."),
                source_sha256=wb_inv_sha.get(wb_path) or wb_state.get("inventorySha256"),
                target_sha256=wb_state.get("selectionSha256"),
            )

    wb_receipt = _find_artifact_json(root, run_dir, "workbook-review-receipt.json")
    wb_decisions_obj = wb_receipt.get("decisions") if isinstance(wb_receipt.get("decisions"), Mapping) else {}
    for q_dec in wb_decisions_obj.get("queries") or []:
        if not isinstance(q_dec, Mapping):
            continue
        wb_name = str(q_dec.get("workbook") or "workbook")
        q_ptr = str(q_dec.get("path") or "query")
        add_record(
            scope="workbook_review",
            item_id=f"{wb_name}:{q_ptr}",
            decision=q_dec.get("decision") or "accept",
            rationale=q_dec.get("rationale") or q_dec.get("reason") or "Reviewed workbook query migration.",
            source_sha256=q_dec.get("workbookSha256") or wb_inv_sha.get(wb_name),
            target_sha256=q_dec.get("querySha256"),
        )
    for w_dec in wb_decisions_obj.get("workbooks") or []:
        if not isinstance(w_dec, Mapping):
            continue
        wb_name = str(w_dec.get("path") or w_dec.get("workbook") or "workbook")
        add_record(
            scope="workbook_review",
            item_id=wb_name,
            decision=w_dec.get("decision") or "accept",
            rationale=w_dec.get("rationale") or w_dec.get("reason") or "Reviewed workbook dependency selection.",
            source_sha256=w_dec.get("workbookSha256") or wb_inv_sha.get(wb_name),
            target_sha256=w_dec.get("targetSha256") or wb_state.get("selectionSha256"),
        )

    # 4. Package selection exclusions
    selection_plan = _find_artifact_json(root, run_dir, "package-selection-plan.json")
    plan_sha = selection_plan.get("planSha256")
    for list_key in ("analyticRules", "xdrDetections"):
        for item in selection_plan.get(list_key) or []:
            if isinstance(item, Mapping) and item.get("included") is False:
                reasons = item.get("reasons") or []
                reason_text = "; ".join(str(r) for r in reasons if r) or "Excluded by package selection plan."
                add_record(
                    scope="exclusion",
                    item_id=item.get("id") or item.get("path") or list_key,
                    decision="excluded",
                    rationale=reason_text,
                    source_sha256=item.get("sourceSha256") or item.get("sha256"),
                    target_sha256=plan_sha,
                )

    # 5. Source runtime waivers
    try:
        runtime_files = existing_artifacts(root, "runtime-validation.*.json")
    except (OSError, ValueError):
        runtime_files = []
    if run_dir is not None and run_dir.is_dir():
        for extra_rt in sorted(run_dir.glob("runtime-validation.*.json")):
            if extra_rt not in runtime_files:
                runtime_files.append(extra_rt)
    for rt_file in runtime_files:
        rt_doc = _read_json_safe(rt_file)
        provider = str(rt_doc.get("provider") or "")
        for sw in rt_doc.get("sourceWhitelist") or []:
            if isinstance(sw, Mapping):
                add_record(
                    scope="waiver",
                    item_id=sw.get("detection") or sw.get("table") or "source-waiver",
                    decision=sw.get("status") or "source-waived",
                    rationale=sw.get("reason") or "Source runtime missing-schema waiver.",
                    source_sha256=sw.get("querySha256"),
                    target_sha256=sw.get("querySha256"),
                )
        for res in rt_doc.get("results") or []:
            if not isinstance(res, Mapping):
                continue
            match = missing_schema_whitelist_match(res, provider=provider)
            if match:
                add_record(
                    scope="waiver",
                    item_id=str(res.get("detection") or match.get("table") or "source-waiver"),
                    decision="source-waived",
                    rationale=str(match.get("reason") or "Source runtime missing-schema waiver."),
                    source_sha256=res.get("querySha256"),
                    target_sha256=res.get("querySha256"),
                )

    # 6. ARM validation decisions
    arm_state = state.get("armValidation") if isinstance(state.get("armValidation"), Mapping) else {}
    arm_plan = _find_artifact_json(root, run_dir, "arm-validation-plan.json")
    arm_ttk = _find_artifact_json(root, run_dir, "arm-ttk-acceptance.json")
    packaging_stage = ((state.get("stages") or {}).get("packaging") or {}) if isinstance(state.get("stages"), Mapping) else {}
    packaging_arts = packaging_stage.get("artifacts") if isinstance(packaging_stage.get("artifacts"), Mapping) else {}
    if (
        arm_state
        or arm_plan
        or arm_ttk
        or context.get("armValidationMethod")
        or state.get("armValidationMethod")
        or packaging_arts.get("armValidationMethod")
    ):
        arm_rationale = (
            arm_state.get("rationale")
            or arm_state.get("reason")
            or arm_ttk.get("summary")
            or arm_plan.get("summary")
            or f"ARM template validation configured via {arm_validation_method}."
        )
        add_record(
            scope="arm_validation",
            item_id=str(arm_state.get("itemId") or "mainTemplate.json"),
            decision=str(arm_state.get("decision") or arm_validation_method),
            rationale=str(arm_rationale),
            source_sha256=(
                arm_state.get("sourceSha256")
                or arm_plan.get("packageInputSha256")
                or packaging_arts.get("packageInputSha256")
            ),
            target_sha256=(
                arm_state.get("targetSha256")
                or arm_ttk.get("templateSha256")
                or arm_plan.get("templateSha256")
                or packaging_arts.get("mainTemplateSha256")
            ),
        )

    # 7. Qualification summary decisions
    qual_state = state.get("qualificationSummary") if isinstance(state.get("qualificationSummary"), Mapping) else {}
    parity_doc = _find_artifact_json(root, run_dir, "alert-parity-report.json")
    query_parity_doc = _find_artifact_json(root, run_dir, "mock-query-parity.json")
    pipeline_doc = _find_artifact_json(root, run_dir, "qualification-pipeline-state.json")
    alert_parity_stage = ((state.get("stages") or {}).get("alertParity") or {}) if isinstance(state.get("stages"), Mapping) else {}
    if (
        qual_state
        or parity_doc
        or query_parity_doc
        or pipeline_doc
        or workflow_profile == "qualification"
        or alert_parity_stage.get("status") in {"passed", "failed", "blocked"}
    ):
        wb_contract = (
            pipeline_doc.get("workbookContractResult")
            if isinstance(pipeline_doc.get("workbookContractResult"), Mapping)
            else {}
        )
        wb_queries = wb_contract.get("queryValidation") if isinstance(wb_contract.get("queryValidation"), list) else []
        wb_query_summary = ""
        if wb_queries and isinstance(wb_queries[0], Mapping):
            executed_cnt = wb_queries[0].get("executedQueryCount")
            failed_cnt = wb_queries[0].get("failedQueryCount")
            if isinstance(executed_cnt, int) and isinstance(failed_cnt, int):
                wb_query_summary = f" Workbook qualification passed ({executed_cnt - failed_cnt}/{executed_cnt} queries)."
        pipeline_summary = ""
        if pipeline_doc.get("status") == "passed" and (pipeline_doc.get("promotionGate") or {}).get("passed") is True:
            pipeline_summary = (
                "Qualification pipeline passed: preflight, disabled ARM template deployment with GET readback, "
                f"synthetic DCR mock ingestion, and functional qualification verified.{wb_query_summary}"
            )
        qual_decision = (
            qual_state.get("decision")
            or qual_state.get("status")
            or parity_doc.get("status")
            or pipeline_doc.get("status")
            or alert_parity_stage.get("status")
            or ("qualified" if workflow_profile == "qualification" else "not-run")
        )
        qual_rationale = (
            qual_state.get("rationale")
            or qual_state.get("reason")
            or parity_doc.get("summary")
            or pipeline_summary
            or alert_parity_stage.get("message")
            or f"Qualification profile summary ({qual_decision})."
        )
        add_record(
            scope="qualification_summary",
            item_id=str(qual_state.get("itemId") or solution_name),
            decision=str(qual_decision),
            rationale=str(qual_rationale),
            source_sha256=(
                qual_state.get("sourceSha256")
                or parity_doc.get("selectionPlanSha256")
                or query_parity_doc.get("sourceSha256")
                or pipeline_doc.get("planSha256")
            ),
            target_sha256=(
                qual_state.get("targetSha256")
                or parity_doc.get("reportSha256")
                or query_parity_doc.get("targetSha256")
                or ((pipeline_doc.get("ingestionEvidence") or {}).get("payloadSha256") if isinstance(pipeline_doc.get("ingestionEvidence"), Mapping) else None)
            ),
        )

    decisions = sorted(
        records_by_key.values(),
        key=lambda r: (r["scope"], r["itemId"], r["decision"], r["id"]),
    )

    default_timestamp_utc = str(
        state.get("updatedAt")
        or state.get("generatedAtUtc")
        or state.get("createdAt")
        or "1970-01-01T00:00:00Z"
    ).strip()

    overrides: list[dict[str, str]] = []
    seen_overrides: set[tuple[str, str, str]] = set()

    def add_override(
        item_id_val: Any,
        override_type: str,
        reason_val: Any,
        timestamp_val: Any = None,
    ) -> None:
        if override_type not in {"waiver", "manual_edit", "rejection"}:
            return
        clean_item = sanitize_decision_text(
            str(item_id_val or "solution"),
            private_identifiers=private_ids,
            solution_root=root,
        )
        clean_reason = sanitize_decision_text(
            str(reason_val or f"Recorded {override_type} decision."),
            private_identifiers=private_ids,
            solution_root=root,
        )
        clean_ts = sanitize_decision_text(
            str(timestamp_val or default_timestamp_utc),
            private_identifiers=private_ids,
            solution_root=root,
        )
        ov_key = (clean_item, override_type, clean_reason)
        if ov_key in seen_overrides:
            return
        seen_overrides.add(ov_key)
        overrides.append(
            {
                "itemId": clean_item,
                "overrideType": override_type,
                "reason": clean_reason,
                "timestampUtc": clean_ts,
            }
        )

    for src_container in state_sources:
        raw_ovs = src_container.get("overrides")
        if isinstance(raw_ovs, list):
            for raw_ov in raw_ovs:
                if not isinstance(raw_ov, Mapping):
                    continue
                ov_type = str(raw_ov.get("overrideType") or raw_ov.get("type") or "").strip().lower()
                if ov_type not in {"waiver", "manual_edit", "rejection"}:
                    ov_type = "manual_edit"
                add_override(
                    raw_ov.get("itemId") or raw_ov.get("id") or raw_ov.get("checkId"),
                    ov_type,
                    raw_ov.get("reason") or raw_ov.get("rationale") or raw_ov.get("authorJustification"),
                    raw_ov.get("timestampUtc") or raw_ov.get("timestamp"),
                )

    for rec in decisions:
        sc = rec["scope"]
        dec_lower = rec["decision"].strip().lower()
        if sc == "waiver" or "waive" in dec_lower:
            add_override(rec["itemId"], "waiver", rec["rationale"])
        elif sc == "exclusion" or dec_lower in {"excluded", "exclude", "rejected", "reject"}:
            add_override(rec["itemId"], "rejection", rec["rationale"])
        elif any(
            tok in dec_lower
            for tok in ("change", "manual", "override", "overridden", "edit", "modified", "fallback", "approved_with_")
        ):
            add_override(rec["itemId"], "manual_edit", rec["rationale"])

    for rule_id, override in sorted(rule_overrides.items()):
        if not isinstance(override, Mapping):
            continue
        dec_val = str(override.get("decision") or override.get("action") or "").strip().lower()
        reason_val = (
            override.get("rationale")
            or override.get("reason")
            or override.get("justification")
            or "Applied manual rule override."
        )
        ts_val = override.get("timestampUtc") or override.get("updatedAt")
        if dec_val in {"reject", "rejected", "exclude", "excluded"}:
            add_override(rule_id, "rejection", reason_val, ts_val)
        elif (
            dec_val in {"change", "manual_edit", "manual_override", "overridden", "modified"}
            or (isinstance(override.get("description"), str) and override["description"].strip())
            or isinstance(override.get("entityMappings"), Mapping)
            or isinstance(override.get("query"), str)
        ):
            add_override(rule_id, "manual_edit", reason_val, ts_val)

    overrides.sort(key=lambda o: (o["overrideType"], o["itemId"], o["reason"]))

    normalized_payload = {
        "schemaVersion": DECISION_MANIFEST_SCHEMA_VERSION,
        "solutionName": solution_name,
        "solutionVersion": solution_version,
        "workflowProfile": workflow_profile,
        "armValidationMethod": arm_validation_method,
        "decisions": decisions,
        "overrides": overrides,
    }
    manifest_sha256 = _sha256_canonical(normalized_payload)
    manifest: dict[str, Any] = {
        **normalized_payload,
        "decisionCount": len(decisions),
        "sanitizedVerified": True,
        "manifestSha256": manifest_sha256,
    }

    verify_sanitized_decision_manifest(
        manifest,
        private_identifiers=private_ids,
        solution_root=root,
    )
    return manifest


def write_sanitized_decision_manifest(
    solution_path: Path | str,
    state_path: Optional[Path | str] = None,
    output_path: Optional[Path | str] = None,
    *,
    strict_reject_private: bool = False,
) -> dict[str, Any]:
    """Build, fail-closed verify, and atomically write the sanitized decision manifest."""
    root = Path(solution_path).expanduser().resolve()
    manifest = build_sanitized_decision_manifest(
        root,
        state_path=state_path,
        strict_reject_private=strict_reject_private,
    )
    state, run_dir = _resolve_state_and_run_dir(root, state_path)
    private_ids = _collect_private_identifiers(root, state, run_dir)
    verify_sanitized_decision_manifest(
        manifest,
        private_identifiers=private_ids,
        solution_root=root,
    )

    if output_path is not None:
        destination = Path(output_path).expanduser().resolve()
    elif run_dir is not None:
        destination = run_dir / DEFAULT_DECISION_MANIFEST_FILENAME
    else:
        destination = report_directory(root, create=True) / DEFAULT_DECISION_MANIFEST_FILENAME

    destination.parent.mkdir(parents=True, exist_ok=True)
    serialized = (json.dumps(manifest, indent=2, ensure_ascii=False) + "\n").encode("utf-8")
    temp_path: Optional[Path] = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="wb",
            prefix=f".{destination.name}.",
            suffix=".tmp",
            dir=destination.parent,
            delete=False,
        ) as handle:
            temp_path = Path(handle.name)
            handle.write(serialized)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temp_path, destination)
        temp_path = None
    finally:
        if temp_path is not None:
            temp_path.unlink(missing_ok=True)

    return manifest


__all__ = [
    "ALLOWED_DECISION_SCOPES",
    "DECISION_MANIFEST_SCHEMA_VERSION",
    "DEFAULT_DECISION_MANIFEST_FILENAME",
    "build_sanitized_decision_manifest",
    "sanitize_decision_text",
    "verify_sanitized_decision_manifest",
    "write_sanitized_decision_manifest",
]
