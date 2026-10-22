from __future__ import annotations

import hashlib
import json
import os
import re
import warnings
import uuid
from contextlib import contextmanager
from contextvars import ContextVar
from datetime import datetime, timezone
from pathlib import Path, PureWindowsPath
from typing import Any

import yaml

REPORT_FOLDER_NAME = "sentinel-xdr-migration"
MIGRATION_RECEIPT = "legacy-artifacts.json"
RUN_MARKER = "run.json"
_RUN_SELECTION: ContextVar[tuple[Path, str] | None] = ContextVar("migration_run", default=None)


def reports_base(solution: str | Path) -> Path:
    root = Path(solution).expanduser().resolve()
    base = root / "Logs" / REPORT_FOLDER_NAME
    if (root / "Logs").is_symlink() or base.is_symlink():
        raise ValueError("symlink report directories are not supported")
    return base


def _validate_run_id(run_id: str) -> str:
    if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_.-]{0,95}", run_id):
        raise ValueError("run ID must be a single safe directory name (1-96 characters)")
    return run_id


def new_run_id() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ-") + uuid.uuid4().hex


def select_run(solution: str | Path, run_id: str | None):
    selection = (Path(solution).expanduser().resolve(), _validate_run_id(run_id)) if run_id else None
    return _RUN_SELECTION.set(selection)


def reset_run_selection(token) -> None:
    _RUN_SELECTION.reset(token)


@contextmanager
def using_run(solution: str | Path, run_id: str | None):
    token = select_run(solution, run_id)
    try:
        yield
    finally:
        reset_run_selection(token)


def requested_run_id(solution: str | Path) -> str | None:
    selected = _RUN_SELECTION.get()
    return selected[1] if selected and selected[0] == Path(solution).expanduser().resolve() else None


def list_runs(solution: str | Path) -> list[str]:
    base = reports_base(solution)
    runs = []
    for path in sorted(base.iterdir()) if base.exists() else []:
        if not path.is_dir():
            continue
        if not (path / RUN_MARKER).exists():
            state_path = path / "workflow-state.json"
            state_run = (
                json.loads(state_path.read_text(encoding="utf-8")).get("runId")
                if state_path.is_file() else None
            )
            if state_run == path.name or re.fullmatch(r"\d{8}T\d{6}Z-[0-9a-f]{32}", path.name):
                raise ValueError(f"migration run marker is missing: {path.name}; restore it before resuming")
            continue
        if path.is_symlink() or (path / RUN_MARKER).is_symlink():
            raise ValueError("symlink run directories are not supported")
        marker = json.loads((path / RUN_MARKER).read_text(encoding="utf-8"))
        if marker.get("runId") != _validate_run_id(path.name):
            raise ValueError(f"invalid run identity: {path.name}")
        runs.append(path.name)
    return runs


def _selected_run_id(solution: str | Path) -> str | None:
    selected = requested_run_id(solution)
    runs = list_runs(solution)
    if selected:
        return selected
    if len(runs) > 1:
        raise ValueError("multiple migration runs; specify --run-id: " + ", ".join(runs))
    return runs[0] if runs else None


def create_run(solution: str | Path, *, run_id: str | None = None, migrating: bool = False) -> Path:
    if not migrating and _unmigrated(solution):
        raise ValueError("legacy migration artifacts exist; run migrate-reports --apply before creating a run")
    path = reports_base(solution) / _validate_run_id(run_id or new_run_id())
    path.parent.mkdir(parents=True, exist_ok=True)
    path.mkdir()  # Never overwrite or reuse an unrelated directory.
    (path / RUN_MARKER).write_text(json.dumps({
        "runId": path.name, "createdAt": datetime.now(timezone.utc).isoformat(),
    }, indent=2) + "\n", encoding="utf-8")
    return path


def solution_for_artifact(path: Path) -> Path:
    for parent in path.parents:
        if parent.name == REPORT_FOLDER_NAME and parent.parent.name == "Logs":
            return parent.parent.parent
    raise ValueError("artifact is not inside a solution migration Logs directory")


