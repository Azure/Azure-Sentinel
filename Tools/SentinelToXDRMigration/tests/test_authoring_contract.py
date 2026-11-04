from __future__ import annotations

import copy
import unittest

from sentinel_xdr_migration.authoring_contract import (
    AuthoringContractError,
    AUTHORING_SCHEMA_VERSION,
    calculate_coverage,
    calculate_inventory_sha256,
    calculate_operation_eligibility,
    seal_authoring_contract,
    validate_authoring_contract,
)


HASH = "a" * 64
TARGET_HASH = "b" * 64
EVIDENCE_HASH = "c" * 64
PARITY_POLICY = {
    "assertion": "value-preserved-in-actual-corresponding-alert",
    "comparison": "value-only",
    "entityTypeIdentifierAndCustomFieldMayDiffer": True,
    "requiredForQualification": True,
}


def make_contract(statuses: list[str]) -> dict:
    inventory = []
    results = []
    for index, status in enumerate(statuses):
        rule_id = f"rule-{index}"
        source_hash = f"{index:064x}"
        inventory.append({
            "ruleId": rule_id,
            "sha256": source_hash,
            "evidenceReferences": [],
        })
        disposition = {
            "migrated": "normal",
            "blocked": "deploymentBlocked",
            "suppressed": "suppressed",
            "unprocessed": "normal",
        }[status]
        findings = []
        if status in {"blocked", "suppressed"}:
            findings.append({
                "findingId": "error-1",
                "kind": "error",
                "message": "Rule-specific conversion error",
                "unresolved": True,
                "evidenceReferences": [],
            })
        results.append({
            "ruleId": rule_id,
            "sourceSha256": source_hash,
            "status": status,
            "deploymentDisposition": disposition,
            "target": {
                "path": f"XDR Detections/{rule_id}.yaml",
                "sha256": TARGET_HASH,
                "structurallyValid": True,
            } if status != "unprocessed" else None,
            "reviewRequired": False,
            "mappingAssumptions": [],
            "findings": findings,
            "qualificationStatus": "untested",
            "qualificationEvidenceReferences": [],
            "evidenceReferences": [],
        })
    return seal_authoring_contract({
        "schemaVersion": "1.0.0",
        "runId": "run-1",
        "source": {"identity": "Sample solution", "sha256": HASH},
        "inventory": {"complete": True, "rules": inventory},
        "results": results,
        "environmentErrors": [],
        "entityValueParityPolicy": copy.deepcopy(PARITY_POLICY),
    })


