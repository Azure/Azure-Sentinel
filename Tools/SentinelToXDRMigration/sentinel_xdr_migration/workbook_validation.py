"""Versioned candidate ARM validation; no implicit cloud dispatch or legacy upgrades."""
from __future__ import annotations

import hashlib
import json
import re
import zipfile
import uuid
from pathlib import Path
from typing import Any, Callable, Mapping

from .arm_acceptance_support import _canonical_sha256, _deployment_provisioning_state
from .content_paths import content_path
from .target_context import workspace_identity

LAB_ARM_CONFIRMATION = "I approve the exact current candidate ARM deployment validation"
_HASH = re.compile(r"^[a-f0-9]{64}$")
_TARGET_KEYS = ("tenantId", "subscriptionId", "resourceGroup", "workspaceResourceId", "workspaceCustomerId")
_GATES = ("conversion", "review", "structure", "package")
_FLAG_KINDS = {
    "DeployAnalyticsRule": "AnalyticsRule", "DeployPlaybook": "Playbook",
    "DeployWorkbook": "Workbook", "DeployDefenderWorkbook": "DefenderWorkbook",
    "DeployDataConnector": "DataConnector", "DeployCustomDetection": "CustomDetection",
    "DeployHuntingQuery": "HuntingQuery", "DeployInvestigationQuery": "InvestigationQuery",
    "DeployParser": "Parser", "DeployWatchlist": "Watchlist", "DeployNotebook": "Notebook",
    "DeployAutomationRule": "AutomationRule", "DeploySummaryRule": "SummaryRule",
}


def _utc_now() -> str:
    from .arm_acceptance import _utc_now as now
    return now()


def _parse_build_validation_receipt(*args: Any, **kwargs: Any) -> dict[str, Any]:
    from .arm_acceptance import _parse_build_validation_receipt as parse
    return parse(*args, **kwargs)


def arm_validation_method(context: Mapping[str, Any]) -> str:
    """Absent capability preserves legacy ARM-TTK; new contexts must persist a method."""
    if "workbookCapabilityVersion" not in context:
        return "arm-ttk"
    if type(context["workbookCapabilityVersion"]) is not int or context["workbookCapabilityVersion"] != 1:
        raise ValueError("unsupported workbook capability version")
    method = context.get("armValidationMethod")
    if method not in {"arm-ttk", "lab-deployment"}:
        raise ValueError("versioned context requires an explicit persisted ARM validation method")
    if context.get("workflowProfile") not in {"authoring", "qualification"} or context.get("profileSelectionConfirmed") is not True:
        raise ValueError("ARM validation requires an explicitly selected workflow profile")
    if method == "arm-ttk" and context["workflowProfile"] != "authoring":
        raise ValueError("the new Qualification route requires lab-deployment")
    if context["workflowProfile"] == "qualification" and context.get("targetContextLocked") is not True:
        raise ValueError("Qualification candidate validation requires its existing locked target")
    return method


def _digest_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _sealed(value: Mapping[str, Any], field: str) -> bool:
    body = dict(value)
    digest = body.pop(field, None)
    return isinstance(digest, str) and _HASH.fullmatch(digest) is not None and _canonical_sha256(body) == digest


