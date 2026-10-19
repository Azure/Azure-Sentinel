"""PR content-type detection, migration classification, and check applicability engine."""
from __future__ import annotations

from copy import deepcopy
import json
from pathlib import Path
import re
from typing import Any, Iterable, Mapping

import yaml

CONTENT_TYPES: tuple[str, ...] = (
    "solution-package",
    "analytic-rules",
    "xdr-detections",
    "workbooks",
    "xdr-workbooks",
    "data-connectors",
    "parsers",
    "hunting-queries",
    "playbooks",
    "notebooks",
    "logos",
    "sample-data",
)

DEFAULT_DOCS_DIR: Path = Path(__file__).resolve().parents[2] / "docs" / "qualification"

CHECK_DOC_FILENAMES: tuple[tuple[str, str], ...] = (
    ("validation", "validation-checks.md"),
    ("qualification", "qualification-checks.md"),
    ("migration", "migration-checks.md"),
)

BUILTIN_CHECK_CATALOG: list[dict[str, Any]] = [
    # -------------------------------------------------------------------------
    # Validation Checklist (validation)
    # -------------------------------------------------------------------------
    {
        "id": "VAL-CI-01",
        "checklist": "validation",
        "title": "Existing PR validations / CI checks passed",
        "originalCriterion": "Verify all existing repository PR validation workflows and CI syntax checks pass.",
        "contentType": "solution-package",
        "category": "validation",
        "sourceChecklist": "pr-checklist-2-docx",
    },
    {
        "id": "VAL-PKG-01",
        "checklist": "validation",
        "title": "Package version incremented from latest live version and >= 3.2.2",
        "originalCriterion": "Verify the solution package version is incremented above the live version and is at least 3.2.2.",
        "contentType": "solution-package",
        "category": "validation",
        "sourceChecklist": "pr-checklist-2-docx + toolkit-contract",
    },
    {
        "id": "VAL-PKG-02",
        "checklist": "validation",
        "title": "SolutionMetadata.json, Data/Solution_*.json, ReleaseNotes.md, and Package/<version>.zip version quartet match",
        "originalCriterion": "Verify the version string matches across SolutionMetadata.json, Data/Solution_*.json, ReleaseNotes.md, and Package/<version>.zip.",
        "contentType": "solution-package",
        "category": "validation",
        "sourceChecklist": "master-excel + toolkit-contract",
    },
    {
        "id": "VAL-PKG-03",
        "checklist": "validation",
        "title": "createUiDefinition.json Basics and Manage step component counts match packaged resources",
        "originalCriterion": "Verify createUiDefinition.json Basics description and Manage steps match the resources packaged in mainTemplate.json.",
        "contentType": "solution-package",
        "category": "validation",
        "sourceChecklist": "pr-checklist-2-docx",
    },
    {
        "id": "VAL-PKG-04",
        "checklist": "validation",
        "title": "Required XDR properties exist in mainTemplate.json (requiredWorkloads, requiredDataConnectors, extra.customDetections / Defender workbook metadata)",
        "originalCriterion": "Verify requiredWorkloads, requiredDataConnectors, and extra.customDetections / Defender workbook metadata exist in mainTemplate.json.",
        "contentType": "xdr-detections,xdr-workbooks",
        "category": "validation",
        "sourceChecklist": "pr-checklist-2-docx",
    },
    {
        "id": "VAL-URL-01",
        "checklist": "validation",
        "title": "Short URLs (aka.ms) and changed documentation/logo URLs are valid and formatted properly",
        "originalCriterion": "Verify short URLs (aka.ms) and all changed documentation or logo URLs use valid HTTPS formatting.",
        "contentType": "solution-package,logos",
        "category": "validation",
        "sourceChecklist": "pr-checklist-2-docx + master-excel",
    },
    {
        "id": "VAL-AR-01",
        "checklist": "validation",
        "title": "Analytic Rule YAML schema, GUID format, MITRE ATT&CK mappings, severity, and entity mappings valid",
        "originalCriterion": "Verify Analytic Rule YAML schema fields, GUID format, MITRE ATT&CK tactics/techniques, severity, and entity mappings.",
        "contentType": "analytic-rules,xdr-detections",
        "category": "validation",
        "sourceChecklist": "master-excel",
    },
    {
        "id": "VAL-WB-01",
        "checklist": "validation",
        "title": "Workbook JSON schema, top-level items, and ARM template embedding valid",
        "originalCriterion": "Verify Workbook JSON schema structure, top-level items array, and mainTemplate.json embedding.",
        "contentType": "workbooks,xdr-workbooks",
        "category": "validation",
        "sourceChecklist": "master-excel",
    },
    {
        "id": "VAL-DC-01",
        "checklist": "validation",
        "title": "Data Connector JSON/CCF structure, table definitions, and configuration instructions valid",
        "originalCriterion": "Verify Data Connector JSON/CCF definitions, target table declarations, and configuration instruction steps.",
        "contentType": "data-connectors",
        "category": "validation",
        "sourceChecklist": "master-excel",
    },
    {
        "id": "VAL-PRS-01",
        "checklist": "validation",
        "title": "Parser YAML structure and KQL function definition valid",
        "originalCriterion": "Verify Parser YAML metadata structure, function alias, and non-empty KQL body.",
        "contentType": "parsers",
        "category": "validation",
        "sourceChecklist": "master-excel",
    },
    {
        "id": "E2E-V01",
        "checklist": "validation",
        "title": "Complete subject inventory accounted for (100% packaged or exclusions explicitly acknowledged by author)",
        "originalCriterion": "Verify 100% of solution content items are packaged or any partial exclusions are explicitly acknowledged in decision-manifest.json / acknowledged_exclusions.",
        "contentType": "solution-package",
        "category": "validation",
        "sourceChecklist": "user-e2e-requirement",
    },
    {
        "id": "E2E-V02",
        "checklist": "validation",
        "title": "Detection mock data (mock.json) exists and is schema-valid JSON for every packaged detection",
        "originalCriterion": "Verify mock.json exists and contains schema-valid JSON records covering every packaged Sentinel Analytic Rule and Defender XDR Custom Detection.",
        "contentType": "analytic-rules,xdr-detections,sample-data",
        "category": "validation",
        "sourceChecklist": "user-e2e-requirement",
    },
    {
        "id": "E2E-V03",
        "checklist": "validation",
        "title": "Workbook mock data exists and is schema-valid JSON covering every packaged Workbook",
        "originalCriterion": "Verify mock data exists and contains schema-valid JSON records covering every packaged Sentinel and Defender XDR Workbook.",
        "contentType": "workbooks,xdr-workbooks,sample-data",
        "category": "validation",
        "sourceChecklist": "user-e2e-requirement",
    },
    # -------------------------------------------------------------------------
    # Qualification Checklist (qualification)
    # -------------------------------------------------------------------------
    {
        "id": "QUAL-00",
        "checklist": "qualification",
        "title": "Validation checklist passed (Hard prerequisite: Validation rollup is Validated or Partially Validated)",
        "originalCriterion": "Require Validation checklist rollup to be Validated or Partially Validated before Qualification can pass.",
        "contentType": "solution-package",
        "category": "qualification",
        "sourceChecklist": "user-e2e-requirement + pr-checklist-2-docx",
    },
    {
        "id": "E2E-G01",
        "checklist": "qualification",
        "title": "No simulated fallbacks in Qualification mode (live Azure/KQL/browser provider receipts verified)",
        "originalCriterion": "Verify live Azure, KQL, and browser provider receipts were used; fail closed if dry-run or simulated fallback stubs were used.",
        "contentType": "solution-package",
        "category": "qualification",
        "sourceChecklist": "user-e2e-requirement + toolkit-contract",
    },
    {
        "id": "QUAL-DEP-01",
        "checklist": "qualification",
        "title": "Solution ARM template deployed to lab workspace and verified via GET readback",
        "originalCriterion": "Deploy the packaged solution ARM template disabled to the lab workspace and verify deployed resources via independent GET readback.",
        "contentType": "solution-package",
        "category": "qualification",
        "sourceChecklist": "toolkit-contract",
    },
    {
        "id": "E2E-Q01",
        "checklist": "qualification",
        "title": "Mock data for all detections and workbooks injected into live lab workspace via DCR and verified in target tables",
        "originalCriterion": "Inject synthetic mock data via DCR into the live lab workspace and verify row landing across all target tables.",
        "contentType": "analytic-rules,xdr-detections,workbooks,xdr-workbooks,sample-data",
        "category": "qualification",
        "sourceChecklist": "user-e2e-requirement",
    },
    {
        "id": "E2E-Q02",
        "checklist": "qualification",
        "title": "Controlled alert lifecycle & firing (TK-Q11: verified disabled at start, enabled, fires >= 1 real alert, and returned to disabled)",
        "originalCriterion": "Verify every packaged detection starts disabled, is enabled in a controlled window, fires at least 1 real alert correlated to the injected mock scenario, and is returned to disabled.",
        "contentType": "analytic-rules,xdr-detections",
        "category": "qualification",
        "sourceChecklist": "user-e2e-requirement + toolkit-contract",
    },
    {
        "id": "E2E-Q04",
        "checklist": "qualification",
        "title": "Every Workbook query executes against injected lab data and returns non-empty data (rowCount > 0)",
        "originalCriterion": "Execute every Workbook KQL query against the injected lab telemetry and verify rowCount > 0 with non-zero scenario values.",
        "contentType": "workbooks,xdr-workbooks",
        "category": "qualification",
        "sourceChecklist": "user-e2e-requirement",
    },
    {
        "id": "E2E-Q05",
        "checklist": "qualification",
        "title": "UI agent traverses all user-facing content in the portal and captures DOM + screenshot evidence",
        "originalCriterion": "Traverse Detections, Workbooks across tabs/pickers, and Data Connectors in the portal via UI agent and capture DOM + screenshot evidence.",
        "contentType": "analytic-rules,xdr-detections,workbooks,xdr-workbooks,data-connectors",
        "category": "qualification",
        "sourceChecklist": "user-e2e-requirement",
    },
    {
        "id": "E2E-Q06",
        "checklist": "qualification",
        "title": "UI agent verifies all images, logos, SVG diagrams, and visualizations render properly (naturalWidth > 0, HTTP 200, 0 broken assets)",
        "originalCriterion": "Verify all images, logos, SVG diagrams, and chart visualizations render in the browser with naturalWidth > 0, HTTP 200, and 0 broken assets.",
        "contentType": "logos,workbooks,xdr-workbooks,data-connectors",
        "category": "qualification",
        "sourceChecklist": "user-e2e-requirement + master-excel",
    },
    {
        "id": "QUAL-URL-01",
        "checklist": "qualification",
        "title": "Changed URLs opened and verified in browser",
        "originalCriterion": "Open and verify all changed documentation, short-link, and logo URLs in a live browser session.",
        "contentType": "solution-package,logos",
        "category": "qualification",
        "sourceChecklist": "pr-checklist-2-docx",
    },
    {
        "id": "QUAL-HR-01",
        "checklist": "qualification",
        "title": "Reviewer confirmation of supplied XDR / portal behavioral artifacts",
        "originalCriterion": "Human reviewer confirmation of supplied portal screenshots, alert lifecycle receipts, and behavioral artifacts.",
        "contentType": "solution-package",
        "category": "human-review",
        "sourceChecklist": "pr-checklist-2-docx",
    },
    # -------------------------------------------------------------------------
    # Migration Checklist (migration — activated ONLY when is_migration=True)
    # -------------------------------------------------------------------------
    {
        "id": "MIG-V01",
        "checklist": "migration",
        "title": "XDR detection identity contract (TK-V02: xdr-<source GUID>, source path & SHA-256 provenance)",
        "originalCriterion": "Verify every converted XDR detection uses id xdr-<source GUID> and records sourceRulePath and sourceRuleSha256 provenance.",
        "contentType": "xdr-detections",
        "category": "validation",
        "sourceChecklist": "toolkit-contract",
    },
    {
        "id": "MIG-V02",
        "checklist": "migration",
        "title": "NRT (kind: NRT) and schedule contract (TK-V03: PT0S Continuous eligibility, cosmetic summarize rewrite, or PT1H fallback documented)",
        "originalCriterion": "Verify NRT and scheduled detections follow PT0S Continuous eligibility rules, cosmetic summarize rewrites, or documented PT1H fallback.",
        "contentType": "xdr-detections",
        "category": "validation",
        "sourceChecklist": "toolkit-contract",
    },
    {
        "id": "MIG-V03",
        "checklist": "migration",
        "title": "XDR entity binding and custom-detail column integrity (TK-V04/V05)",
        "originalCriterion": "Verify XDR entity mappings and customDetails reference valid query output columns and supported XDR entity identifiers.",
        "contentType": "xdr-detections",
        "category": "validation",
        "sourceChecklist": "toolkit-contract",
    },
    {
        "id": "MIG-Q01",
        "checklist": "migration",
        "title": "Dual-surface runtime KQL execution (TK-Q01..Q03: Sentinel Log Analytics + Defender XDR Advanced Hunting output-schema binding)",
        "originalCriterion": "Verify source Sentinel KQL executes on Log Analytics and converted XDR KQL executes on Defender XDR Advanced Hunting with valid output-schema binding.",
        "contentType": "analytic-rules,xdr-detections,workbooks,xdr-workbooks",
        "category": "qualification",
        "sourceChecklist": "toolkit-contract",
    },
    {
        "id": "E2E-Q03",
        "checklist": "migration",
        "title": "Sentinel Analytic Rule <-> Defender XDR Custom Detection strict alert parity from shared mock injection (TK-Q09/Q10)",
        "originalCriterion": "Verify strict alert, entity, and custom-detail parity between each Sentinel Analytic Rule and its migrated Defender XDR Custom Detection from shared mock data.",
        "contentType": "analytic-rules,xdr-detections",
        "category": "qualification",
        "sourceChecklist": "user-e2e-requirement + toolkit-contract",
    },
]

