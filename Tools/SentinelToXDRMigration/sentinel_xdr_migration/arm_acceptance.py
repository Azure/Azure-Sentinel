from __future__ import annotations

import hashlib
import json
import os
import re
import stat
from datetime import datetime, timezone
from pathlib import Path, PurePosixPath, PureWindowsPath
from typing import Any

from .artifacts import (
    artifact_path,
    existing_artifact_path,
    repository_root,
    resolve_artifact_reference,
    using_run,
    write_json_artifact,
)
from .deployment_planning import _current_package
from .arm_acceptance_support import (
    CommandRunner,
    _canonical_sha256,
    _deployment_provisioning_state,
    _parameter_values,
    _run_cli,
    _validated_members,
    _validated_shared_decisions,
    _verify_existing_cli_target,
)
from .onboarding import _state_dir
from .target_context import require_locked_target, workspace_identity
from .workflow import workflow_status

ARM_ACCEPTANCE_BATCH_PLAN = "arm-template-deployment-acceptance-batch-plan.json"
ARM_ACCEPTANCE_BATCH_REPORT = "arm-template-deployment-acceptance-batch.json"
ARM_ACCEPTANCE_ATTEMPT_PREFIX = "arm-template-deployment-acceptance-attempt-"
ARM_ACCEPTANCE_TEMPLATE_SNAPSHOT_PREFIX = "arm-template-deployment-acceptance-template-"
_SHA256 = re.compile(r"^[a-f0-9]{64}$")
_BATCH_ARM_ACCEPTANCE_CONFIRMATION = (
    "I approve the exact enumerated ARM template deployment acceptance batch"
)
_TARGET_KEYS = (
    "tenantId",
    "subscriptionId",
    "resourceGroup",
    "workspaceResourceId",
    "workspaceCustomerId",
)
_SOURCE_PATH_SEMANTICS = {"posix", "windows", "platform-neutral"}
_PRODUCER_PLATFORMS = {"posix", "windows"}


