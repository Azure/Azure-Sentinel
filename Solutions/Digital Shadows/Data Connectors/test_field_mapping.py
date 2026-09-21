"""
Unit test for the SearchLight → V2 row mapping in DS_poller._build_v2_row.

Verifies every declared DCR column maps to the right SearchLight field,
that the id field routes to IncidentId (real) or AlertId (string) by
context (per the architect-approved design), and that missing optional
fields default to the empty string / None as the DCR schema expects.

Run from the repo root:
    python3 "Solutions/Digital Shadows/Data Connectors/test_field_mapping.py"
"""
import importlib.util
import json
import sys
import unittest
from pathlib import Path


# Load DS_poller.py as a standalone module so we can call the pure
# `_build_v2_row` helper without triggering the package's __init__.py
# (which reads env vars and imports azure.functions at module load time).
_DS_POLLER_PATH = (
    Path(__file__).resolve().parent
    / "DigitalShadowsConnectorAzureFunction"
    / "DS_poller.py"
)

# DS_poller does `from . import AS_api` / `from .state_serializer import State`
# at module load. Provide minimal stubs so the import succeeds without pulling
# in the whole connector package.
_pkg = "DigitalShadowsConnectorAzureFunction"

import types
sys.modules.setdefault(_pkg, types.ModuleType(_pkg))
_as_stub = types.ModuleType(f"{_pkg}.AS_api")
class _LogsApiStub:
    def __init__(self, *a, **kw): pass
    def post_data(self, *a, **kw): pass
_as_stub.logs_api = _LogsApiStub
sys.modules[f"{_pkg}.AS_api"] = _as_stub

_ds_stub = types.ModuleType(f"{_pkg}.DS_api")
class _DSApiStub:
    def __init__(self, *a, **kw): pass
_ds_stub.api = _DSApiStub
sys.modules[f"{_pkg}.DS_api"] = _ds_stub

_state_stub = types.ModuleType(f"{_pkg}.state_serializer")
class _StateStub:
    def __init__(self, *a, **kw): pass
    def get_last_event(self, *a, **kw): return 0
_state_stub.State = _StateStub
sys.modules[f"{_pkg}.state_serializer"] = _state_stub

_spec = importlib.util.spec_from_file_location(f"{_pkg}.DS_poller", _DS_POLLER_PATH)
DS_poller = importlib.util.module_from_spec(_spec)
sys.modules[f"{_pkg}.DS_poller"] = DS_poller
_spec.loader.exec_module(DS_poller)

_build_v2_row = DS_poller._build_v2_row


SAMPLE_TRIAGE_INCIDENT = {
    "id": "triage-uuid-1",
    "state": "unread",
    "raised": "2026-06-22T11:00:00Z",
    "updated": "2026-06-22T11:05:00Z",
    "source": {"incident-id": 424242, "alert-id": None},
}

SAMPLE_INCIDENT = {
    "id": 424242,
    "title": "Suspicious credential exposure",
    "raised": "2026-06-22T10:55:00Z",
    "updated": "2026-06-22T11:03:00Z",
    "classification": "exposed-credential",
    "risk-level": "high",
    "risk-assessment": {"risk-level": "high"},
    "gm_link": "https://greymatter.myreliaquest.com/incidents/424242",
    "assets": ["example.com", "1.2.3.4"],
    "description": "Customer credential found on a paste site.",
    "impact_description": "Credential reuse possible.",
    "mitigation": "Force password reset.",
    "risk_factors": ["credential-exposure"],
    "portal_id": "RQ-INC-9988",
}

SAMPLE_TRIAGE_ALERT = {
    "id": "triage-uuid-2",
    "state": "read",
    "raised": "2026-06-22T11:10:00Z",
    "updated": "2026-06-22T11:11:00Z",
    "source": {"incident-id": None, "alert-id": "alert-guid-7777"},
}

SAMPLE_ALERT = {
    "id": "alert-guid-7777",
    "title": "Domain lookalike",
    "raised": "2026-06-22T11:08:00Z",
    "updated": "2026-06-22T11:09:00Z",
    "classification": "impersonating-domain",
    "risk-level": "medium",
    "risk-assessment": {"risk-level": "medium"},
    "gm_link": "https://greymatter.myreliaquest.com/alerts/alert-guid-7777",
    "assets": ["evil.example.com"],
    "description": "Lookalike domain detected.",
    "impact_description": "Phishing risk.",
    "mitigation": "Block at email gateway.",
    "risk_factors": ["impersonation"],
    "portal_id": "RQ-ALT-1234",
}


EXPECTED_COMMON = {
    "TimeGenerated", "App", "Title", "TimeRaised", "TimeUpdated",
    "Classification", "RiskLevel", "RiskAssessmentRiskLevel",
    "GreyMatterLink", "Assets", "Description", "ImpactDescription",
    "Mitigation", "RiskFactors", "Comments", "PortalId",
    "Status", "TriageId", "TriageRaisedTime", "TriageUpdatedTime",
}