_YAML_CHECK_BLOCK_RE = re.compile(
    r"```(?:yaml|yml)\s+check-definition\s*\n(.*?)```",
    re.DOTALL | re.IGNORECASE,
)


def _normalize_check_entry(raw: Mapping[str, Any], default_checklist: str | None = None) -> dict[str, Any]:
    """Normalize a parsed YAML check definition into canonical camelCase keys."""
    check_id = str(raw.get("id") or raw.get("checkId") or raw.get("check_id") or "").strip()
    checklist = str(raw.get("checklist") or default_checklist or "validation").strip().lower()
    content_type_raw = raw.get("contentType") or raw.get("content_type") or raw.get("contentTypes") or "solution-package"
    if isinstance(content_type_raw, (list, tuple, set)):
        content_type = ",".join(str(x).strip() for x in content_type_raw if str(x).strip())
    else:
        content_type = str(content_type_raw).strip()

    return {
        "id": check_id,
        "checklist": checklist,
        "title": str(raw.get("title") or raw.get("name") or check_id).strip(),
        "originalCriterion": str(
            raw.get("originalCriterion")
            or raw.get("original_criterion")
            or raw.get("criterion")
            or raw.get("description")
            or raw.get("title")
            or ""
        ).strip(),
        "contentType": content_type,
        "category": str(raw.get("category") or checklist).strip().lower(),
        "sourceChecklist": str(
            raw.get("sourceChecklist")
            or raw.get("source_checklist")
            or raw.get("source")
            or "toolkit-contract"
        ).strip(),
    }


