from __future__ import annotations

import io
import unittest
from pathlib import Path
from unittest.mock import patch

import yaml

from sentinel_xdr_migration.converter import (
    ConversionResult,
    ENTITY_MAP,
    assess_schedule,
    build_xdr_document,
    convert_entities,
    convert_query,
    constrain_event_window,
    validate_document,
)


def entity(kind: str, **fields: str) -> dict:
    return {
        "entityType": kind,
        "fieldMappings": [{"identifier": key, "columnName": value} for key, value in fields.items()],
    }


HOST_QUERY = """DeviceEvents
| project DeviceName
| extend HostName = iff(DeviceName has '.', substring(DeviceName, 0, indexof(DeviceName, '.')), DeviceName)
| extend DnsDomain = iff(DeviceName has '.', substring(DeviceName, indexof(DeviceName, '.') + 1), "")
"""

LOG_DELETION_QUERY = """// Look for use of wevtutil to clear multiple logs
DeviceProcessEvents
| where ProcessCommandLine has "WEVTUTIL" and ProcessCommandLine has "CL"
| summarize LogClearCount = dcount(tostring(ProcessCommandLine)), ClearedLogList = make_set(ProcessCommandLine, 100000) by DeviceId, DeviceName, bin(TimeGenerated, 5m)
| where LogClearCount > 10
| extend HostName = iff(DeviceName has '.', substring(DeviceName, 0, indexof(DeviceName, '.')), DeviceName)
| extend DnsDomain = iff(DeviceName has '.', substring(DeviceName, indexof(DeviceName, '.') + 1), "")
"""