def repository_root(solution: str | Path) -> Path:
    root = Path(solution).expanduser().resolve()
    return root.parent.parent if root.parent.name.lower() == "solutions" else root.parent


def legacy_directories(solution: str | Path) -> list[Path]:
    root = Path(solution).expanduser().resolve()
    directories = [repository_root(root) / "Reports" / root.name / REPORT_FOLDER_NAME]
    configured = os.getenv("AZURE_SENTINEL_REPORTS_ROOT")
    if configured:
        directories.insert(0, Path(configured).expanduser().resolve() / root.name / REPORT_FOLDER_NAME)
    directories.append(root / "XDR Detections")
    return list(dict.fromkeys(directories))


def _legacy_files(solution: str | Path) -> dict[str, list[Path]]:
    files: dict[str, list[Path]] = {}
    for directory in legacy_directories(solution):
        if directory.is_symlink():
            raise ValueError("symlink legacy report directories are not supported")
        for path in sorted(directory.rglob("*")) if directory.exists() else []:
            if path.is_symlink():
                raise ValueError("symlink legacy reports are not supported")
            if not path.is_file():
                continue
            if directory.name == "XDR Detections":
                if path.suffix.lower() in {".yaml", ".yml"} and path.name.lower() not in {
                    "migration-config.yaml", "migration-config.yml"
                }:
                    continue
            files.setdefault(path.relative_to(directory).as_posix(), []).append(path)
    # A previous flat-Logs migration already superseded some root Reports files.
    # Verify that ledger before treating the newer flat state as authoritative.
    base = reports_base(solution)
    flat_receipt = base / MIGRATION_RECEIPT
    if flat_receipt.exists():
        receipt = json.loads(flat_receipt.read_text(encoding="utf-8"))
        for name in list(files):
            if name in receipt:
                if sorted(_digest(path) for path in files[name]) != receipt[name]:
                    raise ValueError(f"legacy artifact changed after migration: {name}; reconcile explicitly")
                if not (base / name).is_file():
                    raise ValueError(f"migrated flat artifact is missing: {name}")
                del files[name]
    runs = set(list_runs(solution))
    for path in sorted(base.rglob("*")) if base.exists() else []:
        relative = path.relative_to(base)
        if relative.parts[0] in runs or relative.as_posix() == MIGRATION_RECEIPT:
            continue
        if path.is_symlink():
            raise ValueError("symlink legacy reports are not supported")
        if path.is_file():
            files.setdefault(relative.as_posix(), []).append(path)
    return files


def _digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _unmigrated(solution: str | Path) -> dict[str, list[Path]]:
    remaining = _legacy_files(solution)
    # Legacy artifacts belong only to the run that explicitly imported them.
    for run_id in list_runs(solution):
        destination = reports_base(solution) / run_id
        receipt_path = destination / MIGRATION_RECEIPT
        receipt = json.loads(receipt_path.read_text(encoding="utf-8")) if receipt_path.exists() else {}
        for name in list(remaining):
            if name not in receipt:
                continue
            if sorted(_digest(path) for path in remaining[name]) != receipt[name]:
                raise ValueError(f"legacy artifact changed after migration: {name}; reconcile explicitly")
            if not (destination / name).is_file():
                raise ValueError(f"migrated artifact is missing: {name}; restore it before resuming")
            del remaining[name]
    return remaining


def report_directory(solution: str | Path, *, create: bool = False) -> Path:
    root = Path(solution).expanduser().resolve()
    base = reports_base(root)
    selected = _selected_run_id(root)
    if selected and selected not in list_runs(root):
        raise ValueError(f"migration run does not exist: {selected}; initialize a new workflow or migrate reports")
    path = base / selected if selected else base
    if create:
        if _unmigrated(root):
            raise ValueError(
                "legacy migration artifacts exist; run migrate-reports, review the plan, "
                "then migrate-reports --apply before writing solution Logs"
            )
        if selected is None:
            path = create_run(root)
    return path


def artifact_path(solution: str | Path, name: str, *, create_parent: bool = False) -> Path:
    from solution_manager.core.content_paths import content_path

    return content_path(report_directory(solution, create=create_parent), name)