def load_check_catalog(docs_dir: str | Path | None = None) -> list[dict[str, Any]]:
    """Load check definitions from docs/qualification/*.md and merge with BUILTIN_CHECK_CATALOG."""
    catalog_by_id: dict[str, dict[str, Any]] = {
        entry["id"]: deepcopy(entry) for entry in BUILTIN_CHECK_CATALOG
    }
    ordered_ids: list[str] = [entry["id"] for entry in BUILTIN_CHECK_CATALOG]

    resolved_docs_dir = Path(docs_dir).expanduser().resolve() if docs_dir is not None else DEFAULT_DOCS_DIR
    allow_override_builtin = docs_dir is not None
    if resolved_docs_dir.is_dir():
        for default_checklist, filename in CHECK_DOC_FILENAMES:
            md_path = resolved_docs_dir / filename
            if not md_path.is_file() or md_path.is_symlink():
                continue
            try:
                text = md_path.read_text(encoding="utf-8-sig")
            except Exception:
                continue
            for match in _YAML_CHECK_BLOCK_RE.finditer(text):
                block_text = match.group(1)
                try:
                    parsed = yaml.safe_load(block_text)
                except Exception:
                    continue
                entries: list[Mapping[str, Any]] = []
                if isinstance(parsed, Mapping):
                    entries.append(parsed)
                elif isinstance(parsed, list):
                    entries.extend(item for item in parsed if isinstance(item, Mapping))
                for raw_entry in entries:
                    normalized = _normalize_check_entry(raw_entry, default_checklist=default_checklist)
                    cid = normalized["id"]
                    if not cid:
                        continue
                    if cid in catalog_by_id:
                        if allow_override_builtin:
                            existing = catalog_by_id[cid]
                            for k, v in normalized.items():
                                if v:
                                    existing[k] = v
                    else:
                        catalog_by_id[cid] = normalized
                        ordered_ids.append(cid)

    return [catalog_by_id[cid] for cid in ordered_ids]