class AuthoringContractTests(unittest.TestCase):
    def coverage(self, record: dict):
        return calculate_coverage(validate_authoring_contract(record))

    def test_eight_of_ten_passes_seven_of_ten_fails_without_rounding(self):
        eight = self.coverage(make_contract(["migrated"] * 8 + ["unprocessed"] * 2))
        seven = self.coverage(make_contract(["migrated"] * 7 + ["unprocessed"] * 3))
        self.assertTrue(eight.migration_threshold_met)
        self.assertEqual((10, 8, 0), (eight.N, eight.M, eight.E))
        self.assertFalse(seven.migration_threshold_met)
        self.assertEqual((10, 7), (seven.N, seven.M))

    def test_error_stop_boundary_is_strict_and_uses_integer_comparison(self):
        five = self.coverage(make_contract(["blocked"] * 5 + ["unprocessed"] * 5))
        six = self.coverage(make_contract(["blocked"] * 6 + ["unprocessed"] * 4))
        self.assertEqual(5, five.E)
        self.assertFalse(five.stop_threshold_reached)
        self.assertEqual(6, six.E)
        self.assertTrue(six.stop_threshold_reached)

    def test_two_of_three_is_below_threshold(self):
        coverage = self.coverage(make_contract(["migrated", "migrated", "unprocessed"]))
        self.assertEqual((3, 2), (coverage.N, coverage.M))
        self.assertFalse(coverage.migration_threshold_met)

    def test_warnings_and_assumptions_are_retained_without_verification_claims(self):
        record = make_contract(["migrated"])
        result = record["results"][0]
        result["reviewRequired"] = True
        result["mappingAssumptions"] = ["Table availability is assumed, not queried."]
        result["findings"] = [
            {
                "findingId": "warning-1",
                "kind": "warning",
                "message": "Advisory warning",
                "unresolved": False,
                "evidenceReferences": [],
            },
            {
                "findingId": "assumption-1",
                "kind": "assumption",
                "message": "Mapping premise remains subject to review.",
                "unresolved": False,
                "evidenceReferences": [],
            },
        ]
        parsed = validate_authoring_contract(record)
        coverage = calculate_coverage(parsed)
        self.assertEqual(1, coverage.M)
        self.assertTrue(parsed.results[0].review_required)
        self.assertEqual(("Table availability is assumed, not queried.",),
                         parsed.results[0].mapping_assumptions)
        self.assertEqual("untested", parsed.results[0].qualification_status)
        self.assertEqual(0, coverage.qualified)
        self.assertEqual(1, coverage.untested)

    def test_unprocessed_and_suppressed_remain_in_denominator_and_suppressed_is_error(self):
        coverage = self.coverage(make_contract(["migrated", "suppressed", "unprocessed"]))
        self.assertEqual((3, 1, 1), (coverage.N, coverage.M, coverage.E))

    def test_multiple_findings_for_one_rule_count_once(self):
        record = make_contract(["blocked", "unprocessed"])
        record["results"][0]["findings"].extend(
            {
                "findingId": f"error-{index}",
                "kind": "error",
                "message": "Another unresolved error",
                "unresolved": True,
                "evidenceReferences": [],
            }
            for index in range(2, 20)
        )
        coverage = self.coverage(record)
        self.assertEqual(1, coverage.E)
        self.assertEqual(19, len(record["results"][0]["findings"]))

    def test_shared_provider_outage_stays_separate_from_rule_errors(self):
        record = make_contract(["unprocessed", "unprocessed"])
        record["environmentErrors"].append({
            "code": "providerUnavailable",
            "message": "Shared provider outage",
            "evidenceReferences": [],
        })
        parsed = validate_authoring_contract(record)
        coverage = calculate_coverage(parsed)
        self.assertEqual(1, len(parsed.environment_errors))
        self.assertEqual(0, coverage.E)
        self.assertEqual(2, coverage.N)

    def test_empty_and_duplicate_inventory_are_rejected(self):
        with self.assertRaisesRegex(AuthoringContractError, "non-empty"):
            validate_authoring_contract(make_contract([]))
        duplicate = make_contract(["unprocessed", "unprocessed"])
        duplicate["inventory"]["rules"][1]["ruleId"] = "rule-0"
        with self.assertRaisesRegex(AuthoringContractError, "duplicate rule identities"):
            validate_authoring_contract(duplicate)

    def test_unsupported_version_malformed_hash_and_escaping_paths_are_rejected(self):
        record = make_contract(["migrated"])
        record["schemaVersion"] = "2.0.0"
        with self.assertRaisesRegex(AuthoringContractError, "unsupported authoring contract version"):
            validate_authoring_contract(record)

        record = make_contract(["migrated"])
        record["source"]["sha256"] = "not-a-hash"
        with self.assertRaises(AuthoringContractError):
            validate_authoring_contract(record)

        record = make_contract(["migrated"])
        record["results"][0]["evidenceReferences"] = [{
            "path": "../outside.json",
            "sha256": EVIDENCE_HASH,
            "kind": "other",
        }]
        with self.assertRaisesRegex(AuthoringContractError, "safe repository-relative path"):
            validate_authoring_contract(record)

    def test_duplicate_results_cross_reference_and_status_inconsistencies_fail(self):
        duplicate = make_contract(["unprocessed", "unprocessed"])
        duplicate["results"][1]["ruleId"] = "rule-0"
        with self.assertRaisesRegex(AuthoringContractError, "duplicate rule identities"):
            validate_authoring_contract(duplicate)

        mismatch = make_contract(["unprocessed"])
        mismatch["results"][0]["sourceSha256"] = TARGET_HASH
        with self.assertRaisesRegex(AuthoringContractError, "source hash does not match"):
            validate_authoring_contract(mismatch)

        invalid_status = make_contract(["migrated"])
        invalid_status["results"][0]["target"]["structurallyValid"] = False
        with self.assertRaisesRegex(AuthoringContractError, "migrated rule"):
            validate_authoring_contract(invalid_status)

        error_mismatch = make_contract(["migrated"])
        error_mismatch["results"][0]["findings"] = [{
            "findingId": "bad",
            "kind": "error",
            "message": "Unresolved",
            "unresolved": True,
            "evidenceReferences": [],
        }]
        with self.assertRaisesRegex(AuthoringContractError, "migrated rule"):
            validate_authoring_contract(error_mismatch)

    def test_qualified_requires_runtime_and_actual_alert_parity_evidence(self):
        record = make_contract(["migrated"])
        record["results"][0]["qualificationStatus"] = "qualified"
        with self.assertRaisesRegex(AuthoringContractError, "needs runtimeVerification and alertParity"):
            validate_authoring_contract(record)

        record["results"][0]["qualificationEvidenceReferences"] = [
            {"path": "evidence/runtime.json", "sha256": EVIDENCE_HASH, "kind": "runtimeVerification"},
            {"path": "evidence/alert.json", "sha256": TARGET_HASH, "kind": "alertParity"},
        ]
        record.pop("coverage")
        record.pop("operationEligibility")
        parsed = validate_authoring_contract(seal_authoring_contract(record))
        self.assertEqual(1, calculate_coverage(parsed).qualified)

    def test_inconsistent_embedded_coverage_counts_are_rejected(self):
        record = make_contract(["migrated", "unprocessed"])
        record["coverage"]["M"] = 2
        with self.assertRaisesRegex(AuthoringContractError, "coverage counts or thresholds"):
            validate_authoring_contract(record)

    def test_operation_eligibility_is_advisory_and_never_authorizes_actions(self):
        coverage = self.coverage(make_contract(["migrated"] * 8 + ["unprocessed"] * 2))
        eligibility = calculate_operation_eligibility(coverage).as_dict()
        self.assertTrue(eligibility["migrationThresholdMet"])
        self.assertTrue(eligibility["successAndPrThresholdMet"])
        self.assertTrue(eligibility["requiresExactScopeAuthorization"])
        self.assertFalse(eligibility["coverageAuthorizesOperations"])
        self.assertFalse(eligibility["deploymentAuthorized"])
        self.assertFalse(eligibility["packagingAuthorized"])
        self.assertFalse(eligibility["ingestionAuthorized"])
        self.assertFalse(eligibility["prCreationAuthorized"])
        record = make_contract(["migrated"])
        record["operationEligibility"]["deploymentAuthorized"] = True
        with self.assertRaises(AuthoringContractError):
            validate_authoring_contract(record)

    def test_version_1_1_binds_complete_paths_queries_and_immutable_snapshot_revision(self):
        record = make_contract(["migrated", "unprocessed"])
        record["schemaVersion"] = AUTHORING_SCHEMA_VERSION
        record["snapshot"] = {"revision": 1, "previousSha256": None}
        for index, rule in enumerate(record["inventory"]["rules"]):
            rule["path"] = f"Analytic Rules/Nested/Rule{index}.yaml"
            rule["querySha256"] = f"{index + 3:064x}"
            result = record["results"][index]
            result["conversionStatus"] = "converted" if index == 0 else "unprocessed"
            result["validationStatus"] = "passed" if index == 0 else "notRun"
            if result["target"]:
                result["target"]["querySha256"] = f"{index + 5:064x}"
        record["inventory"]["sha256"] = calculate_inventory_sha256(
            record["inventory"]["rules"]
        )
        record["source"]["sha256"] = record["inventory"]["sha256"]
        record.pop("coverage")
        record.pop("operationEligibility")
        record = seal_authoring_contract(record)

        parsed = validate_authoring_contract(record)
        self.assertEqual(AUTHORING_SCHEMA_VERSION, parsed.schema_version)
        self.assertEqual(1, parsed.revision)
        self.assertEqual(
            "Analytic Rules/Nested/Rule0.yaml",
            parsed.inventory[0].path,
        )
        self.assertEqual(f"{5:064x}", parsed.results[0].target.query_sha256)
        self.assertEqual((2, 1, 0), (
            calculate_coverage(parsed).N,
            calculate_coverage(parsed).M,
            calculate_coverage(parsed).E,
        ))

        stale = copy.deepcopy(record)
        stale["inventory"]["rules"][0]["querySha256"] = "f" * 64
        stale.pop("coverage")
        stale.pop("operationEligibility")
        with self.assertRaisesRegex(AuthoringContractError, "inventory SHA-256"):
            seal_authoring_contract(stale)

    def test_version_1_1_requires_safe_paths_query_hashes_and_snapshot_chain_shape(self):
        record = make_contract(["unprocessed"])
        record["schemaVersion"] = AUTHORING_SCHEMA_VERSION
        record["snapshot"] = {"revision": 1, "previousSha256": None}
        record["inventory"]["rules"][0]["path"] = "../outside.yaml"
        record["inventory"]["rules"][0]["querySha256"] = HASH
        record["inventory"]["sha256"] = calculate_inventory_sha256(
            record["inventory"]["rules"]
        )
        record["results"][0]["conversionStatus"] = "unprocessed"
        record["results"][0]["validationStatus"] = "notRun"
        record.pop("coverage")
        record.pop("operationEligibility")
        with self.assertRaisesRegex(AuthoringContractError, "safe repository-relative path"):
            seal_authoring_contract(record)

        record = make_contract(["unprocessed"])
        record["schemaVersion"] = AUTHORING_SCHEMA_VERSION
        record["snapshot"] = {"revision": 2, "previousSha256": None}
        record["inventory"]["rules"][0]["path"] = "Analytic Rules/Rule.yaml"
        record["inventory"]["rules"][0]["querySha256"] = HASH
        record["inventory"]["sha256"] = calculate_inventory_sha256(
            record["inventory"]["rules"]
        )
        record["results"][0]["conversionStatus"] = "unprocessed"
        record["results"][0]["validationStatus"] = "notRun"
        record.pop("coverage")
        record.pop("operationEligibility")
        with self.assertRaisesRegex(AuthoringContractError, "revision 1"):
            seal_authoring_contract(record)


if __name__ == "__main__":
    unittest.main()