class EntitySemanticsTests(unittest.TestCase):
    def convert(self, mappings: list[dict], query: str, renames: dict | None = None):
        information: list[str] = []
        output, warnings = convert_entities(
            {"entityMappings": mappings}, query, renames, informational=information,
        )
        return output, warnings, information

    def test_added_direct_contracts(self):
        cases = [
            ("DNS", "DomainName", "dns", "domainNameColumn"),
            ("File", "Name", "files", "nameColumn"),
            ("MailCluster", "Query", "mailClusters", "queryColumn"),
            ("MailCluster", "Source", "mailClusters", "sourceColumn"),
            ("RegistryValue", "Name", "registryValues", "valueNameColumn"),
            ("SecurityGroup", "DistinguishedName", "securityGroups", "distinguishedNameColumn"),
            ("SecurityGroup", "SID", "securityGroups", "sidColumn"),
            ("SecurityGroup", "ObjectGuid", "securityGroups", "objectIdColumn"),
        ]
        for kind, identifier, collection, field in cases:
            with self.subTest(kind=kind, identifier=identifier):
                output, warnings, information = self.convert(
                    [entity(kind, **{identifier: "Evidence"})],
                    "DeviceEvents | project Evidence",
                )
                self.assertEqual(output[collection][0][field], "Evidence")
                self.assertEqual(warnings, [])
                self.assertEqual(information, [])

    def test_all_direct_targets_follow_verified_graph_contracts(self):
        contracts = {
            "hosts": {"deviceIdColumn", "dnsDomainColumn", "nameColumn", "netBiosNameColumn", "ntDomainColumn"},
            "accounts": {"aadUserIdColumn", "dnsDomainColumn", "nameColumn", "ntDomainColumn", "sidColumn", "upnColumn", "upnSuffixColumn"},
            "ips": {"addressColumn"}, "urls": {"addressColumn"},
            "azureResources": {"resourceIdColumn"},
            "cloudApplications": {"appIdColumn", "nameColumn"},
            "mailboxes": {"primaryAddressColumn"},
            "mailMessages": {"networkMessageIdColumn", "recipientColumn", "senderColumn", "subjectColumn"},
            "dns": {"domainNameColumn", "hostIpAddressColumn", "serverIpColumn"},
            "files": {"nameColumn", "sha1Column", "sha256Column"},
            "processes": {"sha1Column", "sha256Column"},
            "mailClusters": {"queryColumn", "sourceColumn"},
            "registryValues": {"keyColumn", "valueNameColumn"},
            "securityGroups": {"distinguishedNameColumn", "objectIdColumn", "sidColumn"},
        }
        for collection, fields in ENTITY_MAP.values():
            self.assertLessEqual(set(fields.values()), contracts[collection])

    def test_internal_references_and_unrepresentable_fields_warn(self):
        for kind, identifier in [
            ("DNS", "DnsServerIp"), ("DNS", "HostIpAddress"),
            ("File", "Directory"), ("File", "FileHashes"),
            ("RegistryValue", "Key"), ("RegistryValue", "Value"),
            ("Process", "ProcessId"), ("Process", "ImageFile"), ("Process", "CommandLine"),
            ("Host", "AzureID"), ("SecurityGroup", "Name"),
        ]:
            with self.subTest(kind=kind, identifier=identifier):
                output, warnings, info = self.convert(
                    [entity(kind, **{identifier: "Evidence"})], "DeviceEvents | project Evidence",
                )
                self.assertFalse(output)
                self.assertTrue(any(f"converter cannot map {kind}.{identifier}" in value for value in warnings))
                self.assertEqual(info, [])

    def test_missing_final_columns_and_configured_column_mapping(self):
        for query in ("DeviceEvents | project Other", "DeviceEvents | extend Evidence=Other | project Other"):
            output, warnings, _ = self.convert([entity("File", Name="Evidence")], query)
            self.assertFalse(output)
            self.assertIn("not produced by the query", warnings[0])
        output, warnings, _ = self.convert(
            [entity("File", Name="Original")], "DeviceEvents | project Renamed", {"Original": "Renamed"},
        )
        self.assertEqual("Renamed", output["files"][0]["nameColumn"])
        self.assertFalse(warnings)

    def test_hash_algorithm_is_proven_from_query_not_column_spelling(self):
        for algorithm, target in [("SHA1", "sha1Column"), ("SHA256", "sha256Column")]:
            output, warnings, info = self.convert(
                [entity("FileHash", Algorithm="Algorithm", Value="Hash")],
                f'DeviceEvents | extend Algorithm="{algorithm}" | project Algorithm, Hash',
            )
            self.assertEqual("Hash", output["files"][0][target])
            self.assertFalse(warnings)
            self.assertEqual(1, len(info))
        for query in [
            'DeviceEvents | extend Algorithm="MD5" | project Algorithm, Hash',
            "DeviceEvents | project Algorithm, Hash",
            'DeviceEvents | extend Algorithm=iff(Flag, "SHA1", "SHA256") | project Algorithm, Hash',
            'DeviceEvents | extend Algorithm="SHA1" | extend Algorithm=Other | project Algorithm, Hash',
            'DeviceEvents | extend Algorithm="SHA1" | project Algorithm',
            'DeviceEvents | project Algorithm, Hash // Algorithm="SHA1"',
            'DeviceEvents | extend Algorithm="SHA1" | union OtherTable',
            'DeviceEvents | extend Algorithm="SHA1"',
        ]:
            with self.subTest(query=query):
                output, warnings, info = self.convert(
                    [entity("FileHash", Algorithm="Algorithm", Value="Hash")], query,
                )
                self.assertFalse(output)
                self.assertTrue(any("converter cannot map FileHash.Algorithm/Value" in warning for warning in warnings))
                self.assertFalse(info)

    def test_deimos_fullname_decomposition_is_informational(self):
        output, warnings, info = self.convert(
            [entity("Host", FullName="DeviceName", HostName="HostName", DnsDomain="DnsDomain")],
            HOST_QUERY,
        )
        self.assertEqual("HostName", output["hosts"][0]["nameColumn"])
        self.assertNotIn("fullNameColumn", output["hosts"][0])
        self.assertFalse(warnings)
        self.assertIn("safely represented", info[0])

    def test_fullname_loss_or_conflicts_remain_warnings(self):
        for query in [
            "DeviceEvents | project DeviceName, HostName, DnsDomain",
            HOST_QUERY.replace("indexof(DeviceName, '.') + 1", "indexof(DeviceName, '.') + 2"),
            HOST_QUERY + "| extend HostName=Other",
            HOST_QUERY + "| extend DeviceName=Other",
            HOST_QUERY + "| project DeviceName, DnsDomain",
            HOST_QUERY + "| union OtherTable",
            "DeviceEvents | project DeviceName, HostName, DnsDomain // " + HOST_QUERY.replace("\n", " "),
        ]:
            with self.subTest(query=query):
                _, warnings, info = self.convert(
                    [entity("Host", FullName="DeviceName", HostName="HostName", DnsDomain="DnsDomain")], query,
                )
                self.assertTrue(any(
                    "Best-effort entity mapping requires review:" in value
                    or "converter cannot map Host.FullName" in value
                    for value in warnings
                ))
                self.assertFalse(info)

    def test_fullname_decomposition_after_preserving_aggregation(self):
        for query in (
            LOG_DELETION_QUERY,
            LOG_DELETION_QUERY.replace("TimeGenerated", "Timestamp"),
            HOST_QUERY + "| summarize Count=count() by DeviceName, HostName, DnsDomain",
        ):
            with self.subTest(query=query):
                output, warnings, info = self.convert(
                    [entity("Host", FullName="DeviceName", HostName="HostName", DnsDomain="DnsDomain")], query,
                )
                self.assertEqual("HostName", output["hosts"][0]["nameColumn"])
                self.assertEqual("DnsDomain", output["hosts"][0]["dnsDomainColumn"])
                self.assertFalse(warnings)
                self.assertIn("safely represented", info[0])

    def test_destructive_aggregation_overwrites_and_joins_do_not_prove_fullname(self):
        for query in (
            LOG_DELETION_QUERY.replace("by DeviceId, DeviceName,", "by DeviceId,"),
            LOG_DELETION_QUERY.replace("by DeviceId, DeviceName,", "by DeviceId, DeviceName=tostring(Other),"),
            LOG_DELETION_QUERY.replace("by DeviceId, DeviceName,", "by DeviceId, tolower(DeviceName),"),
            LOG_DELETION_QUERY + "| extend DeviceName=Other",
            LOG_DELETION_QUERY + "| extend HostName=Other",
            LOG_DELETION_QUERY + "| join kind=inner (DeviceInfo) on DeviceName",
            HOST_QUERY + "| summarize Count=count() by DeviceName",
            HOST_QUERY + "| summarize HostName=take_any(HostName) by DeviceName, DnsDomain",
            HOST_QUERY + "| summarize Count=count() by HostName, DnsDomain | project DeviceName, HostName, DnsDomain",
            HOST_QUERY.replace("| project DeviceName", "| project Other | project DeviceName"),
        ):
            with self.subTest(query=query):
                _, warnings, info = self.convert(
                    [entity("Host", FullName="DeviceName", HostName="HostName", DnsDomain="DnsDomain")], query,
                )
                self.assertTrue(any(
                    "Best-effort entity mapping requires review:" in value
                    or "converter cannot map Host.FullName" in value
                    for value in warnings
                ))
                self.assertFalse(info)

    def test_multiple_source_identifiers_do_not_silently_overwrite(self):
        output, warnings, _ = self.convert(
            [entity("MailMessage", Sender="Envelope", P2Sender="Header")],
            "EmailEvents | project Envelope, Header",
        )
        self.assertEqual("Envelope", output["mailMessages"][0]["senderColumn"])
        self.assertTrue(any("conflicting senderColumn" in value for value in warnings))

    def test_legacy_two_value_unpacking_is_preserved(self):
        output, warnings = convert_entities(
            {"entityMappings": [entity("IP", Address="IPAddress")]}, "DeviceEvents",
        )
        self.assertEqual("IPAddress", output["ips"][0]["addressColumn"])
        self.assertFalse(warnings)