def _normalize_rel_path(path_str: str, solution_root: Path) -> str:
    """Normalize a file path (relative to repo root or solution root) into a POSIX path relative to solution_root."""
    cleaned = path_str.strip().replace("\\", "/")
    while cleaned.startswith("./"):
        cleaned = cleaned[2:]
    sol_name = solution_root.name
    prefixes = (
        f"Solutions/{sol_name}/",
        f"{sol_name}/",
    )
    for prefix in prefixes:
        if cleaned.lower().startswith(prefix.lower()):
            cleaned = cleaned[len(prefix) :]
            break
    try:
        candidate = Path(path_str).expanduser()
        if candidate.is_absolute():
            cleaned = candidate.resolve().relative_to(solution_root).as_posix()
    except Exception:
        pass
    return cleaned.strip("/")


def _classify_relative_path(rel_path: str) -> list[str]:
    """Classify a solution-relative POSIX path into one or more canonical content types."""
    norm = rel_path.strip("/").replace("\\", "/")
    if not norm:
        return []
    lower = norm.lower()
    parts = norm.split("/")
    top = parts[0].lower()
    name = parts[-1].lower()
    ext = Path(name).suffix.lower()

    if name in {"migration-config.yaml", "migration-config.yml"}:
        return []

    matched: list[str] = []

    # 1. solution-package
    if (
        name == "solutionmetadata.json"
        or name == "releasenotes.md"
        or (top == "data" and name.startswith("solution_") and ext == ".json")
        or (top == "package" and (name in {"maintemplate.json", "createuidefinition.json"} or ext == ".zip"))
    ):
        matched.append("solution-package")

    # 2. analytic-rules
    if top in {"analytic rules", "analytics rules"} and ext in {".yaml", ".yml"}:
        matched.append("analytic-rules")

    # 3. xdr-detections
    if top == "xdr detections" and ext in {".yaml", ".yml"}:
        matched.append("xdr-detections")

    # 4. workbooks
    if top == "workbooks" and ext == ".json" and "mock" not in name:
        matched.append("workbooks")

    # 5. xdr-workbooks
    if top == "xdr workbooks" and ext == ".json" and "mock" not in name:
        matched.append("xdr-workbooks")

    # 6. data-connectors
    if top in {"data connectors", "dataconnectors"} and not name.startswith("."):
        matched.append("data-connectors")

    # 7. parsers
    if top == "parsers" and ext in {".yaml", ".yml"}:
        matched.append("parsers")

    # 8. hunting-queries
    if top == "hunting queries" and ext in {".yaml", ".yml"}:
        matched.append("hunting-queries")

    # 9. playbooks
    if top == "playbooks" and ext == ".json":
        matched.append("playbooks")

    # 10. notebooks
    if top == "notebooks" and not name.startswith("."):
        matched.append("notebooks")

    # 11. logos
    if ext in {".svg", ".png"} or top in {"logos", "logo", "images"} or "logo" in lower:
        matched.append("logos")

    # 12. sample-data
    if (
        top in {"sample data", "mocks", "mock"}
        or name == "mock.json"
        or (name.endswith(".json") and "mock" in name)
    ):
        matched.append("sample-data")

    return matched


