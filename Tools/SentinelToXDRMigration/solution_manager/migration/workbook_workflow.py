from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from solution_manager.core.artifacts import (
    existing_artifact_path,
    report_directory,
    resolve_artifact_reference,
)
from solution_manager.core.content_paths import content_path


CAPABILITY_VERSION = 1
ARM_VALIDATION_METHODS = ("arm-ttk", "lab-deployment")
DEFAULT_ARM_VALIDATION_METHOD = "lab-deployment"


def default_arm_validation_method(workflow_profile: str = "authoring") -> str:
    if workflow_profile not in ("authoring", "qualification"):
        raise ValueError(f"unsupported workflow profile: {workflow_profile}")
    return DEFAULT_ARM_VALIDATION_METHOD


def enabled(state: dict[str, Any]) -> bool:
    return state.get("context", {}).get("workbookCapabilityVersion") == CAPABILITY_VERSION


def has_analytic_rules(solution: str | Path) -> bool:
    root = Path(solution).expanduser().resolve()
    from solution_manager.migration.converter import analytic_rule_files

    return (
        any((root / name).is_dir() for name in ("Analytic Rules", "Analytics Rules"))
        and bool(analytic_rule_files(root))
    )


def _digest(value: Any) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest()


def _inventory(solution: Path) -> list[dict[str, str]]:
    from solution_manager.migration.workbooks import inventory_workbooks

    rows = inventory_workbooks(solution)
    inventory = [
        {"path": row["path"], "sha256": row["sha256"]}
        for row in rows
    ]
    inventory.sort(key=lambda row: row["path"])
    if len({row["path"] for row in inventory}) != len(inventory):
        raise ValueError("workbook inventory contains duplicate source paths")
    return inventory


def _data(solution: Path) -> tuple[Path, dict[str, Any]]:
    from solution_manager.packaging.packaging import _read_json, _solution_data_file

    path = _solution_data_file(solution / "Data")
    return path, _read_json(path)


def selected_workbook_references(
    solution: str | Path,
    document: dict[str, Any] | None = None,
    *,
    require_existing: bool = True,
) -> list[Path]:
    root = Path(solution).expanduser().resolve()
    from solution_manager.packaging.packaging import _solution_relative_reference

    if document is None:
        _, document = _data(root)
    keys = [key for key in document if key.casefold() == "xdr workbooks"]
    if len(keys) > 1:
        raise ValueError("solution Data has duplicate XDR Workbooks selection keys")
    if not keys:
        return []
    references = document[keys[0]]
    if isinstance(references, str):
        references = json.loads(references)
    if not isinstance(references, list) or any(
        not isinstance(reference, str) or not reference.strip()
        for reference in references
    ):
        raise ValueError("solution Data XDR Workbooks must be a content-reference array")
    paths = []
    for reference in references:
        if require_existing:
            path = _solution_relative_reference(root, reference, "XDR Workbooks")
        else:
            normalized = reference.replace("\\", "/")
            parts = normalized.split("/")
            if parts[:2] == ["Solutions", root.name]:
                normalized = "/".join(parts[2:])
            path = content_path(root, normalized)
        paths.append(path)
    if len(set(paths)) != len(paths):
        raise ValueError("solution Data selects the same Defender workbook more than once")
    for path in paths:
        if not path.is_relative_to(root / "XDR Workbooks") or path.suffix.lower() != ".json":
            raise ValueError("XDR Workbooks selections must reference authored workbook JSON")
    return paths


def freeze_inventory(solution: str | Path) -> dict[str, Any]:
    root = Path(solution).expanduser().resolve()
    inventory = _inventory(root)
    included = [row["path"] for row in inventory]
    excluded: list[dict[str, str]] = []
    explicit_selection = False
    if (root / "Data").is_dir():
        _, document = _data(root)
        if any(key.casefold() == "xdr workbooks" for key in document):
            explicit_selection = True
            included = []
            known_sources = {row["path"] for row in inventory}
            for path in selected_workbook_references(root, document):
                target = json.loads(path.read_text(encoding="utf-8-sig"))
                source = target.get("contentProvenance", {}).get("source", {}).get("path")
                if source not in known_sources or source in included:
                    raise ValueError("explicit workbook selection does not match the source inventory")
                expected_output = root / "XDR Workbooks" / source.removeprefix("Workbooks/")
                if path != expected_output:
                    raise ValueError("explicit workbook selection must preserve the original relative workbook path")
                included.append(source)
            excluded = [
                {"path": row["path"], "reason": "Excluded by the explicit solution Data selection."}
                for row in inventory
                if row["path"] not in included
            ]
    selection = {"included": sorted(included), "excluded": excluded}
    return {
        "schemaVersion": "1.0.0",
        "inventory": inventory,
        "inventorySha256": _digest(inventory),
        "selection": selection,
        "selectionSha256": _digest(selection),
        "selectionExplicit": explicit_selection,
    }


def verify_inventory(solution: str | Path, state: dict[str, Any]) -> None:
    if not enabled(state):
        return
    frozen = state["workbooks"]
    current = _inventory(Path(solution).expanduser().resolve())
    if current != frozen["inventory"] or _digest(current) != frozen["inventorySha256"]:
        raise ValueError(
            "frozen workbook inventory changed; preserve this run and initialize a new run"
        )
    selection = frozen["selection"]
    if _digest(selection) != frozen["selectionSha256"]:
        raise ValueError("frozen workbook selection changed; initialize a new run")
    included = selection["included"]
    excluded = [row["path"] for row in selection["excluded"]]
    if (
        len(set(included + excluded)) != len(included + excluded)
        or set(included + excluded) != {row["path"] for row in current}
        or any(not row["reason"].strip() for row in selection["excluded"])
    ):
        raise ValueError("workbook selection must account for the entire frozen inventory")
    root = Path(solution).expanduser().resolve()
    if (root / "Data").is_dir():
        _, document = _data(root)
        present = any(key.casefold() == "xdr workbooks" for key in document)
        if present:
            expected = {root / "XDR Workbooks" / reference.removeprefix("Workbooks/")
                        for reference in included}
            if set(selected_workbook_references(
                root, document,
                require_existing=state["stages"]["conversion"]["status"] == "passed",
            )) != expected:
                raise ValueError("solution Data workbook selection differs from the frozen run selection")
        elif frozen["selectionExplicit"] or (
            current and state["stages"]["conversion"]["status"] == "passed"
        ):
            raise ValueError("the frozen explicit workbook selection cannot be removed")


def bind_conversion(
    solution: str | Path,
    state: dict[str, Any],
) -> dict[str, str]:
    if not enabled(state):
        return {}
    verify_inventory(solution, state)
    if not state["workbooks"]["inventory"]:
        return {}
    root = Path(solution).expanduser().resolve()
    path = report_directory(root) / "workbooks-manifest.json"
    manifest = json.loads(path.read_text(encoding="utf-8-sig"))
    inventory = {row["path"]: row["sha256"] for row in state["workbooks"]["inventory"]}
    results = manifest.get("results")
    if (
        not isinstance(results, list)
        or any(not isinstance(row, dict) for row in results)
        or len(results) != len(inventory)
        or {row.get("sourceRelativePath") for row in results} != set(inventory)
    ):
        raise ValueError("workbook conversion manifest must retain the complete frozen inventory")
    for row in results:
        if row.get("sourceSha256") != inventory[row["sourceRelativePath"]]:
            raise ValueError("workbook conversion manifest has stale source evidence")
        if row.get("outputRelativePath"):
            output = content_path(root, row["outputRelativePath"])
            if (
                not output.is_relative_to(root / "XDR Workbooks")
                or not output.is_file()
                or hashlib.sha256(output.read_bytes()).hexdigest() != row.get("outputSha256")
            ):
                raise ValueError("workbook conversion manifest has stale target evidence")
            if row.get("status") == "converted":
                authored = json.loads(output.read_bytes())
                provenance = authored.get("contentProvenance") or {}
                conversion = provenance.get("conversion") or {}
                if (
                    provenance.get("source", {}).get("path") != row["sourceRelativePath"]
                    or conversion.get("queries") != row.get("queries")
                    or conversion.get("reviewRequired") != row.get("reviewRequired")
                    or row.get("managedOutputSha256") != row.get("outputSha256")
                ):
                    raise ValueError("workbook manifest per-query review evidence differs from the current authored bytes")
                if row["sourceRelativePath"] in state["workbooks"]["selection"]["included"]:
                    from solution_manager.authoring.workbook_functions import validate_functions
                    validate_functions(root, provenance.get("requiredWorkspaceFunctions", []))
    binding = {
        "workbookManifest": path.relative_to(root).as_posix(),
        "workbookManifestSha256": hashlib.sha256(path.read_bytes()).hexdigest(),
        "workbookSelectionSha256": _digest(state["workbooks"]["selection"]),
    }
    function_records = []
    for row in results:
        if row["sourceRelativePath"] in state["workbooks"]["selection"]["included"] and row.get("outputRelativePath"):
            authored = json.loads(content_path(root, row["outputRelativePath"]).read_bytes())
            records = authored.get("contentProvenance", {}).get("requiredWorkspaceFunctions", [])
            if records:
                function_records.append({"workbook": row["sourceRelativePath"], "functions": records})
    if function_records:
        binding["workbookFunctionDependenciesSha256"] = _digest(function_records)
    return binding