class ScheduleSemanticsTests(unittest.TestCase):
    def assess(self, period="4h", frequency="1h", target="PT1H", query=None, source=None):
        query = query or f"DeviceEvents | where Timestamp > ago({period}) | project DeviceName"
        return assess_schedule(
            {"queryFrequency": frequency, "queryPeriod": period, "kind": "Scheduled"},
            source or query, query, target,
        )

    def test_documented_native_lookbacks_with_explicit_matching_event_bounds(self):
        for frequency, period, target in [("1h", "4h", "PT1H"), ("3h", "12h", "PT3H"),
                                          ("12h", "48h", "PT12H"), ("24h", "30d", "P1D")]:
            with self.subTest(frequency=frequency):
                warnings, info = self.assess(period, frequency, target)
                self.assertFalse(warnings)
                self.assertIn("frequency and explicit event-time window are preserved", info[0])
                self.assertIn("source frequency=", info[0])
                self.assertIn("https://learn.microsoft.com", info[0])

    def test_literal_duration_or_comment_is_not_equivalence(self):
        for query in [
            "DeviceEvents // 4h",
            'DeviceEvents | where ActionType == "4h"',
            "DeviceEvents | where Timestamp > ago(1h) // queryPeriod 4h",
        ]:
            # Equal configured lookbacks may safely share the same explicit narrower bound.
            warnings, info = self.assess(query=query)
            if "Timestamp >" in query:
                self.assertFalse(warnings)
                self.assertIn("source=3600s, target=3600s", info[0])
            else:
                self.assertTrue(warnings)
                self.assertFalse(info)
        warnings, info = self.assess("1h", query="DeviceEvents")
        self.assertIn("source and native service windows differ", warnings[0])
        self.assertFalse(info)

    def test_frequency_unknown_surface_and_time_basis_remain_warnings(self):
        cases = [
            {"frequency": "3h"}, {"frequency": "nonsense"}, {"period": "unknown"},
            {"query": "SecurityEvent | where TimeGenerated > ago(4h)"},
            {"query": "UnknownTable | where Timestamp > ago(4h)"},
            {"query": "union DeviceEvents, SecurityEvent | where Timestamp > ago(4h)"},
            {"query": "DeviceEvents | join kind=inner (SecurityEvent) on DeviceName"},
            {"query": "DeviceEvents | where ingestion_time() > ago(4h)"},
            {"query": "DeviceEvents | where Timestamp > ago(4h) or Flag"},
            {"query": "DeviceEvents | where Timestamp > ago(Window)"},
            {"query": "DeviceEvents | extend Timestamp=Other | where Timestamp > ago(4h)"},
            {"query": "DeviceEvents | where Timestamp > ago(2h)",
             "source": "DeviceEvents | where Timestamp > ago(4h)"},
            {"frequency": "2h", "target": "PT2H"},
            {"source": "DeviceProcessEvents | where Timestamp > ago(4h)"},
        ]
        for case in cases:
            with self.subTest(case=case):
                warnings, info = self.assess(**case)
                self.assertTrue(warnings)
                self.assertFalse(info)

    def test_nrt_is_not_silently_equated_with_hourly(self):
        warnings, info = assess_schedule(
            {"kind": "NRT", "queryPeriod": "4h"}, "DeviceEvents", "DeviceEvents", "PT1H",
        )
        self.assertIn("NRT timing is not preserved", warnings[0])
        self.assertFalse(info)

    def test_native_surface_after_aggregation_reports_concrete_daily_mismatch(self):
        warnings, info = self.assess(
            period="1d", frequency="1d", target="P1D",
            source=LOG_DELETION_QUERY, query=LOG_DELETION_QUERY.replace("TimeGenerated", "Timestamp"),
        )
        self.assertFalse(info)
        self.assertIn("source frequency=1d, lookback=1d", warnings[0])
        self.assertIn("target frequency=P1D, native lookback=2592000s", warnings[0])
        self.assertIn("source and native service windows differ", warnings[0])
        self.assertNotIn("unknown query surface", warnings[0])

    def test_native_surface_is_not_a_proof_of_aggregate_time_equivalence(self):
        warnings, info = self.assess(
            period="30d", frequency="1d", target="P1D",
            query=LOG_DELETION_QUERY.replace("TimeGenerated", "Timestamp"),
        )
        self.assertFalse(info)
        self.assertIn("native lookback=2592000s", warnings[0])
        self.assertIn("no explicit event-time bound proves equivalence", warnings[0])
        for suffix in (
            "| join kind=inner (SecurityEvent) on DeviceName",
            "| union SecurityEvent",
            "| invoke UnknownFunction()",
        ):
            warnings, info = self.assess(query=LOG_DELETION_QUERY + suffix)
            self.assertFalse(info)
            self.assertIn("unknown query surface", warnings[0])

    def test_time_column_rename_can_preserve_window_without_rewriting(self):
        warnings, info = self.assess(
            source="DeviceEvents | where TimeGenerated > ago(4h)",
            query="DeviceEvents | where Timestamp > ago(4h)",
        )
        self.assertFalse(warnings)
        self.assertTrue(info)

    def test_narrower_source_window_is_injected_before_aggregation(self):
        for period, expected in (("30m", 1800), ("2h", 7200), ("3h", 10800)):
            query = "DeviceEvents | summarize Count=count() by DeviceId, Timestamp"
            converted, evidence, review = constrain_event_window(
                {"queryPeriod": period, "queryFrequency": "1h"},
                query, query, "PT1H",
            )
            with self.subTest(period=period):
                self.assertIsNone(review)
                self.assertIn(f"where Timestamp >= ago({period})", converted)
                self.assertLess(converted.index("where Timestamp"), converted.index("summarize"))
                self.assertEqual(evidence["effectiveEventWindowSeconds"], expected)
                self.assertEqual(evidence["xdrServiceWindowSeconds"], 14400)
                self.assertTrue(evidence["filterInjected"])
                self.assertIn("Late-ingestion risk", evidence["lateIngestionRisk"])

    def test_timegenerated_binding_is_lexical_and_targets_timestamp(self):
        query = (
            'DeviceEvents | summarize Values=make_set("TimeGenerated") '
            "by bin(TimeGenerated, 5m) // TimeGenerated is only a source comment\n"
        )
        converted, evidence, review = constrain_event_window(
            {"queryPeriod": "2h", "queryFrequency": "1h"},
            query, query, "PT1H",
        )
        self.assertIsNone(review)
        self.assertIn("where Timestamp >= ago(2h)", converted)
        self.assertIn("bin(Timestamp, 5m)", converted)
        self.assertIn('"TimeGenerated"', converted)
        self.assertIn("// TimeGenerated is only a source comment", converted)
        self.assertEqual("TimeGenerated", evidence["sourceTimeColumn"])
        self.assertEqual("Timestamp", evidence["targetTimeColumn"])

    def test_unsafe_native_query_shapes_require_review_without_rewrite(self):
        for query in (
            "DeviceEvents | join kind=inner (DeviceInfo) on DeviceId",
            "union DeviceEvents, DeviceInfo | where Timestamp > ago(2h)",
            "let baseline = DeviceEvents | summarize count(); DeviceEvents | where Timestamp > ago(2h)",
        ):
            with self.subTest(query=query):
                converted, evidence, review = constrain_event_window(
                    {"queryPeriod": "2h", "queryFrequency": "1h"},
                    query, query, "PT1H",
                )
                self.assertEqual(query, converted)
                self.assertIsNone(evidence)
                self.assertIn("cannot be proven equivalent", review)


