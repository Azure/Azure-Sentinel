from __future__ import annotations

import copy
import json
import shutil
import tempfile
import unittest
from pathlib import Path
from unittest import mock

import yaml
from jsonschema import Draft202012Validator

from sentinel_xdr_migration.converter import convert_solution, validate_document, validate_solution
from sentinel_xdr_migration.deployment import graph_detection_payload

import test_customer_usage_attribution as attribution
from test_converter import RULE


SOURCE_ID = "11111111-2222-3333-4444-555555555555"
OTHER_ID = "11111111-2222-3333-4444-666666666666"
LEGACY_ID = "xdr-suspicious-test-activity-11111111"
CANONICAL_ID = f"xdr-{SOURCE_ID}"


class DetectionIdentityTests(unittest.TestCase):
    def setUp(self):
        self.fixture = tempfile.TemporaryDirectory(dir=Path.cwd())
        self.addCleanup(self.fixture.cleanup)
        self.solution = Path(self.fixture.name)
        self.source = self.solution / "Analytic Rules/Rule.yaml"
        self.source.parent.mkdir()
        self.source.write_text(RULE)
        self.output = self.solution / "XDR Detections/Rule.yaml"

    def read_output(self):
        return yaml.safe_load(self.output.read_text())

    def write_output(self, document):
        self.output.write_text(yaml.safe_dump(document, sort_keys=False))

    def legacy_output(self, *, version="3.1.1"):
        convert_solution(self.solution)
        document = self.read_output()
        document["properties"]["id"] = LEGACY_ID
        document["version"] = version
        self.write_output(document)
        return document

    def test_full_source_guid_is_stable_across_name_changes_and_shared_prefixes(self):
        second = self.source.with_name("Second.yaml")
        second.write_text(RULE.replace(SOURCE_ID, OTHER_ID))
        source_bytes = self.source.read_bytes(), second.read_bytes()
        result = convert_solution(self.solution)
        self.assertEqual(2, result["converted"])
        self.assertEqual(CANONICAL_ID, self.read_output()["properties"]["id"])
        other = yaml.safe_load(self.output.with_name("Second.yaml").read_text())
        self.assertEqual(f"xdr-{OTHER_ID}", other["properties"]["id"])
        self.assertEqual(source_bytes, (self.source.read_bytes(), second.read_bytes()))
        self.source.write_text(RULE.replace("Suspicious test activity", "Renamed test activity"))
        self.assertEqual(0, convert_solution(self.solution, overwrite=True)["conflicts"])
        document = self.read_output()
        self.assertEqual(CANONICAL_ID, document["properties"]["id"])
        self.assertEqual(SOURCE_ID, document["contentProvenance"]["source"]["id"])
        self.assertEqual(CANONICAL_ID, graph_detection_payload(document)["id"])
        self.assertEqual("3.1.0", document["version"])
        self.assertEqual("disabled", document["properties"]["status"])

    def test_source_guid_format_and_case_are_preserved_not_normalized(self):
        for source_id, valid in (
            ("ABCDEF12-2222-3333-4444-555555555555", True),
            ("source-id", False),
            ("11111111222233334444555555555555", False),
            ("{11111111-2222-3333-4444-555555555555}", False),
            (SOURCE_ID + " ", False),
        ):
            with self.subTest(source_id=source_id):
                if self.output.exists():
                    self.output.unlink()
                self.source.write_text(RULE.replace(SOURCE_ID, json.dumps(source_id)))
                convert_solution(self.solution)
                document = self.read_output()
                self.assertEqual(f"xdr-{source_id}", document["properties"]["id"])
                self.assertEqual(valid, not validate_document(document))

    def test_legacy_reconversion_is_explicit_local_only_and_idempotent(self):
        self.legacy_output()
        before = self.output.read_bytes()
        with mock.patch("sentinel_xdr_migration.deployment._graph_request") as graph:
            self.assertEqual(1, convert_solution(self.solution)["conflicts"])
            self.assertEqual(before, self.output.read_bytes())
            self.source.write_text(RULE.replace("Suspicious test activity", "Renamed"))
            result = convert_solution(self.solution, overwrite=True)
            graph.assert_not_called()
        self.assertEqual(0, result["conflicts"])
        document = self.read_output()
        self.assertEqual("3.1.1", document["version"])
        self.assertEqual(CANONICAL_ID, document["properties"]["id"])
        self.assertEqual("disabled", document["properties"]["status"])
        conversion = document["contentProvenance"]["conversion"]
        self.assertEqual({
            "previousId": LEGACY_ID, "currentId": CANONICAL_ID, "scope": "local-artifact-only",
        }, conversion["identityChange"])
        warning = next(value for value in conversion["warnings"] if "Local detection ID changed" in value)
        self.assertIn("No cloud rules were updated, deleted, or migrated", warning)
        manifest = json.loads(Path(result["manifest"]).read_text())
        self.assertIn(warning, manifest["results"][0]["warnings"])
        self.assertIn("Local detection ID changed", Path(result["transformationReport"]).read_text())
        self.assertEqual([], validate_document(document))
        after = self.output.read_bytes()
        self.assertEqual(0, convert_solution(self.solution)["conflicts"])
        self.assertEqual(after, self.output.read_bytes())

    def test_unversioned_legacy_output_migrates_but_custom_ids_do_not(self):
        document = self.legacy_output()
        document.pop("version")
        self.write_output(document)
        self.assertEqual(0, convert_solution(self.solution, overwrite=True)["conflicts"])
        self.assertEqual("3.1.0", self.read_output()["version"])
        self.assertEqual(CANONICAL_ID, self.read_output()["properties"]["id"])
        for custom_id in ("hand-authored-id", "xdr-custom-authored-11111111", OTHER_ID):
            with self.subTest(custom_id=custom_id):
                document = self.read_output()
                document["properties"]["id"] = custom_id
                self.write_output(document)
                before = self.output.read_bytes()
                result = convert_solution(self.solution, overwrite=True)
                self.assertEqual(1, result["conflicts"])
                self.assertIn("custom identity", result["results"][0]["errors"][0])
                self.assertEqual(before, self.output.read_bytes())

    def test_conflicting_or_missing_provenance_is_never_overwritten_or_excluded(self):
        original = self.legacy_output()
        for field, value in (("id", OTHER_ID), ("path", "Analytic Rules/Other.yaml"),
                             ("platform", "Unrelated"), ("kind", "Other")):
            for versioned in (True, False):
                with self.subTest(field=field, versioned=versioned):
                    document = copy.deepcopy(original)
                    document["contentProvenance"]["source"][field] = value
                    # A converter marker must not override conflicting source provenance.
                    if not versioned:
                        document.pop("version")
                    self.write_output(document)
                    before = self.output.read_bytes()
                    result = convert_solution(self.solution, overwrite=True)
                    self.assertEqual(1, result["conflicts"])
                    self.assertEqual(before, self.output.read_bytes())
        document = copy.deepcopy(original)
        document.pop("contentProvenance")
        self.write_output(document)
        config = self.solution / "exclude.json"
        config.write_text(json.dumps({"excludedRuleIds": {SOURCE_ID: "test"}}))
        before = self.output.read_bytes()
        self.assertEqual(1, convert_solution(self.solution, overwrite=True, config_path=config)["conflicts"])
        self.assertEqual(before, self.output.read_bytes())

    def test_legacy_shape_without_converter_marker_is_not_auto_migrated(self):
        document = self.legacy_output()
        document["contentProvenance"]["conversion"]["tool"] = "other"
        self.write_output(document)
        before = self.output.read_bytes()
        self.assertEqual(1, convert_solution(self.solution, overwrite=True)["conflicts"])
        self.assertEqual(before, self.output.read_bytes())

    def test_duplicate_source_guids_block_all_colliding_outputs(self):
        for source_id in (SOURCE_ID, "ABCDEF12-2222-3333-4444-555555555555"):
            with self.subTest(source_id=source_id):
                self.source.write_text(RULE.replace(SOURCE_ID, source_id))
                self.source.with_name("Second.yaml").write_text(RULE.replace(SOURCE_ID, source_id.lower()))
                result = convert_solution(self.solution, overwrite=True)
                self.assertEqual(2, result["conflicts"])
                self.assertFalse(self.output.exists())

    def test_id_owned_by_another_output_is_not_reused(self):
        convert_solution(self.solution)
        document = self.read_output()
        document["contentProvenance"]["source"]["id"] = OTHER_ID
        document["contentProvenance"]["source"]["path"] = "Analytic Rules/Other.yaml"
        other_output = self.output.with_name("Unrelated.yaml")
        other_output.write_text(yaml.safe_dump(document))
        before = self.output.read_bytes(), other_output.read_bytes()
        result = convert_solution(self.solution, overwrite=True)
        self.assertEqual(1, result["conflicts"])
        self.assertEqual(before, (self.output.read_bytes(), other_output.read_bytes()))
        validation = validate_solution(self.solution)
        self.assertEqual(2, validation["invalid"])
        self.assertTrue(all(any("duplicate Custom Detection" in error for error in row["errors"])
                            for row in validation["results"]))

    def test_validation_contract_is_source_derived_only(self):
        convert_solution(self.solution)
        document = self.read_output()
        document["properties"]["id"] = OTHER_ID
        self.assertTrue(any("canonical xdr- prefix" in error for error in validate_document(document)))
        document["properties"]["id"] = LEGACY_ID
        errors = validate_document(document)
        self.assertTrue(any("canonical xdr- prefix" in error for error in errors))
        with self.assertRaisesRegex(ValueError, "canonical xdr- prefix"):
            graph_detection_payload(document)
        document["contentProvenance"]["source"]["platform"] = "Other"
        document["contentProvenance"]["source"]["kind"] = "Other"
        document["contentProvenance"]["source"]["id"] = "other-source"
        document["contentProvenance"]["conversion"]["tool"] = "other-tool"
        self.assertEqual([], validate_document(document))
        schema = json.loads((attribution.ROOT / "Tools/SentinelToXDRMigration/schema/xdr-detection.schema.json").read_text())
        Draft202012Validator.check_schema(schema)