def validate_evidence(solution: str | Path, state: dict[str, Any]) -> dict[str, Any]:
    if not enabled(state):
        return {"total": 0, "valid": 0, "invalid": 0, "results": []}
    root = Path(solution).expanduser().resolve()
    current = bind_conversion(root, state)
    recorded = state["stages"]["conversion"].get("artifacts") or {}
    if any(current[key] != recorded.get(key) for key in current):
        raise ValueError("workbook conversion evidence is missing, changed, or bound to another selection")
    included = state["workbooks"]["selection"]["included"]
    if not state["workbooks"]["inventory"]:
        return {"total": 0, "valid": 0, "invalid": 0, "results": []}
    manifest_path = resolve_artifact_reference(root, current["workbookManifest"])
    manifest = json.loads(manifest_path.read_text(encoding="utf-8-sig"))
    selected = [
        row for row in manifest["results"] if row["sourceRelativePath"] in included
    ]
    if any(
        row.get("status") != "converted" or row.get("reviewRequired") is not False
        for row in selected
    ):
        raise ValueError("selected workbooks have unresolved conversion or review blockers")
    expected = {content_path(root, row["outputRelativePath"]) for row in selected}
    if set(selected_workbook_references(root)) != expected:
        raise ValueError("solution Data workbook selection differs from the frozen reviewed selection")
    from solution_manager.migration.workbooks import validate_workbooks

    result = validate_workbooks(root, selected_only=True)
    from solution_manager.authoring.workbook_publication import is_public, publication_errors
    for path in selected_workbook_references(root):
        document = json.loads(path.read_bytes())
        if is_public(document):
            blockers = publication_errors(root, document)
            if blockers:
                raise ValueError("; ".join(blockers))
    if (
        result.get("total") != len(selected)
        or result.get("valid") != len(selected)
        or result.get("invalid") != 0
        or len(result.get("results") or []) != len(selected)
        or any(row.get("valid") is not True for row in result.get("results") or [])
    ):
        raise ValueError("selected workbooks must individually pass current structural validation")
    return result


def inspect_content(solution: str | Path) -> dict[str, Any]:
    from solution_manager.migration.converter import inspect_solution
    from solution_manager.migration.workbooks import inventory_workbooks

    root = Path(solution).expanduser().resolve()
    state = current_state(root)
    if not state or not enabled(state):
        return inspect_solution(root)
    verify_inventory(root, state)
    result = inspect_solution(root) if has_analytic_rules(root) else {
        "solution": str(root), "analyticRuleCount": 0, "analyticRules": [],
        "existingXdrDetectionCount": 0,
    }
    inventory = inventory_workbooks(root)
    return {**result, "workbookCount": len(inventory),
            "workbookQueryCount": sum(len(row["queries"]) for row in inventory),
            "workbooks": inventory, "workbookSelection": state["workbooks"]["selection"]}


def convert_content(solution: str | Path, *, overwrite: bool = False,
                    config_path: str | Path | None = None,
                    rule_id: str | None = None,
                    overwrite_workbooks: bool = False) -> dict[str, Any]:
    from solution_manager.migration.converter import convert_solution, load_config
    from solution_manager.migration.workbooks import convert_workbooks

    root = Path(solution).expanduser().resolve()
    state = current_state(root)
    if not state or not enabled(state):
        if overwrite_workbooks:
            raise ValueError("--overwrite-workbooks requires a workbook-capable frozen workflow run.")
        return convert_solution(root, overwrite=overwrite, config_path=config_path, rule_id=rule_id)
    verify_inventory(root, state)
    if rule_id:
        if overwrite_workbooks:
            raise ValueError("--overwrite-workbooks cannot be combined with rule-scoped conversion.")
        # Rule-scoped repairs must never rewrite workbook evidence or selection.
        return convert_solution(root, overwrite=overwrite, config_path=config_path, rule_id=rule_id)
    from solution_manager.packaging.packaging import solution_data_version, validate_v31_effective_version, validate_v31_target_version
    selected_version = state["context"].get("targetVersion")
    bump = state["context"].get("versionBump")
    if state["workbooks"]["inventory"] and (selected_version is not None or bump is not None):
        selected_version = validate_v31_effective_version(
            solution_data_version(root), bump or "none", selected_version,
        )
    config = load_config(root / "XDR Detections", config_path) if state["workbooks"]["inventory"] else {}
    if "targetVersion" in config:
        validate_v31_target_version(config["targetVersion"])
    if selected_version and config.get("targetVersion") not in (None, selected_version):
        raise ValueError("workbook targetVersion conflicts with the selected solution release")
    result = convert_solution(root, overwrite=overwrite, config_path=config_path) if has_analytic_rules(root) else {
        "solution": str(root), "total": 0, "converted": 0, "blocked": 0, "results": [],
        "needsReview": 0, "conflicts": 0,
    }
    if not state["workbooks"]["inventory"]:
        return {**result, "workbooks": {"total": 0, "converted": 0, "blocked": 0,
                                       "selectedBlocked": 0, "results": []},
                "workbookArtifacts": {}, "workbookExcluded": []}
    if selected_version is None:
        current_version = solution_data_version(root)
        try:
            selected_version = validate_v31_effective_version(current_version, "none")
        except ValueError:
            # Older solution releases are not silently promoted by workbook conversion.
            pass
    if selected_version:
        if config.get("targetVersion") not in (None, selected_version):
            raise ValueError("workbook targetVersion conflicts with the selected solution release")
        config["targetVersion"] = selected_version
    workbook_result = convert_workbooks(root, config=config,
                                       report_directory=report_directory(root),
                                       overwrite=overwrite or overwrite_workbooks)
    binding = bind_conversion(root, state)
    manifest = json.loads(Path(workbook_result["manifestPath"]).read_bytes())
    selected_sources = set(state["workbooks"]["selection"]["included"])
    selected_rows = [row for row in manifest["results"] if row["sourceRelativePath"] in selected_sources]
    workbook_result["selectedBlocked"] = sum(
        row.get("status") != "converted" or row.get("reviewRequired") is not False
        for row in selected_rows
    )
    data_path, data = _data(root)
    if not any(key.casefold() == "xdr workbooks" for key in data):
        # Preserve blocked sources in the selection; validation must reject them.
        data["XDR Workbooks"] = [row["outputRelativePath"] for row in selected_rows]
        from solution_manager.core.workflow import _atomic_json
        _atomic_json(data_path, data)
    expected = {content_path(root, row["outputRelativePath"]) for row in selected_rows}
    if set(selected_workbook_references(root)) != expected:
        raise ValueError("edited workbook selection conflicts with the frozen run selection")
    return {**result, "workbooks": workbook_result, "workbookArtifacts": binding,
            "workbookExcluded": state["workbooks"]["selection"]["excluded"]}


def validate_content(solution: str | Path) -> dict[str, Any]:
    from solution_manager.migration.converter import validate_solution

    root = Path(solution).expanduser().resolve()
    state = current_state(root)
    if not state or not enabled(state):
        return validate_solution(root)
    verify_inventory(root, state)
    result = validate_solution(root) if has_analytic_rules(root) else {
        "solution": str(root), "total": 0, "valid": 0, "invalid": 0, "results": [],
    }
    workbook_result = validate_evidence(root, state)
    return {**result, "workbooks": workbook_result,
            "workbookExcluded": state["workbooks"]["selection"]["excluded"]}