def existing_artifact_path(solution: str | Path, name: str) -> Path:
    preferred = artifact_path(solution, name)
    legacy = _unmigrated(solution).get(name, [])
    candidates = list(dict.fromkeys(([preferred] if preferred.exists() else []) + legacy))
    if len({_digest(path) for path in candidates}) > 1:
        raise ValueError(f"conflicting migration artifacts: {name}; reconcile explicitly")
    if legacy:
        warnings.warn(
            f"reading legacy artifact {name}; run migrate-reports --apply before resuming writes",
            UserWarning,
            stacklevel=2,
        )
    return candidates[0] if candidates else preferred


def existing_artifacts(solution: str | Path, pattern: str) -> list[Path]:
    from fnmatch import fnmatch

    names = set(_unmigrated(solution))
    names.update(path.name for path in report_directory(solution).glob(pattern))
    return [existing_artifact_path(solution, name) for name in sorted(names) if fnmatch(name, pattern)]


def conversion_scope(solution: str | Path) -> dict[str, Any]:
    path = existing_artifact_path(solution, "manifest.json")
    if not path.is_file():
        return {}
    manifest = json.loads(path.read_text(encoding="utf-8-sig"))
    scope = manifest.get("scope", {})
    if not isinstance(scope, dict):
        raise ValueError("conversion manifest scope must be an object")
    return scope


def require_solution_conversion_scope(solution: str | Path) -> None:
    scope = conversion_scope(solution)
    if scope and scope.get("kind") != "solution":
        raise ValueError(
            "rule-scoped conversion is not full-solution readiness; run full-solution "
            "conversion and validation before completing solution stages or packaging"
        )


def migrate_legacy_artifact(solution: str | Path, name: str) -> Path:
    """Compatibility entry point for writers; migration now requires explicit approval."""
    return artifact_path(solution, name, create_parent=True)


def resolve_artifact_reference(solution: str | Path, value: str | Path) -> Path:
    """New persisted references are solution-relative; accept old absolute/repo references."""
    root = Path(solution).expanduser().resolve()
    text = str(value).replace("\\", "/")
    path = Path(text).expanduser()
    if path.is_absolute():
        base = reports_base(root)
        if path.is_relative_to(base):
            relative = path.relative_to(base)
            if relative.parts and relative.parts[0] in list_runs(root):
                if relative.parts[0] != _selected_run_id(root):
                    raise ValueError("artifact belongs to a different migration run")
                return path
            return existing_artifact_path(root, relative.as_posix())
        for directory in legacy_directories(root):
            if path.is_relative_to(directory):
                name = path.relative_to(directory).as_posix()
                if directory.name != "XDR Detections" or name in _legacy_files(root):
                    return existing_artifact_path(root, name)
        return path
    if PureWindowsPath(text).drive:
        raise ValueError("foreign absolute artifact path; migrate reports on the original host first")
    if text.startswith("Solutions/"):
        return resolve_artifact_reference(root, repository_root(root) / path)
    prefix = f"Reports/{root.name}/{REPORT_FOLDER_NAME}/"
    if text.startswith(prefix):
        return existing_artifact_path(root, text[len(prefix):])
    if text.startswith(f"Logs/{REPORT_FOLDER_NAME}/"):
        return resolve_artifact_reference(root, root / path)
    return root / path


_SECRET_KEY = re.compile(
    r"^(?:authorization|access[_-]?token|refresh[_-]?token|id[_-]?token|"
    r"client[_-]?secret|password|accountkey|sharedaccesssignature|sas[_-]?token)$", re.I
)
_SECRET_TEXT = re.compile(
    r"(?i)(\bBearer\s+)[A-Za-z0-9._~+/\-=]+|"
    r"(\b(?:access_token|refresh_token|client_secret|AccountKey|SharedAccessSignature)"
    r"\s*[=:]\s*[\"']?)[^\"'\s;&]+|"
    r"([?&](?:sig|signature|token|access_token|code|se|sp|sv|sr|st|skoid|sktid|skt|ske|sks|skv)=)[^&\s\"'<>]+"
)


