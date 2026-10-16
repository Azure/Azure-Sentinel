"""Offline validation and deterministic advisory metrics for authoring records.

These helpers neither persist stopped state nor authorize runtime operations.
"""

from __future__ import annotations

import json
import re
from copy import deepcopy
from dataclasses import dataclass
from pathlib import Path, PurePosixPath, PureWindowsPath
from typing import Any, Mapping

from jsonschema import Draft202012Validator
from jsonschema.exceptions import SchemaError

SCHEMA_VERSION = "1.0.0"
AUTHORING_SCHEMA_VERSION = "1.1.0"
SUPPORTED_SCHEMA_VERSIONS = {SCHEMA_VERSION, AUTHORING_SCHEMA_VERSION}
SCHEMA_PATH = Path(__file__).resolve().parents[1] / "schema" / "authoring-contract.schema.json"
_SHA256 = re.compile(r"[a-f0-9]{64}\Z")
_MIGRATION_PERCENT = 80
_STOP_PERCENT = 50


class AuthoringContractError(ValueError):
    """A malformed or semantically inconsistent authoring contract."""


@dataclass(frozen=True)
class EvidenceReference:
    path: str
    sha256: str
    kind: str


@dataclass(frozen=True)
class Finding:
    finding_id: str
    kind: str
    message: str
    unresolved: bool
    evidence_references: tuple[EvidenceReference, ...]


@dataclass(frozen=True)
class SourceRule:
    rule_id: str
    sha256: str
    evidence_references: tuple[EvidenceReference, ...]
    path: str | None = None
    query_sha256: str | None = None


@dataclass(frozen=True)
class TargetArtifact:
    path: str
    sha256: str
    structurally_valid: bool
    query_sha256: str | None = None


@dataclass(frozen=True)
class RuleResult:
    rule_id: str
    source_sha256: str
    status: str
    conversion_status: str | None
    validation_status: str | None
    deployment_disposition: str
    target: TargetArtifact | None
    review_required: bool
    mapping_assumptions: tuple[str, ...]
    findings: tuple[Finding, ...]
    qualification_status: str
    qualification_evidence_references: tuple[EvidenceReference, ...]
    evidence_references: tuple[EvidenceReference, ...]

    @property
    def target_structurally_valid(self) -> bool:
        return self.target is not None and self.target.structurally_valid

    @property
    def unresolved_error_count(self) -> int:
        return sum(finding.kind == "error" and finding.unresolved for finding in self.findings)


@dataclass(frozen=True)
class EnvironmentError:
    code: str
    message: str
    evidence_references: tuple[EvidenceReference, ...]


@dataclass(frozen=True)
class AuthoringContract:
    run_id: str
    source_identity: str
    source_sha256: str
    inventory: tuple[SourceRule, ...]
    results: tuple[RuleResult, ...]
    environment_errors: tuple[EnvironmentError, ...]
    schema_version: str = SCHEMA_VERSION
    inventory_sha256: str | None = None
    revision: int | None = None
    previous_sha256: str | None = None


@dataclass(frozen=True)
class Coverage:
    """Exact integer-based counts; no rounded percentage is used for decisions."""

    run_id: str
    source_identity: str
    source_sha256: str
    schema_version: str
    N: int
    M: int
    E: int
    qualified: int
    untested: int
    qualification_failed: int
    migration_threshold_met: bool
    stop_threshold_reached: bool

    def as_dict(self) -> dict[str, str | int | bool]:
        return {
            "schemaVersion": self.schema_version,
            "runId": self.run_id,
            "sourceIdentity": self.source_identity,
            "sourceSha256": self.source_sha256,
            "N": self.N,
            "M": self.M,
            "E": self.E,
            "qualified": self.qualified,
            "untested": self.untested,
            "qualificationFailed": self.qualification_failed,
            "migrationThresholdMet": self.migration_threshold_met,
            "stopThresholdReached": self.stop_threshold_reached,
        }