def _context(state: dict[str, Any]) -> dict[str, Any]:
    if not enabled(state) or not state.get("runId"):
        raise ValueError("candidate lifecycle requires an explicitly selected workbook-capable run")
    context = {**state["context"], "runId": state["runId"]}
    if context.get("workspaceResourceId"):
        from solution_manager.core.target_context import workspace_identity
        context["resourceGroup"] = workspace_identity(context["workspaceResourceId"])["resourceGroup"]
    return context


def _plan_target(plan: dict[str, Any]) -> dict[str, Any]:
    target = dict(plan["target"])
    if plan.get("parameters", {}).get("workspace-location"):
        target["workspaceLocation"] = plan["parameters"]["workspace-location"]
    return target


def _read_run_json(solution: str | Path, name: str) -> dict[str, Any]:
    path = existing_artifact_path(solution, name)
    if path.is_symlink() or not path.is_file():
        raise ValueError(f"selected run is missing {name}")
    value = json.loads(path.read_text(encoding="utf-8-sig"))
    if not isinstance(value, dict):
        raise ValueError(f"invalid selected-run artifact: {name}")
    return value


def _write_run_json(solution: str | Path, name: str, value: dict[str, Any]) -> Path:
    from solution_manager.core.artifacts import artifact_path
    from solution_manager.core.workflow import _atomic_json
    path = artifact_path(solution, name, create_parent=True)
    _atomic_json(path, value)
    return path


def create_candidate(solution: str | Path, *, validation_receipt: str | Path | None = None,
                     toolkit_root: str | Path | None = None) -> dict[str, Any]:
    """Produce gates only after deterministic checks, and verify the official receipt."""
    import shutil
    import subprocess
    import uuid
    from solution_manager.core import workflow
    from solution_manager.core.artifacts import repository_root
    from solution_manager.packaging.packaging import package_input_identity, _read_json, _verify_workbook_package
    from solution_manager.authoring.workbook_validation import create_arm_candidate

    root = Path(solution).expanduser().resolve()
    with workflow._state_writer_lock(root) as state_path:
        state = workflow._load(root)[1]
        context = _context(state)
        verify_inventory(root, state)
        validate_evidence(root, state)
        if state["stages"]["conversion"]["status"] != "passed" or state["stages"]["validation"]["status"] != "passed":
            raise ValueError("candidate creation requires passed conversion and content validation")
        if context["workflowProfile"] == "authoring":
            workflow._validate_offline_authoring_gates(root, state_path, state)
        else:
            if has_analytic_rules(root):
                from solution_manager.qualification.runtime import current_runtime_evidence
                if current_runtime_evidence(root).get("passed") is not True:
                    raise ValueError("combined Qualification still requires all current detection runtime gates")
            elif context.get("workbookQualificationAfterArm") is not True:
                from solution_manager.qualification.workbook_qualification import require_current_qualification
                require_current_qualification(root, state)
        artifacts = state["stages"]["packaging"].get("artifacts") or {}
        workflow._validate_packaging_evidence(state, artifacts, root, allow_candidate=True)
        report_path = resolve_artifact_reference(root, artifacts["packageReport"])
        report = _read_json(report_path)
        template = _read_json(resolve_artifact_reference(root, report["mainTemplate"]))
        _verify_workbook_package(root, selected_workbook_references(root), template,
                                 resolve_artifact_reference(root, report["zip"]))
        current = package_input_identity(root)
        if report["packageInputs"]["after"]["sha256"] != current["sha256"]:
            raise ValueError("candidate package input identity is stale")
        official_report = None
        if validation_receipt is None:
            toolkit = Path(toolkit_root).expanduser().resolve() if toolkit_root else repository_root(root)
            script = toolkit / ".script" / "local-validation" / "build-and-validate.ps1"
            pwsh = shutil.which("pwsh")
            if not pwsh or not script.is_file():
                raise ValueError("candidate validation requires the official build-and-validate producer and PowerShell 7")
            evidence = toolkit / ".script" / "local-validation" / "Logs" / f"candidate-{state['runId']}-{uuid.uuid4().hex}"
            command = [pwsh, "-NoProfile", "-File", str(script), "-SolutionName", root.name,
                       "-ContentRoot", str(repository_root(root)), "-EvidenceDirectory", str(evidence),
                       "-SkipPackaging", "-PackageReportPath", str(report_path),
                       "-ValidationSkip", "kql,detection-schema,non-ascii",
                       "-ArmValidationMethod", context["armValidationMethod"]]
            completed = subprocess.run(command, cwd=toolkit, capture_output=True, text=True, check=False)
            official_report = completed.stdout
            if completed.returncode:
                raise RuntimeError(f"official candidate static validation failed ({completed.returncode}): {completed.stdout[-4000:]}\n{completed.stderr[-1000:]}")
            validation_receipt = evidence / "build-and-validate-report.md"
            if not validation_receipt.is_file() and evidence.is_dir():
                nested_receipts = sorted(evidence.glob("*/build-and-validate-report.md"))
                if len(nested_receipts) == 1:
                    validation_receipt = nested_receipts[0]
        gate_names = ["conversion", "review", "structure", "package"]
        if context["workflowProfile"] == "qualification" and context.get("workbookQualificationAfterArm") is not True:
            gate_names.append("qualification")
        gates = {}
        for name in gate_names:
            gate = {
                "status": "passed", "gate": name, "workflowRunId": state["runId"],
                "packageInputSha256": current["sha256"],
                "checks": {
                    "conversion": "current full source inventory and hash-bound conversion",
                    "review": "selected outputs have no unresolved technical/dependency/query review findings",
                    "structure": "current deterministic content structure and full package workbook projection",
                    "package": "V3.1 current attempt artifacts, selections and ZIP",
                    "qualification": "Existing detection runtime prerequisites; workbook query/UI qualification remains post-ARM.",
                }[name],
            }
            if name in {"structure", "package"}:
                gate["packageArtifactsSha256"] = report["packageArtifactsSha256"]
            if name == "qualification":
                from solution_manager.core.target_context import workspace_identity
                gate["qualificationRuntimeVerified"] = True
                gate["target"] = {key: context[key] for key in
                                  ("tenantId", "subscriptionId", "workspaceResourceId", "workspaceCustomerId")}
                gate["target"]["resourceGroup"] = workspace_identity(context["workspaceResourceId"])["resourceGroup"]
            gate_path = _write_run_json(root, f"arm-candidate-gate-{name}.json", gate)
            gates[name] = {"path": gate_path.relative_to(root).as_posix(),
                           "sha256": hashlib.sha256(gate_path.read_bytes()).hexdigest()}
        candidate = create_arm_candidate(context, solution=root, package_report=report_path.relative_to(root).as_posix(),
                                         validation_receipt=validation_receipt, prerequisite_evidence=gates)
        candidate_path = _write_run_json(root, "arm-candidate.json", candidate)
        state["stages"]["packaging"]["artifacts"].update({
            "armCandidate": str(candidate_path),
            "armCandidateSha256": hashlib.sha256(candidate_path.read_bytes()).hexdigest(),
        })
        workflow._write_unlocked(state_path, state)
        preflight_summary = build_lab_deployment_preflight_prompt(root, state=state)
        return {
            **candidate,
            "candidatePath": str(candidate_path),
            "officialReport": official_report,
            "expectedContentCounts": preflight_summary["expectedContentCounts"],
            "labDeploymentPreflightPrompt": preflight_summary["labDeploymentPreflightPrompt"],
        }