def _source_paths_in_order(paths: list[str], semantics: str) -> bool:
    if semantics == "posix":
        expected = sorted(paths, key=PurePosixPath)
    elif semantics == "windows":
        expected = sorted(paths, key=PureWindowsPath)
    elif semantics == "platform-neutral":
        posix_order = sorted(paths, key=PurePosixPath)
        windows_order = sorted(paths, key=PureWindowsPath)
        if posix_order != windows_order:
            raise ValueError(
                "validation binding claims platform-neutral source ordering but POSIX and Windows Path orders differ"
            )
        expected = posix_order
    else:
        raise ValueError(
            "validation binding has unsupported source Path ordering semantics"
        )
    return paths == expected


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _parse_build_validation_receipt(
    solution: Path,
    receipt_path: str | Path,
    *,
    package_report_path: Path,
    package_identity: dict[str, Any],
    arm_validation_method: str | None = None,
) -> dict[str, Any]:
    candidate = Path(receipt_path).expanduser()
    if candidate.is_symlink() or not candidate.is_file():
        raise ValueError(
            "ARM template acceptance requires the current build-and-validate-report.md receipt"
        )
    resolved = candidate.resolve(strict=True)
    if resolved.name != "build-and-validate-report.md":
        raise ValueError("validation receipt must be build-and-validate-report.md")
    try:
        content = resolved.read_bytes()
        report = content.decode("utf-8-sig")
    except (OSError, UnicodeError) as exc:
        raise ValueError(f"validation receipt is unreadable: {exc}") from exc

    if (
        report.count("[REPORT_START]") != 1
        or report.count("[REPORT_END]") != 1
        or report.index("[REPORT_START]") > report.index("[REPORT_END]")
    ):
        raise ValueError("validation receipt is not a complete build-and-validate report")
    lines = report.splitlines()

    def field(name: str) -> str:
        values = [
            line[len(name) + 2 :].strip()
            for line in lines
            if line.startswith(name + ": ")
        ]
        if len(values) != 1 or not values[0]:
            raise ValueError(f"validation receipt must contain one {name} field")
        return values[0]

    report_lines = [
        line.strip()
        for line in lines
        if line.strip() not in {"[REPORT_START]", "[REPORT_END]"}
    ]
    if not report_lines or report_lines[0] != "# BUILD & VALIDATION REPORT":
        raise ValueError("validation receipt was not produced by the repository build-and-validate report")
    if field("Solution") != solution.name:
        raise ValueError("validation receipt belongs to a different solution")
    expected_content_root = repository_root(solution).resolve()
    try:
        reported_content_root = Path(field("Content root")).expanduser().resolve(strict=True)
        toolkit_root = Path(field("Toolkit root")).expanduser().resolve(strict=True)
        evidence_path = Path(field("Evidence")).expanduser().resolve(strict=True)
    except OSError as exc:
        raise ValueError(
            f"validation receipt references an unavailable repository or evidence path: {exc}"
        ) from exc
    if reported_content_root != expected_content_root:
        raise ValueError("validation receipt content root does not match the selected solution repository")
    if evidence_path != resolved.parent:
        raise ValueError("validation receipt evidence path does not match its containing run directory")
    expected_script = toolkit_root / ".script" / "local-validation" / "build-and-validate.ps1"
    evidence_root = (toolkit_root / ".script" / "local-validation" / "Logs").resolve()
    if (
        expected_script.is_symlink()
        or not expected_script.is_file()
        or evidence_root not in evidence_path.parents
    ):
        raise ValueError(
            "validation receipt does not reference the repository build-and-validate evidence layout"
        )
    candidate_route = arm_validation_method == "lab-deployment"
    expected_result = "CANDIDATE_GENERATED" if candidate_route else "PASSED"
    expected_banner = "**CANDIDATE GENERATED — NOT ACCEPTED**" if candidate_route else "**BUILD SUCCESSFUL**"
    if field("Result") != expected_result or expected_banner not in report:
        raise ValueError("repository build-and-validate receipt did not report success")
    if field("Validation binding result") != "PASSED":
        raise ValueError("repository build-and-validate producer binding did not report success")

    validator_rows: list[dict[str, str]] = []
    for line in lines:
        match = re.fullmatch(
            r"\|\s*(TS|\.NET|CI-PS)\s*\|\s*([^|]+?)\s*\|\s*(PASS|FAIL|SKIP)\s*\|.*\|",
            line.strip(),
        )
        if match:
            validator_rows.append(
                {
                    "step": match.group(1),
                    "validator": match.group(2).strip(),
                    "status": match.group(3),
                }
            )
    summaries = [
        match
        for match in (
            re.fullmatch(
                r"Total:\s*(\d+)\s+validators\s*\|\s*(\d+)\s+passed\s*\|\s*(\d+)\s+failed\s*\|\s*(\d+)\s+skipped",
                line.strip(),
            )
            for line in lines
        )
        if match
    ]
    if len(summaries) != 1 or not validator_rows:
        raise ValueError(
            "validation receipt has no completed validator results; skipped validation is not success"
        )
    total, passed, failed, skipped = (int(value) for value in summaries[0].groups())
    actual_passed = sum(row["status"] == "PASS" for row in validator_rows)
    actual_failed = sum(row["status"] == "FAIL" for row in validator_rows)
    actual_skipped = sum(row["status"] == "SKIP" for row in validator_rows)
    if (
        total != len(validator_rows)
        or passed != actual_passed
        or failed != actual_failed
        or skipped != actual_skipped
        or failed
        or not passed
    ):
        raise ValueError(
            "validation receipt validator statuses are incomplete, inconsistent, or failed"
        )

    binding_path = Path(field("Validation binding")).expanduser()
    if binding_path.is_symlink() or not binding_path.is_file():
        raise ValueError("validation receipt is missing its producer binding artifact")
    binding_path = binding_path.resolve(strict=True)
    if (
        binding_path.name != "build-and-validate-binding.json"
        or binding_path.parent != evidence_path
    ):
        raise ValueError("validation binding is copied or is outside its report evidence directory")
    binding_bytes = binding_path.read_bytes()
    binding_sha256 = field("Validation binding SHA256")
    if not _SHA256.fullmatch(binding_sha256) or hashlib.sha256(binding_bytes).hexdigest() != binding_sha256:
        raise ValueError("validation binding artifact hash does not match the report")
    try:
        binding = json.loads(binding_bytes.decode("utf-8-sig"))
    except (UnicodeError, json.JSONDecodeError) as exc:
        raise ValueError(f"validation binding artifact is invalid JSON: {exc}") from exc
    if not isinstance(binding, dict) or binding.get("schemaVersion") != 1:
        raise ValueError("validation binding artifact has an unsupported schema")
    recorded_method = binding.get("armValidationMethod", "arm-ttk")
    if recorded_method not in {"arm-ttk", "lab-deployment"}:
        raise ValueError("validation binding has an unsupported ARM validation method")
    if recorded_method != (arm_validation_method or "arm-ttk"):
        raise ValueError("validation binding ARM validation method does not match this route")
    if candidate_route and (
        binding.get("armValidationStatus") != "pending"
        or binding.get("packageLifecycleStatus") != "candidate-generated"
        or binding.get("packageAccepted") is not False
        or binding.get("workbookCapabilityVersion") != 1
        or len([row for row in validator_rows if row["validator"] == "ARM-TTK" and row["status"] == "SKIP"]) != 1
        or any(row["validator"] == "ARM-TTK" and row["status"] != "SKIP" for row in validator_rows)
    ):
        raise ValueError("lab validation binding must be a pending, unaccepted versioned candidate")
    if arm_validation_method == "arm-ttk" and not any(
        row["validator"] == "ARM-TTK" and row["status"] == "PASS" for row in validator_rows
    ):
        raise ValueError("the selected ARM-TTK method requires an actual passed ARM-TTK result")
    source_path_semantics = binding.get("sourcePathSemantics")
    producer_platform = binding.get("producerPlatform")
    if (
        not isinstance(source_path_semantics, str)
        or source_path_semantics not in _SOURCE_PATH_SEMANTICS
    ):
        raise ValueError(
            "validation binding has no supported packager Path ordering semantics"
        )
    if (
        not isinstance(producer_platform, str)
        or producer_platform not in _PRODUCER_PLATFORMS
    ):
        raise ValueError("validation binding has no supported producer platform")

    solution_root = solution.resolve(strict=True)
    producer_paths = {
        "build-and-validate.ps1": toolkit_root / ".script" / "local-validation" / "build-and-validate.ps1",
        "validation-binding.ps1": toolkit_root / ".script" / "local-validation" / "validation-binding.ps1",
    }
    producer_before = binding.get("producerFilesBefore")
    producer_after = binding.get("producerFilesAfter")
    if (
        not isinstance(producer_before, dict)
        or not isinstance(producer_after, dict)
        or set(producer_before) != set(producer_paths)
        or producer_before != producer_after
    ):
        raise ValueError("validation binding does not prove stable producer scripts")
    for name, producer_path in producer_paths.items():
        if producer_path.is_symlink() or not producer_path.is_file():
            raise ValueError(f"validation binding producer script is unavailable: {name}")
        actual_hash = hashlib.sha256(producer_path.read_bytes()).hexdigest()
        if producer_before.get(name) != actual_hash:
            raise ValueError(f"validation binding was produced by a different {name}")

    if (
        binding.get("producer") != "build-and-validate.ps1"
        or binding.get("validationResult") != "PASSED"
        or binding.get("validationRan") is not True
        or binding.get("packagingSkipped") is not True
        or binding.get("contentRoot") != str(expected_content_root)
        or binding.get("solutionPath") != str(solution_root)
        or binding.get("toolkitRoot") != str(toolkit_root)
        or binding.get("evidenceRunPath") != str(evidence_path)
    ):
        raise ValueError("validation binding does not match this solution, ContentRoot, toolkit, and evidence run")
    try:
        validation_started = datetime.fromisoformat(binding["validationStartedAtUtc"])
        validation_completed = datetime.fromisoformat(binding["validationCompletedAtUtc"])
    except (KeyError, TypeError, ValueError) as exc:
        raise ValueError("validation binding has invalid start/completion timestamps") from exc
    if validation_completed < validation_started:
        raise ValueError("validation binding completed before it started")

    binding_summary = binding.get("validatorSummary")
    if binding_summary != {
        "total": total,
        "passed": passed,
        "failed": failed,
        "skipped": skipped,
    }:
        raise ValueError("validation binding validator totals do not match the human-readable report")

    def fingerprint_list(value: Any, label: str) -> list[dict[str, str]]:
        if not isinstance(value, list):
            raise ValueError(f"validation binding has no {label} file fingerprints")
        normalized: list[dict[str, str]] = []
        for item in value:
            if (
                not isinstance(item, dict)
                or set(item) != {"path", "sha256"}
                or not isinstance(item.get("path"), str)
                or not item["path"]
                or Path(item["path"]).is_absolute()
                or ".." in Path(item["path"].replace("\\", "/")).parts
                or not isinstance(item.get("sha256"), str)
                or not _SHA256.fullmatch(item["sha256"])
            ):
                raise ValueError(f"validation binding contains an invalid {label} file fingerprint")
            normalized.append({"path": item["path"].replace("\\", "/"), "sha256": item["sha256"]})
        paths = [item["path"] for item in normalized]
        if label == "source-input":
            if not _source_paths_in_order(paths, source_path_semantics):
                raise ValueError(
                    "validation binding source-input fingerprints do not match recorded Path ordering semantics"
                )
            expected_paths = paths
        else:
            expected_paths = sorted(paths)
        if paths != expected_paths or len(paths) != len(set(paths)):
            raise ValueError(f"validation binding {label} fingerprints are not uniquely sorted")
        return normalized

    source_before = fingerprint_list(binding.get("inputFilesBefore"), "source-input")
    source_after = fingerprint_list(binding.get("inputFilesAfter"), "source-input")
    package_before = fingerprint_list(binding.get("packageFilesBefore"), "package")
    package_after = fingerprint_list(binding.get("packageFilesAfter"), "package")
    if source_before != source_after or package_before != package_after:
        raise ValueError("solution inputs or V3.1 package artifacts changed during validation")
    source_fingerprint = hashlib.sha256(
        json.dumps(source_after, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest()
    package_fingerprint = hashlib.sha256(
        json.dumps(
            package_after,
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=False,
        ).encode("utf-8")
    ).hexdigest()
    if source_fingerprint != package_identity.get("packageInputSha256"):
        raise ValueError("validation binding source fingerprints do not match current V3.1 package inputs")
    if package_fingerprint != package_identity.get("packageContentSha256"):
        raise ValueError("validation binding package fingerprints do not match current V3.1 package artifacts")

    binding_package = binding.get("package")
    if not isinstance(binding_package, dict):
        raise ValueError("validation binding has no V3.1 package report identity")
    expected_package_report_reference = package_report_path.resolve(strict=True).relative_to(
        solution_root
    ).as_posix()
    expected_package = {
        "path": expected_package_report_reference,
        "sha256": package_identity.get("packageReportSha256"),
        "version": package_identity.get("version"),
        "packageAttemptId": package_identity.get("packageAttemptId"),
        "workflowRunId": package_identity.get("workflowRunId"),
        "packageInputSha256": package_identity.get("packageInputSha256"),
        "packageArtifactsSha256": package_identity.get("packageArtifactsSha256"),
        "packageArtifactHashes": package_identity.get("recordedPackageArtifactHashes"),
    }
    if any(binding_package.get(key) != value for key, value in expected_package.items()):
        raise ValueError("validation binding package report identity does not match the current V3.1 package")
    if binding_package.get("packageFiles") != package_after:
        raise ValueError("validation binding package report does not cover the exact packaged file inventory")

    return {
        "path": str(resolved),
        "sha256": hashlib.sha256(content).hexdigest(),
        "status": "PASSED",
        "solution": solution.name,
        "contentRoot": str(reported_content_root),
        "toolkitRoot": str(toolkit_root),
        "evidencePath": str(evidence_path),
        "buildAndValidateScriptSha256": hashlib.sha256(expected_script.read_bytes()).hexdigest(),
        "validatorResults": validator_rows,
        "validatorSummary": {
            "total": total,
            "passed": passed,
            "failed": failed,
            "skipped": skipped,
        },
        "bindingPath": str(binding_path),
        "bindingSha256": binding_sha256,
        "binding": binding,
        "sourcePathSemantics": source_path_semantics,
        "producerPlatform": producer_platform,
        "validatedPackage": binding_package,
    }


def _write_template_snapshot(path: Path, content: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.is_symlink() or path.parent.is_symlink():
        raise ValueError("ARM template snapshot path cannot traverse a symlink")
    try:
        descriptor = os.open(path, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o400)
    except FileExistsError:
        if path.is_symlink() or not path.is_file() or path.read_bytes() != content:
            raise ValueError("existing ARM template snapshot does not match the approved bytes")
        path.chmod(stat.S_IRUSR)
        return
    try:
        with os.fdopen(descriptor, "wb") as stream:
            stream.write(content)
            stream.flush()
            os.fsync(stream.fileno())
        path.chmod(stat.S_IRUSR)
    except Exception:
        path.unlink(missing_ok=True)
        raise


def _acceptance_package_plan(
    solution: str | Path,
    validation_receipt_path: str | Path,
) -> dict[str, Any]:
    root = Path(solution).expanduser().resolve()
    state = workflow_status(root)
    context = state.get("context") or {}
    if (
        context.get("workflowProfile") != "qualification"
        or context.get("profileSelectionConfirmed") is not True
        or context.get("targetContextLocked") is not True
    ):
        raise ValueError(
            "ARM template deployment acceptance requires an explicitly selected Qualification workflow and locked target"
        )
    stages = state.get("stages") or {}
    packaging = stages.get("packaging") or {}
    if packaging.get("status") != "passed":
        raise ValueError("ARM template deployment acceptance requires a passed V3.1 package stage")
    if (packaging.get("artifacts") or {}).get("packager") != "V3.1":
        raise ValueError("ARM template deployment acceptance requires packaging evidence from V3.1")

    target = require_locked_target(root, materialize_missing=False)
    package_freshness = state.get("packageFreshness") or {}
    package = _current_package(root, state)
    if (
        package_freshness.get("status") != "current"
        or package.get("status") != "current"
    ):
        raise ValueError(
            "ARM template deployment acceptance requires the current V3.1 package identity"
        )

    package_state = state.get("packaging") or {}
    successful = package_state.get("lastSuccessful") or {}
    package_report_reference = successful.get("packageReport")
    if not isinstance(package_report_reference, str) or not package_report_reference:
        raise ValueError("current V3.1 package receipt has no package report reference")
    try:
        package_report_path = resolve_artifact_reference(root, package_report_reference)
    except (OSError, ValueError) as exc:
        raise ValueError(f"current V3.1 package report cannot be resolved: {exc}") from exc
    package_identity = {
        "version": package.get("version"),
        "packageAttemptId": successful.get("attemptId"),
        "workflowRunId": state.get("runId"),
        "packageReportPath": package_report_reference.replace("\\", "/"),
        "packageInputSha256": package.get("packageInputSha256"),
        "packageArtifactHashes": package.get("packageArtifactHashes") or {},
        "recordedPackageArtifactHashes": package.get("recordedPackageArtifactHashes") or {},
        "packageContentSha256": package.get("packageContentSha256"),
        "packageReportSha256": successful.get("packageReportSha256"),
        "packageArtifactsSha256": successful.get("packageArtifactsSha256"),
    }
    validation_receipt = _parse_build_validation_receipt(
        root,
        validation_receipt_path,
        package_report_path=package_report_path,
        package_identity=package_identity,
    )

    template_path = root / "Package" / "mainTemplate.json"
    if (
        not template_path.is_file()
        or template_path.is_symlink()
        or template_path.parent.is_symlink()
    ):
        raise ValueError("current V3.1 Package/mainTemplate.json is missing or unsafe")
    template_bytes = template_path.read_bytes()
    template_sha256 = hashlib.sha256(template_bytes).hexdigest()
    expected_template_sha256 = (package.get("packageArtifactHashes") or {}).get("mainTemplate")
    if (
        not isinstance(expected_template_sha256, str)
        or not _SHA256.fullmatch(expected_template_sha256)
        or template_sha256 != expected_template_sha256
    ):
        raise ValueError("mainTemplate.json no longer matches the current V3.1 package identity")
    try:
        template = json.loads(template_bytes.decode("utf-8-sig"))
    except (UnicodeError, json.JSONDecodeError) as exc:
        raise ValueError(f"cannot read the current V3.1 ARM template: {exc}") from exc
    if not isinstance(template, dict) or not isinstance(template.get("parameters"), dict):
        raise ValueError("current V3.1 ARM template has no declared parameters object")

    declared_flags = {
        name: definition
        for name, definition in template["parameters"].items()
        if isinstance(name, str) and name.startswith("Deploy")
    }
    if any(
        not isinstance(definition, dict) or definition.get("type") != "bool"
        for definition in declared_flags.values()
    ):
        raise ValueError("every declared Deploy* package selection flag must be boolean")
    workspace = workspace_identity(target["workspaceResourceId"])["workspaceName"]
    flags = {name: True for name in declared_flags}
    parameters = _parameter_values(template, workspace, flags)

    snapshot_path = artifact_path(
        root,
        f"{ARM_ACCEPTANCE_TEMPLATE_SNAPSHOT_PREFIX}{template_sha256}.json",
        create_parent=True,
    )
    _write_template_snapshot(snapshot_path, template_bytes)
    body: dict[str, Any] = {
        "schemaVersion": 1,
        "stage": "post-validation-arm-template-deployment-acceptance",
        "status": "ready",
        "qualificationOnly": True,
        "solution": str(root),
        "runId": state.get("runId"),
        "target": {key: target[key] for key in _TARGET_KEYS},
        "deploymentRoute": "Azure CLI az deployment group create",
        "deploymentMode": "Incremental",
        "mainTemplatePath": str(template_path),
        "mainTemplateSha256": template_sha256,
        "mainTemplateSnapshotPath": str(snapshot_path),
        "mainTemplateSnapshotSha256": template_sha256,
        "packageIdentity": package_identity,
        "bicepExtensibilityImports": package.get("bicepExtensibilityImports") or [],
        "validationReceipt": validation_receipt,
        "declaredContentFlags": flags,
        "parameters": parameters,
        "parametersSha256": _canonical_sha256(parameters),
        "acceptanceCriterion": (
            "the command response records terminal ARM deployment provisioningState Succeeded"
        ),
        "resourceReadbackRequired": False,
        "resourceReadbackPerformed": False,
        "installationVerified": False,
        "activationPerformed": False,
        "alertParityPerformed": False,
        "qualificationCompleted": False,
        "planningConsentIsNotWriteApproval": True,
        "environmentWritesAuthorized": False,
        "confirmation": _BATCH_ARM_ACCEPTANCE_CONFIRMATION,
        "noAutomaticRetryAfterAttempt": True,
    }
    body["packagePlanSha256"] = _canonical_sha256(body)
    return body


def _arm_acceptance_batch_plan(
    members: list[dict[str, str]],
    *,
    shared_decisions_path: str | Path,
    validation_receipts: list[str | Path],
) -> dict[str, Any]:
    normalized = _validated_members(members)
    if len(validation_receipts) != len(normalized):
        raise ValueError(
            "provide exactly one current repository validation receipt for every batch member"
        )
    package_plans: list[dict[str, Any]] = []
    first_target: dict[str, Any] | None = None
    for member, receipt_path in zip(normalized, validation_receipts):
        root = Path(member["solutionPath"])
        with using_run(root, member["runId"]):
            plan = _acceptance_package_plan(root, receipt_path)
        if plan.get("runId") != member["runId"]:
            raise ValueError(
                f"{member['solution']}: selected workflow run changed while planning ARM acceptance"
            )
        target = plan["target"]
        if first_target is None:
            first_target = target
        elif any(
            str(target.get(key) or "").casefold()
            != str(first_target.get(key) or "").casefold()
            for key in _TARGET_KEYS
        ):
            raise ValueError("one ARM acceptance batch cannot cross locked lab targets")
        package_plans.append(plan)

    if first_target is None:
        raise ValueError("ARM acceptance batch has no members")
    receipt, receipt_binding = _validated_shared_decisions(
        shared_decisions_path,
        first_target,
        normalized,
    )
    known_flags = (receipt.get("decisions") or {}).get("knownFlagSelections")
    if not isinstance(known_flags, dict):
        raise ValueError("shared PR/lab decision receipt has no declared-flag selection map")
    declared_union = {
        name
        for plan in package_plans
        for name in (plan.get("declaredContentFlags") or {})
    }
    if set(known_flags) != declared_union or any(
        type(known_flags.get(name)) is not bool or known_flags[name] is not True
        for name in declared_union
    ):
        raise ValueError(
            "shared PR/lab decisions must exactly enumerate every currently declared package flag as true"
        )

    planned_members: list[dict[str, Any]] = []
    for member, plan in zip(normalized, package_plans):
        parameters = plan["parameters"]
        if not isinstance(parameters, dict) or any(
            not isinstance(name, str)
            or not name
            or not isinstance(value, (str, bool, int, float))
            for name, value in parameters.items()
        ):
            raise ValueError(
                f"{member['solution']}: ARM CLI parameters must be explicit scalar values"
            )
        deployment_name = "sentinel-arm-" + _canonical_sha256(
            {
                "solution": member["solution"],
                "runId": member["runId"],
                "target": first_target,
                "mainTemplateSha256": plan["mainTemplateSha256"],
                "parametersSha256": plan["parametersSha256"],
            }
        )[:32]
        planned_members.append(
            {
                "solution": member["solution"],
                "solutionPath": member["solutionPath"],
                "runId": member["runId"],
                "status": "ready",
                "packagePlanSha256": plan["packagePlanSha256"],
                "packageIdentity": plan["packageIdentity"],
                "bicepExtensibilityImports": plan.get("bicepExtensibilityImports") or [],
                "mainTemplatePath": plan["mainTemplatePath"],
                "mainTemplateSha256": plan["mainTemplateSha256"],
                "mainTemplateSnapshotPath": plan["mainTemplateSnapshotPath"],
                "mainTemplateSnapshotSha256": plan["mainTemplateSnapshotSha256"],
                "validationReceipt": plan["validationReceipt"],
                "declaredContentFlags": plan["declaredContentFlags"],
                "parameters": parameters,
                "parametersSha256": plan["parametersSha256"],
                "deploymentName": deployment_name,
            }
        )
    batch: dict[str, Any] = {
        "schemaVersion": 1,
        "stage": "post-validation-arm-template-deployment-acceptance",
        "status": "ready",
        "qualificationOnly": True,
        "target": {key: first_target[key] for key in _TARGET_KEYS},
        "sharedDecisionReceipt": receipt_binding,
        "members": planned_members,
        "writeCount": len(planned_members),
        "deploymentRoute": "Azure CLI az deployment group create",
        "deploymentMode": "Incremental",
        "acceptanceCriterion": (
            "every submitted member has a recorded terminal ARM deployment provisioningState Succeeded"
        ),
        "resourceReadbackRequired": False,
        "installationVerified": False,
        "activationPerformed": False,
        "alertParityPerformed": False,
        "qualificationCompleted": False,
        "planningConsentIsNotWriteApproval": True,
        "environmentWritesAuthorized": False,
        "confirmation": _BATCH_ARM_ACCEPTANCE_CONFIRMATION,
        "noAutomaticRetryAfterAttempt": True,
    }
    batch["batchPlanSha256"] = _canonical_sha256(batch)
    return batch


def plan_arm_template_acceptance_batch(
    members: list[dict[str, str]],
    *,
    shared_decisions_path: str | Path,
    validation_receipts: list[str | Path],
) -> dict[str, Any]:
    batch = _arm_acceptance_batch_plan(
        members,
        shared_decisions_path=shared_decisions_path,
        validation_receipts=validation_receipts,
    )
    first = _validated_members(members)[0]
    root = Path(first["solutionPath"])
    with using_run(root, first["runId"]):
        path = artifact_path(
            root,
            ARM_ACCEPTANCE_BATCH_PLAN,
            create_parent=True,
        )
        write_json_artifact(root, path, batch)
    return {**batch, "planPath": str(path)}


def _reserve_attempt(path: Path, value: dict[str, Any]) -> None:
    if path.is_symlink():
        raise ValueError("ARM acceptance receipt path cannot be a symlink")
    descriptor = os.open(path, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
    try:
        payload = (json.dumps(value, indent=2) + "\n").encode("utf-8")
        os.write(descriptor, payload)
        os.fsync(descriptor)
    finally:
        os.close(descriptor)


def _member_attempt_path(item: dict[str, Any]) -> Path:
    root = Path(item["solutionPath"])
    with using_run(root, item["runId"]):
        return artifact_path(
            root,
            f"{ARM_ACCEPTANCE_ATTEMPT_PREFIX}{item['deploymentName']}.json",
            create_parent=True,
        )


def _error_status(write_state: str | None) -> str:
    if write_state in {"failed", "canceled", "cancelled", "deleted"}:
        return "failed"
    if write_state:
        return "nonterminal"
    return "unknown"


def _recorded_provisioning_state(value: Any) -> str | None:
    if not isinstance(value, dict):
        return None
    properties = value.get("properties")
    if isinstance(properties, dict) and isinstance(properties.get("provisioningState"), str):
        return properties["provisioningState"]
    state = value.get("provisioningState")
    return state if isinstance(state, str) else None


def execute_arm_template_acceptance_batch(
    members: list[dict[str, str]],
    *,
    expected_batch_plan_sha256: str,
    shared_decisions_path: str | Path,
    validation_receipts: list[str | Path],
    actor: str,
    confirmation: str,
    state_dir: str | Path | None = None,
    command_runner: CommandRunner | None = None,
) -> dict[str, Any]:
    batch = _arm_acceptance_batch_plan(
        members,
        shared_decisions_path=shared_decisions_path,
        validation_receipts=validation_receipts,
    )
    if batch.get("status") != "ready":
        raise ValueError("ARM template acceptance batch is not ready")
    if (
        not isinstance(expected_batch_plan_sha256, str)
        or not _SHA256.fullmatch(expected_batch_plan_sha256)
        or batch.get("batchPlanSha256") != expected_batch_plan_sha256
        or confirmation != _BATCH_ARM_ACCEPTANCE_CONFIRMATION
    ):
        raise ValueError(
            "exact enumerated ARM template acceptance batch plan/confirmation does not match"
        )
    if not isinstance(actor, str) or not actor.strip():
        raise ValueError("ARM template acceptance requires an explicit approval actor")
    normalized = _validated_members(members)
    planned_by_member = {
        (item["solution"], item["runId"]): item for item in batch["members"]
    }
    attempt_paths: dict[tuple[str, str], Path] = {}
    for member in normalized:
        planned = planned_by_member[(member["solution"], member["runId"])]
        attempt_paths[(member["solution"], member["runId"])] = _member_attempt_path(planned)
    reservation_order = sorted(
        batch["members"],
        key=lambda item: (item["deploymentName"], item["solution"], item["runId"]),
    )
    canonical_first = reservation_order[0]
    first_root = Path(canonical_first["solutionPath"])
    first_run_id = canonical_first["runId"]
    with using_run(first_root, first_run_id):
        report_path = artifact_path(
            first_root,
            ARM_ACCEPTANCE_BATCH_REPORT,
            create_parent=True,
        )
        existing_batch = existing_artifact_path(first_root, ARM_ACCEPTANCE_BATCH_REPORT)
    if existing_batch.exists() or existing_batch.is_symlink():
        raise ValueError(
            "this ARM acceptance batch already has a durable attempt/receipt; reconcile it before any new write"
        )
    existing_attempts = [
        path
        for path in attempt_paths.values()
        if path.exists() or path.is_symlink()
    ]
    if existing_attempts:
        raise ValueError(
            "an ARM acceptance attempt already exists for a selected deployment identity; reconcile its durable outcome before any retry"
        )

    account_check = _verify_existing_cli_target(
        batch["target"],
        state_dir=state_dir,
        runner=command_runner,
    )
    if not (
        account_check.get("statusCode") == 0
        and account_check.get("tenantMatches") is True
        and account_check.get("subscriptionMatches") is True
    ):
        return {
            "schemaVersion": 1,
            "stage": batch["stage"],
            "status": "blocked",
            "target": batch["target"],
            "accountCheck": account_check,
            "writeAttempted": False,
            "environmentWritesAuthorized": False,
            "message": (
                account_check.get("error")
                or "existing Azure CLI account does not match the locked tenant and subscription; no login was attempted"
            ),
        }

    current = _arm_acceptance_batch_plan(
        members,
        shared_decisions_path=shared_decisions_path,
        validation_receipts=validation_receipts,
    )
    if current.get("batchPlanSha256") != expected_batch_plan_sha256:
        raise ValueError(
            "package, target, shared decisions, parameters, or V3.1 artifact changed after approval; no deployment attempted"
        )
    report: dict[str, Any] = {
        "schemaVersion": 1,
        "stage": batch["stage"],
        "status": "submitting",
        "batchPlanSha256": batch["batchPlanSha256"],
        "target": batch["target"],
        "sharedDecisionReceipt": batch["sharedDecisionReceipt"],
        "actor": actor.strip(),
        "approvedAt": _utc_now(),
        "confirmation": confirmation,
        "plannedWrites": [
            {
                "solution": item["solution"],
                "runId": item["runId"],
                "target": batch["target"],
                "deploymentName": item["deploymentName"],
                "mainTemplateSha256": item["mainTemplateSha256"],
                "mainTemplateSnapshotSha256": item["mainTemplateSnapshotSha256"],
                "parametersSha256": item["parametersSha256"],
                "validationReceiptSha256": item["validationReceipt"]["sha256"],
            }
            for item in batch["members"]
        ],
        "members": [
            {
                **item,
                "status": "pending",
                "deploymentId": None,
                "provisioningState": None,
                "commandExitCode": None,
                "error": None,
                "submittedParameters": None,
                "submittedMainTemplateSnapshotSha256": None,
            }
            for item in batch["members"]
        ],
        "resourceReadbackPerformed": False,
        "installationVerified": False,
        "activationPerformed": False,
        "alertParityPerformed": False,
        "qualificationCompleted": False,
        "retryAuthorized": False,
        "environmentWritesAuthorized": False,
    }
    with using_run(first_root, first_run_id):
        _reserve_attempt(
            report_path,
            {
                "schemaVersion": 1,
                "stage": batch["stage"],
                "status": "intent-reserved",
                "batchPlanSha256": batch["batchPlanSha256"],
                "deploymentIdentities": [
                    {
                        "solution": item["solution"],
                        "runId": item["runId"],
                        "target": batch["target"],
                        "deploymentName": item["deploymentName"],
                    }
                    for item in reservation_order
                ],
                "writeAttempted": False,
            },
        )
    reserved_members: set[tuple[str, str]] = set()

    def persist() -> None:
        report["updatedAt"] = _utc_now()
        with using_run(first_root, first_run_id):
            write_json_artifact(first_root, report_path, report)
        for member in report["members"]:
            key = (member["solution"], member["runId"])
            if key not in reserved_members:
                continue
            path = attempt_paths[key]
            with using_run(Path(member["solutionPath"]), member["runId"]):
                write_json_artifact(
                    Path(member["solutionPath"]),
                    path,
                    {
                        "schemaVersion": 1,
                        "stage": batch["stage"],
                        "batchPlanSha256": report["batchPlanSha256"],
                        "target": report["target"],
                        "member": member,
                        "updatedAt": report["updatedAt"],
                    },
                )

    for item in reservation_order:
        key = (item["solution"], item["runId"])
        member_record = next(
            entry
            for entry in report["members"]
            if (entry["solution"], entry["runId"]) == key
        )
        try:
            _reserve_attempt(
                attempt_paths[key],
                {
                    "schemaVersion": 1,
                    "stage": batch["stage"],
                    "status": "intent-reserved",
                    "batchPlanSha256": batch["batchPlanSha256"],
                    "target": batch["target"],
                    "deploymentName": item["deploymentName"],
                    "mainTemplateSha256": item["mainTemplateSha256"],
                    "mainTemplateSnapshotSha256": item["mainTemplateSnapshotSha256"],
                    "parametersSha256": item["parametersSha256"],
                    "validationReceiptSha256": item["validationReceipt"]["sha256"],
                    "writeAttempted": False,
                },
            )
            reserved_members.add(key)
            member_record["status"] = "intent-reserved"
        except FileExistsError:
            member_record["status"] = "reservation-conflict"
            member_record["error"] = (
                "a durable attempt already exists for this deployment identity; no member in this batch was submitted"
            )
            report["status"] = "partial-reservation"
            report["message"] = member_record["error"]
            for pending in report["members"]:
                if pending["status"] == "pending":
                    pending["status"] = "not-reserved"
            persist()
            return {**report, "reportPath": str(report_path)}
    report["status"] = "submitting"
    for entry in report["members"]:
        entry["status"] = "intent-reserved"
    persist()

    from .graph_client_config import azure_cli_profile, configured_azure_cli_profile

    profile = configured_azure_cli_profile(_state_dir(state_dir))
    for index, item in enumerate(normalized):
        current = _arm_acceptance_batch_plan(
            members,
            shared_decisions_path=shared_decisions_path,
            validation_receipts=validation_receipts,
        )
        if current.get("batchPlanSha256") != expected_batch_plan_sha256:
            entry = report["members"][index]
            entry["status"] = "blocked-before-write"
            entry["error"] = (
                "approved package, target, shared decisions, parameters, or V3.1 artifact changed before this member's ARM write"
            )
            report["status"] = (
                "partial"
                if any(
                    str(member.get("provisioningState") or "").casefold() == "succeeded"
                    for member in report["members"]
                )
                else "blocked"
            )
            report["message"] = entry["error"]
            persist()
            return {**report, "reportPath": str(report_path)}

        member_plan = next(
            value
            for value in current["members"]
            if value["solution"] == item["solution"]
            and value["runId"] == item["runId"]
        )
        parameters = [
            f"{name}={'true' if value is True else 'false' if value is False else value}"
            for name, value in sorted(member_plan["parameters"].items())
        ]
        snapshot_path = Path(member_plan["mainTemplateSnapshotPath"])
        if (
            snapshot_path.is_symlink()
            or not snapshot_path.is_file()
            or hashlib.sha256(snapshot_path.read_bytes()).hexdigest()
            != member_plan["mainTemplateSnapshotSha256"]
        ):
            entry = report["members"][index]
            entry["status"] = "blocked-before-write"
            entry["error"] = "approved ARM template snapshot is missing, unsafe, or has changed"
            report["status"] = (
                "partial"
                if any(
                    str(member.get("provisioningState") or "").casefold() == "succeeded"
                    for member in report["members"]
                )
                else "blocked"
            )
            report["message"] = entry["error"]
            persist()
            return {**report, "reportPath": str(report_path)}
        command = [
            "deployment",
            "group",
            "create",
            "--name",
            member_plan["deploymentName"],
            "--subscription",
            batch["target"]["subscriptionId"],
            "--resource-group",
            batch["target"]["resourceGroup"],
            "--template-file",
            str(snapshot_path),
            "--mode",
            "Incremental",
            "--parameters",
            *parameters,
            "--output",
            "json",
            "--only-show-errors",
        ]
        entry = report["members"][index]
        entry["status"] = "write-intent-persisted"
        entry["writeIntentAt"] = _utc_now()
        entry["submittedParameters"] = parameters
        entry["submittedMainTemplateSnapshotSha256"] = hashlib.sha256(
            snapshot_path.read_bytes()
        ).hexdigest()
        persist()
        with azure_cli_profile(profile):
            exit_code, deployment, error = _run_cli(
                command,
                runner=command_runner,
            )
        state = _deployment_provisioning_state(deployment)
        recorded_state = _recorded_provisioning_state(deployment)
        deployment_id = (
            deployment.get("id")
            if isinstance(deployment, dict) and isinstance(deployment.get("id"), str)
            else None
        )
        entry.update(
            {
                "status": "accepted" if state == "succeeded" else _error_status(state),
                "deploymentId": deployment_id,
                "provisioningState": recorded_state,
                "normalizedProvisioningState": state,
                "commandExitCode": exit_code,
                "error": error or None,
                "responseRecordedAt": _utc_now(),
            }
        )
        persist()
        if state != "succeeded":
            succeeded_before = any(
                str(member.get("provisioningState") or "").casefold() == "succeeded"
                for member in report["members"][: index + 1]
            )
            outcome = _error_status(state)
            report["status"] = (
                f"partial-{outcome}" if succeeded_before else outcome
            )
            report["message"] = (
                "ARM deployment did not return terminal provisioningState Succeeded; "
                "the remaining batch was not submitted and this attempt must not be retried blindly"
            )
            persist()
            return {**report, "reportPath": str(report_path)}

    report["status"] = "accepted"
    report["completedAt"] = _utc_now()
    report["message"] = (
        "Every enumerated Azure Resource Manager deployment returned provisioningState Succeeded. "
        "This receipt does not verify installed content, enable detections, establish parity, or complete Qualification."
    )
    persist()
    return {**report, "reportPath": str(report_path)}