@dataclass(frozen=True)
class OperationEligibility:
    """Advisory thresholds only; no operation is authorized by this record."""

    run_id: str
    source_identity: str
    source_sha256: str
    schema_version: str
    migration_threshold_met: bool
    stop_threshold_reached: bool

    def as_dict(self) -> dict[str, str | bool]:
        return {
            "schemaVersion": self.schema_version,
            "runId": self.run_id,
            "sourceIdentity": self.source_identity,
            "sourceSha256": self.source_sha256,
            "scope": "advisory-only",
            "migrationThresholdMet": self.migration_threshold_met,
            "successAndPrThresholdMet": self.migration_threshold_met,
            "stopThresholdReached": self.stop_threshold_reached,
            "requiresExactScopeAuthorization": True,
            "coverageAuthorizesOperations": False,
            "deploymentAuthorized": False,
            "packagingAuthorized": False,
            "ingestionAuthorized": False,
            "prCreationAuthorized": False,
        }


def _schema() -> dict[str, Any]:
    try:
        schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
        Draft202012Validator.check_schema(schema)
    except (OSError, json.JSONDecodeError, ValueError, SchemaError) as exc:
        raise AuthoringContractError(f"cannot load authoring contract schema: {exc}") from exc
    return schema


def _path_is_safe(value: str) -> bool:
    if "\\" in value or value.startswith("/") or PureWindowsPath(value).drive:
        return False
    if any(part in {"", ".", ".."} for part in value.split("/")):
        return False
    path = PurePosixPath(value)
    return not path.is_absolute()


def calculate_inventory_sha256(rules: list[Mapping[str, Any]]) -> str:
    """Hash a complete inventory's stable identity, path, source, and query hashes."""
    canonical = [
        {
            "path": rule["path"],
            "querySha256": rule["querySha256"],
            "ruleId": rule["ruleId"],
            "sha256": rule["sha256"],
        }
        for rule in sorted(rules, key=lambda item: item["path"])
    ]
    encoded = json.dumps(
        canonical, sort_keys=True, separators=(",", ":"), ensure_ascii=False
    ).encode("utf-8")
    import hashlib

    return hashlib.sha256(encoded).hexdigest()


def _validate_references(refs: list[dict[str, Any]], where: str) -> None:
    identities: set[str] = set()
    for index, reference in enumerate(refs):
        path = reference["path"]
        if not _path_is_safe(path):
            raise AuthoringContractError(
                f"{where}[{index}].path must be a safe repository-relative path"
            )
        if not _SHA256.fullmatch(reference["sha256"]):
            raise AuthoringContractError(f"{where}[{index}].sha256 must be lowercase SHA-256")
        if path in identities:
            raise AuthoringContractError(f"{where} contains a duplicate evidence reference: {path}")
        identities.add(path)


def _has_unresolved_error(result: Mapping[str, Any]) -> bool:
    return any(item["kind"] == "error" and item["unresolved"] for item in result["findings"])


def _evidence_references(references: list[dict[str, Any]]) -> tuple[EvidenceReference, ...]:
    return tuple(
        EvidenceReference(item["path"], item["sha256"], item["kind"])
        for item in references
    )


