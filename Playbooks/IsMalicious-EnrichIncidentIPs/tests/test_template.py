"""Structural and credential-safety checks, not live Azure deployment tests."""

import json
import unittest
from pathlib import Path


class PlaybookTemplateTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.template = json.loads((Path(__file__).parents[1] / "azuredeploy.json").read_text())
        cls.workflow = next(r for r in cls.template["resources"] if r["type"] == "Microsoft.Logic/workflows")
        cls.definition = cls.workflow["properties"]["definition"]
        cls.actions = cls.definition["actions"]
        cls.loop = cls.actions["For_each_IP"]

    def test_secret_is_secure_at_both_boundaries(self):
        self.assertEqual(self.template["parameters"]["IsMaliciousCredential"]["type"], "secureString")
        self.assertEqual(self.definition["parameters"]["IsMaliciousCredential"]["type"], "SecureString")
        self.assertNotIn("defaultValue", self.template["parameters"]["IsMaliciousCredential"])
        self.assertNotIn("defaultValue", self.definition["parameters"]["IsMaliciousCredential"])

    def test_http_credentials_hidden_from_run_history(self):
        action = self.loop["actions"]["Check_IP"]
        self.assertEqual(set(action["runtimeConfiguration"]["secureData"]["properties"]), {"inputs", "outputs"})
        self.assertEqual(action["inputs"]["headers"]["X-API-KEY"], "@parameters('IsMaliciousCredential')")

    def test_credential_never_in_incident_comment(self):
        comment = json.dumps(self.actions["Add_incident_comment"])
        self.assertNotIn("IsMaliciousCredential", comment)
        for name in ("Append_result", "Append_failure"):
            self.assertNotIn("IsMaliciousCredential", json.dumps(self.loop["actions"][name]))

    def test_bounded_serial_lookups(self):
        self.assertIn("take(", self.loop["foreach"])
        self.assertEqual(self.loop["runtimeConfiguration"]["concurrency"]["repetitions"], 1)
        cap = self.template["parameters"]["MaxIPsPerIncident"]
        self.assertEqual(cap["minValue"], 1)
        self.assertLessEqual(cap["maxValue"], 50)
        self.assertEqual(self.loop["actions"]["Check_IP"]["inputs"]["retryPolicy"]["type"], "none")

    def test_safe_endpoint_and_encoded_indicator(self):
        request = self.loop["actions"]["Check_IP"]["inputs"]
        self.assertEqual(request["method"], "GET")
        self.assertIn("https://api.ismalicious.com/check?query=", request["uri"])
        self.assertIn("uriComponent(items('For_each_IP')?['Address'])", request["uri"])
        self.assertIn("enrichment=standard", request["uri"])

    def test_invalid_response_and_http_failure_become_unknown(self):
        parse = self.loop["actions"]["Validate_response"]
        self.assertEqual(set(parse["inputs"]["schema"]["required"]), {"malicious", "evidence"})
        failure = self.loop["actions"]["Append_failure"]
        self.assertEqual(set(failure["runAfter"]["Validate_response"]), {"Failed", "Skipped", "TimedOut"})
        self.assertEqual(failure["inputs"]["value"]["Verdict"], "unknown")

    def test_risk_and_confidence_separate_and_optional(self):
        row = self.loop["actions"]["Append_result"]["inputs"]["value"]
        self.assertIn("['riskScore']?['score']", row["Risk score"])
        self.assertIn("['confidence']?['score']", row["Confidence"])
        self.assertNotIn("coalesce", row["Risk score"])
        self.assertIn("['blocklistHits']", row["Blocklist hits"])
        self.assertIn("['evidence']?['verdict']", row["Verdict"])
        self.assertNotIn("sources", row["Blocklist hits"])

    def test_deploys_disabled(self):
        self.assertEqual(self.template["parameters"]["WorkflowState"]["defaultValue"], "Disabled")

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