def _has_logo_references_on_disk(solution_root: Path) -> list[str]:
    """Return relative paths of metadata/package files containing logo/svg references."""
    refs: list[str] = []
    candidates: list[Path] = [
        solution_root / "SolutionMetadata.json",
        solution_root / "Package" / "mainTemplate.json",
        solution_root / "Package" / "createUiDefinition.json",
    ]
    data_dir = solution_root / "Data"
    if data_dir.is_dir() and not data_dir.is_symlink():
        candidates.extend(sorted(data_dir.glob("Solution_*.json")))
    for wb_dir in (solution_root / "Workbooks", solution_root / "XDR Workbooks", solution_root / "Data Connectors"):
        if wb_dir.is_dir() and not wb_dir.is_symlink():
            candidates.extend(sorted(wb_dir.rglob("*.json")))

    for path in candidates:
        if not path.is_file() or path.is_symlink():
            continue
        try:
            text = path.read_text(encoding="utf-8-sig")
        except Exception:
            continue
        if re.search(r'"logo"\s*:|"Logo"\s*:|<svg\b|\.svg\b|\.png\b', text):
            refs.append(path.relative_to(solution_root).as_posix())
    return sorted(set(refs))


def detect_solution_content_types(
    solution_path: str | Path,
    changed_files: list[str] | None = None,
) -> dict[str, Any]:
    """Detect all present and changed content types in a solution directory."""
    root = Path(solution_path).expanduser().resolve()
    present_by_type: dict[str, list[str]] = {ct: [] for ct in CONTENT_TYPES}

    if root.is_dir():
        for file_path in sorted(root.rglob("*")):
            if not file_path.is_file() or file_path.is_symlink():
                continue
            rel = file_path.relative_to(root).as_posix()
            # Skip internal log state files except mock.json
            if rel.startswith("Logs/") and not rel.endswith("mock.json"):
                continue
            for ct in _classify_relative_path(rel):
                if rel not in present_by_type[ct]:
                    present_by_type[ct].append(rel)

        logo_ref_files = _has_logo_references_on_disk(root)
        for ref in logo_ref_files:
            if ref not in present_by_type["logos"]:
                present_by_type["logos"].append(ref)

    changed_by_type: dict[str, list[str]] = {ct: [] for ct in CONTENT_TYPES}
    normalized_changed: list[str] = []
    if changed_files is not None:
        for raw_path in changed_files:
            rel = _normalize_rel_path(str(raw_path), root)
            if not rel:
                continue
            normalized_changed.append(rel)
            for ct in _classify_relative_path(rel):
                if rel not in changed_by_type[ct]:
                    changed_by_type[ct].append(rel)
            full = root / rel
            if full.is_file() and not full.is_symlink():
                try:
                    txt = full.read_text(encoding="utf-8-sig")
                    if re.search(r'"logo"\s*:|"Logo"\s*:|<svg\b|\.svg\b|\.png\b', txt):
                        if rel not in changed_by_type["logos"]:
                            changed_by_type["logos"].append(rel)
                except Exception:
                    pass

    present_types = [ct for ct in CONTENT_TYPES if present_by_type[ct]]
    if changed_files is not None:
        active_by_type: dict[str, list[str]] = {ct: list(changed_by_type[ct]) for ct in CONTENT_TYPES}
        # If solution-package or sample-data exists on disk, retain package/sample-data context
        if present_by_type["solution-package"] and not active_by_type["solution-package"]:
            active_by_type["solution-package"] = list(present_by_type["solution-package"])
        if present_by_type["sample-data"] and not active_by_type["sample-data"]:
            active_by_type["sample-data"] = list(present_by_type["sample-data"])
        if present_by_type["logos"] and not active_by_type["logos"] and (
            active_by_type["workbooks"] or active_by_type["xdr-workbooks"] or active_by_type["data-connectors"]
        ):
            active_by_type["logos"] = list(present_by_type["logos"])
        detected_types = [ct for ct in CONTENT_TYPES if active_by_type[ct]]
    else:
        active_by_type = {ct: list(present_by_type[ct]) for ct in CONTENT_TYPES}
        detected_types = list(present_types)

    return {
        "solutionPath": f"Solutions/{root.name}" if root.parent.name == "Solutions" else root.name,
        "solutionName": root.name,
        "detectedContentTypes": detected_types,
        "presentContentTypes": present_types,
        "changedContentTypes": [ct for ct in CONTENT_TYPES if changed_by_type[ct]],
        "filesByContentType": active_by_type,
        "presentFilesByContentType": present_by_type,
        "changedFilesByContentType": changed_by_type,
        "changedFiles": normalized_changed if changed_files is not None else None,
    }