def _semantic_validate(document: Mapping[str, Any]) -> AuthoringContract:
    if document["schemaVersion"] not in SUPPORTED_SCHEMA_VERSIONS:
        raise AuthoringContractError(f"unsupported authoring contract version: {document['schemaVersion']}")
    if not document["inventory"]["complete"]:
        raise AuthoringContractError("inventory must be complete")

    inventory = document["inventory"]["rules"]
    source_ids = [rule["ruleId"] for rule in inventory]
    if not source_ids:
        raise AuthoringContractError("inventory must contain at least one source rule")
    if len(source_ids) != len(set(source_ids)):
        raise AuthoringContractError("inventory contains duplicate rule identities")
    for index, rule in enumerate(inventory):
        if "path" in rule and not _path_is_safe(rule["path"]):
            raise AuthoringContractError(
                f"inventory.rules[{index}].path must be a safe repository-relative path"
            )
        _validate_references(rule["evidenceReferences"], f"inventory.rules[{index}].evidenceReferences")
    inventory_sha256 = document["inventory"].get("sha256")
    if document["schemaVersion"] == AUTHORING_SCHEMA_VERSION:
        if not all("path" in rule and "querySha256" in rule for rule in inventory):
            raise AuthoringContractError(
                "authoring contract 1.1.0 requires every inventory path and query hash"
            )
        calculated_inventory_sha256 = calculate_inventory_sha256(inventory)
        if inventory_sha256 != calculated_inventory_sha256:
            raise AuthoringContractError("inventory SHA-256 does not match the complete inventory")
        snapshot = document["snapshot"]
        revision = snapshot["revision"]
        previous_sha256 = snapshot["previousSha256"]
        if (revision == 1) != (previous_sha256 is None):
            raise AuthoringContractError(
                "snapshot revision 1 must have no previous hash; later revisions must be chained"
            )
    else:
        revision = None
        previous_sha256 = None

    results = document["results"]
    result_ids = [result["ruleId"] for result in results]
    if len(result_ids) != len(set(result_ids)):
        raise AuthoringContractError("results contain duplicate rule identities")
    missing = sorted(set(source_ids) - set(result_ids))
    extra = sorted(set(result_ids) - set(source_ids))
    if missing or extra:
        raise AuthoringContractError(
            f"results must match inventory identities exactly (missing={missing}, extra={extra})"
        )
    source_hashes = {rule["ruleId"]: rule["sha256"] for rule in inventory}
    parsed_results: list[RuleResult] = []
    for index, result in enumerate(results):
        rule_id = result["ruleId"]
        if result["sourceSha256"] != source_hashes[rule_id]:
            raise AuthoringContractError(f"result source hash does not match inventory for rule {rule_id!r}")
        if any(item["kind"] != "error" and item["unresolved"] for item in result["findings"]):
            raise AuthoringContractError(
                f"only error findings may be unresolved for rule {rule_id!r}"
            )
        finding_ids = [item["findingId"] for item in result["findings"]]
        if len(finding_ids) != len(set(finding_ids)):
            raise AuthoringContractError(f"rule {rule_id!r} contains duplicate finding identities")
        _validate_references(result["evidenceReferences"], f"results[{index}].evidenceReferences")
        _validate_references(
            result["qualificationEvidenceReferences"],
            f"results[{index}].qualificationEvidenceReferences",
        )
        for finding_index, finding in enumerate(result["findings"]):
            _validate_references(
                finding["evidenceReferences"],
                f"results[{index}].findings[{finding_index}].evidenceReferences",
            )

        status = result["status"]
        disposition = result["deploymentDisposition"]
        target = result["target"]
        has_error = _has_unresolved_error(result)
        target_valid = target is not None and target["structurallyValid"]
        if target is not None and not _path_is_safe(target["path"]):
            raise AuthoringContractError(f"target path must be repository-relative for rule {rule_id!r}")
        if status == "migrated" and (not target_valid or has_error or disposition != "normal"):
            raise AuthoringContractError(
                f"migrated rule {rule_id!r} needs a structurally valid target, no unresolved errors, "
                "and normal deployment disposition"
            )
        if status == "blocked" and (
            disposition not in {"deploymentBlocked", "authoringBlocked"} or not has_error
        ):
            raise AuthoringContractError(
                f"blocked rule {rule_id!r} needs deploymentBlocked disposition and an unresolved error"
            )
        if status == "suppressed" and (disposition != "suppressed" or not has_error):
            raise AuthoringContractError(
                f"suppressed rule {rule_id!r} needs suppressed disposition and an unresolved error"
            )
        if status == "unprocessed" and disposition != "normal":
            raise AuthoringContractError(f"unprocessed rule {rule_id!r} must have normal disposition")
        if document["schemaVersion"] == AUTHORING_SCHEMA_VERSION:
            if status == "migrated" and (
                result["conversionStatus"] != "converted"
                or result["validationStatus"] != "passed"
            ):
                raise AuthoringContractError(
                    f"migrated rule {rule_id!r} needs successful conversion and structural validation"
                )
            if result["validationStatus"] == "passed" and not target_valid:
                raise AuthoringContractError(
                    f"passed structural validation for {rule_id!r} needs a valid target"
                )
        qualification = result["qualificationStatus"]
        qualification_references = _evidence_references(
            result["qualificationEvidenceReferences"]
        )
        qualification_kinds = {
            reference.kind for reference in qualification_references
        }
        if qualification == "qualified":
            if status != "migrated":
                raise AuthoringContractError(f"qualified rule {rule_id!r} must be migrated")
            if not {"runtimeVerification", "alertParity"}.issubset(qualification_kinds):
                raise AuthoringContractError(
                    f"qualified rule {rule_id!r} needs runtimeVerification and alertParity evidence"
                )
        elif qualification == "failed" and not has_error:
            raise AuthoringContractError(
                f"failed qualification for rule {rule_id!r} must remain an unresolved rule error"
            )

        parsed_results.append(
            RuleResult(
                rule_id=rule_id,
                source_sha256=result["sourceSha256"],
                status=status,
                conversion_status=result.get("conversionStatus"),
                validation_status=result.get("validationStatus"),
                deployment_disposition=disposition,
                target=(
                    TargetArtifact(
                        target["path"], target["sha256"], target["structurallyValid"],
                        target.get("querySha256"),
                    )
                    if target is not None else None
                ),
                review_required=result["reviewRequired"],
                mapping_assumptions=tuple(result["mappingAssumptions"]),
                findings=tuple(
                    Finding(
                        finding["findingId"],
                        finding["kind"],
                        finding["message"],
                        finding["unresolved"],
                        _evidence_references(finding["evidenceReferences"]),
                    )
                    for finding in result["findings"]
                ),
                qualification_status=qualification,
                qualification_evidence_references=qualification_references,
                evidence_references=_evidence_references(result["evidenceReferences"]),
            )
        )
    parsed_inventory = tuple(
        SourceRule(
            rule["ruleId"],
            rule["sha256"],
            _evidence_references(rule["evidenceReferences"]),
            rule.get("path"),
            rule.get("querySha256"),
        )
        for rule in inventory
    )
    parsed_environment_errors = tuple(
        EnvironmentError(
            error["code"],
            error["message"],
            _evidence_references(error["evidenceReferences"]),
        )
        for error in document["environmentErrors"]
    )
    for index, error in enumerate(document["environmentErrors"]):
        _validate_references(error["evidenceReferences"], f"environmentErrors[{index}].evidenceReferences")

    return AuthoringContract(
        run_id=document["runId"],
        source_identity=document["source"]["identity"],
        source_sha256=document["source"]["sha256"],
        inventory=parsed_inventory,
        results=tuple(parsed_results),
        environment_errors=parsed_environment_errors,
        schema_version=document["schemaVersion"],
        inventory_sha256=inventory_sha256,
        revision=revision,
        previous_sha256=previous_sha256,
    )