def portable_artifact(solution: str | Path, value: Any, *, destination: Path | None = None) -> Any:
    """Normalize known artifact references; never rewrite queries or provider error text."""
    root = Path(solution).expanduser().resolve()
    repository = repository_root(root)
    legacy_names = set(_legacy_files(root))
    destination = destination or report_directory(root)
    destination_reference = destination.relative_to(root).as_posix()
    run_names = set(list_runs(root))
    if destination != reports_base(root):
        run_names.add(destination.name)

    path_fields = {
        "solution", "solutionPath", "output", "outputFile", "file", "sourceFile", "sourceRule",
        "outputDirectory", "reportDirectory", "manifest", "transformationReport",
        "jsonReport", "htmlReport", "reportPath", "statePath", "targetPath",
        "packageReport", "mainTemplate", "createUiDefinition", "testParameters", "zip",
        "solutionData", "contract", "payload", "deploymentReport", "analyticDeploymentReport",
        "queryParityReport", "alertParityReport",
    }
    reference_suffixes = {".json", ".yaml", ".yml", ".zip", ".csv", ".log", ".md", ".txt"}
    literal_containers = {
        "queries", "querycondition", "error", "errors", "errordetails",
        "providererror", "providererrors", "exception", "diagnostic",
        "diagnostics",
    }
    literal_fields = {
        "query", "querytext", "kql", "sourcequery", "targetquery",
        "message", "errormessage", "diagnostictext",
    }

    def looks_like_reference(text: str) -> bool:
        stripped = text.strip()
        if (
            not stripped
            or "\n" in stripped
            or "|" in stripped
            or "://" in stripped
            or "?" in stripped
            or "#" in stripped
        ):
            return False
        return (
            "/" in stripped
            or "\\" in stripped
            or Path(stripped).suffix.lower() in reference_suffixes
            or PureWindowsPath(stripped).suffix.lower() in reference_suffixes
        )

    def is_source_reference(text: str) -> bool:
        stripped = text.strip()
        if not stripped or any(marker in stripped for marker in ("\n", "|", "://", "?", "#")):
            return False
        normalized = stripped.replace("\\", "/")
        known_roots = (
            root.as_posix() + "/",
            repository.as_posix() + "/",
            *(legacy.as_posix() + "/" for legacy in legacy_directories(root)),
        )
        return (
            Path(stripped).suffix.lower() in reference_suffixes
            or PureWindowsPath(stripped).suffix.lower() in reference_suffixes
            or normalized == root.as_posix()
            or normalized.startswith(known_roots)
        )

    def visit(
        item: Any,
        key: str = "",
        references: bool = False,
        parent_key: str = "",
        literal_text: bool = False,
    ) -> Any:
        if isinstance(item, dict):
            child_literal_text = literal_text or key.casefold() in literal_containers
            return {
                name: "[REDACTED]" if _SECRET_KEY.fullmatch(str(name)) else visit(
                    child,
                    str(name),
                    references or key in {"artifacts", "workflowArtifacts"},
                    key,
                    child_literal_text,
                )
                for name, child in item.items()
            }
        if isinstance(item, (list, tuple)):
            return [
                visit(
                    child,
                    key,
                    references or key == "evidence",
                    parent_key,
                    literal_text,
                )
                for child in item
            ]
        if not isinstance(item, str):
            return item
        text = item
        literal_value = (
            literal_text
            or key.casefold() in literal_fields
            or parent_key.casefold() in literal_containers
        )
        source_path = (
            key == "source"
            and not literal_value
            and is_source_reference(text)
        )
        if not literal_value and (
            key in path_fields or source_path or (references and looks_like_reference(text))
        ):
            normalized = text.replace("\\", "/")
            for legacy in legacy_directories(root)[:-1]:
                prefix = legacy.as_posix() + "/"
                if normalized.startswith(prefix):
                    normalized = destination_reference + "/" + normalized[len(prefix):]
            xdr_prefix = (root / "XDR Detections").as_posix() + "/"
            if normalized.startswith(xdr_prefix) and normalized[len(xdr_prefix):] in legacy_names:
                normalized = destination_reference + "/" + normalized[len(xdr_prefix):]
            if normalized == root.as_posix():
                normalized = "."
            elif normalized.startswith(root.as_posix() + "/"):
                normalized = normalized[len(root.as_posix()) + 1:]
            elif normalized.startswith(repository.as_posix() + "/"):
                normalized = os.path.relpath(Path(normalized), root).replace("\\", "/")
            if normalized == f"Logs/{REPORT_FOLDER_NAME}":
                normalized = destination_reference
            legacy_prefixes = (
                f"Logs/{REPORT_FOLDER_NAME}/",
                f"Reports/{root.name}/{REPORT_FOLDER_NAME}/",
                f"../../Reports/{root.name}/{REPORT_FOLDER_NAME}/",
            )
            for prefix in legacy_prefixes:
                if normalized.startswith(prefix):
                    tail = normalized[len(prefix):]
                    if tail.split("/")[0] not in run_names:
                        normalized = destination_reference + "/" + tail
                    break
            text = normalized
        text = _SECRET_TEXT.sub(lambda match: next(group for group in match.groups() if group) + "[REDACTED]", text)
        return text

    return visit(value)