def _has_xdr_detection_migration_provenance(solution_root: Path, rel_paths: Iterable[str]) -> bool:
    """Inspect XDR detection YAML files for migration provenance fields."""
    for rel in rel_paths:
        candidate = solution_root / rel
        if not candidate.is_file() or candidate.is_symlink():
            continue
        try:
            doc = yaml.safe_load(candidate.read_text(encoding="utf-8-sig"))
        except Exception:
            continue
        if not isinstance(doc, Mapping):
            continue
        det_id = str(doc.get("id") or doc.get("ruleId") or "")
        if det_id.lower().startswith("xdr-"):
            return True
        conv = doc.get("conversion")
        if isinstance(conv, Mapping) and (conv.get("sourceRuleId") or conv.get("sourceRulePath")):
            return True
        prov = doc.get("contentProvenance")
        if isinstance(prov, Mapping) and (prov.get("sourceRuleId") or prov.get("sourceRulePath")):
            return True
        if doc.get("sourceRuleId") or doc.get("sourceRulePath"):
            return True
    return False


def _has_xdr_workbook_migration_provenance(solution_root: Path, rel_paths: Iterable[str]) -> bool:
    """Inspect XDR workbook files or decision manifest for migration provenance."""
    for rel in rel_paths:
        wb_name = Path(rel).name
        if (solution_root / "Workbooks" / wb_name).is_file():
            return True
        candidate = solution_root / rel
        if candidate.is_file() and not candidate.is_symlink():
            try:
                raw = json.loads(candidate.read_text(encoding="utf-8-sig"))
                if isinstance(raw, Mapping) and (
                    raw.get("sourceWorkbookPath")
                    or raw.get("migrationProvenance")
                    or isinstance(raw.get("conversion"), Mapping)
                ):
                    return True
            except Exception:
                pass
    manifest_path = solution_root / "Evidence" / "decision-manifest.json"
    if manifest_path.is_file() and not manifest_path.is_symlink():
        try:
            manifest = json.loads(manifest_path.read_text(encoding="utf-8-sig"))
            for dec in manifest.get("decisions") or []:
                if isinstance(dec, Mapping) and str(dec.get("itemId") or "").startswith("XDR "):
                    if dec.get("sourceSha256") and dec.get("targetSha256"):
                        return True
        except Exception:
            pass
    return False


def detect_is_migration(
    solution_path: str | Path,
    changed_files: list[str] | None = None,
    is_migration: bool | None = None,
    *,
    content_info: Mapping[str, Any] | None = None,
) -> tuple[bool, str]:
    """Auto-detect whether a solution PR represents a Sentinel-to-Defender-XDR migration."""
    if is_migration is True:
        return True, "Explicitly marked as Sentinel-to-Defender-XDR migration (is_migration=True)."
    if is_migration is False:
        return False, "Explicitly marked as non-migration solution update (is_migration=False)."

    root = Path(solution_path).expanduser().resolve()
    info = dict(content_info) if content_info is not None else detect_solution_content_types(root, changed_files)
    present = info["presentFilesByContentType"]
    active = info["filesByContentType"]

    xdr_det_files = sorted(set(present.get("xdr-detections", []) + active.get("xdr-detections", [])))
    ar_files = sorted(set(present.get("analytic-rules", []) + active.get("analytic-rules", [])))
    xdr_wb_files = sorted(set(present.get("xdr-workbooks", []) + active.get("xdr-workbooks", [])))
    wb_files = sorted(set(present.get("workbooks", []) + active.get("workbooks", [])))

    if xdr_det_files and ar_files:
        return (
            True,
            f"Detected {len(xdr_det_files)} XDR Detection(s) alongside {len(ar_files)} Sentinel Analytic Rule(s).",
        )
    if xdr_wb_files and wb_files:
        return (
            True,
            f"Detected {len(xdr_wb_files)} XDR Workbook(s) alongside {len(wb_files)} Sentinel Workbook(s).",
        )
    if xdr_det_files and _has_xdr_detection_migration_provenance(root, xdr_det_files):
        return (
            True,
            f"Detected migration provenance (conversion.sourceRuleId / xdr-<GUID>) in {len(xdr_det_files)} XDR Detection(s).",
        )
    if xdr_wb_files and _has_xdr_workbook_migration_provenance(root, xdr_wb_files):
        return (
            True,
            f"Detected migration provenance in {len(xdr_wb_files)} XDR Workbook(s).",
        )
    if xdr_det_files and wb_files:
        return (
            True,
            f"Detected hybrid XDR Detection(s) ({len(xdr_det_files)}) alongside Sentinel Workbook(s) ({len(wb_files)}).",
        )
    if xdr_wb_files and ar_files:
        return (
            True,
            f"Detected hybrid XDR Workbook(s) ({len(xdr_wb_files)}) alongside Sentinel Analytic Rule(s) ({len(ar_files)}).",
        )

    return False, "No Sentinel-to-Defender-XDR migration artifacts or conversion provenance detected."


