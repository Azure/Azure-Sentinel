from __future__ import annotations

import hashlib
import json
import unittest

from sentinel_xdr_migration.converter import convert_query, convert_query_with_mapping_evidence
from sentinel_xdr_migration.mapping_evidence import (
    MappingEvidenceError,
    build_mapping_evidence,
    validate_mapping_evidence_freshness,
)


def evidence(kind: str, path: str, content: str) -> dict[str, str]:
    return {
        "kind": kind,
        "path": path,
        "content": content,
        "sha256": hashlib.sha256(content.encode("utf-8")).hexdigest(),
    }


class MappingEvidenceTests(unittest.TestCase):
    def test_directional_rename_cast_derived_drop_and_filter_evidence(self) -> None:
        source_query = (
            'CiscoASA_CL | where raw_port_d > 1024 and zone_s == "inside" '
            "| project SourceIP_s, raw_port_d, zone_s, retired_s"
        )
        config = {
            "tableMappings": {"CiscoASA_CL": "DeviceNetworkEvents"},
            "columnMappings": {
                "CiscoASA_CL": {
                    "SourceIP_s": "RemoteIP",
                    "raw_port_d": "LocalPort",
                    "zone_s": "NetworkProtocol",
                }
            },
        }
        source_metadata = {
            "CiscoASA_CL": {
                "columns": {
                    "SourceIP_s": "string",
                    "raw_port_d": "real",
                    "zone_s": "string",
                    "retired_s": "string",
                },
                "targetTable": "DeviceNetworkEvents",
                "columnMappings": {
                    "SourceIP_s": {"target": "RemoteIP"},
                    "raw_port_d": {"target": "LocalPort", "transform": "tolong(raw_port_d)"},
                    "zone_s": {"target": "NetworkProtocol", "expression": 'strcat("asa:", zone_s)'},
                },
                "droppedColumns": ["retired_s"],
                "evidence": evidence(
                    "table-schema",
                    "schemas/ciscoasa-source.json",
                    json.dumps({
                        "table": "CiscoASA_CL",
                        "columns": {
                            "SourceIP_s": "string",
                            "raw_port_d": "real",
                            "zone_s": "string",
                            "retired_s": "string",
                        },
                    }, sort_keys=True),
                ),
            }
        }
        target_metadata = {
            "DeviceNetworkEvents": {
                "columns": {
                    "RemoteIP": "string",
                    "LocalPort": "long",
                    "NetworkProtocol": "string",
                },
                "evidence": evidence(
                    "table-schema",
                    "schemas/device-network-events.json",
                    json.dumps({
                        "table": "DeviceNetworkEvents",
                        "columns": {
                            "RemoteIP": "string",
                            "LocalPort": "long",
                            "NetworkProtocol": "string",
                        },
                    }, sort_keys=True),
                ),
            }
        }

        target_query, warnings, errors, record = convert_query_with_mapping_evidence(
            source_query,
            config,
            source_metadata=source_metadata,
            target_metadata=target_metadata,
        )
        self.assertFalse(errors)
        self.assertFalse(warnings)
        self.assertIn("DeviceNetworkEvents", target_query)
        self.assertIn("RemoteIP, LocalPort, NetworkProtocol, retired_s", target_query)
        self.assertIn('> 1024 and NetworkProtocol == "inside"', target_query)
        self.assertEqual(source_query, record["sourceQuery"])
        self.assertEqual(target_query, record["targetQuery"])
        self.assertEqual("sentinel-to-xdr", record["direction"])
        self.assertEqual("schema-verified", record["overallStatus"])

        by_source = {item["sourceColumn"]: item for item in record["mappings"]}
        self.assertEqual(("rename", "RemoteIP"), (by_source["SourceIP_s"]["kind"], by_source["SourceIP_s"]["targetColumn"]))
        self.assertEqual(("cast", "long"), (by_source["raw_port_d"]["kind"], by_source["raw_port_d"]["targetType"]))
        self.assertEqual("derived", by_source["zone_s"]["kind"])
        self.assertFalse(by_source["raw_port_d"]["appliedToTargetQuery"])
        self.assertEqual(("dropped", None), (by_source["retired_s"]["kind"], by_source["retired_s"]["targetColumn"]))
        self.assertTrue(all(item["status"] == "schema-verified" for item in record["mappings"]))
        self.assertEqual("rewritten-by-converter", record["filters"][0]["rewriteStatus"])
        self.assertIn('"inside"', record["filters"][0]["targetPredicate"])

        self.assertEqual([], validate_mapping_evidence_freshness(
            record, source_query, target_query,
            source_metadata=source_metadata, target_metadata=target_metadata, config=config,
        ))
        self.assertIn(
            "sourceQuerySha256 is stale",
            validate_mapping_evidence_freshness(
                record, source_query + " | take 1", target_query,
                source_metadata=source_metadata, target_metadata=target_metadata, config=config,
            ),
        )

    def test_forward_dcr_transform_is_never_inverted(self) -> None:
        query = "CiscoASA_CL | where Action_s == 'deny' | project SourceIP_s"
        descriptor = {
            "columns": {"SourceIP_s": "string", "Action_s": "string"},
            "targetTable": "CiscoASA_CL",
            "transformKql": "source | project SourceIP_s = tostring(src_ip), Action_s = action",
            "evidence": evidence("dcr", "connector/dcr.json", '{"transform":"forward-only"}'),
        }
        record = build_mapping_evidence(query, source_metadata={"CiscoASA_CL": descriptor})
        self.assertEqual(query, record["targetQuery"])
        self.assertTrue(any(
            item["code"] == "forward-dcr-transform-not-inverted" for item in record["issues"]
        ))
        self.assertTrue(all(item["sourceColumn"] != "src_ip" for item in record["mappings"]))
        self.assertIn("Action_s == 'deny'", record["filters"][0]["predicate"])

    def test_join_aliases_are_scoped_and_unqualified_fields_are_not_guessed(self) -> None:
        query = (
            "DeviceEvents as d | join kind=inner (SecurityEvent as s) on d.DeviceId == s.DeviceId "
            "| project d.TimeGenerated, s.AccountUPN, LooseColumn"
        )
        config = {"columnMappings": {"DeviceEvents": {"AccountUPN": "MappedUpn"}}}
        source_metadata = {
            "DeviceEvents": {
                "columns": {"TimeGenerated": "datetime", "AccountUPN": "string"},
                "columnMappings": {"TimeGenerated": "Timestamp"},
                "targetTable": "DeviceEvents",
            },
            "SecurityEvent": {
                "columns": {"AccountUPN": "string"},
                "columnMappings": {"AccountUPN": "AccountUpn"},
                "targetTable": "SecurityEvent",
            },
        }
        target_query, warnings, _, record = convert_query_with_mapping_evidence(
            query, config, source_metadata=source_metadata
        )
        self.assertEqual(query, target_query)
        self.assertTrue(any("ambiguous" in warning for warning in warnings))
        mappings = {(item["sourceTable"], item["sourceAlias"], item["sourceColumn"]) for item in record["mappings"]}
        self.assertEqual(
            {("DeviceEvents", "d", "TimeGenerated"), ("SecurityEvent", "s", "AccountUPN")},
            mappings,
        )
        self.assertNotIn("LooseColumn", {item["sourceColumn"] for item in record["mappings"]})
        self.assertTrue(all(item["appliedToTargetQuery"] is False for item in record["mappings"]))

    def test_duplicate_alias_and_union_bindings_remain_unresolved(self) -> None:
        metadata = {
            "DeviceEvents": {
                "columns": {"TimeGenerated": "datetime"},
                "columnMappings": {"TimeGenerated": "Timestamp"},
                "targetTable": "DeviceEvents",
            },
            "SecurityEvent": {
                "columns": {"TimeGenerated": "datetime"},
                "columnMappings": {"TimeGenerated": "Timestamp"},
                "targetTable": "SecurityEvent",
            },
        }
        duplicate_alias = (
            "DeviceEvents as d | join kind=inner (SecurityEvent as d) on d.DeviceId "
            "| project d.TimeGenerated"
        )
        duplicate_record = build_mapping_evidence(duplicate_alias, source_metadata=metadata)
        self.assertFalse(duplicate_record["mappings"])
        self.assertTrue(any(
            issue["code"] == "alias-binding-ambiguous" for issue in duplicate_record["issues"]
        ))

        union_query = "union DeviceEvents, SecurityEvent | where TimeGenerated > ago(2h)"
        target_query, warnings, errors = convert_query(
            union_query,
            {"columnMappings": {"DeviceEvents": {"TimeGenerated": "Timestamp"}}},
        )
        self.assertEqual(union_query, target_query)
        self.assertTrue(warnings)
        self.assertFalse(errors)
        union_record = build_mapping_evidence(union_query, source_metadata=metadata)
        self.assertFalse(union_record["mappings"])
        self.assertTrue(any(
            issue["code"] == "unqualified-field-unresolved" for issue in union_record["issues"]
        ))

    def test_schema_evidence_hash_mismatch_is_rejected(self) -> None:
        with self.assertRaisesRegex(MappingEvidenceError, "stale"):
            build_mapping_evidence(
                "CiscoASA_CL | project SourceIP_s",
                source_metadata={
                    "CiscoASA_CL": {
                        "columns": {"SourceIP_s": "string"},
                        "evidence": {
                            "kind": "table-schema",
                            "path": "schema.json",
                            "content": '{"columns":["SourceIP_s"]}',
                            "sha256": "0" * 64,
                        },
                    }
                },
            )
        content = json.dumps({
            "table": "CiscoASA_CL",
            "columns": {"SourceIP_s": "string", "Extra_s": "string"},
        }, sort_keys=True)
        with self.assertRaisesRegex(MappingEvidenceError, "does not match"):
            build_mapping_evidence(
                "CiscoASA_CL | project SourceIP_s",
                source_metadata={
                    "CiscoASA_CL": {
                        "columns": {"SourceIP_s": "string"},
                        "evidence": evidence("table-schema", "schema.json", content),
                    }
                },
            )

    def test_runtime_validation_requires_current_source_and_target_reports(self) -> None:
        query = "DeviceEvents | where TimeGenerated > ago(1h) | project DeviceId"
        target = "DeviceEvents | where Timestamp > ago(1h) | project DeviceId"
        source_hash = hashlib.sha256(query.encode()).hexdigest()
        target_hash = hashlib.sha256(target.encode()).hexdigest()

        def report(provider: str, surface: str, query_hash: str) -> dict[str, str]:
            content = json.dumps({
                "provider": provider,
                "querySurface": surface,
                "results": [{"querySha256": query_hash, "status": "passed"}],
            }, sort_keys=True)
            return {"path": f"evidence/{provider}.json", "content": content}

        runtime = {
            "sourceReport": report("log-analytics-cli", "log-analytics-workspace", source_hash),
            "targetReport": report("graph", "defender-advanced-hunting", target_hash),
        }
        record = build_mapping_evidence(
            query, target, source_metadata={
                "DeviceEvents": {
                    "columns": {"TimeGenerated": "datetime"},
                    "targetTable": "DeviceEvents",
                }
            }, runtime_evidence=runtime,
        )
        self.assertEqual("runtime-validated", record["mappings"][0]["status"])
        self.assertEqual(2, sum(
            reference["kind"] == "runtimeVerification"
            for reference in record["mappings"][0]["evidenceReferences"]
        ))

        runtime["targetReport"] = report("graph", "defender-advanced-hunting", "0" * 64)
        stale = build_mapping_evidence(
            query, target, source_metadata={
                "DeviceEvents": {
                    "columns": {"TimeGenerated": "datetime"},
                    "targetTable": "DeviceEvents",
                }
            }, runtime_evidence=runtime,
        )
        self.assertNotEqual("runtime-validated", stale["mappings"][0]["status"])
        self.assertTrue(any(
            issue["code"] == "runtime-evidence-not-current" for issue in stale["issues"]
        ))


if __name__ == "__main__":
    unittest.main()