def write_json_artifact(solution: str | Path, path: Path, value: Any) -> None:
    destination = report_directory(solution, create=True)
    if not path.is_relative_to(destination):
        raise ValueError("artifact write must belong to the selected migration run")
    path.write_text(json.dumps(portable_artifact(solution, value), indent=2) + "\n", encoding="utf-8")


def migrate_reports(solution: str | Path, *, apply: bool = False) -> dict[str, Any]:
    """Copy legacy reports with a hash receipt; never move/delete or overwrite user evidence."""
    root = Path(solution).expanduser().resolve()
    selected = _selected_run_id(root)
    destination = reports_base(root) / (selected or new_run_id())
    legacy = _unmigrated(root)
    if selected and selected not in list_runs(root) and not legacy:
        raise ValueError(f"no unmigrated artifacts for requested run: {selected}")
    prepared: dict[str, bytes] = {}
    for name, paths in legacy.items():
        if name in {MIGRATION_RECEIPT, RUN_MARKER}:
            raise ValueError("reserved migration receipt name in legacy artifacts")
        if len({_digest(path) for path in paths}) != 1:
            raise ValueError(f"conflicting legacy artifacts: {name}")
        source = paths[0]
        content = source.read_bytes()
        if source.suffix.lower() == ".json":
            document = portable_artifact(root, json.loads(content.decode("utf-8-sig")), destination=destination)
            if name == "workflow-state.json":
                if document.get("runId") not in (None, destination.name):
                    raise ValueError("legacy workflow belongs to another run; reconcile explicitly")
                document["runId"] = destination.name
            text = json.dumps(document, indent=2) + "\n"
            content = text.encode("utf-8")
        elif source.suffix.lower() in {".yaml", ".yml"}:
            # Configuration must retain its exact semantics, including KQL.
            text = content.decode("utf-8-sig")
            safe = portable_artifact(root, yaml.safe_load(text), destination=destination)
            if safe != yaml.safe_load(text):
                raise ValueError(f"legacy configuration needs manual portable/credential review: {name}")
        from solution_manager.core.content_paths import content_path
        target = content_path(destination, name)
        if target.exists() and target.read_bytes() != content:
            raise ValueError(f"conflicting migration artifacts: {name}; reconcile explicitly")
        prepared[name] = content
    if apply and prepared:
        if destination.name not in list_runs(root):
            create_run(root, run_id=destination.name, migrating=True)
        receipt_path = destination / MIGRATION_RECEIPT
        receipt = json.loads(receipt_path.read_text()) if receipt_path.exists() else {}
        for name, content in prepared.items():
            target = content_path(destination, name)
            target.parent.mkdir(parents=True, exist_ok=True)
            if not target.exists():
                target.write_bytes(content)
            receipt[name] = sorted(_digest(path) for path in legacy[name])
        receipt_path.write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
    return {"mode": "applied" if apply else "dry-run", "files": sorted(prepared),
            "runId": destination.name, "destination": destination.relative_to(root).as_posix(),
            "originalsPreserved": True}