def _evaluate_single_check_applicability(
    check_def: Mapping[str, Any],
    *,
    active_types: set[str],
    files_by_type: Mapping[str, list[str]],
    is_migration: bool,
    migration_reason: str,
) -> tuple[bool, str]:
    """Determine (applicable, applicabilityReason) for a single check definition."""
    cid = check_def["id"]
    checklist = check_def["checklist"]

    has_ar = "analytic-rules" in active_types
    has_xdr_det = "xdr-detections" in active_types
    has_detections = has_ar or has_xdr_det
    has_wb = "workbooks" in active_types
    has_xdr_wb = "xdr-workbooks" in active_types
    has_workbooks = has_wb or has_xdr_wb
    has_dc = "data-connectors" in active_types
    has_prs = "parsers" in active_types
    has_pkg = "solution-package" in active_types
    has_logos = "logos" in active_types
    has_any_content = bool(active_types)

    # Migration checklist: ONLY active when is_migration=True
    if checklist == "migration":
        if not is_migration:
            return False, f"Not applicable: solution PR is not a migration ({migration_reason})"
        if cid in {"MIG-V01", "MIG-V02", "MIG-V03", "E2E-Q03"}:
            if has_xdr_det:
                return (
                    True,
                    f"Applicable: migration PR includes {len(files_by_type.get('xdr-detections', []))} XDR Detection(s).",
                )
            return (
                False,
                "Not applicable: migration PR contains 0 XDR Detections (workbook-only migration).",
            )
        if cid == "MIG-Q01":
            if has_detections or has_workbooks:
                return (
                    True,
                    "Applicable: migration PR contains dual-surface KQL queries across detections and/or workbooks.",
                )
            return False, "Not applicable: migration PR contains 0 detections or workbooks with KQL queries."
        return True, f"Applicable: migration check ({migration_reason})"

    # Validation checklist
    if cid in {"VAL-CI-01", "E2E-V01"}:
        if has_any_content:
            return True, f"Applicable: solution contains active content types ({', '.join(sorted(active_types))})."
        return False, "Not applicable: no solution content files detected."

    if cid in {"VAL-PKG-01", "VAL-PKG-02", "VAL-PKG-03"}:
        if has_pkg or has_any_content:
            return True, "Applicable: solution package metadata and version hygiene apply to solution PRs."
        return False, "Not applicable: no solution package or content detected."

    if cid == "VAL-PKG-04":
        if has_xdr_det or has_xdr_wb or is_migration:
            return (
                True,
                "Applicable: solution includes Defender XDR content requiring XDR properties in mainTemplate.json.",
            )
        return (
            False,
            "Not applicable: solution contains no XDR Detections or XDR Workbooks requiring XDR mainTemplate properties.",
        )

    if cid in {"VAL-URL-01", "QUAL-URL-01"}:
        if has_pkg or has_logos or has_workbooks or has_dc or has_any_content:
            return True, "Applicable: solution metadata, workbooks, connectors, or logos may contain documentation/logo URLs."
        return False, "Not applicable: no content with URLs detected."

    if cid == "VAL-AR-01":
        if has_detections:
            count = len(files_by_type.get("analytic-rules", [])) + len(files_by_type.get("xdr-detections", []))
            return True, f"Applicable: solution includes {count} detection file(s) (Analytic Rules / XDR Detections)."
        return False, "Not applicable: solution contains 0 Analytic Rules and 0 XDR Detections."

    if cid == "VAL-WB-01":
        if has_workbooks:
            count = len(files_by_type.get("workbooks", [])) + len(files_by_type.get("xdr-workbooks", []))
            return True, f"Applicable: solution includes {count} workbook file(s) (Workbooks / XDR Workbooks)."
        return False, "Not applicable: solution contains 0 Workbooks and 0 XDR Workbooks."

    if cid == "VAL-DC-01":
        if has_dc:
            return (
                True,
                f"Applicable: solution includes {len(files_by_type.get('data-connectors', []))} Data Connector file(s).",
            )
        return False, "Not applicable: solution contains 0 Data Connectors."

    if cid == "VAL-PRS-01":
        if has_prs:
            return (
                True,
                f"Applicable: solution includes {len(files_by_type.get('parsers', []))} Parser file(s).",
            )
        return False, "Not applicable: solution contains 0 Parsers."

    if cid == "E2E-V02":
        if has_detections:
            count = len(files_by_type.get("analytic-rules", [])) + len(files_by_type.get("xdr-detections", []))
            return True, f"Applicable: detection mock data required for {count} packaged detection(s)."
        return False, "Not applicable: solution contains 0 detections requiring detection mock data."

    if cid == "E2E-V03":
        if has_workbooks:
            count = len(files_by_type.get("workbooks", [])) + len(files_by_type.get("xdr-workbooks", []))
            return True, f"Applicable: workbook mock data required for {count} packaged workbook(s)."
        return False, "Not applicable: solution contains 0 workbooks requiring workbook mock data."

    # Qualification checklist
    if cid in {"QUAL-00", "E2E-G01", "QUAL-HR-01"}:
        if has_any_content:
            return True, "Applicable: mandatory qualification gate for solution qualification."
        return False, "Not applicable: no solution content detected."

    if cid == "QUAL-DEP-01":
        if has_pkg or has_detections or has_workbooks or has_dc or has_prs:
            return True, "Applicable: solution package / ARM resources require lab deployment and GET readback."
        return False, "Not applicable: no deployable solution package or ARM content detected."

    if cid == "E2E-Q01":
        if has_detections or has_workbooks:
            return True, "Applicable: live DCR mock data ingestion required for packaged detections and/or workbooks."
        return False, "Not applicable: solution contains 0 detections and 0 workbooks requiring DCR telemetry ingestion."

    if cid == "E2E-Q02":
        if has_detections:
            count = len(files_by_type.get("analytic-rules", [])) + len(files_by_type.get("xdr-detections", []))
            return True, f"Applicable: controlled alert lifecycle & firing required for {count} detection(s)."
        return False, "Not applicable: solution contains 0 Analytic Rules or XDR Detections."

    if cid == "E2E-Q04":
        if has_workbooks:
            count = len(files_by_type.get("workbooks", [])) + len(files_by_type.get("xdr-workbooks", []))
            return True, f"Applicable: live workbook query verification (rowCount > 0) required for {count} workbook(s)."
        return False, "Not applicable: solution contains 0 Workbooks or XDR Workbooks."

    if cid == "E2E-Q05":
        if has_detections or has_workbooks or has_dc:
            return True, "Applicable: portal UI traversal required for user-facing detections, workbooks, or data connectors."
        return False, "Not applicable: solution contains no user-facing portal detections, workbooks, or data connectors."

    if cid == "E2E-Q06":
        if has_logos or has_workbooks or has_dc or has_pkg:
            return True, "Applicable: UI verification of logos, SVG diagrams, and chart visualizations applies."
        return False, "Not applicable: no visual assets, logos, or workbooks detected."

    # Fallback for any check loaded from markdown docs
    declared_types = {
        part.strip()
        for part in str(check_def.get("contentType") or "").split(",")
        if part.strip()
    }
    if cid in {"VAL-RULE-01", "QUAL-RULE-01"}:
        if has_detections or "hunting-queries" in active_types:
            return True, "Applicable: solution contains rules, detections, or hunting queries."
        return False, "Not applicable: solution contains 0 rules, detections, or hunting queries."
    if cid in {"VAL-PARSER-01", "QUAL-PARSER-01"}:
        if has_prs:
            return True, "Applicable: solution contains parsers."
        return False, "Not applicable: solution contains 0 parsers."
    if cid == "VAL-LOGO-01":
        if has_logos:
            return True, "Applicable: solution contains logos."
        return False, "Not applicable: solution contains 0 logos."
    if "all" in declared_types:
        if has_any_content:
            return True, f"Applicable: general check across active content ({', '.join(sorted(active_types))})."
        return False, "Not applicable: no active solution content detected."
    if "workbooks" in declared_types and has_workbooks:
        return True, "Applicable: solution includes Workbooks / XDR Workbooks."
    if declared_types and (declared_types & active_types):
        return True, f"Applicable: matched content type(s) {', '.join(sorted(declared_types & active_types))}."
    return False, f"Not applicable: required content type(s) {', '.join(sorted(declared_types))} not present."


