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

from sentinel_xdr_migration.converter import (
    XDR_SCHEMA_PATH,
    build_xdr_document,
    convert_solution,
    validate_document,
    validate_solution,
)
from sentinel_xdr_migration.deployment import graph_detection_payload

import test_detection_identity as identity
from test_converter import RULE


CONNECTORS = [
    {
        "connectorId": "MicrosoftThreatProtection",
        "dataTypes": ["IdentityInfo", "DeviceEvents", "IdentityInfo"],
        "extension": {"labels": ["CaseSensitive"], "enabled": False},
    },
    {"connectorId": "OtherConnector", "dataTypes": []},
]
ABSENT = object()


class ConnectorMetadataTests(unittest.TestCase):
    def setUp(self):
        self.fixture = tempfile.TemporaryDirectory(dir=Path.cwd())
        self.addCleanup(self.fixture.cleanup)
        self.solution = Path(self.fixture.name)
        self.source = self.solution / "Analytic Rules/Rule.yaml"
        self.source.parent.mkdir()
        self.output = self.solution / "XDR Detections/Rule.yaml"

    def write_source(self, connectors=ABSENT):
        source = yaml.safe_load(RULE)
        if connectors is not ABSENT:
            source["requiredDataConnectors"] = copy.deepcopy(connectors)
        self.source.write_text(yaml.safe_dump(source, sort_keys=False))
        return source

    def test_present_empty_and_absent_round_trip_and_reconversion(self):
        for connectors in (CONNECTORS, [], ABSENT):
            with self.subTest(connectors=connectors):
                self.write_source(connectors)
                source_bytes = self.source.read_bytes()
                result = convert_solution(self.solution, overwrite=True)
                self.assertEqual(1, result["converted"])
                document = yaml.safe_load(self.output.read_text())
                self.assertEqual(connectors is not ABSENT, "requiredDataConnectors" in document)
                if connectors is not ABSENT:
                    self.assertEqual(connectors, document["requiredDataConnectors"])
                self.assertEqual([], validate_document(document))
                self.assertEqual(source_bytes, self.source.read_bytes())
                self.assertEqual(f"xdr-{identity.SOURCE_ID}", document["properties"]["id"])
                self.assertEqual("disabled", document["properties"]["status"])
                document["version"] = "3.1.2"
                self.output.write_text(yaml.safe_dump(document, sort_keys=False))
                self.assertEqual(0, convert_solution(self.solution, overwrite=True)["conflicts"])
                self.assertEqual("3.1.2", yaml.safe_load(self.output.read_text())["version"])
                after = self.output.read_bytes()
                self.assertEqual(0, convert_solution(self.solution)["conflicts"])
                self.assertEqual(after, self.output.read_bytes())

    def test_refreshing_older_output_requires_explicit_overwrite(self):
        self.write_source()
        convert_solution(self.solution)
        before = self.output.read_bytes()
        self.write_source(CONNECTORS)
        self.assertEqual(1, convert_solution(self.solution)["conflicts"])
        self.assertEqual(before, self.output.read_bytes())
        self.assertEqual(0, convert_solution(self.solution, overwrite=True)["conflicts"])
        self.assertEqual(CONNECTORS, yaml.safe_load(self.output.read_text())["requiredDataConnectors"])

    def test_metadata_is_deep_copied_without_mutating_source_aliases(self):
        source = self.write_source(CONNECTORS)
        source["requiredDataConnectors"].append(source["requiredDataConnectors"][0])
        expected = copy.deepcopy(source)
        with mock.patch("sentinel_xdr_migration.converter.yaml.safe_load", return_value=source):
            document = build_xdr_document(self.source, self.solution, {})
        self.assertEqual(expected, source)
        self.assertEqual(source["requiredDataConnectors"], document["requiredDataConnectors"])
        document["requiredDataConnectors"][0]["extension"]["labels"].append("changed")
        document["requiredDataConnectors"][1]["dataTypes"].append("changed")
        self.assertEqual(expected, source)

    def test_malformed_source_is_preserved_but_never_reported_converted(self):
        malformed = (
            None, False, "connector", {}, [None], ["connector"], [{}],
            [{"connectorId": "x"}], [{"dataTypes": []}],
            [{"connectorId": 1, "dataTypes": []}],
            [{"connectorId": "x", "dataTypes": None}],
            [{"connectorId": "x", "dataTypes": "DeviceEvents"}],
            [{"connectorId": "x", "dataTypes": [1]}],
        )
        for value in malformed:
            with self.subTest(value=value):
                self.write_source(value)
                result = convert_solution(self.solution, overwrite=True)
                self.assertEqual(0, result["converted"])
                self.assertEqual(1, result["needsReview"])
                self.assertTrue(any("requiredDataConnectors" in error
                                    for error in result["results"][0]["errors"]))
                document = yaml.safe_load(self.output.read_text())
                self.assertEqual(value, document["requiredDataConnectors"])
                self.assertTrue(any(error.startswith("schema:") for error in validate_document(document)))
                self.assertEqual(1, validate_solution(self.solution)["invalid"])
                with self.assertRaises(ValueError):
                    graph_detection_payload(document)

    def test_schema_rejects_malformed_authored_metadata_without_conversion_errors(self):
        self.write_source()
        document = build_xdr_document(self.source, self.solution, {})
        schema = json.loads(XDR_SCHEMA_PATH.read_text())
        Draft202012Validator.check_schema(schema)
        document["requiredDataConnectors"] = [{"connectorId": [], "dataTypes": {}}]
        self.assertTrue(list(Draft202012Validator(schema).iter_errors(document)))
        self.assertTrue(any(error.startswith("schema:") for error in validate_document(document)))

    def test_graph_payload_excludes_authoring_metadata_and_has_no_aliases(self):
        self.write_source(CONNECTORS)
        document = build_xdr_document(self.source, self.solution, {})
        before = copy.deepcopy(document)
        payload = graph_detection_payload(document)
        self.assertEqual(before, document)
        self.assertNotIn("requiredDataConnectors", payload)
        self.assertNotIn("contentProvenance", payload)
        self.assertEqual(f"xdr-{identity.SOURCE_ID}", payload["id"])
        self.assertEqual("disabled", payload["status"])
        payload["queryCondition"]["queryText"] = "changed"
        self.assertEqual(before, document)