class InformationContractTests(unittest.TestCase):
    def document(self, **updates):
        rule = {
            "id": "11111111-2222-3333-4444-555555555555",
            "name": "Example", "query": HOST_QUERY, "queryFrequency": "1h", "queryPeriod": "4h",
            "entityMappings": [entity("Host", FullName="DeviceName", HostName="HostName", DnsDomain="DnsDomain")],
        }
        rule.update(updates)
        original_open = Path.open
        source = Path("Example/Analytic Rules/Test.yaml")

        def open_input(path, *args, **kwargs):
            return io.StringIO(yaml.safe_dump(rule)) if path == source else original_open(path, *args, **kwargs)

        with patch.object(Path, "open", autospec=True, side_effect=open_input):
            with patch("sentinel_xdr_migration.converter.normalize_parser_bindings", side_effect=lambda query, _: (query, [])):
                return build_xdr_document(source, Path("Example"), {})

    def test_information_nonblocking_and_schema_optional(self):
        document = self.document()
        conversion = document["contentProvenance"]["conversion"]
        self.assertTrue(conversion["informational"])
        self.assertFalse(conversion["errors"])
        self.assertFalse(conversion["reviewRequired"])
        self.assertEqual("converted", conversion["status"])
        self.assertEqual([], validate_document(document))
        conversion["informational"] = "not a list"
        self.assertTrue(any("schema:" in error for error in validate_document(document)))
        conversion["informational"] = [12]
        self.assertTrue(any("schema:" in error for error in validate_document(document)))
        conversion.pop("informational")
        self.assertFalse(validate_document(document))

    def test_information_does_not_override_tactic_or_required_asset_gates(self):
        document = self.document(tactics=["Execution", "Collection"])
        self.assertEqual("converted", document["contentProvenance"]["conversion"]["status"])
        document = self.document(tactics=["Execution", "InvalidTactic"])
        conversion = document["contentProvenance"]["conversion"]
        self.assertEqual("needsReview", conversion["status"])
        self.assertTrue(conversion["reviewRequired"])
        self.assertTrue(conversion["informational"])
        document = self.document(
            query='DeviceEvents | extend Algorithm="SHA1" | project Algorithm, Hash',
            entityMappings=[entity("FileHash", Algorithm="Algorithm", Value="Hash")],
        )
        conversion = document["contentProvenance"]["conversion"]
        self.assertTrue(conversion["informational"])
        self.assertIn("a Host, Account, Mailbox, or IP mapping is required", conversion["errors"])

    def test_narrowed_event_window_is_recorded_without_parity_claim(self):
        query = "DeviceEvents | summarize Count=count() by DeviceId, Timestamp"
        document = self.document(
            query=query,
            queryFrequency="1h",
            queryPeriod="2h",
        )
        conversion = document["contentProvenance"]["conversion"]
        target_query = document["properties"]["queryCondition"]["queryText"]
        self.assertIn("DeviceEvents | where Timestamp >= ago(2h) | summarize", target_query)
        self.assertEqual(conversion["status"], "converted")
        self.assertTrue(conversion["reviewRequired"])
        self.assertTrue(any(
            "Best-effort entity mapping requires review:" in reason
            for reason in conversion["reviewReasons"]
        ))
        window = conversion["eventTimeWindow"]
        self.assertEqual(window["originalSentinelLookbackSeconds"], 7200)
        self.assertEqual(window["effectiveEventWindowSeconds"], 7200)
        self.assertEqual(window["xdrServiceWindowSeconds"], 14400)
        self.assertTrue(window["filterInjected"])
        self.assertTrue(any(
            "event-time window constrained to original Sentinel lookback" in message
            for message in conversion["informational"]
        ))
        self.assertTrue(any("late-ingestion risk" in message for message in conversion["warnings"]))
        self.assertTrue(any(
            "parity is not established" in message.lower()
            for message in conversion["informational"]
        ))

    def test_hourly_1h_1h_rule_defaults_to_native_4h_lookback_without_review(self):
        query = "DeviceEvents | summarize Count=count() by DeviceName, HostName, DnsDomain"
        document = self.document(
            query=query,
            queryFrequency="1h",
            queryPeriod="1h",
            entityMappings=[entity("Host", HostName="HostName")],
        )
        conversion = document["contentProvenance"]["conversion"]
        target_query = document["properties"]["queryCondition"]["queryText"]
        self.assertEqual(target_query, query)
        self.assertEqual(conversion["status"], "converted")
        self.assertFalse(conversion["reviewRequired"])
        self.assertEqual(conversion["reviewReasons"], [])
        window = conversion["eventTimeWindow"]
        self.assertEqual(window["status"], "default-native-lookback")
        self.assertEqual(window["originalSentinelLookbackSeconds"], 3600)
        self.assertEqual(window["effectiveEventWindowSeconds"], 14400)
        self.assertEqual(window["xdrServiceWindowSeconds"], 14400)
        self.assertEqual(window["targetFrequency"], "PT1H")
        self.assertEqual(window["effectiveLookback"], "PT4H")
        self.assertFalse(window["filterInjected"])
        self.assertTrue(window["hasAggregation"])
        self.assertFalse(window["parityClaimed"])
        self.assertEqual(len(window["sourceDocumentSha256"]), 64)
        self.assertEqual(len(window["targetQuerySha256"]), 64)
        self.assertEqual([], validate_document(document))

    def test_unsafe_event_window_shape_remains_needs_review(self):
        query = "DeviceEvents | join kind=inner (DeviceInfo) on DeviceId"
        document = self.document(query=query, queryFrequency="1h", queryPeriod="2h")
        conversion = document["contentProvenance"]["conversion"]
        self.assertEqual("needsReview", conversion["status"])
        self.assertTrue(conversion["reviewRequired"])
        self.assertIn(query, document["properties"]["queryCondition"]["queryText"])
        self.assertTrue(any("source and target table inputs cannot be proven equivalent" in reason
                            for reason in conversion["reviewReasons"]))

    def test_configured_column_and_table_mappings_do_not_cross_join_scopes(self):
        query = (
            "DeviceEvents as d | join kind=inner (SecurityEvent as s) on d.DeviceId == s.DeviceId "
            "| where d.TimeGenerated > ago(2h) | project d.TimeGenerated, s.AccountUPN"
        )
        converted, warnings, errors = convert_query(query, {
            "tableMappings": {"DeviceEvents": "AlertEvidence"},
            "columnMappings": {
                "DeviceEvents": {"TimeGenerated": "Timestamp"},
                "SecurityEvent": {"AccountUPN": "AccountUpn"},
            },
        })
        self.assertEqual(query, converted)
        self.assertFalse(errors)
        self.assertTrue(any("table/alias scope is ambiguous" in warning for warning in warnings))

    def test_table_mapping_rewrites_only_the_table_token(self):
        query = (
            'CiscoASA_CL | extend Label = "CiscoASA_CL" '
            "// CiscoASA_CL is source documentation\n"
            "| where TimeGenerated > ago(1h)"
        )
        converted, warnings, errors = convert_query(
            query, {"tableMappings": {"CiscoASA_CL": "DeviceNetworkEvents"}}
        )
        self.assertTrue(converted.startswith("DeviceNetworkEvents"))
        self.assertIn('"CiscoASA_CL"', converted)
        self.assertIn("// CiscoASA_CL is source documentation", converted)
        self.assertIn("Timestamp > ago(1h)", converted)
        self.assertFalse(warnings)
        self.assertFalse(errors)

    def test_result_serializes_information_without_breaking_positional_callers(self):
        result = ConversionResult(Path("source"), Path("target"), "Example", "converted", False, (), (), ())
        self.assertEqual([], result.as_dict()["informational"])
        result = ConversionResult(Path("source"), Path("target"), "Example", "converted", False, (), (), (), ("Preserved",))
        self.assertEqual(["Preserved"], result.as_dict()["informational"])
        self.assertFalse(result.as_dict()["reviewRequired"])


if __name__ == "__main__":
    unittest.main()