def determine_pr_applicability(
    solution_path: str | Path,
    changed_files: list[str] | None = None,
    is_migration: bool | None = None,
    *,
    docs_dir: str | Path | None = None,
) -> dict[str, Any]:
    """Determine content types, migration mode, and per-check applicability for a solution PR."""
    root = Path(solution_path).expanduser().resolve()
    content_info = detect_solution_content_types(root, changed_files=changed_files)
    migration_flag, migration_reason = detect_is_migration(
        root,
        changed_files=changed_files,
        is_migration=is_migration,
        content_info=content_info,
    )

    catalog = load_check_catalog(docs_dir=docs_dir)
    active_types = set(content_info["detectedContentTypes"])
    files_by_type = content_info["filesByContentType"]

    checks: list[dict[str, Any]] = []
    checks_by_id: dict[str, dict[str, Any]] = {}
    for entry in catalog:
        applicable, reason = _evaluate_single_check_applicability(
            entry,
            active_types=active_types,
            files_by_type=files_by_type,
            is_migration=migration_flag,
            migration_reason=migration_reason,
        )
        enriched = {
            **deepcopy(entry),
            "applicable": applicable,
            "applicabilityReason": reason,
            "defaultStatus": "PENDING" if applicable else "NOT_APPLICABLE",
        }
        checks.append(enriched)
        checks_by_id[enriched["id"]] = enriched

    applicable_ids = [c["id"] for c in checks if c["applicable"]]
    not_applicable_ids = [c["id"] for c in checks if not c["applicable"]]

    return {
        "solutionPath": f"Solutions/{root.name}" if root.parent.name == "Solutions" else root.name,
        "solutionName": root.name,
        "isMigration": migration_flag,
        "migrationReason": migration_reason,
        "detectedContentTypes": content_info["detectedContentTypes"],
        "presentContentTypes": content_info["presentContentTypes"],
        "changedContentTypes": content_info["changedContentTypes"],
        "filesByContentType": content_info["filesByContentType"],
        "presentFilesByContentType": content_info["presentFilesByContentType"],
        "changedFilesByContentType": content_info["changedFilesByContentType"],
        "checks": checks,
        "checksById": checks_by_id,
        "applicableCheckIds": applicable_ids,
        "notApplicableCheckIds": not_applicable_ids,
    }


evaluate_pr_applicability = determine_pr_applicability