def validate_authoring_contract(document: Mapping[str, Any]) -> AuthoringContract:
    """Validate a JSON-like contract and return an immutable typed summary."""
    if not isinstance(document, Mapping):
        raise AuthoringContractError("authoring contract must be an object")
    version = document.get("schemaVersion")
    if version not in SUPPORTED_SCHEMA_VERSIONS:
        raise AuthoringContractError(f"unsupported authoring contract version: {version!r}")
    errors = sorted(
        Draft202012Validator(_schema()).iter_errors(document),
        key=lambda error: (list(error.absolute_path), error.message),
    )
    if errors:
        details = "; ".join(
            f"{'/'.join(map(str, error.absolute_path)) or '<root>'}: {error.message}"
            for error in errors
        )
        raise AuthoringContractError(f"invalid authoring contract: {details}")
    try:
        contract = _semantic_validate(document)
        expected_coverage = calculate_coverage(contract).as_dict()
        if document["coverage"] != expected_coverage:
            raise AuthoringContractError(
                "coverage counts or thresholds are inconsistent with inventory and results"
            )
        expected_eligibility = calculate_operation_eligibility(
            calculate_coverage(contract)
        ).as_dict()
        if document["operationEligibility"] != expected_eligibility:
            raise AuthoringContractError(
                "operation eligibility is inconsistent with coverage or grants authorization"
            )
        return contract
    except AuthoringContractError:
        raise
    except (KeyError, TypeError, ValueError) as exc:
        raise AuthoringContractError(f"invalid authoring contract semantics: {exc}") from exc