class BuildV2RowTests(unittest.TestCase):

    def test_incident_row_populates_incident_id_only(self):
        row = _build_v2_row(
            SAMPLE_INCIDENT, SAMPLE_TRIAGE_INCIDENT,
            app="include", is_incident=True, comments=[],
        )
        self.assertTrue(EXPECTED_COMMON.issubset(row.keys()),
                        f"missing: {EXPECTED_COMMON - set(row.keys())}")
        self.assertIn("IncidentId", row)
        self.assertEqual(row["IncidentId"], 424242.0)
        self.assertNotIn("AlertId", row)
        self.assertEqual(row["Title"], "Suspicious credential exposure")
        self.assertEqual(row["GreyMatterLink"],
                         "https://greymatter.myreliaquest.com/incidents/424242")
        self.assertEqual(row["RiskAssessmentRiskLevel"], "high")
        self.assertEqual(row["App"], "include")
        self.assertEqual(row["Status"], "unread")
        self.assertEqual(row["TriageId"], "triage-uuid-1")
        # Assets is a list — stringified
        self.assertIn("example.com", row["Assets"])

    def test_alert_row_populates_alert_id_only(self):
        row = _build_v2_row(
            SAMPLE_ALERT, SAMPLE_TRIAGE_ALERT,
            app="exclude", is_incident=False, comments=[],
        )
        self.assertTrue(EXPECTED_COMMON.issubset(row.keys()))
        self.assertIn("AlertId", row)
        self.assertEqual(row["AlertId"], "alert-guid-7777")
        self.assertNotIn("IncidentId", row)
        self.assertEqual(row["Title"], "Domain lookalike")
        self.assertEqual(row["App"], "exclude")
        self.assertEqual(row["RiskLevel"], "medium")

    def test_missing_optional_fields_become_empty_string(self):
        minimal = {"id": 1, "title": "minimal"}
        triage = {
            "id": "t-min", "state": "unread", "raised": "", "updated": "",
            "source": {"incident-id": 1, "alert-id": None},
        }
        row = _build_v2_row(minimal, triage,
                            app="include", is_incident=True, comments=[])
        for col in ("Description", "Mitigation", "PortalId",
                    "GreyMatterLink", "Classification", "RiskAssessmentRiskLevel"):
            self.assertEqual(row[col], "",
                             f"{col} should default to '' when source field is missing")
        self.assertEqual(row["IncidentId"], 1.0)

    def test_missing_datetime_fields_become_none_not_empty_string(self):
        # Logs Ingestion rejects '' for datetime columns with HTTP 400.
        minimal = {"id": 1, "title": "minimal"}
        triage = {
            "id": "t-min", "state": "unread", "raised": "", "updated": "",
            "source": {"incident-id": 1, "alert-id": None},
        }
        row = _build_v2_row(minimal, triage,
                            app="include", is_incident=True, comments=[])
        for col in ("TimeRaised", "TimeUpdated",
                    "TriageRaisedTime", "TriageUpdatedTime"):
            self.assertIsNone(row[col],
                              f"{col} must be None (not '') when source value is missing/empty")

    def test_unparseable_incident_id_becomes_null(self):
        weird = {"id": "not-a-number", "title": "weird"}
        triage = {
            "id": "t-w", "state": "unread", "raised": "", "updated": "",
            "source": {"incident-id": "not-a-number", "alert-id": None},
        }
        row = _build_v2_row(weird, triage,
                            app="include", is_incident=True, comments=[])
        self.assertIsNone(row["IncidentId"])

    def test_comments_list_is_json_serialised(self):
        comments = [
            {"user_name": "Alice", "content": "look at this", "id": "c1",
             "created": "2026-06-22T11:00:00Z"},
            {"user_name": None, "content": "hmm", "id": "c2",
             "created": "2026-06-22T11:01:00Z"},
        ]
        row = _build_v2_row(SAMPLE_INCIDENT, SAMPLE_TRIAGE_INCIDENT,
                            app="include", is_incident=True, comments=comments)
        # Comments column is a string (per DCR schema) — should round-trip
        decoded = json.loads(row["Comments"])
        self.assertEqual(len(decoded), 2)
        self.assertEqual(decoded[0]["content"], "look at this")

    def test_top_level_serialisation_is_a_valid_json_array(self):
        """Whatever post_azure assembles must serialise into a JSON array
        (Logs Ingestion API requirement)."""
        row1 = _build_v2_row(SAMPLE_INCIDENT, SAMPLE_TRIAGE_INCIDENT,
                             app="include", is_incident=True, comments=[])
        row2 = _build_v2_row(SAMPLE_ALERT, SAMPLE_TRIAGE_ALERT,
                             app="exclude", is_incident=False, comments=[])
        body = json.dumps([row1, row2])
        decoded = json.loads(body)
        self.assertIsInstance(decoded, list)
        self.assertEqual(len(decoded), 2)


if __name__ == "__main__":
    unittest.main(verbosity=2)