@unittest.skipUnless(shutil.which("pwsh"), "PowerShell 7 is required")
class PackagedIdentityTests(unittest.TestCase):
    setUp = attribution.AttributionTests.setUp
    run_ps = attribution.AttributionTests.run_ps
    prepare_integration = attribution.AttributionTests.prepare_integration
    package = attribution.AttributionTests.package
    write_metadata = attribution.AttributionTests.write_metadata

    def fixture(self):
        entry = self.prepare_integration()
        self.write_metadata(attribution.TRACKING_ID)
        path = self.solution / "XDR Detections/Test.yaml"
        document = json.loads(path.read_text().removeprefix("---\n"))
        document["contentProvenance"]["source"].update(
            platform="Microsoft Sentinel", kind="AnalyticsRule",
        )
        document["properties"]["id"] = SOURCE_ID
        path.write_text("---\n" + json.dumps(document))
        data = json.loads(self.data.read_text())
        data["Include XDR Content Registration"] = True
        self.data.write_text(json.dumps(data))
        return entry, path, document

    def test_packaging_preserves_full_guid_in_install_and_registration_wrappers(self):
        entry, path, document = self.fixture()
        before = path.read_bytes()
        for pipeline in (False, True):
            with self.subTest(pipeline=pipeline):
                result = self.package(entry, pipeline)
                self.assertEqual(0, result.returncode, result.stdout + result.stderr)
                template = json.loads((self.solution / "Package/mainTemplate.json").read_text())
                install = next(r for r in template["resources"] if r["type"] == "Microsoft.Resources/deployments"
                               and r.get("condition") == "[parameters('DeployCustomDetection')]")
                registration = next(r for r in template["resources"]
                                    if r.get("properties", {}).get("contentKind") == "CustomDetection")
                packaged_id = f"xdr-{SOURCE_ID}"
                expected_id = f"[if(true(), '{packaged_id}', '{packaged_id}')]"
                install_properties = install["properties"]["template"]["resources"]["detectionRule"]["properties"]
                registered_properties = registration["properties"]["mainTemplate"]["resources"]["detectionRule"]["properties"]
                self.assertEqual(expected_id, install_properties["id"])
                self.assertEqual(expected_id, registered_properties["id"])
                self.assertEqual(packaged_id, registration["properties"]["contentId"])
                self.assertEqual(
                    f"Sample-CD-{packaged_id}", install["name"],
                )
                self.assertEqual(
                    f"[resourceId('Microsoft.Resources/deployments', 'Sample-CD-{packaged_id}')]",
                    registration["dependsOn"][0],
                )
                self.assertIn(
                    f"uniquestring('{packaged_id}')",
                    registration["name"],
                )
                self.assertIn(
                    f"'{packaged_id}'",
                    registration["properties"]["contentProductId"],
                )
                content_packages = next(
                    resource for resource in template["resources"]
                    if resource["type"].endswith("/contentPackages")
                )
                packaged_criteria = [
                    criterion for criterion in content_packages["properties"]["dependencies"]["criteria"]
                    if criterion.get("kind") == "CustomDetection"
                ]
                self.assertEqual([{
                    "kind": "CustomDetection", "contentId": packaged_id, "version": "3.1.0",
                }], packaged_criteria)
                self.assertEqual(
                    SOURCE_ID,
                    json.loads(path.read_text().removeprefix("---\n"))["contentProvenance"]["source"]["id"],
                )
                self.assertEqual("3.1.0", registration["properties"]["version"])
                self.assertEqual("disabled", install_properties["status"])
                self.assertEqual(before, path.read_bytes())

    def test_already_prefixed_identity_is_idempotent_across_repeated_packaging(self):
        entry, path, document = self.fixture()
        document["properties"]["id"] = f"xdr-{SOURCE_ID}"
        path.write_text("---\n" + json.dumps(document))
        before = path.read_bytes()
        packaged_ids = []
        for pipeline in (False, True):
            result = self.package(entry, pipeline)
            self.assertEqual(0, result.returncode, result.stdout + result.stderr)
            template = json.loads((self.solution / "Package/mainTemplate.json").read_text())
            registration = next(
                resource for resource in template["resources"]
                if resource.get("properties", {}).get("contentKind") == "CustomDetection"
            )
            packaged_ids.append(registration["properties"]["contentId"])
        self.assertEqual([f"xdr-{SOURCE_ID}", f"xdr-{SOURCE_ID}"], packaged_ids)
        self.assertEqual(before, path.read_bytes())

    def test_letter_starting_source_guid_uses_same_canonical_prefix(self):
        entry, path, document = self.fixture()
        source_id = "ABCDEF12-2222-3333-4444-555555555555"
        document["contentProvenance"]["source"]["id"] = source_id
        document["properties"]["id"] = source_id
        path.write_text("---\n" + json.dumps(document))
        analytic = self.solution / "Analytic Rules/Test.yaml"
        rule = yaml.safe_load(analytic.read_text())
        rule["id"] = source_id
        analytic.write_text(yaml.safe_dump(rule, sort_keys=False))
        result = self.package(entry, False)
        self.assertEqual(0, result.returncode, result.stdout + result.stderr)
        template = json.loads((self.solution / "Package/mainTemplate.json").read_text())
        registration = next(
            resource for resource in template["resources"]
            if resource.get("properties", {}).get("contentKind") == "CustomDetection"
        )
        self.assertEqual(f"xdr-{source_id}", registration["properties"]["contentId"])
        self.assertEqual(source_id, json.loads(path.read_text().removeprefix("---\n"))[
            "contentProvenance"]["source"]["id"]
        )

    def test_bare_and_prefixed_copy_collision_is_rejected_after_normalization(self):
        entry, path, document = self.fixture()
        duplicate = self.solution / "XDR Detections/Copy.yaml"
        duplicate_document = copy.deepcopy(document)
        duplicate_document["properties"]["id"] = f"xdr-{SOURCE_ID}"
        duplicate.write_text("---\n" + json.dumps(duplicate_document))
        data = json.loads(self.data.read_text())
        data["XDR Detections"].append("XDR Detections/Copy.yaml")
        self.data.write_text(json.dumps(data))
        result = self.package(entry, False)
        self.assertNotEqual(0, result.returncode, result.stdout + result.stderr)
        self.assertIn("Duplicate Custom Detection id", result.stdout + result.stderr)
        self.assertIn("after canonical ID normalization", result.stdout + result.stderr)

    def test_packaging_rejects_mismatched_legacy_and_malformed_source_ids(self):
        entry, path, original = self.fixture()
        for source_id, detection_id in ((SOURCE_ID, LEGACY_ID), (SOURCE_ID, OTHER_ID),
                                        ("source-id", "source-id")):
            for pipeline in (False, True):
                with self.subTest(source_id=source_id, detection_id=detection_id, pipeline=pipeline):
                    document = copy.deepcopy(original)
                    document["contentProvenance"]["source"]["id"] = source_id
                    document["properties"]["id"] = detection_id
                    path.write_text("---\n" + json.dumps(document))
                    result = self.package(entry, pipeline)
                    self.assertNotEqual(0, result.returncode, result.stdout + result.stderr)
                    output = result.stdout + result.stderr
                    self.assertTrue(
                        "originating Sentinel GUID" in output
                        or "conflicts with originating" in output
                        or "canonical xdr-<GUID>" in output
                        or "originating Sentinel template GUID" in output,
                        output,
                    )
                    self.assertFalse((self.solution / "Package/mainTemplate.json").exists())

    def test_packaging_keeps_unrelated_custom_detection_id_contract(self):
        entry, path, document = self.fixture()
        document["contentProvenance"]["source"].update(platform="Other", kind="Other")
        document["properties"]["id"] = "custom-authored-id"
        path.write_text("---\n" + json.dumps(document))
        result = self.package(entry, False)
        self.assertEqual(0, result.returncode, result.stdout + result.stderr)


if __name__ == "__main__":
    unittest.main()