def seal_authoring_contract(document: Mapping[str, Any]) -> dict[str, Any]:
    """Validate a source/outcome record and attach deterministic advisory summaries."""
    if not isinstance(document, Mapping):
        raise AuthoringContractError("authoring contract must be an object")
    if "coverage" in document or "operationEligibility" in document:
        raise AuthoringContractError(
            "seal_authoring_contract accepts core records only; validate precomputed summaries instead"
        )
    if document.get("schemaVersion") not in SUPPORTED_SCHEMA_VERSIONS:
        raise AuthoringContractError(
            f"unsupported authoring contract version: {document.get('schemaVersion')!r}"
        )
    record = deepcopy(dict(document))
    schema = _schema()
    core_schema = deepcopy(schema)
    core_schema["required"] = [
        key for key in core_schema["required"]
        if key not in {"coverage", "operationEligibility"}
    ]
    errors = sorted(
        Draft202012Validator(core_schema).iter_errors(record),
        key=lambda error: (list(error.absolute_path), error.message),
    )
    if errors:
        details = "; ".join(
            f"{'/'.join(map(str, error.absolute_path)) or '<root>'}: {error.message}"
            for error in errors
        )
        raise AuthoringContractError(f"invalid authoring contract: {details}")
    try:
        contract = _semantic_validate(record)
        coverage = calculate_coverage(contract)
        record["coverage"] = coverage.as_dict()
        record["operationEligibility"] = calculate_operation_eligibility(coverage).as_dict()
        validate_authoring_contract(record)
        return record
    except AuthoringContractError:
        raise
    except (KeyError, TypeError, ValueError) as exc:
        raise AuthoringContractError(f"invalid authoring contract semantics: {exc}") from exc


def calculate_coverage(contract: AuthoringContract) -> Coverage:
    """Calculate exact coverage from a validated immutable inventory and its outcomes."""
    if not isinstance(contract, AuthoringContract):
        raise TypeError("calculate_coverage requires a validated AuthoringContract")
    total = len(contract.inventory)
    if total < 1:
        raise AuthoringContractError("coverage is undefined for an empty source inventory")
    migrated = sum(
        1
        for result in contract.results
        if result.status == "migrated"
        and result.target_structurally_valid
        and result.unresolved_error_count == 0
        and result.deployment_disposition == "normal"
    )
    errored = sum(
        1
        for result in contract.results
        if result.unresolved_error_count > 0 or result.status == "suppressed"
    )
    qualified = sum(result.qualification_status == "qualified" for result in contract.results)
    untested = sum(result.qualification_status == "untested" for result in contract.results)
    failed = sum(result.qualification_status == "failed" for result in contract.results)
    return Coverage(
        run_id=contract.run_id,
        source_identity=contract.source_identity,
        source_sha256=contract.source_sha256,
        schema_version=contract.schema_version,
        N=total,
        M=migrated,
        E=errored,
        qualified=qualified,
        untested=untested,
        qualification_failed=failed,
        migration_threshold_met=100 * migrated >= _MIGRATION_PERCENT * total,
        stop_threshold_reached=100 * errored > _STOP_PERCENT * total,
    )


def calculate_operation_eligibility(coverage: Coverage) -> OperationEligibility:
    """Return threshold signals only; separate exact-scope authorization is always required."""
    if not isinstance(coverage, Coverage):
        raise TypeError("calculate_operation_eligibility requires a Coverage record")
    return OperationEligibility(
        run_id=coverage.run_id,
        source_identity=coverage.source_identity,
        source_sha256=coverage.source_sha256,
        schema_version=coverage.schema_version,
        migration_threshold_met=coverage.migration_threshold_met,
        stop_threshold_reached=coverage.stop_threshold_reached,
    )