def create_arm_candidate(
    context: Mapping[str, Any], *, solution: str | Path, package_report: str | Path,
    validation_receipt: str | Path, prerequisite_evidence: Mapping[str, Mapping[str, str]],
) -> dict[str, Any]:
    """Verify current V3.1 artifacts and official static receipt without prior acceptance.

    The integration owner produces four Authoring gate receipts with status=passed,
    packageInputSha256, and workflowRunId, after its existing conversion/review/
    structure/selection checks. Static/package gates also bind packageArtifactsSha256.
    Qualification additionally requires its existing runtime/locked-target gate.
    References here bind their exact current bytes.
    """
    from .packaging import package_input_file_hashes, package_input_identity, validate_v31_target_version

    method = arm_validation_method(context)
    if context.get("workbookCapabilityVersion") != 1:
        raise ValueError("candidate validation cannot upgrade a legacy workflow")
    if not isinstance(context.get("runId"), str) or not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_.-]{0,95}", context["runId"]):
        raise ValueError("candidate requires a safe exact workflow run identity")
    source_root = Path(solution)
    if source_root.is_symlink():
        raise ValueError("candidate solution cannot be a symlink")
    root = source_root.resolve(strict=True)
    report_path = content_path(root, package_report)
    report = json.loads(report_path.read_text(encoding="utf-8-sig"))
    if report.get("packager") != "V3.1" or report.get("workflowRunId") != context.get("runId") or not context.get("runId"):
        raise ValueError("candidate must belong to the selected V3.1 workflow run")
    if report.get("armValidationMethod") != method:
        raise ValueError("candidate packager method binding is missing or mismatched")
    if not report.get("packageAttemptId"):
        raise ValueError("candidate package attempt identity is missing")
    validate_v31_target_version(report.get("version"))
    inputs = package_input_identity(root)
    recorded_inputs = (report.get("packageInputs") or {}).get("after")
    if (
        not isinstance(recorded_inputs, dict)
        or type(recorded_inputs.get("fileCount")) is not int
        or any(recorded_inputs.get(key) != value for key, value in inputs.items())
    ):
        raise ValueError("candidate package inputs are stale")
    current_files = package_input_file_hashes(root)
    recorded_files = recorded_inputs.get("files")
    manifest_sha256 = _canonical_sha256(
        [{"path": path, "sha256": digest} for path, digest in current_files.items()]
    )
    if (
        not isinstance(recorded_files, dict)
        or recorded_files != current_files
        or len(current_files) != inputs["fileCount"]
        or manifest_sha256 != inputs["sha256"]
    ):
        raise ValueError("candidate package input file manifest is missing, incomplete or stale")
    post_arm_workbook_qualification = context.get("workbookQualificationAfterArm") is True
    if post_arm_workbook_qualification:
        from .workbook_workflow import has_analytic_rules

        if (
            context["workflowProfile"] != "qualification"
            or has_analytic_rules(root)
            or report.get("xdrDetectionCount") not in (None, 0)
        ):
            raise ValueError("post-ARM workbook qualification cannot bypass detection runtime prerequisites")
    required_gates = (
        (*_GATES, "qualification")
        if context["workflowProfile"] == "qualification" and not post_arm_workbook_qualification
        else _GATES
    )
    if set(prerequisite_evidence) != set(required_gates):
        raise ValueError("candidate requires fresh conversion, review, structure and package gate evidence")
    gates = {}
    for name, reference in prerequisite_evidence.items():
        path = content_path(root, reference["path"])
        if _digest_file(path) != reference.get("sha256"):
            raise ValueError(f"{name} gate evidence is stale")
        gate = json.loads(path.read_text(encoding="utf-8-sig"))
        if gate.get("status") != "passed" or gate.get("packageInputSha256") != inputs["sha256"] or gate.get("workflowRunId") != context["runId"]:
            raise ValueError(f"{name} gate did not pass for current inputs/run")
        if name in {"structure", "package"} and gate.get("packageArtifactsSha256") != report.get("packageArtifactsSha256"):
            raise ValueError(f"{name} gate is not bound to exact current candidate artifacts")
        if name == "qualification" and (
            gate.get("qualificationRuntimeVerified") is not True or gate.get("target") != _target(context)
        ):
            raise ValueError("Qualification's existing runtime/target prerequisites remain mandatory")
        gates[name] = dict(reference)
    hashes = report.get("packageArtifactHashes")
    if not isinstance(hashes, dict) or set(hashes) != {"mainTemplate", "createUiDefinition", "testParameters", "zip"}:
        raise ValueError("candidate must bind every V3.1 artifact")
    paths = {}
    for name, digest in hashes.items():
        path = content_path(root, report[name])
        if not isinstance(digest, str) or not _HASH.fullmatch(digest) or _digest_file(path) != digest:
            raise ValueError(f"candidate {name} artifact is stale")
        paths[name] = path
    if _canonical_sha256(hashes) != report.get("packageArtifactsSha256"):
        raise ValueError("candidate artifact aggregate hash is stale")
    with zipfile.ZipFile(paths["zip"]) as archive:
        names = archive.namelist()
        if len(names) != len(set(names)) or any(
            ".." in Path(name.replace("\\", "/")).parts or Path(name).is_absolute()
            or any(part.lower() in {"logs", "reports", "evidence", ".env"} or part.lower().startswith(".env.") for part in name.replace("\\", "/").split("/"))
            for name in names
        ):
            raise ValueError("candidate ZIP contains unsafe, duplicate or operational entries")
        for name in ("mainTemplate", "createUiDefinition"):
            matches = [member for member in names if Path(member).name == paths[name].name]
            if len(matches) != 1 or hashlib.sha256(archive.read(matches[0])).hexdigest() != hashes[name]:
                raise ValueError(f"candidate ZIP {name} does not match exact artifact bytes")
    package_files = []
    for path in sorted((root / "Package").rglob("*")):
        if path.is_symlink():
            raise ValueError("candidate Package contains a symlink")
        if path.is_file():
            package_files.append({"path": path.relative_to(root / "Package").as_posix(), "sha256": _digest_file(path)})
    package_files.sort(key=lambda item: item["path"])
    identity = {
        "version": report["version"], "packageAttemptId": report["packageAttemptId"],
        "workflowRunId": context["runId"], "packageInputSha256": inputs["sha256"],
        "packageArtifactHashes": hashes, "recordedPackageArtifactHashes": hashes,
        "packageReportSha256": _digest_file(report_path),
        "packageArtifactsSha256": report["packageArtifactsSha256"],
        "packageContentSha256": hashlib.sha256(json.dumps(package_files, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()).hexdigest(),
    }
    receipt = _parse_build_validation_receipt(
        root, validation_receipt, package_report_path=report_path,
        package_identity=identity, arm_validation_method=method,
    )
    candidate = {
        "schemaVersion": 1, "workbookCapabilityVersion": 1, "armValidationMethod": method,
        "status": "candidate-generated", "accepted": False, "solutionPath": str(root),
        "workflowProfile": context["workflowProfile"],
        "runId": context["runId"], "packageReport": report_path.relative_to(root).as_posix(),
        "validationReceipt": receipt, "prerequisiteEvidence": gates, "packageIdentity": identity,
        "artifactPaths": {name: path.relative_to(root).as_posix() for name, path in paths.items()},
        "mainTemplateSha256": hashes["mainTemplate"],
    }
    candidate["candidateSha256"] = _canonical_sha256(candidate)
    return candidate


def _target(target: Mapping[str, Any]) -> dict[str, str]:
    if any(not isinstance(target.get(key), str) or not target[key].strip() for key in _TARGET_KEYS):
        raise ValueError("selected lab requires complete tenant/subscription/workspace identity")
    result = {key: target[key] for key in _TARGET_KEYS}
    for key in ("tenantId", "workspaceCustomerId"):
        if str(uuid.UUID(result[key])) != result[key].lower():
            raise ValueError(f"selected lab has an invalid {key}")
    identity = workspace_identity(result["workspaceResourceId"])
    if any(str(identity[key]).casefold() != result[key].casefold() for key in ("subscriptionId", "resourceGroup")):
        raise ValueError("selected lab subscription/resource group conflicts with workspace")
    return result


def refresh_arm_candidate(context: Mapping[str, Any], candidate: Mapping[str, Any]) -> dict[str, Any]:
    """Recompute all input, artifact, official receipt and prerequisite bindings."""
    if not _sealed(candidate, "candidateSha256"):
        raise ValueError("candidate receipt is malformed")
    current = create_arm_candidate(
        context, solution=candidate["solutionPath"], package_report=candidate["packageReport"],
        validation_receipt=candidate["validationReceipt"]["path"],
        prerequisite_evidence=candidate["prerequisiteEvidence"],
    )
    if current["candidateSha256"] != candidate["candidateSha256"]:
        raise ValueError("candidate evidence changed")
    return current


def _arguments(text: str) -> list[str]:
    args, start, depth, quoted = [], 0, 0, False
    index = 0
    while index < len(text):
        char = text[index]
        if char == "'":
            if quoted and index + 1 < len(text) and text[index + 1] == "'":
                index += 2
                continue
            quoted = not quoted
        elif not quoted:
            if char == "(":
                depth += 1
            elif char == ")":
                depth -= 1
            elif char == "," and depth == 0:
                args.append(text[start:index].strip())
                start = index + 1
        index += 1
    if quoted or depth != 0:
        raise ValueError("unresolvable ARM expression")
    return args + ([text[start:].strip()] if text[start:].strip() else [])


def _resolve(value: Any, template: Mapping[str, Any], parameters: Mapping[str, Any], target: Mapping[str, str], *, depth: int = 0) -> Any:
    if depth > 30:
        raise ValueError("recursive ARM expression cannot be resolved safely")
    if not isinstance(value, str) or not value.startswith("["):
        return value
    if value.startswith("[["):
        return value[1:]
    if not value.endswith("]"):
        raise ValueError("unresolvable ARM expression")

    def expression(text: str) -> Any:
        if re.fullmatch(r"'(?:[^']|'')*'", text):
            return text[1:-1].replace("''", "'")
        if text.casefold() in {"true", "false"}:
            return text.casefold() == "true"
        if re.fullmatch(r"-?\d+", text):
            return int(text)
        fixed = {"tenant().tenantId": target["tenantId"], "subscription().subscriptionId": target["subscriptionId"],
                 "resourceGroup().name": target["resourceGroup"],
                 "resourceGroup().id": f"/subscriptions/{target['subscriptionId']}/resourceGroups/{target['resourceGroup']}"}
        if text in fixed:
            return fixed[text]
        prop_match = re.fullmatch(r"variables\((.*)\)\.([A-Za-z_][A-Za-z0-9_]*)", text, re.DOTALL)
        if prop_match:
            var_args = [expression(arg) for arg in _arguments(prop_match.group(1))]
            if len(var_args) == 1:
                variables = template.get("variables") or {}
                obj = variables.get(var_args[0])
                if isinstance(obj, Mapping) and prop_match.group(2) in obj:
                    return _resolve(obj[prop_match.group(2)], template, parameters, target, depth=depth + 1)
            raise ValueError("ARM variable property is not bound")
        match = re.fullmatch(r"([A-Za-z]+)\((.*)\)", text, re.DOTALL)
        if not match:
            raise ValueError(f"unresolvable ARM scope/condition expression: {text}")
        function = match[1].casefold()
        args = [expression(arg) for arg in _arguments(match[2])]
        if function == "parameters" and len(args) == 1:
            if args[0] not in parameters:
                definition = (template.get("parameters") or {}).get(args[0])
                if not isinstance(definition, dict) or "defaultValue" not in definition:
                    raise ValueError("ARM parameter is not bound")
                return _resolve(definition["defaultValue"], template, parameters, target, depth=depth + 1)
            return parameters[args[0]]
        if function == "variables" and len(args) == 1:
            variables = template.get("variables") or {}
            if args[0] not in variables:
                raise ValueError("ARM variable is not bound")
            return _resolve(variables[args[0]], template, parameters, target, depth=depth + 1)
        if function == "concat":
            return "".join(str(arg) for arg in args)
        if function == "format" and args and isinstance(args[0], str):
            return args[0].format(*args[1:])
        if function == "equals" and len(args) == 2:
            return args[0] == args[1]
        if function in {"and", "or"} and args and all(type(arg) is bool for arg in args):
            return all(args) if function == "and" else any(args)
        if function == "not" and len(args) == 1 and type(args[0]) is bool:
            return not args[0]
        if function == "if" and len(args) == 3 and type(args[0]) is bool:
            return args[1] if args[0] else args[2]
        if function == "resourceid" and len(args) >= 2 and isinstance(args[0], str) and "/" in args[0]:
            kinds = args[0].split("/")
            if len(kinds) != len(args):
                raise ValueError("resourceId scope arguments are ambiguous")
            suffix = "/".join(part for kind, name in zip(kinds[1:], args[1:]) for part in (kind, str(name)))
            return f"{fixed['resourceGroup().id']}/providers/{kinds[0]}/{suffix}"
        raise ValueError(f"unresolvable ARM scope/condition function: {function}")

    return expression(value[1:-1].strip())


def _resource_inventory(template: dict[str, Any], parameters: dict[str, Any], target: dict[str, str]) -> list[dict[str, Any]]:
    inventory: list[dict[str, Any]] = []
    rg_scope = f"/subscriptions/{target['subscriptionId']}/resourceGroups/{target['resourceGroup']}"
    tenant_scope = f"/tenants/{target['tenantId']}"
    workspace = workspace_identity(target["workspaceResourceId"])["workspaceName"]

    def walk(document: dict[str, Any], values: dict[str, Any], inherited: str, path: str, depth: int = 0) -> None:
        if depth > 25:
            raise ValueError("nested ARM scope depth exceeded")
        imports = document.get("imports") or {}
        if not isinstance(imports, dict):
            raise ValueError("unknown ARM imports")
        for alias, imported in imports.items():
            if not isinstance(imported, dict) or imported.get("provider") != "MicrosoftSecurity" or imported.get("version") != "1.0.0":
                raise ValueError("unsupported ARM extension scope")
            config = imported.get("config") or {}
            if not isinstance(config, dict) or set(config) - {"tenantId"}:
                raise ValueError("unknown MicrosoftSecurity extension configuration")
            tenant = _resolve(config.get("tenantId", target["tenantId"]), document, values, target)
            if str(tenant).casefold() != target["tenantId"].casefold():
                raise ValueError("MicrosoftSecurity import crosses the approved tenant")
        resources = document.get("resources", [])
        if isinstance(resources, dict):
            entries = list(resources.items())
        elif isinstance(resources, list):
            entries = list(enumerate(resources))
        else:
            raise ValueError("ARM resources must be a list or symbolic object")
        for key, resource in entries:
            if not isinstance(resource, dict) or "copy" in resource:
                raise ValueError("resource copy/unknown inventory cannot be bounded safely")
            condition = _resolve(resource.get("condition", True), document, values, target)
            if type(condition) is not bool:
                raise ValueError("ARM resource condition is unresolved")
            if not condition:
                continue
            kind = resource.get("type")
            if not isinstance(kind, str) or "[" in kind or not re.fullmatch(r"[A-Za-z][A-Za-z0-9.]*/[A-Za-z0-9/]+(?:@[A-Za-z0-9.-]+)?", kind):
                raise ValueError("unknown ARM resource type")
            kind = kind.split("@", 1)[0]
            if kind.casefold().startswith(("microsoft.authorization/", "microsoft.graph/")):
                raise ValueError("deployment consent excludes role/permission grants")
            imported_alias = resource.get("import")
            if imported_alias is not None and imported_alias not in imports:
                raise ValueError("resource refers to an unknown ARM extension")
            is_extension = imported_alias is not None
            if kind.casefold().startswith("microsoft.security/") and not is_extension:
                raise ValueError("MicrosoftSecurity resource scope requires a supported import")
            scope = _resolve(resource.get("scope", tenant_scope if is_extension else inherited), document, values, target)
            allowed_scope = tenant_scope if is_extension else inherited
            if not isinstance(scope, str) or scope.casefold() not in {allowed_scope.casefold(), target["workspaceResourceId"].casefold()}:
                raise ValueError("resource scope is unknown or crosses selected lab")
            props = resource.get("properties") or {}
            if not isinstance(props, dict):
                raise ValueError("unknown resource properties")
            if is_extension and kind.casefold() not in {"microsoft.security/workbooks", "microsoft.security/detectionrules"}:
                raise ValueError("unsupported MicrosoftSecurity resource scope contract")
            if kind.casefold().endswith(("/alertrules", "/detectionrules")):
                enabled_val = props.get("isEnabled", props.get("enabled"))
                if enabled_val is not None:
                    enabled_val = _resolve(enabled_val, document, values, target)
                status_val = _resolve(props.get("status"), document, values, target) if "status" in props else None
                if enabled_val is not False and str(status_val).casefold() != "disabled":
                    raise ValueError("detection deployment requires explicitly disabled content")
            if "microsoft.operationalinsights/workspaces/" in kind.casefold():
                name = resource.get("name")
                raw_name = str(name)
                var_ref = re.fullmatch(r"\[variables\('([^']+)'\)(?:\.([A-Za-z_][A-Za-z0-9_]*))?\]", raw_name.strip())
                if var_ref:
                    var_entry = (document.get("variables") or {}).get(var_ref.group(1))
                    if var_ref.group(2) and isinstance(var_entry, Mapping):
                        var_entry = var_entry.get(var_ref.group(2))
                    if isinstance(var_entry, str):
                        raw_name = var_entry
                # Registration suffixes may use uniqueString; only the workspace prefix
                # must be proven here, not fabricated by an approximate ARM evaluator.
                prefix = re.match(r"^\[concat\(parameters\('workspace'\),\s*'(/[^']*)'", raw_name)
                if not prefix:
                    resolved_name = _resolve(name, document, values, target)
                    if not isinstance(resolved_name, str) or not resolved_name.startswith(workspace + "/"):
                        raise ValueError("workspace-scoped resource name is not bound to selected workspace")
                if scope.casefold() != rg_scope.casefold():
                    raise ValueError("workspace resource cannot have a tenant/extension scope")
            location = f"{path}/resources/{key}"
            inventory.append({"path": location, "type": kind, "scope": scope, "name": resource.get("name"), "import": imported_alias})
            if kind.casefold() == "microsoft.resources/deployments":
                if props.get("mode") != "Incremental" or "templateLink" in props:
                    raise ValueError("only inline Incremental nested deployments are supported")
                for field, expected in (("subscriptionId", target["subscriptionId"]), ("resourceGroup", target["resourceGroup"])):
                    if field in resource and str(_resolve(resource[field], document, values, target)).casefold() != expected.casefold():
                        raise ValueError("nested deployment crosses selected lab")
                nested = props.get("template")
                if not isinstance(nested, dict):
                    raise ValueError("nested deployment template is unresolved")
                evaluation_scope = (props.get("expressionEvaluationOptions") or {}).get("scope", "outer")
                if evaluation_scope not in {"inner", "outer"}:
                    raise ValueError("unknown nested expression scope")
                child_values = {}
                for name, binding in (props.get("parameters") or {}).items():
                    if not isinstance(binding, dict) or set(binding) != {"value"}:
                        raise ValueError("nested parameter binding is unresolved")
                    child_values[name] = _resolve(binding["value"], document, values, target)
                walk(nested, child_values if evaluation_scope == "inner" else values, scope, location + "/properties/template", depth + 1)
            if "resources" in resource:
                raise ValueError("relative child resources require an explicit supported scope contract")
    walk(template, parameters, rg_scope, "")
    return inventory


def _expected_workbook_contracts(template: Mapping[str, Any], selected: bool) -> list[dict[str, Any]]:
    if not selected:
        return []
    installations, registrations, install_templates = {}, {}, {}

    def installed_literals(value: Any) -> Any:
        if isinstance(value, str) and value.startswith("[["):
            return value[1:]
        if isinstance(value, dict):
            return {key: installed_literals(item) for key, item in value.items()}
        if isinstance(value, list):
            return [installed_literals(item) for item in value]
        return value

    def walk(document: Mapping[str, Any]) -> None:
        resources = document.get("resources") or []
        for resource in resources.values() if isinstance(resources, dict) else resources:
            props = resource.get("properties") or {}
            kind = str(resource.get("type") or "").split("@", 1)[0].casefold()
            if kind == "microsoft.security/workbooks":
                notebook = props.get("content")
                if not isinstance(notebook, dict) or notebook.get("version") != "Notebook/1.0":
                    raise ValueError("workbook installation has no complete Notebook content")
                provenance = notebook.get("contentProvenance")
                quartet = {"packageId", "packageVersion", "contentId", "contentVersion"}
                if not isinstance(provenance, dict) or set(provenance) != quartet:
                    raise ValueError("workbook installation provenance must be the exact resolved quartet")
                cid = provenance["contentId"]
                if cid in installations:
                    raise ValueError("duplicate installed workbook content identity")
                installations[cid] = {"contentId": cid, "instanceId": props.get("id"),
                                      "contentSha256": _canonical_sha256(installed_literals(notebook)), "contentProvenance": installed_literals(provenance)}
                install_templates[cid] = _canonical_sha256(document)
            if props.get("contentKind") == "DefenderWorkbook":
                cid = props.get("contentId")
                if cid in registrations:
                    raise ValueError("duplicate workbook registration identity")
                registrations[cid] = props
            if kind == "microsoft.resources/deployments" and isinstance(props.get("template"), dict):
                walk(props["template"])
    walk(template)
    if not installations or set(installations) != set(registrations):
        raise ValueError("selected workbook installation/registration inventory is incomplete")
    result = []
    for cid, installation in sorted(installations.items()):
        registration = registrations[cid]
        provenance = registration.get("contentProvenance")
        if not isinstance(provenance, dict) or any(provenance.get(key) != value for key, value in installation["contentProvenance"].items()):
            raise ValueError("workbook registration provenance mismatches installation")
        iid = installation["instanceId"]
        if not isinstance(iid, str) or iid == cid or str(uuid.UUID(iid)) != iid or str(uuid.UUID(cid)) != cid:
            raise ValueError("installed workbook identity must be distinct")
        if _canonical_sha256(registration.get("mainTemplate")) != install_templates[cid]:
            raise ValueError("registered workbook installation template differs from candidate install")
        quartet = installation["contentProvenance"]
        if any(registration.get(field) != quartet[provenance_field] for field, provenance_field in (
            ("contentId", "contentId"), ("version", "contentVersion"),
            ("packageId", "packageId"), ("packageVersion", "packageVersion"),
        )):
            raise ValueError("registered workbook content/package version/identity mismatches installation")
        registration_contract = {
            "contentId": cid, "contentKind": "DefenderWorkbook", "version": registration.get("version"),
            "packageId": registration.get("packageId"), "packageVersion": registration.get("packageVersion"),
            "contentProvenance": provenance,
            "storedTemplateSha256": _canonical_sha256(registration.get("mainTemplate")),
        }
        result.append({"contentId": cid, "instanceId": iid,
                       "installation": installation, "registration": registration_contract,
                       "repeatInstallation": installation, "update": installation})
    return result


def _candidate_scope_plan(context: Mapping[str, Any], candidate: Mapping[str, Any], *, target: Mapping[str, Any], selected_flags: Mapping[str, bool], expected_workbooks: list[dict[str, Any]] | None = None, lab_route: bool) -> dict[str, Any]:
    method = arm_validation_method(context)
    if context.get("workbookCapabilityVersion") != 1 or (lab_route and method != "lab-deployment"):
        raise ValueError("lab candidate route requires the explicit versioned capability")
    if not _sealed(candidate, "candidateSha256") or candidate.get("status") != "candidate-generated" or candidate.get("accepted") is not False or candidate.get("armValidationMethod") != method:
        raise ValueError("lab validation requires an intact unaccepted candidate")
    if candidate.get("runId") != context.get("runId") or candidate.get("workflowProfile") != context["workflowProfile"]:
        raise ValueError("candidate belongs to another workflow run")
    lab = _target(target)
    if context["workflowProfile"] == "qualification" and lab != _target(context):
        raise ValueError("candidate lab differs from Qualification's locked target")
    root = Path(candidate["solutionPath"])
    template_path = content_path(root, candidate["artifactPaths"]["mainTemplate"])
    if _digest_file(template_path) != candidate["mainTemplateSha256"]:
        raise ValueError("candidate template changed")
    template = json.loads(template_path.read_text(encoding="utf-8-sig"))
    definitions = template.get("parameters") or {}
    declared = {name for name in definitions if name.startswith("Deploy")}
    if set(selected_flags) != declared or any(type(value) is not bool for value in selected_flags.values()) or declared - set(_FLAG_KINDS):
        raise ValueError("every declared content flag requires an exact supported boolean selection")
    parameters = {}
    for name, definition in definitions.items():
        if not isinstance(definition, dict):
            raise ValueError("malformed ARM parameter")
        if name in selected_flags:
            if definition.get("type") != "bool":
                raise ValueError("Deploy flags must be boolean")
            parameters[name] = selected_flags[name]
        elif name == "workspace":
            parameters[name] = workspace_identity(lab["workspaceResourceId"])["workspaceName"]
        elif name == "workspace-location" and isinstance(target.get("workspaceLocation"), str) and target["workspaceLocation"]:
            parameters[name] = target["workspaceLocation"]
        elif "defaultValue" in definition:
            continue
        else:
            raise ValueError(f"unbound required ARM parameter: {name}")
        if not isinstance(parameters[name], (str, bool, int, float)):
            raise ValueError("candidate ARM parameters must be explicit scalar values")
    inventory = _resource_inventory(template, parameters, lab)
    contracts = _expected_workbook_contracts(template, selected_flags.get("DeployDefenderWorkbook") is True)
    if expected_workbooks is not None and expected_workbooks != contracts:
        raise ValueError("expected workbook readback contract does not match candidate template")
    body = {
        "schemaVersion": 1, "workbookCapabilityVersion": 1, "status": "ready",
        "armValidationMethod": method, "runId": candidate["runId"],
        "deploymentAuthorizedRoute": lab_route,
        "purpose": "lab-arm-validation" if lab_route else "workbook-contract-readback",
        "candidateSha256": candidate["candidateSha256"], "target": lab,
        "solutionPath": candidate["solutionPath"],
        "selectedFlags": dict(selected_flags), "parameters": parameters,
        "mainTemplateSha256": candidate["mainTemplateSha256"],
        "packageIdentity": candidate["packageIdentity"], "resources": inventory,
        "artifactPaths": candidate["artifactPaths"], "prerequisiteEvidence": candidate["prerequisiteEvidence"],
        "validationReceiptFingerprint": {key: candidate["validationReceipt"].get(key) for key in ("path", "sha256", "bindingPath", "bindingSha256")},
        "scope": {"lab": lab, "operations": ["arm-incremental-deployment"],
                  "resourceTypes": sorted({item["type"] for item in inventory} | {"Microsoft.Resources/deployments"}),
                  "contentTypes": sorted({_FLAG_KINDS[name] for name, selected in selected_flags.items() if selected})},
        "writeCount": 1, "resourceCount": len(inventory), "confirmation": LAB_ARM_CONFIRMATION,
        "installationVerified": False, "registrationVerified": False,
        "uiVerified": False, "parityVerified": False, "accepted": False,
        "expectedWorkbooks": contracts,
    }
    body["planSha256"] = _canonical_sha256(body)
    return body


def plan_lab_arm_validation(context: Mapping[str, Any], candidate: Mapping[str, Any], *, target: Mapping[str, Any], selected_flags: Mapping[str, bool], expected_workbooks: list[dict[str, Any]] | None = None) -> dict[str, Any]:
    """Local-only exact execution plan; selected flags never default to all-true."""
    return _candidate_scope_plan(context, candidate, target=target, selected_flags=selected_flags,
                                 expected_workbooks=expected_workbooks, lab_route=True)


def plan_workbook_contract_verification(context: Mapping[str, Any], candidate: Mapping[str, Any], *, target: Mapping[str, Any], selected_flags: Mapping[str, bool]) -> dict[str, Any]:
    """Read-only expected contract for either method; never a deployment plan."""
    return _candidate_scope_plan(context, candidate, target=target, selected_flags=selected_flags, lab_route=False)


def review_lab_arm_scope(plan: Mapping[str, Any], *, actor: str, approval_reference: str, approved: bool) -> dict[str, Any]:
    if not _sealed(plan, "planSha256") or plan.get("status") != "ready" or plan.get("deploymentAuthorizedRoute") is not True or plan.get("armValidationMethod") != "lab-deployment":
        raise ValueError("review requires an intact current lab scope plan")
    if not actor.strip() or not approval_reference.strip() or type(approved) is not bool:
        raise ValueError("scope review requires affirmative decision, actor and approval reference")
    return {
        "schemaVersion": 1, "consentPolicyVersion": 1,
        "status": "approved" if approved else "declined", "scope": plan["scope"],
        "actor": actor.strip(), "approvalReference": approval_reference.strip(),
        "recordedAt": _utc_now(), "withdrawn": False,
        "deploymentOnly": True, "activationAuthorized": False, "ingestionAuthorized": False,
        "deletionAuthorized": False, "grantsAuthorized": False, "cleanupAuthorized": False,
        "reviewedPlanSha256": plan["planSha256"],
    }


def withdraw_lab_arm_scope(consent: Mapping[str, Any], *, actor: str, withdrawal_reference: str) -> dict[str, Any]:
    if not actor.strip() or not withdrawal_reference.strip():
        raise ValueError("withdrawal requires actor and reference")
    return {**consent, "status": "withdrawn", "withdrawn": True, "withdrawalActor": actor.strip(),
            "withdrawalReference": withdrawal_reference.strip(), "withdrawnAt": _utc_now()}


def check_lab_arm_scope(plan: Mapping[str, Any], consent: Mapping[str, Any] | None) -> dict[str, Any]:
    reasons = []
    if not _sealed(plan, "planSha256") or plan.get("deploymentAuthorizedRoute") is not True or plan.get("armValidationMethod") != "lab-deployment":
        reasons.append("execution plan is stale or malformed")
    if not isinstance(consent, Mapping) or consent.get("consentPolicyVersion") != 1 or consent.get("status") != "approved" or consent.get("withdrawn") is not False:
        reasons.append("missing, declined, legacy or withdrawn scope approval")
    else:
        scope = consent.get("scope")
        if not isinstance(scope, Mapping):
            return {"status": "blocked", "reasons": ["malformed approved scope"]}
        approved_lab = scope.get("lab")
        if not isinstance(approved_lab, Mapping) or any(
            str(approved_lab.get(key, "")).casefold() != str(plan["scope"]["lab"][key]).casefold()
            for key in _TARGET_KEYS
        ):
            reasons.append("lab changed; new approval required")
        for field in ("operations", "resourceTypes", "contentTypes"):
            approved = scope.get(field)
            if not isinstance(approved, list) or any(not isinstance(item, str) or not item for item in approved) or not set(plan["scope"][field]).issubset(set(approved)):
                reasons.append(f"new {field}; new approval required")
        if not consent.get("actor") or not consent.get("approvalReference") or consent.get("deploymentOnly") is not True or any(consent.get(key) is not False for key in ("activationAuthorized", "ingestionAuthorized", "deletionAuthorized", "grantsAuthorized", "cleanupAuthorized")):
            reasons.append("approval identity or deployment-only boundary is invalid")
    return {"status": "ready" if not reasons else "blocked", "reasons": reasons}


def execute_lab_arm_validation(
    context: Mapping[str, Any], candidate: Mapping[str, Any], *, target: Mapping[str, Any],
    selected_flags: Mapping[str, bool], expected_plan_sha256: str, actor: str,
    approval_reference: str, confirmation: str, evidence_directory: str | Path,
    refresh_candidate: Callable[[], Mapping[str, Any]], read_consent: Callable[[], Mapping[str, Any]],
    identity_check: Callable[[Mapping[str, Any]], Mapping[str, Any]],
    command_runner: Callable[[list[str]], tuple[int, Any, str]],
    expected_workbooks: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    """One reserved executor; callers supply existing auth/provider/consent readers.

    No default dispatcher exists. The command runner receives Azure CLI arguments
    (without executable); the integration adapter may use the existing _run_cli.
    """
    from .arm_acceptance import _error_status, _recorded_provisioning_state, _reserve_attempt, _write_template_snapshot

    plan = plan_lab_arm_validation(context, candidate, target=target, selected_flags=selected_flags, expected_workbooks=expected_workbooks)
    if plan["planSha256"] != expected_plan_sha256 or confirmation != LAB_ARM_CONFIRMATION or not actor.strip() or not approval_reference.strip():
        raise ValueError("immediate exact-plan write approval is missing or stale")
    consent = check_lab_arm_scope(plan, read_consent())
    if consent["status"] != "ready":
        return {**consent, "writeAttempted": False, "accepted": False}
    directory = Path(evidence_directory)
    root = Path(candidate["solutionPath"]).resolve(strict=True)
    expected_directory = root / "Logs" / "sentinel-xdr-migration" / candidate["runId"]
    if directory.resolve() != expected_directory or any(parent.is_symlink() for parent in (directory, *directory.parents)):
        raise ValueError("attempt evidence must remain in the exact selected run Logs directory without links")
    directory.mkdir(parents=True, exist_ok=True)
    identity = _canonical_sha256({"solution": str(root), "runId": candidate["runId"], "target": plan["target"], "candidateSha256": candidate["candidateSha256"], "parameters": plan["parameters"], "approvalReference": approval_reference})
    attempt_path = directory / f"arm-validation-attempt-{identity}.json"
    if attempt_path.exists() or attempt_path.is_symlink():
        raise ValueError("existing durable attempt requires reconciliation before retry")
    current = refresh_candidate()
    current = refresh_arm_candidate(context, current)
    fresh = plan_lab_arm_validation(context, current, target=target, selected_flags=selected_flags, expected_workbooks=expected_workbooks)
    if fresh["planSha256"] != expected_plan_sha256:
        raise ValueError("candidate evidence changed after immediate approval")
    access = identity_check(plan["target"])
    if any(access.get(key) is not True for key in ("tenantMatches", "subscriptionMatches", "workspaceMatches", "nonProduction", "armDeploymentAllowed", "disabledContentVerified", "ownershipVerified")) or (
        any(item["import"] for item in plan["resources"]) and access.get("extensionResourceWriteAllowed") is not True
    ):
        return {"status": "blocked", "writeAttempted": False, "accepted": False, "identityCheck": dict(access)}
    identity_fields = ("tenantId", "subscriptionId", "workspaceResourceId")
    if not isinstance(access.get("identityId"), str) or not access["identityId"].strip() or any(
        str(access.get(key, "")).casefold() != plan["target"][key].casefold() for key in identity_fields
    ):
        return {"status": "blocked", "writeAttempted": False, "accepted": False, "identityCheck": dict(access)}
    # Re-read approval and all evidence after access checks, immediately before reservation.
    current = refresh_candidate()
    current = refresh_arm_candidate(context, current)
    fresh = plan_lab_arm_validation(context, current, target=target, selected_flags=selected_flags, expected_workbooks=expected_workbooks)
    scope = check_lab_arm_scope(fresh, read_consent())
    if fresh["planSha256"] != expected_plan_sha256 or scope["status"] != "ready":
        raise ValueError("candidate/approved scope changed immediately before write")
    snapshot = directory / f"arm-validation-template-{plan['mainTemplateSha256']}.json"
    _write_template_snapshot(snapshot, content_path(root, current["artifactPaths"]["mainTemplate"]).read_bytes())
    report = {
        "schemaVersion": 1, "status": "intent-reserved", "planSha256": plan["planSha256"],
        "candidateSha256": candidate["candidateSha256"], "target": plan["target"],
        "solutionPath": str(root),
        "actor": actor.strip(), "approvalReference": approval_reference.strip(),
        "approvedAt": _utc_now(), "writeAttempted": False, "accepted": False,
        "installationVerified": False, "registrationVerified": False,
        "uiVerified": False, "parityVerified": False, "retryAuthorized": False,
        "workbookContractRequired": bool(plan["expectedWorkbooks"]),
        "mainTemplateSha256": plan["mainTemplateSha256"], "parameters": plan["parameters"],
        "packageIdentity": plan["packageIdentity"],
        "scopeConsentReference": None,
        "attemptPath": str(attempt_path),
    }
    from .workflow import _run_writer_lock
    from .runtime_consent import _atomic_write_json

    guard_path = directory / "arm-validation-executor.json"
    with _run_writer_lock(directory):
        if guard_path.exists() or guard_path.is_symlink():
            if guard_path.is_symlink():
                raise ValueError("executor receipt cannot be a symlink")
            prior_guard = json.loads(guard_path.read_text(encoding="utf-8"))
            prior_path = Path(prior_guard["attemptPath"])
            if prior_path.parent != directory or prior_path.is_symlink():
                raise ValueError("executor receipt does not bind a safe attempt")
            prior = json.loads(prior_path.read_text(encoding="utf-8"))
            if prior.get("status") not in {"failed", "arm-accepted-contract-pending"} or not prior.get("reconciliation"):
                raise ValueError("previous executor requires independent reconciliation before any changed candidate/retry")
        _reserve_attempt(attempt_path, report)
        _atomic_write_json(guard_path, {"attemptPath": str(attempt_path), "identity": identity})

    def persist() -> None:
        _atomic_write_json(attempt_path, report)

    deployment_name = "workbook-arm-" + identity[:32]
    command = ["deployment", "group", "create", "--name", deployment_name,
               "--subscription", plan["target"]["subscriptionId"], "--resource-group", plan["target"]["resourceGroup"],
               "--template-file", str(snapshot), "--mode", "Incremental", "--parameters",
               *(f"{name}={str(value).lower() if type(value) is bool else value}" for name, value in sorted(plan["parameters"].items())),
               "--output", "json", "--only-show-errors"]
    # Reservation happens before submission. A late revocation/freshness/access
    # failure remains durable and cannot become an unrecorded cloud attempt.
    try:
        current = refresh_arm_candidate(context, refresh_candidate())
        immediate = plan_lab_arm_validation(context, current, target=target, selected_flags=selected_flags, expected_workbooks=expected_workbooks)
        latest_access = identity_check(plan["target"])
        latest_consent = read_consent()
        if immediate["planSha256"] != expected_plan_sha256 or check_lab_arm_scope(immediate, latest_consent)["status"] != "ready" or _digest_file(snapshot) != plan["mainTemplateSha256"]:
            raise ValueError("scope/evidence changed at dispatch boundary")
        access_fields = (*identity_fields, "identityId", "tenantMatches", "subscriptionMatches", "workspaceMatches",
                         "nonProduction", "armDeploymentAllowed", "disabledContentVerified", "ownershipVerified",
                         "extensionResourceWriteAllowed")
        if any(latest_access.get(key) != access.get(key) for key in access_fields):
            raise ValueError("execution identities/access changed at dispatch boundary")
        report["scopeConsentReference"] = latest_consent["approvalReference"]
    except Exception as exc:
        report.update(status="blocked-before-write", error=f"{type(exc).__name__}: current approval/evidence/access check failed")
        persist()
        return report
    report.update(status="write-intent-persisted", writeAttempted=True, deploymentName=deployment_name)
    persist()
    try:
        code, response, error = command_runner(command)
        state = _deployment_provisioning_state(response)
        status = "arm-accepted-contract-pending" if code == 0 and state == "succeeded" else ("failed" if code and state == "succeeded" else _error_status(state))
        report.update(status=status, commandExitCode=code, provisioningState=_recorded_provisioning_state(response),
                      deploymentId=response.get("id") if isinstance(response, dict) else None, error=error or None)
    except Exception as exc:
        report.update(status="unknown", error=f"{type(exc).__name__}: write outcome requires reconciliation")
    report["completedAt"] = _utc_now()
    persist()
    return report


def reconcile_lab_arm_attempt(attempt_path: str | Path, *, observation: Mapping[str, Any], actor: str, reference: str) -> dict[str, Any]:
    """Record an exact independent deployment GET; never authorizes a retry."""
    path = Path(attempt_path)
    if path.is_symlink() or not path.is_file() or not actor.strip() or not reference.strip():
        raise ValueError("reconciliation requires an existing attempt, actor and evidence reference")
    record = json.loads(path.read_text(encoding="utf-8"))
    expected_id = (
        f"/subscriptions/{record['target']['subscriptionId']}/resourceGroups/{record['target']['resourceGroup']}"
        f"/providers/Microsoft.Resources/deployments/{record.get('deploymentName')}"
    )
    if observation.get("httpMethod") != "GET" or str(observation.get("deploymentId", "")).casefold() != expected_id.casefold() or observation.get("target") != record["target"] or not isinstance(observation.get("responseSha256"), str) or not _HASH.fullmatch(observation["responseSha256"]):
        raise ValueError("reconciliation is not bound to independent exact deployment readback")
    outcome = str(observation.get("provisioningState") or "").casefold()
    if outcome not in {"succeeded", "failed", "canceled", "cancelled"} or observation.get("status") != "passed":
        raise ValueError("nonterminal/denied/unknown readback cannot reconcile an attempt")
    response_path = content_path(Path(record["solutionPath"]), observation.get("responsePath"))
    if not response_path.is_relative_to(Path(record["solutionPath"]) / "Logs") or _digest_file(response_path) != observation["responseSha256"]:
        raise ValueError("reconciliation raw response bytes are missing or stale")
    response = json.loads(response_path.read_text(encoding="utf-8-sig"))
    if str(response.get("id", "")).casefold() != expected_id.casefold() or _deployment_provisioning_state(response) != outcome:
        raise ValueError("reconciliation raw deployment identity/outcome mismatched")
    record["reconciliation"] = {**observation, "actor": actor.strip(), "reference": reference.strip(), "recordedAt": _utc_now()}
    record["status"] = "arm-accepted-contract-pending" if outcome == "succeeded" else "failed"
    record["accepted"] = False
    record["retryAuthorized"] = False
    from .runtime_consent import _atomic_write_json
    from .workflow import _run_writer_lock
    with _run_writer_lock(path.parent):
        current = json.loads(path.read_text(encoding="utf-8"))
        if current.get("completedAt") != record.get("completedAt") or current.get("status") not in {"unknown", "nonterminal", "failed", "arm-accepted-contract-pending"}:
            raise ValueError("active/changed attempt cannot be reconciled")
        _atomic_write_json(path, record)
    return record


def verify_workbook_readback(plan: Mapping[str, Any], evidence: Mapping[str, Any]) -> dict[str, Any]:
    """Require independent install, registration and repeat/update observations.

    Expected workbook records are plan-bound by the integration adapter. Each
    observation supplies a solution-relative raw response path/hash and distinct
    exact GET operation identity (not ARM outputs or caller-asserted summaries).
    """
    from .packaging import package_input_identity

    reasons = []
    if not _sealed(plan, "planSha256") or evidence.get("planSha256") != plan.get("planSha256") or evidence.get("target") != plan.get("target"):
        reasons.append("readback plan/target binding is missing or stale")
    try:
        root = Path(plan["solutionPath"])
        identity = plan["packageIdentity"]
        if package_input_identity(root)["sha256"] != identity["packageInputSha256"]:
            raise ValueError("readback refers to stale candidate inputs")
        for name, digest in identity["packageArtifactHashes"].items():
            if _digest_file(content_path(root, plan["artifactPaths"][name])) != digest:
                raise ValueError("readback refers to stale candidate artifacts")
        for reference in plan["prerequisiteEvidence"].values():
            if _digest_file(content_path(root, reference["path"])) != reference["sha256"]:
                raise ValueError("readback prerequisite evidence changed")
        fingerprints = plan["validationReceiptFingerprint"]
        for path_key, hash_key in (("path", "sha256"), ("bindingPath", "bindingSha256")):
            path_value = fingerprints.get(path_key)
            if path_value is not None and _digest_file(Path(path_value)) != fingerprints.get(hash_key):
                raise ValueError("readback static receipt/binding changed")
    except (KeyError, TypeError, ValueError, OSError) as exc:
        reasons.append(f"readback current candidate/evidence binding failed ({type(exc).__name__})")
    expected = plan.get("expectedWorkbooks")
    if not isinstance(expected, list) or not expected:
        reasons.append("no exact expected workbook install/registration contract")
    if evidence.get("armStatus") != "succeeded" or not evidence.get("deploymentId"):
        reasons.append("terminal ARM acceptance evidence is missing")
    observations = evidence.get("workbooks")
    if not isinstance(observations, list) or not isinstance(expected, list) or len(observations) != len(expected):
        reasons.append("workbook readback inventory is incomplete")
    else:
        seen_operations: set[str] = set()
        seen_writes: set[str] = set()
        for wanted, observed in zip(expected, observations):
            if wanted.get("contentId") == wanted.get("instanceId") or not wanted.get("contentId") or not wanted.get("instanceId"):
                reasons.append("distinct canonical content/installation identity required")
            for phase in ("installation", "registration", "repeatInstallation", "update"):
                result = observed.get(phase) or {}
                expected_phase = wanted.get(phase)
                operation = result.get("operationId")
                if not isinstance(expected_phase, dict) or not expected_phase:
                    reasons.append(f"missing exact expected {phase} contract")
                if result.get("status") != "passed" or result.get("httpMethod") != "GET" or result.get("provider") not in {"azure-resource-manager", "microsoft-security"} or not isinstance(result.get("responseSha256"), str) or not _HASH.fullmatch(result["responseSha256"]) or not isinstance(operation, str) or not operation or operation in seen_operations:
                    reasons.append(f"{phase} independent readback failed/denied/unknown")
                    continue
                seen_operations.add(operation)
                if phase != "registration":
                    write_id = result.get("writeOperationId")
                    if result.get("writeStatus") != "succeeded" or not isinstance(write_id, str) or not write_id or write_id in seen_writes:
                        reasons.append(f"{phase} requires a distinct successful bounded installation/update operation")
                    else:
                        seen_writes.add(write_id)
                    try:
                        attempt_path = content_path(Path(plan["solutionPath"]), result.get("writeAttemptPath"))
                        if not attempt_path.is_relative_to(Path(plan["solutionPath"]) / "Logs") or _digest_file(attempt_path) != result.get("writeAttemptSha256"):
                            raise ValueError("installation/update attempt bytes are stale")
                        attempt = json.loads(attempt_path.read_text(encoding="utf-8-sig"))
                        if (
                            attempt.get("status") != "arm-accepted-contract-pending"
                            or attempt.get("target") != plan["target"]
                            or attempt.get("mainTemplateSha256") != plan["mainTemplateSha256"]
                            or attempt.get("parameters") != plan["parameters"]
                            or attempt.get("deploymentId") != write_id
                            or (attempt.get("packageIdentity") or {}).get("packageInputSha256") != plan["packageIdentity"]["packageInputSha256"]
                        ):
                            raise ValueError("installation/update operation does not bind current approved candidate")
                    except (KeyError, TypeError, ValueError, OSError) as exc:
                        reasons.append(f"{phase} successful bounded attempt could not be verified ({type(exc).__name__})")
                try:
                    response_path = content_path(Path(plan["solutionPath"]), result.get("responsePath"))
                    if not response_path.is_relative_to(Path(plan["solutionPath"]) / "Logs") or _digest_file(response_path) != result["responseSha256"]:
                        raise ValueError("readback raw response hash/path is stale")
                    response = json.loads(response_path.read_text(encoding="utf-8-sig"))
                    props = response["properties"]
                    resource_id = response["id"]
                    if not isinstance(props, dict) or not isinstance(resource_id, str) or result.get("requestResourceId") != resource_id:
                        raise ValueError("readback does not match its exact GET resource identity")
                    if phase == "registration":
                        prefix = plan["target"]["workspaceResourceId"] + "/providers/Microsoft.SecurityInsights/contentTemplates/"
                        if not resource_id.casefold().startswith(prefix.casefold()) or result["provider"] != "azure-resource-manager":
                            raise ValueError("registration readback is not in selected workspace")
                        actual = {key: props.get(key) for key in expected_phase if key != "storedTemplateSha256"}
                        actual["storedTemplateSha256"] = _canonical_sha256(props.get("mainTemplate"))
                    else:
                        prefix = f"/tenants/{plan['target']['tenantId']}/providers/Microsoft.Security/workbooks/"
                        if resource_id.casefold() != (prefix + wanted["instanceId"]).casefold() or result["provider"] != "microsoft-security":
                            raise ValueError("installation readback crosses selected tenant or instance identity")
                        notebook = props["content"]
                        actual = {"contentId": notebook["contentProvenance"]["contentId"],
                                  "instanceId": props["id"], "contentSha256": _canonical_sha256(notebook),
                                  "contentProvenance": notebook["contentProvenance"]}
                    if actual != expected_phase:
                        raise ValueError("readback content identity/provenance mismatched")
                except (KeyError, TypeError, ValueError, OSError) as exc:
                    reasons.append(f"{phase} raw independent readback could not verify contract ({type(exc).__name__})")
    return {"status": "verified" if not reasons else "blocked", "accepted": not reasons,
            "installationVerified": not reasons, "registrationVerified": not reasons,
            "repeatInstallUpdateVerified": not reasons, "uiVerified": False, "parityVerified": False, "reasons": reasons}
