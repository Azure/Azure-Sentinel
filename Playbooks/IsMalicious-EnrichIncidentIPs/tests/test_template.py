"""Structural and credential-safety checks, not live Azure deployment tests."""

import json
import unittest
from pathlib import Path


class PlaybookTemplateTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.template = json.loads(
            (Path(__file__).parents[1] / "azuredeploy.json").read_text(encoding="utf-8")
        )
        cls.workflow = next(
            r
            for r in cls.template["resources"]
            if r["type"] == "Microsoft.Logic/workflows"
        )
        cls.definition = cls.workflow["properties"]["definition"]
        cls.actions = cls.definition["actions"]
        cls.loop = cls.actions["For_each_IP"]

    def test_secret_is_secure_at_both_boundaries(self):
        self.assertEqual(
            self.template["parameters"]["IsMaliciousCredential"]["type"], "secureString"
        )
        self.assertEqual(
            self.definition["parameters"]["IsMaliciousCredential"]["type"],
            "SecureString",
        )
        self.assertNotIn(
            "defaultValue", self.template["parameters"]["IsMaliciousCredential"]
        )
        self.assertNotIn(
            "defaultValue", self.definition["parameters"]["IsMaliciousCredential"]
        )

    def test_http_credentials_hidden_from_run_history(self):
        action = self.loop["actions"]["Check_IP"]
        self.assertEqual(
            set(action["runtimeConfiguration"]["secureData"]["properties"]),
            {"inputs", "outputs"},
        )
        self.assertEqual(
            action["inputs"]["headers"]["X-API-KEY"],
            "@parameters('IsMaliciousCredential')",
        )

    def test_credential_never_in_incident_comment(self):
        comment = json.dumps(self.actions["Add_incident_comment"])
        self.assertNotIn("IsMaliciousCredential", comment)
        for name in ("Append_result", "Append_failure"):
            self.assertNotIn(
                "IsMaliciousCredential", json.dumps(self.loop["actions"][name])
            )

    def test_bounded_serial_lookups(self):
        self.assertIn("take(", self.loop["foreach"])
        self.assertEqual(
            self.loop["runtimeConfiguration"]["concurrency"]["repetitions"], 1
        )
        cap = self.template["parameters"]["MaxIPsPerIncident"]
        self.assertEqual(cap["minValue"], 1)
        self.assertLessEqual(cap["maxValue"], 50)
        self.assertEqual(
            self.loop["actions"]["Check_IP"]["inputs"]["retryPolicy"]["type"], "none"
        )

    def test_safe_endpoint_and_encoded_indicator(self):
        request = self.loop["actions"]["Check_IP"]["inputs"]
        self.assertEqual(request["method"], "GET")
        self.assertIn("https://api.ismalicious.com/check?query=", request["uri"])
        self.assertIn("uriComponent(items('For_each_IP')?['Address'])", request["uri"])
        self.assertIn("enrichment=standard", request["uri"])

    def test_invalid_response_and_http_failure_become_unknown(self):
        parse = self.loop["actions"]["Validate_response"]
        self.assertEqual(
            set(parse["inputs"]["schema"]["required"]), {"malicious", "evidence"}
        )
        failure = self.loop["actions"]["Append_failure"]
        self.assertEqual(
            set(failure["runAfter"]["Validate_response"]),
            {"Failed", "Skipped", "TimedOut"},
        )
        self.assertEqual(failure["inputs"]["value"]["Verdict"], "unknown")

    def test_failure_row_does_not_require_http_outputs(self):
        status = self.loop["actions"]["Append_failure"]["inputs"]["value"]["Status"]
        self.assertNotIn("outputs('Check_IP')", status)
        self.assertIn("actions('Check_IP')?['outputs']?['statusCode']", status)
        self.assertIn(
            "coalesce(actions('Check_IP')?['status'], 'not executed')", status
        )

    def test_sentinel_uses_system_assigned_managed_identity(self):
        connection = next(
            r
            for r in self.template["resources"]
            if r["type"] == "Microsoft.Web/connections"
        )
        self.assertEqual(connection["kind"], "V1")
        self.assertEqual(connection["properties"]["parameterValueType"], "Alternative")
        self.assertEqual(self.workflow["identity"]["type"], "SystemAssigned")
        authentication = self.workflow["properties"]["parameters"]["$connections"][
            "value"
        ]["azuresentinel"]["connectionProperties"]["authentication"]
        self.assertEqual(authentication["type"], "ManagedServiceIdentity")

    def test_ip_cap_is_supplied_from_arm_without_a_second_default(self):
        self.assertNotIn(
            "defaultValue", self.definition["parameters"]["MaxIPsPerIncident"]
        )
        self.assertEqual(
            self.workflow["properties"]["parameters"]["MaxIPsPerIncident"]["value"],
            "[parameters('MaxIPsPerIncident')]",
        )

    def test_risk_and_confidence_separate_and_optional(self):
        row = self.loop["actions"]["Append_result"]["inputs"]["value"]
        self.assertIn("['riskScore']?['score']", row["Risk score"])
        self.assertIn("['confidence']?['score']", row["Confidence"])
        self.assertNotIn("coalesce", row["Risk score"])
        self.assertIn("['blocklistHits']", row["Blocklist hits"])
        self.assertIn("['evidence']?['verdict']", row["Verdict"])
        self.assertNotIn("sources", row["Blocklist hits"])

    def test_finalizes_failed_and_skipped_loops(self):
        self.assertEqual(
            set(self.actions["Create_result_table"]["runAfter"]["For_each_IP"]),
            {"Succeeded", "Failed", "TimedOut", "Skipped"},
        )
        self.assertEqual(self.actions["Initialize_results"]["runAfter"], {})
        self.assertIn("Initialize_results", self.actions["Get_IP_entities"]["runAfter"])
        comment = self.actions["Add_incident_comment"]["inputs"]["body"]["message"]
        self.assertIn("Results may be partial", comment)

    def test_deploys_disabled(self):
        self.assertEqual(
            self.template["parameters"]["WorkflowState"]["defaultValue"], "Disabled"
        )

    def test_deployment_metadata_contains_operator_instructions(self):
        for field in ("prerequisites", "postDeployment"):
            with self.subTest(field=field):
                instructions = self.template["metadata"].get(field)
                self.assertIsInstance(instructions, list)
                self.assertGreater(len(instructions), 0)
                for instruction in instructions:
                    self.assertIsInstance(instruction, str)
                    self.assertTrue(instruction.strip())

    def test_arm_parameters_have_deployment_descriptions(self):
        for name, parameter in self.template["parameters"].items():
            with self.subTest(parameter=name):
                description = parameter.get("metadata", {}).get("description")
                self.assertIsInstance(description, str)
                self.assertTrue(description.strip())

    def test_all_run_after_edges_reference_sibling_actions(self):
        def validate(actions):
            for action in actions.values():
                for predecessor in action.get("runAfter", {}):
                    self.assertIn(predecessor, actions)
                if "actions" in action:
                    validate(action["actions"])

        validate(self.actions)


if __name__ == "__main__":
    unittest.main()
