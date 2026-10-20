import csv
import importlib.util
import json
import sys
import tempfile
import unittest
import unittest.mock
from pathlib import Path


MODULE_PATH = Path(__file__).resolve().parents[1] / "asim_fixture_preparation.py"
SPEC = importlib.util.spec_from_file_location(
    "asim_fixture_preparation", MODULE_PATH
)
FIXTURES = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = FIXTURES
SPEC.loader.exec_module(FIXTURES)


class TimestampTests(unittest.TestCase):
    def test_round_trips_exact_kusto_tick(self):
        value = "2026-10-16T12:34:56.1234567Z"
        self.assertEqual(
            value,
            FIXTURES.ticks_to_kusto_datetime(
                FIXTURES.parse_kusto_datetime_ticks(value)
            ),
        )

    def test_normalizes_iso_offset_to_utc(self):
        self.assertEqual(
            "2026-10-16T10:34:56.1234567Z",
            FIXTURES.ticks_to_kusto_datetime(
                FIXTURES.parse_kusto_datetime_ticks(
                    "2026-10-16T12:34:56.1234567+02:00"
                )
            ),
        )

    def test_accepts_existing_iso_variants(self):
        cases = {
            "2026-10-16": "2026-10-16T00:00:00.0000000Z",
            "2026-10-16T12:34": "2026-10-16T12:34:00.0000000Z",
            "2026-10-16T12:34:56+0200":
                "2026-10-16T10:34:56.0000000Z",
            "2026-W42-5": "2026-10-16T00:00:00.0000000Z",
        }
        for source, expected in cases.items():
            with self.subTest(source=source):
                self.assertEqual(
                    expected,
                    FIXTURES.ticks_to_kusto_datetime(
                        FIXTURES.parse_kusto_datetime_ticks(source)
                    ),
                )

    def test_parses_existing_legacy_timestamp_format(self):
        self.assertEqual(
            "2026-07-03T18:52:57.7940000Z",
            FIXTURES.ticks_to_kusto_datetime(
                FIXTURES.parse_kusto_datetime_ticks(
                    "7/3/2026, 6:52:57.794 PM"
                )
            ),
        )

    def test_allocates_non_overlapping_slots_per_target_group(self):
        namespaces = FIXTURES.allocate_timestamp_namespaces(
            [
                ("parser-c", "ASimAuthenticationEventLogs"),
                ("parser-a", "ASimAuthenticationEventLogs"),
                ("parser-b", "ASimAuthenticationEventLogs"),
                ("parser-d", "ASimAlertEventLogs"),
            ]
        )

        self.assertEqual(10, namespaces["parser-a"].quantum_ticks)
        self.assertEqual(0, namespaces["parser-a"].slot)
        self.assertEqual(1, namespaces["parser-b"].slot)
        self.assertEqual(2, namespaces["parser-c"].slot)
        self.assertEqual(1, namespaces["parser-d"].quantum_ticks)

    def test_rebase_is_deterministic_and_preserves_target_slot(self):
        rows = [
            {"TimeGenerated": "2026-01-01T00:00:00.0000001Z"},
            {"TimeGenerated": "2026-01-01T00:00:01.0000002Z"},
            {"TimeGenerated": "2026-01-01T00:00:01.0000002Z"},
        ]
        namespace = FIXTURES.TimestampNamespace(
            "parser-b", "ASimAuthenticationEventLogs", 1, 10
        )
        now_ticks = FIXTURES.parse_kusto_datetime_ticks(
            "2026-10-16T20:00:00.0000000Z"
        )
        run_key = FIXTURES.build_run_key(
            "Azure/Azure-Sentinel", "123", "456", 1
        )

        first_rows, first_metadata = FIXTURES.rebase_time_generated(
            rows, run_key, namespace, now_ticks
        )
        second_rows, second_metadata = FIXTURES.rebase_time_generated(
            rows, run_key, namespace, now_ticks
        )

        self.assertEqual(first_rows, second_rows)
        self.assertEqual(first_metadata, second_metadata)
        output_ticks = [
            FIXTURES.parse_kusto_datetime_ticks(row["TimeGenerated"])
            for row in first_rows
        ]
        self.assertTrue(all(tick % 10 == 1 for tick in output_ticks))
        self.assertLess(output_ticks[0], output_ticks[1])
        self.assertEqual(output_ticks[1], output_ticks[2])

    def test_different_parser_slots_do_not_overlap(self):
        rows = [
            {"TimeGenerated": "2026-01-01T00:00:00Z"},
            {"TimeGenerated": "2026-01-01T00:00:01Z"},
        ]
        now_ticks = FIXTURES.parse_kusto_datetime_ticks(
            "2026-10-16T20:00:00Z"
        )
        run_key = FIXTURES.build_run_key(
            "Azure/Azure-Sentinel", "123", "456", 1
        )
        artifacts = []
        for target_id, slot in (("parser-a", 0), ("parser-b", 1)):
            namespace = FIXTURES.TimestampNamespace(
                target_id,
                "ASimAuthenticationEventLogs",
                slot,
                10,
            )
            prepared_rows, metadata = FIXTURES.rebase_time_generated(
                rows, run_key, namespace, now_ticks
            )
            artifacts.append(
                {
                    "namespace": {
                        **namespace.to_dict(),
                        **metadata,
                    },
                    "rows": prepared_rows,
                }
            )

        FIXTURES.assert_disjoint_timestamp_sets(artifacts)
        self.assertTrue(
            set(artifacts[0]["namespace"]["timestampValues"]).isdisjoint(
                artifacts[1]["namespace"]["timestampValues"]
            )
        )

    def test_different_run_ids_produce_different_timestamp_sets(self):
        rows = [{"TimeGenerated": "2026-01-01T00:00:00Z"}]
        namespace = FIXTURES.TimestampNamespace(
            "parser-a", "ASimAuthenticationEventLogs", 0, 1
        )
        now_ticks = FIXTURES.parse_kusto_datetime_ticks(
            "2026-10-16T20:00:00Z"
        )
        first = FIXTURES.rebase_time_generated(
            rows,
            FIXTURES.build_run_key(
                "Azure/Azure-Sentinel", "123", "456", 1
            ),
            namespace,
            now_ticks,
        )[1]["timestampValues"]
        second = FIXTURES.rebase_time_generated(
            rows,
            FIXTURES.build_run_key(
                "Azure/Azure-Sentinel", "123", "457", 1
            ),
            namespace,
            now_ticks,
        )[1]["timestampValues"]
        self.assertNotEqual(first, second)

    def test_different_runs_cannot_overlap_across_multiple_rows(self):
        rows = [
            {"TimeGenerated": "2026-01-01T00:00:00.0000000Z"},
            {"TimeGenerated": "2026-01-01T00:00:00.1830888Z"},
        ]
        namespace = FIXTURES.TimestampNamespace(
            "parser-a", "ASimAuthenticationEventLogs", 0, 1
        )
        now_ticks = FIXTURES.parse_kusto_datetime_ticks(
            "2026-10-16T20:00:00Z"
        )
        artifacts = []
        for run_id in ("456", "457"):
            prepared_rows, metadata = FIXTURES.rebase_time_generated(
                rows,
                FIXTURES.build_run_key(
                    "Azure/Azure-Sentinel", "123", run_id, 1
                ),
                namespace,
                now_ticks,
            )
            artifacts.append(
                {
                    "namespace": {
                        **namespace.to_dict(),
                        **metadata,
                    },
                    "rows": prepared_rows,
                }
            )
        FIXTURES.assert_disjoint_timestamp_sets(artifacts)

    def test_compresses_sample_span_to_36_hours(self):
        rows = [
            {"TimeGenerated": "2026-01-01T00:00:00Z"},
            {"TimeGenerated": "2026-01-03T00:00:00Z"},
        ]
        namespace = FIXTURES.TimestampNamespace(
            "parser-a", "ASimAlertEventLogs", 0, 1
        )
        _, metadata = FIXTURES.rebase_time_generated(
            rows,
            "run-key",
            namespace,
            FIXTURES.parse_kusto_datetime_ticks(
                "2026-10-16T20:00:00Z"
            ),
        )
        self.assertTrue(metadata["compressed"])
        self.assertLessEqual(
            metadata["rebasedSpanTicks"],
            FIXTURES.MAX_SAMPLE_SPAN_TICKS,
        )

    def test_compression_reserves_space_for_remaining_timestamps(self):
        rows = [
            {"TimeGenerated": "2026-01-01T00:00:00.0000000Z"},
            {"TimeGenerated": "2026-01-01T00:00:00.0000001Z"},
            {"TimeGenerated": "2026-01-11T00:00:00.0000000Z"},
        ]
        namespace = FIXTURES.TimestampNamespace(
            "parser-a", "ASimAlertEventLogs", 0, 10
        )
        _, metadata = FIXTURES.rebase_time_generated(
            rows,
            "run-key",
            namespace,
            FIXTURES.parse_kusto_datetime_ticks(
                "2026-10-16T20:00:00Z"
            ),
        )
        self.assertTrue(metadata["compressed"])
        self.assertLessEqual(
            metadata["rebasedSpanTicks"],
            FIXTURES.MAX_SAMPLE_SPAN_TICKS,
        )

    def test_detects_overlapping_artifacts(self):
        artifact = {
            "namespace": {
                "targetGroup": "ASimAlertEventLogs",
                "targetId": "parser-a",
                "timestampValues": ["2026-10-16T19:55:00.0000000Z"],
            }
        }
        duplicate = {
            "namespace": {
                "targetGroup": "ASimAlertEventLogs",
                "targetId": "parser-b",
                "timestampValues": ["2026-10-16T19:55:00.0000000Z"],
            }
        }
        with self.assertRaisesRegex(ValueError, "Timestamp overlap"):
            FIXTURES.assert_disjoint_timestamp_sets(
                [artifact, duplicate]
            )