@unittest.skipUnless(shutil.which("pwsh"), "PowerShell 7 is required")
class PackagedConnectorMetadataTests(unittest.TestCase):
    setUp = identity.PackagedIdentityTests.setUp
    run_ps = identity.PackagedIdentityTests.run_ps
    prepare_integration = identity.PackagedIdentityTests.prepare_integration
    package = identity.PackagedIdentityTests.package
    write_metadata = identity.PackagedIdentityTests.write_metadata
    fixture = identity.PackagedIdentityTests.fixture

    def test_packager_rejects_missing_unknown_or_unreviewed_dependencies(self):
        entry, path, document = self.fixture()
        for mutation in ("missing", "unknown", "unreviewed"):
            candidate = copy.deepcopy(document)
            if mutation == "missing":
                del candidate["contentProvenance"]["requiredWorkloads"]
            elif mutation == "unknown":
                candidate["contentProvenance"]["requiredWorkloads"] = [
                    {"workload": "defender", "dataTypes": ["DeviceEvents"]},
                ]
            else:
                candidate["contentProvenance"]["dependencyReviewRequired"] = True
            path.write_text("---\n" + json.dumps(candidate))
            result = self.package(entry, False)
            self.assertNotEqual(0, result.returncode, mutation)
            self.assertTrue(any(word in result.stdout + result.stderr for word in (
                "contentProvenance.requiredWorkloads", "workload 'defender'", "unresolved dependency",
            )), result.stdout + result.stderr)

    def test_dependency_records_are_kept_in_registration_not_install(self):
        entry, path, document = self.fixture()
        document["requiredDataConnectors"] = CONNECTORS
        document["contentProvenance"]["requiredDataConnectors"] = CONNECTORS
        document["contentProvenance"]["requiredWorkloads"] = [
            {"workload": "mde", "dataTypes": ["DeviceEvents"]},
        ]
        path.write_text("---\n" + json.dumps(document))
        before = path.read_bytes()
        result = self.package(entry, False)
        self.assertEqual(0, result.returncode, result.stdout + result.stderr)
        template = json.loads((self.solution / "Package/mainTemplate.json").read_text())
        install = next(r for r in template["resources"] if r["type"] == "Microsoft.Resources/deployments"
                       and r.get("condition") == "[parameters('DeployCustomDetection')]")
        registration = next(r for r in template["resources"]
                            if r.get("properties", {}).get("contentKind") == "CustomDetection")
        deployed = install["properties"]["template"]["resources"]["detectionRule"]["properties"]["contentProvenance"]
        stored = registration["properties"]["mainTemplate"]["resources"]["detectionRule"]["properties"]["contentProvenance"]
        full = registration["properties"]["contentProvenance"]
        self.assertEqual({
            "packageId": "testpublisher.test-sentinel", "packageVersion": "3.2.0",
            "contentId": registration["properties"]["contentId"], "contentVersion": "3.1.0",
        }, deployed)
        self.assertEqual(deployed, stored)
        self.assertEqual(deployed, {key: full[key] for key in deployed})
        self.assertEqual(CONNECTORS, full["requiredDataConnectors"])
        self.assertEqual(document["contentProvenance"]["requiredWorkloads"], full["requiredWorkloads"])
        self.assertNotIn("requiredDataConnectors", json.dumps(install))
        self.assertNotIn("OtherConnector", json.dumps(install))
        self.assertEqual(before, path.read_bytes())
        self.assertEqual(CONNECTORS, yaml.safe_load(path.read_text())["requiredDataConnectors"])


if __name__ == "__main__":
    unittest.main()