def expected_content_counts(
    solution: str | Path,
    state: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Compute expected content counts (Sentinel rules, workbooks breakdown, custom detections)."""
    from solution_manager.migration.converter import analytic_rule_files, xdr_detection_files
    from solution_manager.packaging.packaging_selection import current_applied_package_selection

    root = Path(solution).expanduser().resolve()
    if state is None:
        state = current_state(root)

    data_doc: dict[str, Any] = {}
    if (root / "Data").is_dir():
        try:
            _, data_doc = _data(root)
        except Exception:
            data_doc = {}

    def _data_list(field_name: str) -> list[str] | None:
        for key, value in data_doc.items():
            if key.casefold() == field_name.casefold():
                if isinstance(value, str):
                    try:
                        value = json.loads(value)
                    except json.JSONDecodeError:
                        return None
                if isinstance(value, list):
                    return [str(item).strip() for item in value if isinstance(item, str) and str(item).strip()]
        return None

    applied_selection = current_applied_package_selection(root)
    selected_plan = applied_selection["plan"] if isinstance(applied_selection, dict) and isinstance(applied_selection.get("plan"), dict) else None

    if selected_plan and isinstance(selected_plan.get("selectedAnalyticRules"), list):
        sentinel_rules_count = len(selected_plan["selectedAnalyticRules"])
    else:
        data_rules = _data_list("Analytic Rules") or _data_list("Analytics Rules")
        if data_rules is not None:
            sentinel_rules_count = len(data_rules)
        elif has_analytic_rules(root):
            sentinel_rules_count = len(analytic_rule_files(root))
        else:
            sentinel_rules_count = 0

    if selected_plan and isinstance(selected_plan.get("selectedXdrDetections"), list):
        custom_detections_count = len(selected_plan["selectedXdrDetections"])
    else:
        data_xdr_det = _data_list("XDR Detections")
        if data_xdr_det is not None:
            custom_detections_count = len(data_xdr_det)
        elif (root / "XDR Detections").is_dir():
            custom_detections_count = len(xdr_detection_files(root))
        else:
            custom_detections_count = 0

    data_wb = _data_list("Workbooks")
    if data_wb is not None:
        sentinel_workbooks_count = len(data_wb)
    elif state and enabled(state):
        sentinel_workbooks_count = len(state["workbooks"]["inventory"])
    else:
        try:
            sentinel_workbooks_count = len(_inventory(root))
        except Exception:
            sentinel_workbooks_count = 0

    data_xdr_wb = _data_list("XDR Workbooks")
    if state and enabled(state):
        defender_workbooks_count = len(state["workbooks"]["selection"]["included"])
    elif data_xdr_wb is not None:
        defender_workbooks_count = len(data_xdr_wb)
    elif (root / "XDR Workbooks").is_dir():
        defender_workbooks_count = sum(
            1 for path in (root / "XDR Workbooks").rglob("*.json") if path.is_file()
        )
    else:
        defender_workbooks_count = 0

    workbooks_count = sentinel_workbooks_count + defender_workbooks_count
    return {
        "sentinelRulesCount": sentinel_rules_count,
        "workbooksCount": workbooks_count,
        "sentinelWorkbooksCount": sentinel_workbooks_count,
        "defenderWorkbooksCount": defender_workbooks_count,
        "workbooksBreakdown": {
            "sentinel": sentinel_workbooks_count,
            "defender": defender_workbooks_count,
        },
        "customDetectionsCount": custom_detections_count,
    }


def build_lab_deployment_preflight_prompt(
    solution: str | Path,
    *,
    state: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Build preflight preapproval summary for deploying solution ARM templates to the lab."""
    root = Path(solution).expanduser().resolve()
    if state is None:
        state = current_state(root)
    counts = expected_content_counts(root, state=state)
    x = counts["sentinelRulesCount"]
    y = counts["workbooksCount"]
    z = counts["customDetectionsCount"]
    prompt = (
        "Requesting preflight preapproval to deploy the solution ARM templates to the "
        "selected non-production lab to verify ARM template deployment validity "
        f"(expected content items: {x} Sentinel rules, {y} workbooks, and {z} custom detections). "
        "Deployment verification alone does not establish functional/runtime qualification or alert parity."
    )
    method = (
        (state or {}).get("context", {}).get("armValidationMethod")
        or default_arm_validation_method((state or {}).get("context", {}).get("workflowProfile", "authoring"))
    )
    return {
        "schemaVersion": 1,
        "armValidationMethod": method,
        "defaultArmValidationMethod": DEFAULT_ARM_VALIDATION_METHOD,
        "skipsArmTtk": method == "lab-deployment",
        "expectedContentCounts": counts,
        "labDeploymentPreflightPrompt": prompt,
        "functionalQualificationVerified": False,
        "alertParityVerified": False,
    }


def plan_lab_deployment_preflight(
    solution: str | Path,
    *,
    run_id: str | None = None,
    persist: bool = True,
) -> dict[str, Any]:
    """Compute and optionally persist the lab deployment preflight preapproval artifact."""
    from solution_manager.core.artifacts import using_run

    root = Path(solution).expanduser().resolve()
    with using_run(root, run_id):
        state = current_state(root)
        payload = build_lab_deployment_preflight_prompt(root, state=state)
        if state and state.get("runId"):
            payload["runId"] = state["runId"]
            if persist:
                path = _write_run_json(root, "arm-deployment-preflight.json", payload)
                payload["preflightPromptPath"] = path.relative_to(root).as_posix()
        return payload


def record_lab_deployment_validation_findings(
    solution: str | Path,
    result: dict[str, Any],
    *,
    candidate: dict[str, Any] | None = None,
    plan: dict[str, Any] | None = None,
    run_id: str | None = None,
) -> dict[str, Any]:
    """Record lab deployment validation findings (including failures and target/artifact bindings) as durable workflow evidence."""
    from solution_manager.core.artifacts import using_run
    from solution_manager.core import workflow
    root = Path(solution).expanduser().resolve()
    with using_run(root, run_id):
        state = current_state(root)
        if candidate is None:
            try:
                candidate = _read_run_json(root, "arm-candidate.json")
            except Exception:
                candidate = {}
        if plan is None:
            try:
                plan = _read_run_json(root, "arm-validation-plan.json")
            except Exception:
                plan = {}

        status = str(result.get("status") or "unknown")
        prov_state = str(result.get("provisioningState") or "").strip()
        if status == "arm-accepted-contract-pending" or prov_state.casefold() == "succeeded":
            outcome = "passed"
        elif status in {"failed", "unknown"} or prov_state.casefold() in {"failed", "canceled"}:
            outcome = "failed"
        else:
            outcome = "blocked"

        findings: list[dict[str, Any]] = []
        for reason in result.get("reasons") or []:
            if isinstance(reason, str) and reason.strip():
                findings.append({"kind": "scope-or-gate-blocker", "severity": "error", "message": reason.strip()})
        identity_check = result.get("identityCheck")
        if isinstance(identity_check, dict):
            for reason in identity_check.get("reasons") or []:
                if isinstance(reason, str) and reason.strip():
                    findings.append({"kind": "identity-check", "severity": "error", "message": reason.strip()})
        if isinstance(result.get("error"), str) and result["error"].strip():
            findings.append({"kind": "deployment-execution", "severity": "error", "message": result["error"].strip()})
        reconciliation = result.get("reconciliation")
        if isinstance(reconciliation, dict) and reconciliation.get("status") not in (None, "passed"):
            findings.append({
                "kind": "reconciliation",
                "severity": "error",
                "message": f"reconciliation status: {reconciliation.get('status')}",
            })
        if outcome == "passed" and not findings:
            findings.append({
                "kind": "deployment-verification",
                "severity": "info",
                "message": "ARM incremental deployment succeeded in the selected non-production lab; deployment verification alone does not establish functional/runtime qualification or alert parity.",
            })

        pkg_identity = (
            result.get("packageIdentity")
            or (plan or {}).get("packageIdentity")
            or (candidate or {}).get("packageIdentity")
            or {}
        )
        artifact_bindings = {
            "candidateSha256": result.get("candidateSha256") or (candidate or {}).get("candidateSha256"),
            "planSha256": result.get("planSha256") or (plan or {}).get("planSha256"),
            "mainTemplateSha256": result.get("mainTemplateSha256") or (plan or {}).get("mainTemplateSha256") or (candidate or {}).get("mainTemplateSha256"),
            "packageArtifactsSha256": pkg_identity.get("packageArtifactsSha256") if isinstance(pkg_identity, dict) else None,
            "packageReportSha256": pkg_identity.get("packageReportSha256") if isinstance(pkg_identity, dict) else None,
            "packageInputSha256": pkg_identity.get("packageInputSha256") if isinstance(pkg_identity, dict) else None,
            "artifactPaths": (plan or {}).get("artifactPaths") or (candidate or {}).get("artifactPaths") or {},
            "selectedFlags": (plan or {}).get("selectedFlags") or {},
            "parameters": result.get("parameters") or (plan or {}).get("parameters") or {},
        }
        target_binding = result.get("target") or (plan or {}).get("target") or (plan or {}).get("scope", {}).get("lab") or {}
        preflight_summary = build_lab_deployment_preflight_prompt(root, state=state)
        evidence_record = {
            "schemaVersion": 1,
            "runId": (state or {}).get("runId") or (candidate or {}).get("runId") or (plan or {}).get("runId"),
            "armValidationMethod": "lab-deployment",
            "status": status,
            "outcome": outcome,
            "writeAttempted": bool(result.get("writeAttempted", False)),
            "deploymentName": result.get("deploymentName"),
            "deploymentId": result.get("deploymentId"),
            "provisioningState": result.get("provisioningState"),
            "commandExitCode": result.get("commandExitCode"),
            "target": target_binding,
            "artifactBindings": artifact_bindings,
            "expectedContentCounts": preflight_summary["expectedContentCounts"],
            "labDeploymentPreflightPrompt": preflight_summary["labDeploymentPreflightPrompt"],
            "findings": findings,
            "attemptPath": result.get("attemptPath"),
            "reconciliation": reconciliation if isinstance(reconciliation, dict) else None,
            "functionalQualificationVerified": False,
            "alertParityVerified": False,
            "installationVerified": False,
            "registrationVerified": False,
            "uiVerified": False,
            "parityVerified": False,
            "accepted": False,
        }
        if state and state.get("runId"):
            evidence_path = _write_run_json(root, "arm-deployment-validation-evidence.json", evidence_record)
            rel_path = evidence_path.relative_to(root).as_posix()
            evidence_record["evidencePath"] = rel_path
            try:
                with workflow._state_writer_lock(root) as state_path:
                    latest_state = workflow._load(root)[1]
                    pkg_stage = latest_state.get("stages", {}).get("packaging")
                    if isinstance(pkg_stage, dict):
                        pkg_artifacts = pkg_stage.setdefault("artifacts", {})
                        if isinstance(pkg_artifacts, dict):
                            pkg_artifacts["labArmDeploymentEvidence"] = rel_path
                            pkg_artifacts["labArmDeploymentStatus"] = status
                            pkg_artifacts["labArmDeploymentOutcome"] = outcome
                            pkg_artifacts["functionalQualificationVerified"] = "false"
                            pkg_artifacts["alertParityVerified"] = "false"
                            workflow._write_unlocked(state_path, latest_state)
            except Exception:
                pass
        return evidence_record


def plan_candidate(solution: str | Path, *, target: dict[str, Any],
                   selected_flags: dict[str, bool], contract_only: bool = False) -> dict[str, Any]:
    from solution_manager.authoring.workbook_validation import (refresh_arm_candidate, plan_lab_arm_validation,
                                     plan_workbook_contract_verification)
    state = current_state(solution)
    context = _context(state or {})
    candidate = refresh_arm_candidate(context, _read_run_json(solution, "arm-candidate.json"))
    plan = (plan_workbook_contract_verification if contract_only else plan_lab_arm_validation)(
        context, candidate, target=target, selected_flags=selected_flags)
    _write_run_json(solution, "workbook-contract-plan.json" if contract_only else "arm-validation-plan.json", plan)
    if not contract_only:
        plan_lab_deployment_preflight(solution, persist=True)
    return plan


def review_scope(solution: str | Path, *, actor: str, reference: str, approved: bool,
                 expected_plan_sha256: str) -> dict[str, Any]:
    from solution_manager.authoring.workbook_validation import review_lab_arm_scope
    plan = _read_run_json(solution, "arm-validation-plan.json")
    if plan["planSha256"] != expected_plan_sha256:
        raise ValueError("scope review requires the exact current displayed plan hash")
    current = plan_candidate(solution, target=_plan_target(plan), selected_flags=plan["selectedFlags"])
    if current["planSha256"] != plan["planSha256"]:
        raise ValueError("candidate scope changed before review")
    consent = review_lab_arm_scope(current, actor=actor, approval_reference=reference, approved=approved)
    _write_run_json(solution, "arm-validation-consent.json", consent)
    return consent


def withdraw_scope(solution: str | Path, *, actor: str, reference: str) -> dict[str, Any]:
    from solution_manager.authoring.workbook_validation import withdraw_lab_arm_scope
    consent = withdraw_lab_arm_scope(_read_run_json(solution, "arm-validation-consent.json"),
                                    actor=actor, withdrawal_reference=reference)
    _write_run_json(solution, "arm-validation-consent.json", consent)
    return consent


def execute_candidate(solution: str | Path, *, expected_plan_sha256: str, actor: str,
                      reference: str, confirmation: str, identity_check=None,
                      command_runner=None) -> dict[str, Any]:
    from solution_manager.authoring.workbook_validation import execute_lab_arm_validation
    from solution_manager.qualification.arm_acceptance_support import _run_cli
    from solution_manager.qualification.workbook_preflight_workflow import production_identity_check, execution_profile

    state = current_state(solution)
    context = _context(state or {})
    candidate = _read_run_json(solution, "arm-candidate.json")
    plan = _read_run_json(solution, "arm-validation-plan.json")
    profile = execution_profile() if identity_check is None or command_runner is None else None

    def dispatch(command: list[str]):
        from solution_manager.qualification.graph_client_config import azure_cli_profile

        if execution_profile() != profile:
            raise ValueError("ARM execution authentication profile changed before dispatch")
        with azure_cli_profile(profile):
            return _run_cli(command)

    result = execute_lab_arm_validation(
        context, candidate, target=_plan_target(plan), selected_flags=plan["selectedFlags"],
        expected_plan_sha256=expected_plan_sha256, actor=actor, approval_reference=reference,
        confirmation=confirmation, evidence_directory=report_directory(solution),
        refresh_candidate=lambda: _read_run_json(solution, "arm-candidate.json"),
        read_consent=lambda: _read_run_json(solution, "arm-validation-consent.json"),
        identity_check=identity_check or (lambda target: production_identity_check(solution, target, profile=profile)),
        command_runner=command_runner or dispatch,
    )
    findings_evidence = record_lab_deployment_validation_findings(
        solution, result, candidate=candidate, plan=plan
    )
    result = {
        **result,
        "functionalQualificationVerified": False,
        "alertParityVerified": False,
        "artifactBindings": findings_evidence["artifactBindings"],
        "findings": findings_evidence["findings"],
        "evidencePath": findings_evidence.get("evidencePath"),
    }
    _write_run_json(solution, "arm-validation-result.json", result)
    return result


def reconcile_attempt(solution: str | Path, *, attempt: str | Path,
                      observation: str | Path, actor: str, reference: str) -> dict[str, Any]:
    from solution_manager.authoring.workbook_validation import reconcile_lab_arm_attempt
    root = Path(solution).expanduser().resolve()
    attempt_path = content_path(root, attempt)
    if attempt_path.parent != report_directory(root):
        raise ValueError("attempt reconciliation must use the selected run")
    observation_path = content_path(root, observation)
    result = reconcile_lab_arm_attempt(attempt_path, observation=json.loads(observation_path.read_bytes()),
                                      actor=actor, reference=reference)
    findings_evidence = record_lab_deployment_validation_findings(root, result)
    result = {
        **result,
        "functionalQualificationVerified": False,
        "alertParityVerified": False,
        "artifactBindings": findings_evidence["artifactBindings"],
        "findings": findings_evidence["findings"],
        "evidencePath": findings_evidence.get("evidencePath"),
    }
    _write_run_json(root, "arm-validation-result.json", result)
    return result


def import_contract(solution: str | Path, *, evidence: str | Path,
                    contract_only: bool = False) -> dict[str, Any]:
    from solution_manager.authoring.workbook_validation import verify_workbook_readback, refresh_arm_candidate
    from solution_manager.core import workflow
    root = Path(solution).expanduser().resolve()
    with workflow._state_writer_lock(root) as path:
        state = workflow._load(root)[1]
        context = _context(state)
        candidate = refresh_arm_candidate(context, _read_run_json(root, "arm-candidate.json"))
        plan_name = "workbook-contract-plan.json" if contract_only else "arm-validation-plan.json"
        plan = _read_run_json(root, plan_name)
        current = plan_candidate(root, target=_plan_target(plan), selected_flags=plan["selectedFlags"], contract_only=contract_only)
        if current["planSha256"] != plan["planSha256"]:
            raise ValueError("contract evidence refers to a stale plan")
        if len(plan["expectedWorkbooks"]) != len(state["workbooks"]["selection"]["included"]):
            raise ValueError("contract plan must select every included Defender workbook")
        source = content_path(root, evidence)
        proof = json.loads(source.read_bytes())
        result = verify_workbook_readback(plan, proof)
        proof_path = _write_run_json(root, "workbook-contract-evidence.json", proof)
        result_path = _write_run_json(root, "workbook-contract-result.json", result)
        if result["accepted"] is not True:
            return result
        artifacts = state["stages"]["packaging"]["artifacts"]
        artifacts.update({"workbookContractPlan": str(existing_artifact_path(root, plan_name)),
                          "workbookContractEvidence": str(proof_path),
                          "workbookContractResult": str(result_path),
                          "packageLifecycleStatus": "accepted"})
        state["packaging"]["currentAttempt"]["status"] = "passed"
        state["packaging"]["lastConsumedAction"]["packageSucceeded"] = True
        state["stages"]["packaging"].update(status="passed", message="Selected ARM route and independently verified workbook contract accepted.")
        report_path = resolve_artifact_reference(root, artifacts["packageReport"])
        report = json.loads(report_path.read_bytes())
        state["packaging"]["lastSuccessful"] = {
            **state["packaging"]["lastConsumedAction"], "packageReport": str(report_path),
            "packageReportSha256": hashlib.sha256(report_path.read_bytes()).hexdigest(),
            "packageArtifactsSha256": report["packageArtifactsSha256"], "version": report["version"],
        }
        state["workflowStatus"] = "inProgress"
        workflow._validate_packaging_evidence(state, artifacts, root)
        workflow._write_unlocked(path, state)
        return {**result, "runId": candidate["runId"], "next": workflow._next_stage_name(state)}


def require_accepted(solution: str | Path, state: dict[str, Any]) -> None:
    from solution_manager.authoring.workbook_validation import (refresh_arm_candidate, verify_workbook_readback,
                                     plan_lab_arm_validation, plan_workbook_contract_verification)
    artifacts = state["stages"]["packaging"].get("artifacts") or {}
    candidate = refresh_arm_candidate(_context(state), _read_run_json(solution, "arm-candidate.json"))
    if not state["workbooks"]["selection"]["included"]:
        attempt = _read_run_json(solution, "arm-validation-result.json")
        _verify_arm_only(solution, candidate, _read_run_json(solution, "arm-validation-plan.json"), attempt)
        return
    for key in ("workbookContractPlan", "workbookContractEvidence", "workbookContractResult"):
        if not artifacts.get(key):
            raise ValueError("candidate packaging is not accepted; independent workbook contract evidence is required")
    plan = json.loads(resolve_artifact_reference(solution, artifacts["workbookContractPlan"]).read_bytes())
    fresh = (plan_workbook_contract_verification if plan.get("purpose") == "workbook-contract-readback"
             else plan_lab_arm_validation)(_context(state), candidate,
                                          target=_plan_target(plan), selected_flags=plan["selectedFlags"])
    if (
        fresh["planSha256"] != plan.get("planSha256")
        or len(plan.get("expectedWorkbooks") or []) != len(state["workbooks"]["selection"]["included"])
    ):
        raise ValueError("accepted workbook contract plan is not current for this run and selection")
    proof = json.loads(resolve_artifact_reference(solution, artifacts["workbookContractEvidence"]).read_bytes())
    recorded = json.loads(resolve_artifact_reference(solution, artifacts["workbookContractResult"]).read_bytes())
    result = verify_workbook_readback(plan, proof)
    if result.get("accepted") is not True or result != recorded:
        raise ValueError("workbook contract acceptance is missing, blocked or stale")


def _verify_arm_only(solution: str | Path, candidate: dict[str, Any],
                     plan: dict[str, Any], attempt: dict[str, Any]) -> None:
    from solution_manager.qualification.arm_acceptance_support import _deployment_provisioning_state
    from solution_manager.authoring.workbook_validation import plan_lab_arm_validation

    state = current_state(solution)
    fresh = plan_lab_arm_validation(_context(state or {}), candidate,
                                   target=_plan_target(plan), selected_flags=plan["selectedFlags"])
    if (
        fresh["planSha256"] != plan["planSha256"] or plan["expectedWorkbooks"]
        or attempt.get("planSha256") != plan["planSha256"]
        or attempt.get("candidateSha256") != candidate["candidateSha256"]
        or attempt.get("status") != "arm-accepted-contract-pending"
        or attempt.get("target") != plan["target"]
        or attempt.get("parameters") != plan["parameters"]
        or attempt.get("packageIdentity") != plan["packageIdentity"]
    ):
        raise ValueError("ARM-only acceptance requires the exact current terminal attempt")
    observation = attempt.get("reconciliation") or {}
    if not observation.get("responsePath"):
        raise ValueError("independent current ARM deployment GET reconciliation is required")
    response_path = content_path(Path(solution).expanduser().resolve(), observation.get("responsePath"))
    if (
        observation.get("httpMethod") != "GET" or observation.get("status") != "passed"
        or observation.get("target") != plan["target"]
        or hashlib.sha256(response_path.read_bytes()).hexdigest() != observation.get("responseSha256")
    ):
        raise ValueError("independent current ARM deployment GET reconciliation is required")
    response = json.loads(response_path.read_bytes())
    expected_id = (
        f"/subscriptions/{plan['target']['subscriptionId']}/resourceGroups/{plan['target']['resourceGroup']}"
        f"/providers/Microsoft.Resources/deployments/{attempt.get('deploymentName')}"
    )
    if (
        str(response.get("id", "")).casefold() != expected_id.casefold()
        or str(observation.get("deploymentId", "")).casefold() != expected_id.casefold()
        or _deployment_provisioning_state(response) != "succeeded"
    ):
        raise ValueError("ARM deployment identity/outcome is not independently accepted")


def import_arm_only(solution: str | Path, *, attempt: str | Path, observation: str | Path,
                    actor: str, reference: str) -> dict[str, Any]:
    from solution_manager.core import workflow
    from solution_manager.authoring.workbook_validation import refresh_arm_candidate
    root = Path(solution).expanduser().resolve()
    with workflow._state_writer_lock(root) as path:
        state = workflow._load(root)[1]
        _context(state)
        if state["workbooks"]["selection"]["included"]:
            raise ValueError("selected Defender workbooks require independent full contract evidence, not ARM-only acceptance")
        candidate = refresh_arm_candidate(_context(state), _read_run_json(root, "arm-candidate.json"))
        result = reconcile_attempt(root, attempt=attempt, observation=observation, actor=actor, reference=reference)
        _verify_arm_only(root, candidate, _read_run_json(root, "arm-validation-plan.json"), result)
        state["packaging"]["currentAttempt"]["status"] = "passed"
        state["packaging"]["lastConsumedAction"]["packageSucceeded"] = True
        stage = state["stages"]["packaging"]
        stage.update(status="passed", message="Selected ARM method accepted by exact independent terminal deployment evidence.")
        stage["artifacts"]["packageLifecycleStatus"] = "accepted"
        report_path = resolve_artifact_reference(root, stage["artifacts"]["packageReport"])
        report = json.loads(report_path.read_bytes())
        state["packaging"]["lastSuccessful"] = {
            **state["packaging"]["lastConsumedAction"], "packageReport": str(report_path),
            "packageReportSha256": hashlib.sha256(report_path.read_bytes()).hexdigest(),
            "packageArtifactsSha256": report["packageArtifactsSha256"], "version": report["version"],
        }
        state["workflowStatus"] = "inProgress"
        workflow._validate_packaging_evidence(state, stage["artifacts"], root)
        workflow._write_unlocked(path, state)
        return {"status": "accepted", "accepted": True, "workbookContractApplicable": False,
                "uiVerified": False, "parityVerified": False, "next": workflow._next_stage_name(state)}


def current_state(solution: str | Path) -> dict[str, Any] | None:
    path = existing_artifact_path(solution, "workflow-state.json")
    if not path.is_file():
        return None
    from solution_manager.core.workflow import _load

    return _load(solution)[1]


def summary(solution: str | Path, state: dict[str, Any]) -> dict[str, Any] | None:
    if not enabled(state):
        return None
    workbook_state = state["workbooks"]
    rows = {}
    manifest_path = report_directory(solution) / "workbooks-manifest.json"
    issues = []
    try:
        verify_inventory(solution, state)
        if manifest_path.is_file():
            bind_conversion(solution, state)
            rows = {row["sourceRelativePath"]: row for row in json.loads(manifest_path.read_bytes())["results"]}
    except (OSError, ValueError, KeyError, TypeError) as exc:
        issues.append(str(exc))
    contract_support = "unverified" if workbook_state["selection"]["included"] else "notApplicable"
    if workbook_state["selection"]["included"] and state["stages"]["packaging"]["status"] == "passed":
        try:
            require_accepted(solution, state)
            contract_support = "verified"
        except (OSError, ValueError, KeyError, TypeError):
            issues.append("previous workbook acceptance evidence is no longer current")
    preflight_summary = build_lab_deployment_preflight_prompt(solution, state=state)
    return {
        "inventoryCount": len(workbook_state["inventory"]),
        "selectedCount": len(workbook_state["selection"]["included"]),
        "excluded": workbook_state["selection"]["excluded"],
        "inventorySha256": workbook_state["inventorySha256"],
        "armValidationMethod": state["context"]["armValidationMethod"],
        "defaultArmValidationMethod": DEFAULT_ARM_VALIDATION_METHOD,
        "expectedContentCounts": preflight_summary["expectedContentCounts"],
        "labDeploymentPreflightPrompt": preflight_summary["labDeploymentPreflightPrompt"],
        "contractSupport": contract_support,
        "issues": issues,
        "sources": [{
            **source, "selected": source["path"] in workbook_state["selection"]["included"],
            "status": rows.get(source["path"], {}).get("status", "not-converted"),
            "issues": rows.get(source["path"], {}).get("issues", []),
        } for source in workbook_state["inventory"]],
        "manifest": str(manifest_path) if manifest_path.is_file() else None,
        "qualificationSeparateFromArmAndDetectionParity": True,
    }


def assess_qualification_readiness(
    solution_path: str | Path,
    *,
    run_id: str | None = None,
) -> dict[str, Any]:
    """Inspect current workflow state, authorization/consent records, and preflight receipts.

    Separately reports:
    - authorizationChecks (target locked, runtime query consent, ARM preflight read consent, deployment consent)
    - deploymentPermissionReadiness (ARM control-plane access, resource group/workspace write readiness, extension readiness)
    - ingestionPermissionReadiness (DCR/DCE/Logs Ingestion readiness, kept strictly separate from deployment readiness)
    """
    from solution_manager.core.artifacts import using_run
    from solution_manager.core.target_context import workspace_identity

    root = Path(solution_path).expanduser().resolve()
    with using_run(root, run_id):
        state = current_state(root)
        context = (state or {}).get("context") or {}
        effective_run_id = (state or {}).get("runId") or run_id
        run_dir = report_directory(root) if effective_run_id else None

        def _read_optional_run_json(name: str) -> dict[str, Any] | None:
            if run_dir is None:
                return None
            candidate_file = run_dir / name
            if candidate_file.is_symlink() or not candidate_file.is_file():
                return None
            try:
                loaded = json.loads(candidate_file.read_text(encoding="utf-8-sig"))
                return loaded if isinstance(loaded, dict) else None
            except Exception:
                return None

        target_fields = ("tenantId", "subscriptionId", "workspaceResourceId", "workspaceCustomerId")
        missing_target = [key for key in target_fields if not context.get(key)]
        target_locked = bool(context.get("targetContextLocked") is True and not missing_target)
        resource_group = None
        if context.get("workspaceResourceId"):
            try:
                resource_group = workspace_identity(str(context["workspaceResourceId"]))["resourceGroup"]
            except Exception:
                resource_group = None

        runtime_consent = _read_optional_run_json("runtime-query-consent.json") or _read_optional_run_json(
            "authoring-runtime-query-consent.json"
        )
        runtime_consent_status = (
            "approved"
            if isinstance(runtime_consent, dict)
            and runtime_consent.get("status") in {"approved", "confirmed"}
            and runtime_consent.get("withdrawn") is not True
            and runtime_consent.get("revoked") is not True
            else ("revoked" if isinstance(runtime_consent, dict) and (runtime_consent.get("withdrawn") or runtime_consent.get("revoked")) else "missing")
        )

        arm_preflight_consent = _read_optional_run_json("arm-preflight-consent.json")
        arm_preflight_consent_status = (
            "approved"
            if isinstance(arm_preflight_consent, dict)
            and arm_preflight_consent.get("status") == "approved"
            and arm_preflight_consent.get("revoked") is not True
            else (
                "revoked"
                if isinstance(arm_preflight_consent, dict)
                and (arm_preflight_consent.get("status") == "revoked" or arm_preflight_consent.get("revoked") is True)
                else "missing"
            )
        )

        deployment_consent = _read_optional_run_json("arm-validation-consent.json")
        deployment_consent_status = (
            "approved"
            if isinstance(deployment_consent, dict)
            and deployment_consent.get("status") == "approved"
            and deployment_consent.get("withdrawn") is not True
            and deployment_consent.get("deploymentOnly") is True
            else (
                "withdrawn"
                if isinstance(deployment_consent, dict)
                and (deployment_consent.get("status") == "withdrawn" or deployment_consent.get("withdrawn") is True)
                else "missing"
            )
        )

        auth_ready = (
            target_locked
            and runtime_consent_status == "approved"
            and arm_preflight_consent_status == "approved"
            and deployment_consent_status == "approved"
        )
        authorization_checks = {
            "status": "ready" if auth_ready else "blocked",
            "targetLocked": {
                "status": "ready" if target_locked else "blocked",
                "locked": target_locked,
                "missingFields": missing_target,
                "resourceGroup": resource_group,
            },
            "runtimeQueryConsent": {
                "status": runtime_consent_status,
                "ready": runtime_consent_status == "approved",
                "approvedFamilies": (runtime_consent or {}).get("approvedFamilies", []),
            },
            "armPreflightReadConsent": {
                "status": arm_preflight_consent_status,
                "ready": arm_preflight_consent_status == "approved",
                "writesAuthorized": False,
            },
            "deploymentConsent": {
                "status": deployment_consent_status,
                "ready": deployment_consent_status == "approved",
                "deploymentOnly": bool((deployment_consent or {}).get("deploymentOnly") is True),
                "ingestionAuthorized": False,
            },
        }

        arm_preflight = _read_optional_run_json("arm-preflight-result.json")
        arm_checks = (arm_preflight or {}).get("checks") if isinstance(arm_preflight, dict) else {}
        if not isinstance(arm_checks, dict):
            arm_checks = {}

        control_plane_ok = bool(
            isinstance(arm_preflight, dict)
            and arm_preflight.get("tenantMatches") is True
            and arm_preflight.get("subscriptionMatches") is True
            and arm_preflight.get("workspaceMatches") is True
            and arm_preflight.get("nonProduction") is True
        )
        rg_ws_write_ok = bool(
            isinstance(arm_preflight, dict)
            and arm_preflight.get("armDeploymentAllowed") is True
            and arm_preflight.get("disabledContentVerified") is True
            and arm_preflight.get("ownershipVerified") is True
        )
        ext_check = arm_checks.get("extensionResourceWriteAllowed") if isinstance(arm_checks.get("extensionResourceWriteAllowed"), dict) else {}
        ext_required = bool(ext_check.get("required", True)) if arm_preflight else True
        ext_ok = bool(
            isinstance(arm_preflight, dict)
            and (not ext_required or arm_preflight.get("extensionResourceWriteAllowed") is True)
        )
        deployment_ready = bool(
            isinstance(arm_preflight, dict)
            and arm_preflight.get("status") == "ready"
            and control_plane_ok
            and rg_ws_write_ok
            and ext_ok
        )
        deployment_permission_readiness = {
            "status": (
                "ready"
                if deployment_ready
                else ("not-evaluated" if arm_preflight is None else str(arm_preflight.get("status") or "blocked"))
            ),
            "ready": deployment_ready,
            "receiptPresent": arm_preflight is not None,
            "armControlPlaneAccess": {
                "status": "ready" if control_plane_ok else ("not-evaluated" if arm_preflight is None else "blocked"),
                "tenantMatches": (arm_preflight or {}).get("tenantMatches"),
                "subscriptionMatches": (arm_preflight or {}).get("subscriptionMatches"),
                "workspaceMatches": (arm_preflight or {}).get("workspaceMatches"),
                "nonProduction": (arm_preflight or {}).get("nonProduction"),
            },
            "resourceGroupAndWorkspaceWriteReadiness": {
                "status": "ready" if rg_ws_write_ok else ("not-evaluated" if arm_preflight is None else "blocked"),
                "armDeploymentAllowed": (arm_preflight or {}).get("armDeploymentAllowed"),
                "disabledContentVerified": (arm_preflight or {}).get("disabledContentVerified"),
                "ownershipVerified": (arm_preflight or {}).get("ownershipVerified"),
            },
            "extensionReadiness": {
                "status": (
                    "not-required"
                    if isinstance(arm_preflight, dict) and not ext_required
                    else ("ready" if ext_ok else ("not-evaluated" if arm_preflight is None else "blocked"))
                ),
                "required": ext_required,
                "extensionResourceWriteAllowed": (arm_preflight or {}).get("extensionResourceWriteAllowed"),
            },
            "reasons": list((arm_preflight or {}).get("reasons") or []) if isinstance(arm_preflight, dict) else ["ARM preflight receipt is missing"],
            "impliesIngestionReadiness": False,
        }

        dcr_preflight = _read_optional_run_json("qualification-dcr-preflight.json")
        dcr_summary = (dcr_preflight or {}).get("summary") if isinstance(dcr_preflight, dict) else {}
        if not isinstance(dcr_summary, dict):
            dcr_summary = {}
        dcr_candidates = (dcr_preflight or {}).get("candidates") if isinstance(dcr_preflight, dict) else []
        if not isinstance(dcr_candidates, list):
            dcr_candidates = []

        dcr_status = str((dcr_preflight or {}).get("status") or ("not-evaluated" if dcr_preflight is None else "blocked"))
        dcr_dce_ready = bool(
            isinstance(dcr_preflight, dict)
            and bool(dcr_candidates)
            and all(
                isinstance(cand, dict)
                and (cand.get("resourceProvisioningAuthorization") or {}).get("status") in {"ready", "not-needed"}
                and (cand.get("tableSchemaCompatibility") or {}).get("status") == "compatible"
                for cand in dcr_candidates
            )
        )
        logs_ingestion_ready = bool(
            isinstance(dcr_preflight, dict)
            and bool(dcr_candidates)
            and all(
                isinstance(cand, dict)
                and (cand.get("ingestionAuthorization") or {}).get("status") == "ready"
                for cand in dcr_candidates
            )
        )
        ingestion_ready = bool(dcr_dce_ready and logs_ingestion_ready and dcr_status in {"ready", "passed"})
        ingestion_permission_readiness = {
            "status": "ready" if ingestion_ready else ("not-evaluated" if dcr_preflight is None else dcr_status),
            "ready": ingestion_ready,
            "receiptPresent": dcr_preflight is not None,
            "dcrAndDceReadiness": {
                "status": "ready" if dcr_dce_ready else ("not-evaluated" if dcr_preflight is None else "blocked"),
                "candidateCount": len(dcr_candidates),
                "summary": dcr_summary,
            },
            "logsIngestionReadiness": {
                "status": "ready" if logs_ingestion_ready else ("not-evaluated" if dcr_preflight is None else "blocked"),
                "requiredAction": "Microsoft.Insights/Telemetry/Write",
            },
            "queryPermission": (dcr_preflight or {}).get("queryPermission") if isinstance(dcr_preflight, dict) else None,
            "blockers": list((dcr_preflight or {}).get("blockers") or []) if isinstance(dcr_preflight, dict) else ["DCR/ingestion preflight receipt is missing"],
            "separateFromDeploymentReadiness": True,
        }

        preflight_prompt = build_lab_deployment_preflight_prompt(root, state=state)
        overall_ready = bool(auth_ready and deployment_ready and ingestion_ready)
        return {
            "schemaVersion": 1,
            "solution": str(root),
            "runId": effective_run_id,
            "workflowProfile": context.get("workflowProfile"),
            "status": "ready" if overall_ready else "blocked",
            "authorizationChecks": authorization_checks,
            "deploymentPermissionReadiness": deployment_permission_readiness,
            "ingestionPermissionReadiness": ingestion_permission_readiness,
            "deploymentAndIngestionSeparated": True,
            "expectedContentCounts": preflight_prompt["expectedContentCounts"],
            "labDeploymentPreflightPrompt": preflight_prompt["labDeploymentPreflightPrompt"],
        }


def audit_private_config_and_support_export(
    solution_path: str | Path,
    *,
    run_id: str | None = None,
) -> dict[str, Any]:
    """Audit private target configuration and support/evidence export artifacts before making exposure claims."""
    import re
    from solution_manager.core.artifacts import using_run
    from solution_manager.core.target_config import ENV_FILE_NAME, read_solution_target_config
    from solution_manager.core.target_context import workspace_identity

    root = Path(solution_path).expanduser().resolve()
    with using_run(root, run_id):
        state = current_state(root)
        context = (state or {}).get("context") or {}
        effective_run_id = (state or {}).get("runId") or run_id
        run_dir = report_directory(root) if effective_run_id else None

        env_path = root / ENV_FILE_NAME
        env_present = env_path.is_file() and not env_path.is_symlink()
        env_config: dict[str, str] = {}
        env_error: str | None = None
        if env_present:
            try:
                env_config = read_solution_target_config(root)
            except Exception as exc:
                env_error = str(exc)

        private_identifiers: dict[str, str] = {}
        for key in ("tenantId", "subscriptionId", "workspaceResourceId", "workspaceCustomerId"):
            val = context.get(key) or env_config.get(key)
            if isinstance(val, str) and val.strip():
                private_identifiers[key] = val.strip()

        ws_res_id = private_identifiers.get("workspaceResourceId")
        if ws_res_id:
            try:
                ws_id = workspace_identity(ws_res_id)
                private_identifiers.setdefault("subscriptionId", ws_id["subscriptionId"])
                private_identifiers["resourceGroup"] = ws_id["resourceGroup"]
                private_identifiers["workspaceName"] = ws_id["workspaceName"]
            except Exception:
                pass

        local_unexported_files: list[str] = []
        if env_present:
            local_unexported_files.append(ENV_FILE_NAME)
        if run_dir and run_dir.is_dir():
            for local_name in (
                "workflow-state.json",
                "qualification-target.json",
                "qualification-dcr-preflight.json",
                "arm-validation-plan.json",
                "arm-preflight-plan.json",
                "arm-preflight-result.json",
            ):
                candidate_file = run_dir / local_name
                if candidate_file.is_file():
                    local_unexported_files.append(candidate_file.relative_to(root).as_posix())

        export_files_checked: list[str] = []
        exposed_in_exports: list[dict[str, str]] = []
        evidence_root = root / "Evidence"
        export_dirs: list[Path] = []
        if effective_run_id and (evidence_root / effective_run_id).is_dir():
            export_dirs.append(evidence_root / effective_run_id)
        elif evidence_root.is_dir():
            export_dirs.extend(sorted(p for p in evidence_root.iterdir() if p.is_dir()))

        uuid_pattern = re.compile(
            r"\b[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}\b",
            re.IGNORECASE,
        )
        for export_dir in export_dirs:
            for file_path in sorted(export_dir.rglob("*")):
                if not file_path.is_file() or file_path.is_symlink():
                    continue
                rel = file_path.relative_to(root).as_posix()
                export_files_checked.append(rel)
                try:
                    content = file_path.read_text(encoding="utf-8-sig")
                except Exception:
                    continue
                for id_kind, id_value in sorted(private_identifiers.items()):
                    if len(id_value) >= 4 and id_value.casefold() in content.casefold():
                        exposed_in_exports.append({
                            "file": rel,
                            "identifierKind": id_kind,
                        })
                for match in uuid_pattern.findall(content):
                    for id_kind in ("tenantId", "subscriptionId", "workspaceCustomerId"):
                        expected = private_identifiers.get(id_kind)
                        if expected and match.casefold() == expected.casefold():
                            entry = {"file": rel, "identifierKind": id_kind}
                            if entry not in exposed_in_exports:
                                exposed_in_exports.append(entry)

        private_config_isolated = not exposed_in_exports
        return {
            "schemaVersion": 1,
            "solution": str(root),
            "runId": effective_run_id,
            "status": "isolated" if private_config_isolated else "exposed-in-support-export",
            "privateConfigIsolatedToLocalUnexportedConfig": private_config_isolated,
            "supportExportsRedacted": private_config_isolated,
            "exposureClaimVerified": not private_config_isolated,
            "localConfig": {
                "envFilePresent": env_present,
                "envParseError": env_error,
                "trackedIdentifierKinds": sorted(private_identifiers.keys()),
                "localUnexportedArtifacts": local_unexported_files,
            },
            "supportExports": {
                "checkedFiles": export_files_checked,
                "exposures": exposed_in_exports,
            },
        }