class FixturePreparationTests(unittest.TestCase):
    def setUp(self):
        self.temp_directory = tempfile.TemporaryDirectory()
        self.root = Path(self.temp_directory.name)

    def tearDown(self):
        self.temp_directory.cleanup()

    def write_fixture(self, content):
        path = self.root / "Sample.csv"
        path.write_text(content, encoding="utf-8")
        return path

    def prepare(
        self,
        fixture_path,
        schema_path=None,
        expected_source_raw_table=None,
    ):
        if expected_source_raw_table is None:
            _, expected_source_raw_table, _ = (
                FIXTURES.load_fixture_csv(fixture_path)
            )
        return FIXTURES.prepare_fixture(
            fixture_path=fixture_path,
            expected_source_raw_table=expected_source_raw_table,
            target_id="parser-a",
            target_group="ASimAuthenticationEventLogs",
            repository="Azure/Azure-Sentinel",
            pull_request="123",
            run_id="456",
            run_attempt=1,
            schema_path=schema_path,
            now_ticks=FIXTURES.parse_kusto_datetime_ticks(
                "2026-10-16T20:00:00Z"
            ),
        )

    def test_infers_schema_and_converts_fixture_values(self):
        fixture = self.write_fixture(
            "TimeGenerated [UTC],Type,Count,Enabled,Payload,Message\n"
            '2026-01-01T00:00:00.1234567Z,Contoso_CL,2,true,'
            '"{""key"":""value""}",hello\n'
        )

        artifact = self.prepare(fixture)

        schema = {
            column["name"]: column["type"]
            for column in artifact["schema"]
        }
        self.assertEqual("datetime", schema["TimeGenerated"])
        self.assertEqual("int", schema["Count"])
        self.assertEqual("boolean", schema["Enabled"])
        self.assertEqual("dynamic", schema["Payload"])
        self.assertEqual("string", schema["Message"])
        self.assertEqual(2, artifact["rows"][0]["Count"])
        self.assertIs(artifact["rows"][0]["Enabled"], True)
        self.assertEqual(
            {"key": "value"}, artifact["rows"][0]["Payload"]
        )
        self.assertEqual("Contoso_CL", artifact["sourceRawTable"])
        self.assertEqual("inferred", artifact["schemaSource"])

    def test_uses_discovered_table_schema(self):
        fixture = self.write_fixture(
            "TimeGenerated,Type,Enabled,Payload\n"
            '2026-01-01T00:00:00Z,Contoso_CL,false,"{""x"":1}"\n'
        )
        schema_path = self.root / "Contoso_CL_Schema.csv"
        schema_path.write_text(
            "ColumnName,ColumnType\n"
            "TimeGenerated,datetime\n"
            "Enabled,bool\n"
            "Payload,dynamic\n",
            encoding="utf-8",
        )

        artifact = self.prepare(fixture)

        self.assertEqual("discovered", artifact["schemaSource"])
        self.assertEqual(
            schema_path.resolve(),
            Path(artifact["schemaPath"]).resolve(),
        )
        self.assertIs(artifact["rows"][0]["Enabled"], False)
        self.assertEqual({"x": 1}, artifact["rows"][0]["Payload"])

    def test_adapts_repository_style_schema_aliases(self):
        fixture = self.write_fixture(
            "TimeGenerated,Type,Enabled,Count,Payload\n"
            '2026-01-01T00:00:00Z,Contoso_CL,true,7,"{""x"":1}"\n'
        )
        schema_path = self.root / "ContosoSchema.csv"
        schema_path.write_text(
            "ColumnName,ColumnType\n"
            "TimeGenerated,DateTime\n"
            "Enabled,SByte\n"
            "Count,Int32\n"
            "Payload,Object\n",
            encoding="utf-8",
        )

        artifact = self.prepare(fixture, schema_path=schema_path)

        schema = {
            column["name"]: column["type"]
            for column in artifact["schema"]
        }
        self.assertEqual("boolean", schema["Enabled"])
        self.assertEqual("int", schema["Count"])
        self.assertEqual("dynamic", schema["Payload"])
        self.assertIs(artifact["rows"][0]["Enabled"], True)
        self.assertEqual(7, artifact["rows"][0]["Count"])
        self.assertEqual({"x": 1}, artifact["rows"][0]["Payload"])

    def test_rejects_multiple_source_table_types(self):
        fixture = self.write_fixture(
            "TimeGenerated,Type\n"
            "2026-01-01T00:00:00Z,First_CL\n"
            "2026-01-01T00:00:01Z,Second_CL\n"
        )
        with self.assertRaisesRegex(ValueError, "multiple Type values"):
            self.prepare(fixture)

    def test_rejects_fixture_over_size_limit(self):
        fixture = self.write_fixture(
            "TimeGenerated,Type\n"
            "2026-01-01T00:00:00Z,Contoso_CL\n"
        )
        with unittest.mock.patch.object(
            FIXTURES, "MAX_FIXTURE_BYTES", 10
        ):
            with self.assertRaisesRegex(ValueError, "fixture limit"):
                self.prepare(fixture)

    def test_rejects_schema_over_size_limit(self):
        fixture = self.write_fixture(
            "TimeGenerated,Type\n"
            "2026-01-01T00:00:00Z,Contoso_CL\n"
        )
        schema = self.root / "schema.csv"
        schema.write_text(
            "ColumnName,ColumnType\nTimeGenerated,datetime\n",
            encoding="utf-8",
        )
        with unittest.mock.patch.object(
            FIXTURES, "MAX_SCHEMA_BYTES", 10
        ):
            with self.assertRaisesRegex(ValueError, "schema limit"):
                self.prepare(fixture, schema_path=schema)

    def test_rejects_fixture_type_that_does_not_match_itp_source(self):
        fixture = self.write_fixture(
            "TimeGenerated,Type\n"
            "2026-01-01T00:00:00Z,Other_CL\n"
        )

        with self.assertRaisesRegex(
            ValueError, "Fixture Type must be 'Contoso_CL'"
        ):
            self.prepare(
                fixture,
                expected_source_raw_table="Contoso_CL",
            )

    def test_artifact_is_deterministic_for_same_inputs(self):
        fixture = self.write_fixture(
            "TimeGenerated,Type,Value\n"
            "2026-01-01T00:00:00Z,Contoso_CL,one\n"
        )
        first = self.prepare(fixture)
        second = self.prepare(fixture)
        self.assertEqual(first, second)

    def test_inference_preserves_identifier_and_numeric_ranges(self):
        fixture = self.write_fixture(
            "TimeGenerated,Type,AccountId,SmallCount,LargeCount,HugeNumber,"
            "SchemaVersion\n"
            "2026-01-01T00:00:00Z,Unknown_CL,00123,7,"
            "2147483648,9223372036854775808,2.0\n"
        )

        artifact = self.prepare(fixture)

        schema = {
            column["name"]: column["type"]
            for column in artifact["schema"]
        }
        self.assertEqual("string", schema["AccountId"])
        self.assertEqual("int", schema["SmallCount"])
        self.assertEqual("long", schema["LargeCount"])
        self.assertEqual("string", schema["HugeNumber"])
        self.assertEqual("string", schema["SchemaVersion"])

    def test_rejects_target_slot_outside_target_count(self):
        fixture = self.write_fixture(
            "TimeGenerated,Type\n"
            "2026-01-01T00:00:00Z,Contoso_CL\n"
        )
        with self.assertRaisesRegex(ValueError, "target_slot"):
            FIXTURES.prepare_fixture(
                fixture_path=fixture,
                expected_source_raw_table="Contoso_CL",
                target_id="parser-a",
                target_group="ASimAuthenticationEventLogs",
                repository="Azure/Azure-Sentinel",
                pull_request="123",
                run_id="456",
                run_attempt=1,
                target_slot=2,
                target_count=2,
            )

    def test_cli_writes_prepared_artifact(self):
        fixture = self.write_fixture(
            "TimeGenerated,Type,Value\n"
            "2026-01-01T00:00:00Z,Contoso_CL,one\n"
        )
        output = self.root / "prepared.json"

        exit_code = FIXTURES.main(
            [
                "prepare",
                str(fixture),
                "--expected-source-raw-table",
                "Contoso_CL",
                "--target-id",
                "parser-a",
                "--target-group",
                "ASimAuthenticationEventLogs",
                "--run-id",
                "456",
                "--now",
                "2026-10-16T20:00:00Z",
                "--output",
                str(output),
            ]
        )

        self.assertEqual(0, exit_code)
        artifact = json.loads(output.read_text(encoding="utf-8"))
        self.assertEqual("parser-a", artifact["targetId"])
        self.assertEqual(1, artifact["rowCount"])

    def test_artifact_write_is_no_clobber(self):
        output = self.root / "prepared.json"
        payload = {"version": 1, "value": "first"}
        FIXTURES._write_json(payload, output)
        FIXTURES._write_json(payload, output)
        with self.assertRaisesRegex(ValueError, "Refusing to overwrite"):
            FIXTURES._write_json(
                {"version": 1, "value": "different"}, output
            )

    def test_cli_rejects_output_path_equal_to_fixture(self):
        fixture = self.write_fixture(
            "TimeGenerated,Type\n"
            "2026-01-01T00:00:00Z,Contoso_CL\n"
        )
        exit_code = FIXTURES.main(
            [
                "prepare",
                str(fixture),
                "--expected-source-raw-table",
                "Contoso_CL",
                "--target-id",
                "parser-a",
                "--target-group",
                "ASimAuthenticationEventLogs",
                "--run-id",
                "456",
                "--output",
                str(fixture),
            ]
        )
        self.assertEqual(1, exit_code)

    def test_prepares_real_guardduty_fixture(self):
        repo_root = Path(__file__).resolve().parents[5]
        fixture = (
            repo_root
            / "Sample Data/ASIM/"
            "AWS_GuardDuty_AlertEvent_AWSGuardDuty_IngestedLogs.csv"
        )
        artifact = FIXTURES.prepare_fixture(
            fixture_path=fixture,
            expected_source_raw_table="AWSGuardDuty",
            target_id="asimalerteventawsguardduty",
            target_group="ASimAlertEventLogs",
            repository="Azure/Azure-Sentinel",
            pull_request="123",
            run_id="456",
            run_attempt=1,
            now_ticks=FIXTURES.parse_kusto_datetime_ticks(
                "2026-10-16T20:00:00Z"
            ),
        )

        self.assertGreater(artifact["rowCount"], 0)
        self.assertEqual("AWSGuardDuty", artifact["sourceRawTable"])
        self.assertEqual("repository", artifact["schemaSource"])
        self.assertRegex(
            artifact["rows"][0]["TimeGenerated"],
            r"\.\d{7}Z$",
        )
        self.assertIsInstance(artifact["rows"][0]["AccountId"], str)
        self.assertIsInstance(
            artifact["rows"][0]["SchemaVersion"], str
        )
        self.assertRegex(
            artifact["rows"][0]["TimeCreated"], r"\.\d{7}Z$"
        )
        self.assertIsInstance(
            artifact["rows"][0]["ResourceDetails"], dict
        )
        self.assertTrue(
            artifact["namespace"]["timestampSetHash"].startswith(
                "sha256:"
            )
        )

    def test_prepares_all_available_source_specific_fixtures(self):
        repo_root = Path(__file__).resolve().parents[5]
        cases = (
            (
                "CrowdStrike_Falcon_AlertEvent_"
                "CrowdStrikeDetections_IngestedLogs.csv",
                "CrowdStrikeDetections",
                "ASimAlertEventLogs",
            ),
            (
                "Salesforce_Service Cloud_Authentication_"
                "SalesforceServiceCloudV3_CL_IngestedLogs.csv",
                "SalesforceServiceCloudV3_CL",
                "ASimAuthenticationEventLogs",
            ),
            (
                "Salesforce_Salesforce Service Cloud_WebSession_"
                "SalesforceServiceCloudV3_CL_IngestedLogs.csv",
                "SalesforceServiceCloudV3_CL",
                "ASimWebSessionLogs",
            ),
        )
        for index, (filename, source_table, target_group) in enumerate(
            cases
        ):
            with self.subTest(filename=filename):
                artifact = FIXTURES.prepare_fixture(
                    fixture_path=repo_root / "Sample Data/ASIM" / filename,
                    expected_source_raw_table=source_table,
                    target_id=f"fixture-{index}",
                    target_group=target_group,
                    repository="Azure/Azure-Sentinel",
                    pull_request="123",
                    run_id="456",
                    run_attempt=1,
                    now_ticks=FIXTURES.parse_kusto_datetime_ticks(
                        "2026-10-16T20:00:00Z"
                    ),
                )
                self.assertGreater(artifact["rowCount"], 0)
                self.assertEqual(
                    source_table, artifact["sourceRawTable"]
                )
                self.assertEqual(
                    "repository", artifact["schemaSource"]
                )

    def test_salesforce_fixtures_include_rejected_filter_rows(self):
        repo_root = Path(__file__).resolve().parents[5]
        cases = (
            (
                "Salesforce_Service Cloud_Authentication_"
                "SalesforceServiceCloudV3_CL_IngestedLogs.csv",
                {"Login", "LoginAs", "Logout"},
            ),
            (
                "Salesforce_Salesforce Service Cloud_WebSession_"
                "SalesforceServiceCloudV3_CL_IngestedLogs.csv",
                {
                    "ApiTotalUsage",
                    "RestApi",
                    "BulkApi2",
                    "ApexCallout",
                    "ExternalODataCallout",
                    "MetadataApiOperation",
                    "NamedCredential",
                    "URI",
                    "AuraRequest",
                    "LightningPageView",
                    "LightningPerformance",
                    "LightningInteraction",
                    "UiTelemetryResourceTiming",
                    "UiTelemetryNavigationTiming",
                    "CSPViolation",
                },
            ),
        )
        for filename, accepted_types in cases:
            with self.subTest(filename=filename):
                path = repo_root / "Sample Data/ASIM" / filename
                with path.open(
                    "r", encoding="utf-8-sig", newline=""
                ) as stream:
                    rows = list(csv.DictReader(stream))
                event_types = {
                    row["EventType"] for row in rows
                }
                self.assertTrue(event_types & accepted_types)
                self.assertTrue(event_types - accepted_types)


if __name__ == "__main__":
    unittest.main()
