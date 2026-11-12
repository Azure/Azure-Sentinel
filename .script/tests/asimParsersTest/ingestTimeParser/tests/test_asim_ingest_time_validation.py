import importlib.util
import sys
import tempfile
import unittest
import unittest.mock
from pathlib import Path

import yaml


MODULE_PATH = Path(__file__).resolve().parents[1] / "asim_ingest_time_validation.py"
SPEC = importlib.util.spec_from_file_location(
    "asim_ingest_time_validation", MODULE_PATH
)
VALIDATION = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = VALIDATION
SPEC.loader.exec_module(VALIDATION)

from asim_ingestion.parser import static_validation as STATIC_VALIDATION
from asim_ingestion.parser.kusto_analyzer import (
    KustoAnalyzerError,
    analyze_kql,
)


class AsimIngestTimeValidationTests(unittest.TestCase):
    def setUp(self):
        self.temp_directory = tempfile.TemporaryDirectory()
        self.repo_root = Path(self.temp_directory.name)
        self.write_fixture(
            "Contoso",
            "Contoso",
            "Authentication",
            "Contoso_CL",
        )

    def tearDown(self):
        self.temp_directory.cleanup()

    def write_yaml(self, relative_path, document):
        path = self.repo_root / relative_path
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(
            yaml.safe_dump(document, sort_keys=False),
            encoding="utf-8",
        )
        return path

    def write_fixture(
        self,
        event_vendor,
        event_product,
        schema,
        source_table,
    ):
        relative_path = (
            "Sample Data/ASIM/"
            f"{event_vendor}_{event_product}_{schema}_{source_table}"
            "_IngestedLogs.csv"
        )
        path = self.repo_root / relative_path
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(
            "TimeGenerated,Type,EventType\n"
            f"2026-10-19T00:00:00Z,{source_table},Login\n"
            f"2026-10-19T00:00:01Z,{source_table},Logout\n",
            encoding="utf-8",
        )
        return relative_path

    def query_parser(
        self,
        parser_name="ASimAuthenticationContoso",
        product="Contoso",
        schema="Authentication",
        schema_version="1.0.0",
        source_table="Contoso_CL",
        parser_query=None,
    ):
        parser_suffix = parser_name.removeprefix(f"ASim{schema}")
        if parser_query is None:
            parser_query = (
                "let parser=(disabled:bool=false, pack:bool=false) {\n"
                f"  {source_table}\n"
                "  | where not(disabled)\n"
                '  | where EventType == "Login"\n'
                "  | project TimeGenerated, EventType\n"
                "};\n"
                "parser(disabled=false, pack=true)"
            )
        return {
            "Parser": {
                "Title": f"{product} query-time parser",
                "Version": "1.0.0",
                "LastUpdated": "Oct 14, 2026",
            },
            "Product": {"Name": product},
            "Normalization": {
                "Schema": schema,
                "Version": schema_version,
            },
            "ParserName": parser_name,
            "EquivalentBuiltInParser": f"_ASim_{schema}_{parser_suffix}",
            "ParserParams": [
                {"Name": "disabled", "Type": "bool", "Default": False},
                {"Name": "pack", "Type": "bool", "Default": False},
            ],
            "ParserQuery": parser_query,
        }

    def ingest_parser(
        self,
        parser_name="ASimAuthenticationContoso",
        product="Contoso",
        schema="Authentication",
        schema_version="1.0.0",
        source_table="Contoso_CL",
        target_table="ASimAuthenticationEventLogs",
        parser_filter_query='source\n| where EventType == "Login"',
        parser_query=None,
        dcr_type="Standard",
        input_stream="Custom-Contoso_CL",
        event_vendor=None,
        event_product=None,
    ):
        event_vendor = event_vendor or product
        event_product = event_product or product
        if parser_query is None:
            parser_query = (
                'source\n| where EventType == "Login"\n'
                f'| extend EventVendor = "{event_vendor}", '
                f'EventProduct = "{event_product}"\n'
                "| project TimeGenerated, EventType, "
                "EventVendor, EventProduct"
            )
        document = {
            "Parser": {
                "DisplayName": f"{product} ingestion-time parser",
                "Version": "1.0.0",
                "LastUpdated": "2026-10-14",
            },
            "Product": {"Name": product},
            "Normalization": {
                "Schema": schema,
                "Version": schema_version,
            },
            "Author": "Microsoft",
            "Description": f"Normalizes {source_table} into {target_table}.",
            "ParserName": parser_name,
            "DCRType": dcr_type,
            "SourceRawTable": source_table,
            "TargetASIMTable": target_table,
            "ParserFilterQuery": parser_filter_query,
            "ParserQuery": parser_query,
            "Change": {
                "Date": "2026-10-14",
                "Description": "Initial ingestion-time parser.",
            },
        }
        if input_stream is not None:
            document["InputStream"] = input_stream
        return document

    def parser_query_with_length(self, length):
        prefix = (
            'source\n| where EventType == "Login"\n'
            '| extend EventVendor = "Contoso", '
            'EventProduct = "Contoso", Padding = "'
        )
        suffix = (
            '"\n| project TimeGenerated, EventType, '
            "EventVendor, EventProduct, Padding"
        )
        padding_length = length - len(prefix) - len(suffix)
        self.assertGreaterEqual(padding_length, 0)
        query = prefix + ("x" * padding_length) + suffix
        self.assertEqual(length, len(query))
        return query

    def test_discovers_exact_pair_from_ingestion_change(self):
        query_path = (
            "Parsers/ASimAuthentication/Parsers/"
            "ASimAuthenticationContoso.yaml"
        )
        ingest_path = (
            "Parsers/ASimAuthentication/IngestTimeParsers/"
            "ASimAuthenticationContoso.yaml"
        )
        self.write_yaml(query_path, self.query_parser())
        self.write_yaml(ingest_path, self.ingest_parser())

        manifest = VALIDATION.build_validation_manifest(
            self.repo_root, [ingest_path]
        )

        self.assertEqual(1, len(manifest["targets"]))
        target = manifest["targets"][0]
        self.assertEqual("paired", target["pairStatus"])
        self.assertEqual(query_path, target["queryTimeParserPath"])
        self.assertEqual("identity", target["pairEvidence"]["tier"])

    def test_uses_product_and_source_for_abbreviated_pair_name(self):
        query_path = (
            "Parsers/ASimAuthentication/Parsers/"
            "ASimAuthenticationSalesforceSC.yaml"
        )
        ingest_path = (
            "Parsers/ASimAuthentication/IngestTimeParsers/"
            "ASimAuthenticationSalesforceServiceCloud.yaml"
        )
        self.write_yaml(
            query_path,
            self.query_parser(
                parser_name="ASimAuthenticationSalesforceSC",
                product="Salesforce Service Cloud",
                source_table="SalesforceServiceCloudV3_CL",
            ),
        )
        self.write_yaml(
            ingest_path,
            self.ingest_parser(
                parser_name="ASimAuthenticationSalesforceServiceCloud",
                product="Salesforce Service Cloud",
                source_table="SalesforceServiceCloudV3_CL",
                input_stream="Custom-SalesforceServiceCloudV3_CL",
            ),
        )

        target = VALIDATION.build_validation_manifest(
            self.repo_root, [ingest_path]
        )["targets"][0]

        self.assertEqual("paired", target["pairStatus"])
        self.assertEqual(query_path, target["queryTimeParserPath"])
        self.assertEqual("product", target["pairEvidence"]["tier"])

    def test_reports_ambiguous_product_pair(self):
        ingest_path = (
            "Parsers/ASimAuthentication/IngestTimeParsers/"
            "ASimAuthenticationContosoService.yaml"
        )
        self.write_yaml(
            ingest_path,
            self.ingest_parser(
                parser_name="ASimAuthenticationContosoService",
                product="Contoso Service",
            ),
        )
        for suffix in ("A", "B"):
            self.write_yaml(
                "Parsers/ASimAuthentication/Parsers/"
                f"ASimAuthenticationContoso{suffix}.yaml",
                self.query_parser(
                    parser_name=f"ASimAuthenticationContoso{suffix}",
                    product="Contoso Service",
                ),
            )

        target = VALIDATION.build_validation_manifest(
            self.repo_root, [ingest_path]
        )["targets"][0]

        self.assertEqual("ambiguous", target["pairStatus"])
        self.assertIsNone(target["queryTimeParserPath"])
        self.assertEqual(2, len(target["pairCandidates"]))

    def test_identity_match_still_requires_product_agreement(self):
        query_path = (
            "Parsers/ASimAuthentication/Parsers/"
            "ASimAuthenticationContoso.yaml"
        )
        ingest_path = (
            "Parsers/ASimAuthentication/IngestTimeParsers/"
            "ASimAuthenticationContoso.yaml"
        )
        self.write_yaml(
            query_path,
            self.query_parser(product="Different Product"),
        )
        self.write_yaml(ingest_path, self.ingest_parser())

        target = VALIDATION.build_validation_manifest(
            self.repo_root, [ingest_path]
        )["targets"][0]

        self.assertEqual("unpaired", target["pairStatus"])
        self.assertIsNone(target["queryTimeParserPath"])

    def test_qtp_identifier_must_be_used_as_a_source_table(self):
        query_path = (
            "Parsers/ASimAuthentication/Parsers/"
            "ASimAuthenticationContoso.yaml"
        )
        ingest_path = (
            "Parsers/ASimAuthentication/IngestTimeParsers/"
            "ASimAuthenticationContoso.yaml"
        )
        self.write_yaml(
            query_path,
            self.query_parser(
                parser_query=(
                    "let parser=(disabled:bool=false) {\n"
                    "  Other_CL\n"
                    "  | extend Contoso_CL = EventType\n"
                    "  | project TimeGenerated\n"
                    "};\n"
                    "parser(disabled=false)"
                )
            ),
        )
        self.write_yaml(ingest_path, self.ingest_parser())

        target = VALIDATION.build_validation_manifest(
            self.repo_root, [ingest_path]
        )["targets"][0]

        self.assertEqual("unpaired", target["pairStatus"])

    def test_resolves_source_table_specific_fixture_metadata(self):
        ingest_path = (
            "Parsers/ASimAuthentication/IngestTimeParsers/"
            "ASimAuthenticationContoso.yaml"
        )
        self.write_yaml(ingest_path, self.ingest_parser())

        target = VALIDATION.build_validation_manifest(
            self.repo_root, [ingest_path]
        )["targets"][0]

        self.assertEqual("Contoso", target["eventVendor"])
        self.assertEqual("Contoso", target["eventProduct"])
        self.assertEqual(
            "Sample Data/ASIM/"
            "Contoso_Contoso_Authentication_Contoso_CL"
            "_IngestedLogs.csv",
            target["fixturePath"],
        )
        self.assertEqual("resolved", target["fixtureStatus"])
        self.assertEqual([], target["discoveryErrors"])

    def test_non_static_event_product_blocks_fixture_resolution(self):
        ingest_path = (
            "Parsers/ASimAuthentication/IngestTimeParsers/"
            "ASimAuthenticationContoso.yaml"
        )
        self.write_yaml(
            ingest_path,
            self.ingest_parser(
                parser_query=(
                    'source\n| where EventType == "Login"\n'
                    '| extend EventVendor = "Contoso", '
                    "EventProduct = ProductName\n"
                    "| project TimeGenerated, EventType, "
                    "EventVendor, EventProduct"
                )
            ),
        )

        target = VALIDATION.build_validation_manifest(
            self.repo_root, [ingest_path]
        )["targets"][0]

        self.assertEqual("invalid", target["fixtureStatus"])
        self.assertIsNone(target["fixturePath"])
        self.assertTrue(target["discoveryErrors"])

    def test_any_non_static_event_product_assignment_blocks_fixture(self):
        ingest_path = (
            "Parsers/ASimAuthentication/IngestTimeParsers/"
            "ASimAuthenticationContoso.yaml"
        )
        self.write_yaml(
            ingest_path,
            self.ingest_parser(
                parser_query=(
                    "source\n"
                    "| project-rename EventProduct = ProductName\n"
                    '| extend EventVendor = "Contoso", '
                    'EventProduct = "Contoso"\n'
                    "| project TimeGenerated, EventType, "
                    "EventVendor, EventProduct"
                )
            ),
        )

        target = VALIDATION.build_validation_manifest(
            self.repo_root, [ingest_path]
        )["targets"][0]

        self.assertEqual("invalid", target["fixtureStatus"])
        self.assertTrue(
            any(
                "non-static expression" in error
                for error in target["discoveryErrors"]
            ),
            target["discoveryErrors"],
        )

    def test_deduplicates_target_when_both_parser_files_change(self):
        query_path = (
            "Parsers/ASimAuthentication/Parsers/"
            "ASimAuthenticationContoso.yaml"
        )
        ingest_path = (
            "Parsers/ASimAuthentication/IngestTimeParsers/"
            "ASimAuthenticationContoso.yaml"
        )
        self.write_yaml(query_path, self.query_parser())
        self.write_yaml(ingest_path, self.ingest_parser())

        manifest = VALIDATION.build_validation_manifest(
            self.repo_root, [query_path, ingest_path]
        )

        self.assertEqual(1, len(manifest["targets"]))
        self.assertEqual(
            sorted([query_path, ingest_path]),
            manifest["targets"][0]["triggerPaths"],
        )

    def test_deduplicates_itp_qtp_and_fixture_triggers(self):
        query_path = (
            "Parsers/ASimAuthentication/Parsers/"
            "ASimAuthenticationContoso.yaml"
        )
        ingest_path = (
            "Parsers/ASimAuthentication/IngestTimeParsers/"
            "ASimAuthenticationContoso.yaml"
        )
        fixture_path = (
            "Sample Data/ASIM/"
            "Contoso_Contoso_Authentication_Contoso_CL"
            "_IngestedLogs.csv"
        )
        self.write_yaml(query_path, self.query_parser())
        self.write_yaml(ingest_path, self.ingest_parser())

        manifest = VALIDATION.build_validation_manifest(
            self.repo_root,
            [fixture_path, query_path, ingest_path],
        )

        self.assertEqual(1, len(manifest["targets"]))
        self.assertEqual(
            sorted([fixture_path, query_path, ingest_path]),
            manifest["targets"][0]["triggerPaths"],
        )

    def test_fixture_change_selects_standalone_ingestion_target(self):
        ingest_path = (
            "Parsers/ASimAuthentication/IngestTimeParsers/"
            "ASimAuthenticationContoso.yaml"
        )
        fixture_path = (
            "Sample Data/ASIM/"
            "Contoso_Contoso_Authentication_Contoso_CL"
            "_IngestedLogs.csv"
        )
        self.write_yaml(ingest_path, self.ingest_parser())

        target = VALIDATION.build_validation_manifest(
            self.repo_root, [fixture_path]
        )["targets"][0]

        self.assertEqual("unpaired", target["pairStatus"])
        self.assertEqual("ingest-only", target["validationKind"])
        self.assertEqual(fixture_path, target["fixturePath"])
        self.assertEqual([fixture_path], target["triggerPaths"])

    def test_query_change_selects_every_mapped_ingestion_target(self):
        query_path = (
            "Parsers/ASimAuthentication/Parsers/"
            "ASimAuthenticationContoso.yaml"
        )
        first_ingest_path = (
            "Parsers/ASimAuthentication/IngestTimeParsers/"
            "ASimAuthenticationContosoFirst.yaml"
        )
        second_ingest_path = (
            "Parsers/ASimAuthentication/IngestTimeParsers/"
            "ASimAuthenticationContosoSecond.yaml"
        )
        self.write_yaml(
            query_path,
            self.query_parser(
                parser_query=(
                    "let parser=(disabled:bool=false, pack:bool=false) {\n"
                    "  union First_CL, Second_CL\n"
                    "  | where not(disabled)\n"
                    "  | project TimeGenerated, EventType\n"
                    "};\n"
                    "parser(disabled=false, pack=true)"
                )
            ),
        )
        self.write_yaml(
            first_ingest_path,
            self.ingest_parser(
                parser_name="ASimAuthenticationContosoFirst",
                source_table="First_CL",
                input_stream="Custom-First_CL",
            ),
        )
        self.write_yaml(
            second_ingest_path,
            self.ingest_parser(
                parser_name="ASimAuthenticationContosoSecond",
                source_table="Second_CL",
                input_stream="Custom-Second_CL",
            ),
        )

        targets = VALIDATION.build_validation_manifest(
            self.repo_root, [query_path]
        )["targets"]

        self.assertEqual(2, len(targets))
        self.assertEqual(
            {first_ingest_path, second_ingest_path},
            {
                target["ingestTimeParserPath"]
                for target in targets
            },
        )
        self.assertTrue(
            all(target["triggerPaths"] == [query_path] for target in targets)
        )

    def test_query_time_parser_without_ingestion_counterpart_adds_no_target(self):
        query_path = (
            "Parsers/ASimAuthentication/Parsers/"
            "ASimAuthenticationContoso.yaml"
        )
        self.write_yaml(query_path, self.query_parser())

        manifest = VALIDATION.build_validation_manifest(
            self.repo_root, [query_path]
        )

        self.assertEqual([], manifest["targets"])

    def test_invalid_changed_query_parser_is_left_to_existing_qtp_ci(self):
        query_path = (
            "Parsers/ASimAuthentication/Parsers/"
            "ASimAuthenticationBroken.yaml"
        )
        path = self.repo_root / query_path
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("ParserName: Broken\nParserName: Duplicate\n")

        manifest = VALIDATION.build_validation_manifest(
            self.repo_root, [query_path]
        )

        self.assertEqual([], manifest["targets"])
        self.assertTrue(
            any(
                error["path"] == query_path
                for error in manifest["indexErrors"]
            )
        )

    def test_valid_ingestion_parser_passes_contract_validation(self):
        query_path = self.write_yaml(
            "Parsers/ASimAuthentication/Parsers/"
            "ASimAuthenticationContoso.yaml",
            self.query_parser(),
        )
        ingest_path = self.write_yaml(
            "Parsers/ASimAuthentication/IngestTimeParsers/"
            "ASimAuthenticationContoso.yaml",
            self.ingest_parser(),
        )

        result = VALIDATION.validate_ingest_time_parser(
            ingest_path, query_time_path=query_path
        )

        self.assertTrue(result["valid"], result["findings"])
        self.assertEqual([], result["findings"])
        self.assertEqual(
            "resolved", result["fixtureResolution"]["status"]
        )
        self.assertEqual(
            "eligible", result["queryTimeEligibility"]["status"]
        )
        self.assertTrue(
            result["queryTimeEligibility"]["supportsDisabled"]
        )
        self.assertTrue(result["queryTimeEligibility"]["supportsPack"])

    def test_allows_parser_query_at_dcr_transform_limit(self):
        limit = VALIDATION.parser_common.MAX_DCR_TRANSFORM_KQL_CHARS
        parser_query = self.parser_query_with_length(limit)
        ingest_path = self.write_yaml(
            "Parsers/ASimAuthentication/IngestTimeParsers/"
            "ASimAuthenticationContoso.yaml",
            self.ingest_parser(
                parser_query=parser_query
            ),
        )

        result = VALIDATION.validate_ingest_time_parser(ingest_path)

        self.assertTrue(result["valid"], result["findings"])

    def test_rejects_parser_query_over_dcr_transform_limit(self):
        limit = VALIDATION.parser_common.MAX_DCR_TRANSFORM_KQL_CHARS
        parser_query = self.parser_query_with_length(limit + 1)
        ingest_path = self.write_yaml(
            "Parsers/ASimAuthentication/IngestTimeParsers/"
            "ASimAuthenticationContoso.yaml",
            self.ingest_parser(
                parser_query=parser_query
            ),
        )

        result = VALIDATION.validate_ingest_time_parser(ingest_path)

        finding = next(
            item
            for item in result["findings"]
            if item["code"] == "KQL044"
        )
        self.assertFalse(result["valid"])
        self.assertIn(str(limit + 1), finding["message"])
        self.assertIn(str(limit), finding["message"])

    def test_query_length_includes_comments_and_indentation(self):
        limit = VALIDATION.parser_common.MAX_DCR_TRANSFORM_KQL_CHARS
        parser_query = (
            "// formatting counts toward TransformKql length\n"
            "    " + self.parser_query_with_length(limit)
        )
        ingest_path = self.write_yaml(
            "Parsers/ASimAuthentication/IngestTimeParsers/"
            "ASimAuthenticationContoso.yaml",
            self.ingest_parser(parser_query=parser_query),
        )

        result = VALIDATION.validate_ingest_time_parser(ingest_path)

        finding = next(
            item
            for item in result["findings"]
            if item["code"] == "KQL044"
        )
        self.assertFalse(result["valid"])
        self.assertIn(str(len(parser_query)), finding["message"])

    def test_standalone_ingestion_parser_is_valid_without_qtp(self):
        ingest_path = self.write_yaml(
            "Parsers/ASimAuthentication/IngestTimeParsers/"
            "ASimAuthenticationContoso.yaml",
            self.ingest_parser(),
        )

        result = VALIDATION.validate_ingest_time_parser(ingest_path)

        self.assertTrue(result["valid"], result["findings"])
        self.assertEqual(
            "not-applicable",
            result["queryTimeEligibility"]["status"],
        )

    def test_qtp_mismatch_blocks_optional_stages_only(self):
        query_path = self.write_yaml(
            "Parsers/ASimAuthentication/Parsers/"
            "ASimAuthenticationContoso.yaml",
            self.query_parser(
                product="Different Product",
                schema_version="9.9.9",
            ),
        )
        ingest_path = self.write_yaml(
            "Parsers/ASimAuthentication/IngestTimeParsers/"
            "ASimAuthenticationContoso.yaml",
            self.ingest_parser(),
        )

        result = VALIDATION.validate_ingest_time_parser(
            ingest_path, query_time_path=query_path
        )

        self.assertTrue(result["valid"], result["findings"])
        self.assertEqual(
            "blocked", result["queryTimeEligibility"]["status"]
        )
        pair_findings = [
            finding
            for finding in result["findings"]
            if finding["code"].startswith("PAIR")
        ]
        self.assertEqual(["PAIR004"], [
            finding["code"] for finding in pair_findings
        ])
        self.assertTrue(
            all(
                finding["severity"] == "blocked"
                for finding in pair_findings
            )
        )

    def test_malformed_qtp_blocks_optional_stages_only(self):
        query_path = (
            self.repo_root
            / "Parsers/ASimAuthentication/Parsers/"
            "ASimAuthenticationContoso.yaml"
        )
        query_path.parent.mkdir(parents=True, exist_ok=True)
        query_path.write_text(
            "ParserName: ASimAuthenticationContoso\n"
            "ParserName: Duplicate\n",
            encoding="utf-8",
        )
        ingest_path = self.write_yaml(
            "Parsers/ASimAuthentication/IngestTimeParsers/"
            "ASimAuthenticationContoso.yaml",
            self.ingest_parser(),
        )

        result = VALIDATION.validate_ingest_time_parser(
            ingest_path, query_time_path=query_path
        )

        self.assertTrue(result["valid"], result["findings"])
        self.assertEqual(
            "blocked", result["queryTimeEligibility"]["status"]
        )
        self.assertIn(
            "PAIR001",
            {finding["code"] for finding in result["findings"]},
        )

    def test_rejects_target_table_that_does_not_match_schema(self):
        ingest_path = self.write_yaml(
            "Parsers/ASimAuthentication/IngestTimeParsers/"
            "ASimAuthenticationContoso.yaml",
            self.ingest_parser(target_table="ASimAuditEventLogs"),
        )

        result = VALIDATION.validate_ingest_time_parser(ingest_path)

        self.assertFalse(result["valid"])
        self.assertIn(
            "META012", {finding["code"] for finding in result["findings"]}
        )

    def test_rejects_standard_parser_with_none_input_stream(self):
        ingest_path = self.write_yaml(
            "Parsers/ASimAuthentication/IngestTimeParsers/"
            "ASimAuthenticationContoso.yaml",
            self.ingest_parser(input_stream="none"),
        )

        result = VALIDATION.validate_ingest_time_parser(ingest_path)

        self.assertIn(
            "META008", {finding["code"] for finding in result["findings"]}
        )

    def test_rejects_standard_parser_without_input_stream(self):
        ingest_path = self.write_yaml(
            "Parsers/ASimAuthentication/IngestTimeParsers/"
            "ASimAuthenticationContoso.yaml",
            self.ingest_parser(input_stream=None),
        )

        result = VALIDATION.validate_ingest_time_parser(ingest_path)

        codes = {finding["code"] for finding in result["findings"]}
        self.assertIn("META008", codes)
        self.assertNotIn("META001", codes)

    def test_standard_parser_allows_connector_specific_input_stream(self):
        ingest_path = self.write_yaml(
            "Parsers/ASimAuthentication/IngestTimeParsers/"
            "ASimAuthenticationContoso.yaml",
            self.ingest_parser(input_stream="Custom-Bogus_CL"),
        )

        result = VALIDATION.validate_ingest_time_parser(ingest_path)

        self.assertTrue(result["valid"], result["findings"])

    def test_workspace_parser_accepts_missing_input_stream(self):
        self.write_fixture(
            "Legacy",
            "Legacy",
            "Authentication",
            "Legacy_CL",
        )
        ingest_path = self.write_yaml(
            "Parsers/ASimAuthentication/IngestTimeParsers/"
            "ASimAuthenticationLegacy.yaml",
            self.ingest_parser(
                parser_name="ASimAuthenticationLegacy",
                product="Legacy",
                source_table="Legacy_CL",
                dcr_type="Workspace",
                input_stream=None,
            ),
        )

        result = VALIDATION.validate_ingest_time_parser(ingest_path)

        self.assertTrue(result["valid"], result["findings"])

    def test_workspace_parser_accepts_none_input_stream(self):
        self.write_fixture(
            "Legacy",
            "Legacy",
            "Authentication",
            "Legacy_CL",
        )
        ingest_path = self.write_yaml(
            "Parsers/ASimAuthentication/IngestTimeParsers/"
            "ASimAuthenticationLegacy.yaml",
            self.ingest_parser(
                parser_name="ASimAuthenticationLegacy",
                product="Legacy",
                source_table="Legacy_CL",
                dcr_type="Workspace",
                input_stream="none",
            ),
        )

        result = VALIDATION.validate_ingest_time_parser(ingest_path)

        self.assertTrue(result["valid"], result["findings"])

    def test_workspace_parser_accepts_declared_input_stream(self):
        ingest_path = self.write_yaml(
            "Parsers/ASimAuthentication/IngestTimeParsers/"
            "ASimAuthenticationContoso.yaml",
            self.ingest_parser(
                dcr_type="Workspace",
                input_stream="Custom-Contoso_CL",
            ),
        )

        result = VALIDATION.validate_ingest_time_parser(ingest_path)

        self.assertTrue(result["valid"], result["findings"])

    def test_rejects_filter_stage_missing_from_parser_query(self):
        ingest_path = self.write_yaml(
            "Parsers/ASimAuthentication/IngestTimeParsers/"
            "ASimAuthenticationContoso.yaml",
            self.ingest_parser(
                parser_filter_query=(
                    'source\n| where EventType == "Logout"'
                )
            ),
        )

        result = VALIDATION.validate_ingest_time_parser(ingest_path)

        self.assertIn(
            "FILTER002", {finding["code"] for finding in result["findings"]}
        )

    def test_requires_filter_where_when_parser_has_where(self):
        ingest_path = self.write_yaml(
            "Parsers/ASimAuthentication/IngestTimeParsers/"
            "ASimAuthenticationContoso.yaml",
            self.ingest_parser(parser_filter_query="source"),
        )

        result = VALIDATION.validate_ingest_time_parser(ingest_path)

        self.assertIn(
            "FILTER004", {finding["code"] for finding in result["findings"]}
        )

    def test_non_pass_through_filter_requires_where(self):
        stage = '| extend FilterValue = tostring(EventType)'
        ingest_path = self.write_yaml(
            "Parsers/ASimAuthentication/IngestTimeParsers/"
            "ASimAuthenticationContoso.yaml",
            self.ingest_parser(
                parser_filter_query=f"source\n{stage}",
                parser_query=(
                    f"source\n{stage}\n"
                    '| extend EventVendor = "Contoso", '
                    'EventProduct = "Contoso"\n'
                    "| project TimeGenerated, EventType, "
                    "EventVendor, EventProduct"
                ),
            ),
        )

        result = VALIDATION.validate_ingest_time_parser(ingest_path)

        self.assertIn(
            "FILTER001", {finding["code"] for finding in result["findings"]}
        )

    def test_filter_let_is_rejected_by_source_pipeline_shape(self):
        ingest_path = self.write_yaml(
            "Parsers/ASimAuthentication/IngestTimeParsers/"
            "ASimAuthenticationContoso.yaml",
            self.ingest_parser(
                parser_filter_query=(
                    'let selectedType = "Login";\n'
                    "source\n"
                    "| where EventType == selectedType"
                ),
            ),
        )

        result = VALIDATION.validate_ingest_time_parser(ingest_path)

        self.assertIn(
            "KQL039", {finding["code"] for finding in result["findings"]}
        )

    def test_filter_stage_comparison_ignores_formatting(self):
        ingest_path = self.write_yaml(
            "Parsers/ASimAuthentication/IngestTimeParsers/"
            "ASimAuthenticationContoso.yaml",
            self.ingest_parser(
                parser_filter_query=(
                    "source\n"
                    '| where EventType=="Login"'
                ),
                parser_query=(
                    "source\n"
                    '| where EventType == "Login"\n'
                    '| extend EventVendor = "Contoso", '
                    'EventProduct = "Contoso"\n'
                    "| project TimeGenerated, EventType, "
                    "EventVendor, EventProduct"
                ),
            ),
        )

        result = VALIDATION.validate_ingest_time_parser(ingest_path)

        self.assertNotIn(
            "FILTER002", {finding["code"] for finding in result["findings"]}
        )

    def test_allows_filter_with_one_of_multiple_parser_wheres(self):
        ingest_path = self.write_yaml(
            "Parsers/ASimAuthentication/IngestTimeParsers/"
            "ASimAuthenticationContoso.yaml",
            self.ingest_parser(
                parser_query=(
                    'source\n| where EventType == "Login"\n'
                    '| where EventResult == "Success"\n'
                    '| extend EventVendor = "Contoso", '
                    'EventProduct = "Contoso"\n'
                    "| project TimeGenerated, EventType, EventResult, "
                    "EventVendor, EventProduct"
                ),
            ),
        )

        result = VALIDATION.validate_ingest_time_parser(ingest_path)

        self.assertTrue(result["valid"], result["findings"])

    def test_allows_pass_through_filter_when_parser_has_no_where(self):
        ingest_path = self.write_yaml(
            "Parsers/ASimAuthentication/IngestTimeParsers/"
            "ASimAuthenticationContoso.yaml",
            self.ingest_parser(
                parser_filter_query="source",
                parser_query=(
                    'source\n| extend EventVendor = "Contoso", '
                    'EventProduct = "Contoso"\n'
                    "| project TimeGenerated, EventType, "
                    "EventVendor, EventProduct"
                ),
            ),
        )

        result = VALIDATION.validate_ingest_time_parser(ingest_path)

        self.assertTrue(result["valid"], result["findings"])

    def test_rejects_unsupported_kql_construct(self):
        ingest_path = self.write_yaml(
            "Parsers/ASimAuthentication/IngestTimeParsers/"
            "ASimAuthenticationContoso.yaml",
            self.ingest_parser(
                parser_filter_query=(
                    "source\n"
                    '| where EventType in~ ("login") '
                    'or EventType !in~ ("logout")'
                ),
                parser_query=(
                    'source\n| where EventType == "Login"\n'
                    "| join kind=inner OtherTable on EventUid"
                )
            ),
        )

        result = VALIDATION.validate_ingest_time_parser(ingest_path)

        codes = {finding["code"] for finding in result["findings"]}
        self.assertIn("KQL031", codes)

    def test_kusto_analyzer_returns_ast_contract(self):
        analysis = analyze_kql(
            'source\n| where EventType in~ ("Login")\n'
            '// | join OtherTable on EventUid\n'
            '| extend Message = "coalesce(join)", '
            "ParsedIp = parse_ipv4(SourceIp)\n"
            "| project-away Temp*"
        )

        self.assertEqual(3, analysis["version"])
        self.assertEqual([], analysis["diagnostics"])
        self.assertEqual(
            {
                "isValid": True,
                "statementCount": 1,
                "statementType": "ExpressionStatement",
                "rootType": "NameReference",
                "rootText": "source",
                "sourceLocation": {
                    "start": 0,
                    "length": 6,
                    "line": 1,
                    "column": 1,
                    "text": "source",
                    "normalizedText": "source",
                },
            },
            analysis["sourcePipeline"],
        )
        self.assertEqual("source", analysis["pipeline"]["rootText"])
        self.assertEqual(
            [
                "FilterOperator",
                "ExtendOperator",
                "ProjectAwayOperator",
            ],
            [
                operator["type"]
                for operator in analysis["pipeline"]["operators"]
            ],
        )
        self.assertEqual(
            ["parse_ipv4"],
            [function["name"] for function in analysis["functions"]],
        )
        self.assertEqual(
            ["InCsExpression", "WildcardedName"],
            [construct["kind"] for construct in analysis["constructs"]],
        )
        self.assertEqual(
            ["Message", "ParsedIp"],
            [assignment["name"] for assignment in analysis["assignments"]],
        )
        self.assertEqual(
            ["source"],
            [
                reference["name"]
                for reference in analysis["sourceReferences"]
            ],
        )

    def test_kusto_analyzer_validates_exact_source_pipeline_shape(self):
        cases = {
            "source": (True, None),
            "source | where (": (False, "diagnostics"),
            "let selected = true; source": (
                False,
                "statementCount",
            ),
            "let selected = source": (False, "statementType"),
            "Source | project EventType": (False, "root"),
            "(source | project EventType)": (False, "root"),
            "print Value=1": (False, "root"),
            "datatable(Value:int)[1]": (False, "root"),
        }

        for query, expected in cases.items():
            with self.subTest(query=query):
                source_pipeline = analyze_kql(query)["sourcePipeline"]
                self.assertEqual(expected[0], source_pipeline["isValid"])
                self.assertEqual(expected[1], source_pipeline.get("failure"))

    def test_ast_policy_mapping_covers_existing_kql_rules(self):
        query = """\
let invoke_test = source | invoke f();
let lookup_test = source | lookup Other on Key;
let union_test = union source, Other;
let distinct_test = source | distinct Key;
let materialize_test = materialize(source | project Key);
let reorder_test = source | project-reorder Key;
let parse_kv_test = source | parse-kv Data as (Key:string);
let parse_where_test = source | parse-where Data with Key ":" Value;
let mv_apply_test = source | mv-apply Value on (project Value);
let mv_expand_test = source | mv-expand Value;
let summarize_test = source | summarize count() by Key;
let join_test = source | join Other on Key;
let keep_test = source | project-keep Key*;
let external_test =
    externaldata(Key:string)["https://example.test/data"];
source
| extend Asim = _ASIM_Test(Key),
    DynamicValue = dynamic({"a":1}),
    Coalesced = coalesce(A, B),
    Existing = column_ifexists("A", ""),
    Unix = unixtime_seconds_todatetime(Seconds),
    Packed = bag_pack("a", A),
    Replaced = replace_string(A, "b", "c"),
    ArrayIndex = array_index_of(Values, A),
    ArraySlice = array_slice(Values, 0, 1),
    Trimmed = trim("a", A),
    Url = parse_url(A),
    Agent = parse_user_agent(A, "browser"),
    Aggregated = make_set(A),
    Merged = bag_merge(A, B),
    Hex = tohex(A),
    Ip = ipv6_is_match(A, B),
    Decoded = url_decode(A),
    Scalar = toscalar(Other | count)
| where Text has_any ("a")
    and Text has_all ("b")
    and Text in~ ("a")
    and Number between (1 .. 2)
| project-away Temp*
"""
        analysis = analyze_kql(query)
        findings = STATIC_VALIDATION._scan_kql(
            analysis,
            "ParserQuery",
        )

        self.assertEqual([], analysis["diagnostics"])
        self.assertEqual(
            sorted(finding.code for finding in findings),
            [finding.code for finding in findings],
        )
        self.assertEqual(
            {
                "KQL002",
                "KQL003",
                "KQL004",
                "KQL006",
                "KQL007",
                "KQL027",
                "KQL028",
                "KQL029",
                "KQL031",
                "KQL035",
                "KQL037",
                "KQL038",
            },
            {
                finding.code
                for finding in findings
            },
        )

    def test_reports_official_kusto_syntax_diagnostics(self):
        ingest_path = self.write_yaml(
            "Parsers/ASimAuthentication/IngestTimeParsers/"
            "ASimAuthenticationContoso.yaml",
            self.ingest_parser(
                parser_query=(
                    'source\n| extend EventVendor = "Contoso", '
                    'EventProduct = "Contoso"\n'
                    "| where ("
                )
            ),
        )

        result = VALIDATION.validate_ingest_time_parser(ingest_path)

        syntax_findings = [
            finding
            for finding in result["findings"]
            if finding["code"] == "KQL001"
        ]
        self.assertGreaterEqual(len(syntax_findings), 1)
        self.assertTrue(
            all("KS" in finding["message"] for finding in syntax_findings)
        )

    def test_reports_kusto_analyzer_failure(self):
        ingest_path = self.write_yaml(
            "Parsers/ASimAuthentication/IngestTimeParsers/"
            "ASimAuthenticationContoso.yaml",
            self.ingest_parser(),
        )

        with unittest.mock.patch.object(
            STATIC_VALIDATION,
            "analyze_kql",
            side_effect=KustoAnalyzerError("test failure"),
        ):
            result = VALIDATION.validate_ingest_time_parser(ingest_path)

        analyzer_findings = [
            finding
            for finding in result["findings"]
            if finding["code"] == "KQL000"
        ]
        self.assertEqual(2, len(analyzer_findings), result["findings"])
        self.assertTrue(
            all(
                "test failure" in finding["message"]
                for finding in analyzer_findings
            )
        )

    def test_allows_supported_case_insensitive_string_operators(self):
        ingest_path = self.write_yaml(
            "Parsers/ASimAuthentication/IngestTimeParsers/"
            "ASimAuthenticationContoso.yaml",
            self.ingest_parser(
                parser_filter_query=(
                    "source\n"
                    '| where EventType =~ "login" '
                    'or EventType !~ "logout"'
                ),
                parser_query=(
                    "source\n"
                    '| where EventType =~ "login" '
                    'or EventType !~ "logout"\n'
                    '| extend EventVendor = "Contoso", '
                    'EventProduct = "Contoso"\n'
                    "| project TimeGenerated, EventType, "
                    "EventVendor, EventProduct"
                )
            ),
        )

        result = VALIDATION.validate_ingest_time_parser(ingest_path)

        self.assertNotIn(
            "KQL016",
            {finding["code"] for finding in result["findings"]},
        )
        self.assertTrue(result["valid"], result["findings"])

    def test_defers_case_insensitive_membership_to_live_dcr(self):
        ingest_path = self.write_yaml(
            "Parsers/ASimAuthentication/IngestTimeParsers/"
            "ASimAuthenticationContoso.yaml",
            self.ingest_parser(
                parser_filter_query=(
                    "source\n"
                    '| where EventType in~ ("login") '
                    'or EventType !in~ ("logout")'
                ),
                parser_query=(
                    "source\n"
                    '| where EventType in~ ("login") '
                    'or EventType !in~ ("logout")\n'
                    '| extend EventVendor = "Contoso", '
                    'EventProduct = "Contoso"\n'
                    "| project TimeGenerated, EventType, "
                    "EventVendor, EventProduct"
                )
            ),
        )

        result = VALIDATION.validate_ingest_time_parser(ingest_path)

        self.assertTrue(result["valid"], result["findings"])

    def test_invalid_double_equals_tilde_uses_syntax_diagnostic(self):
        ingest_path = self.write_yaml(
            "Parsers/ASimAuthentication/IngestTimeParsers/"
            "ASimAuthenticationContoso.yaml",
            self.ingest_parser(
                parser_query=(
                    "source\n"
                    '| where EventType ==~ "login"\n'
                    '| extend EventVendor = "Contoso", '
                    'EventProduct = "Contoso"\n'
                    "| project TimeGenerated, EventType, "
                    "EventVendor, EventProduct"
                )
            ),
        )

        result = VALIDATION.validate_ingest_time_parser(ingest_path)

        codes = {finding["code"] for finding in result["findings"]}
        self.assertIn("KQL001", codes)
        self.assertNotIn("KQL016", codes)

    def test_limits_wildcard_rule_to_projection_operators(self):
        analysis = analyze_kql("union source, Other*")

        codes = {
            finding.code
            for finding in STATIC_VALIDATION._scan_kql(
                analysis,
                "ParserQuery",
            )
        }
        self.assertIn("KQL006", codes)
        self.assertNotIn("KQL037", codes)

    def test_allows_newly_supported_dcr_constructs(self):
        ingest_path = self.write_yaml(
            "Parsers/ASimAuthentication/IngestTimeParsers/"
            "ASimAuthenticationContoso.yaml",
            self.ingest_parser(
                parser_filter_query=(
                    "source\n"
                    "| parse-kv Data as (ParsedKey:string)\n"
                    '| where ParsedKey == "allow"'
                ),
                parser_query=(
                    "source\n"
                    "| parse-kv Data as (ParsedKey:string)\n"
                    '| where ParsedKey == "allow"\n'
                    "| extend MergedBag = bag_merge(BagOne, BagTwo),\n"
                    "    HexValue = tohex(Number),\n"
                    "    ParsedIpv4 = parse_ipv4(SourceIp),\n"
                    "    ParsedIpv6 = parse_ipv6(SourceIp),\n"
                    '    Ipv4Match = ipv4_is_match(SourceIp, "10.0.0.0/8"),\n'
                    '    Ipv4InRange = ipv4_is_in_range(SourceIp, "10.0.0.0/8"),\n'
                    "    Ipv4IsPrivate = ipv4_is_private(SourceIp),\n"
                    '    EventVendor = "Contoso", EventProduct = "Contoso"\n'
                    "| project TimeGenerated, EventType, ParsedKey, "
                    "MergedBag, HexValue, ParsedIpv4, ParsedIpv6, "
                    "Ipv4Match, Ipv4InRange, Ipv4IsPrivate, EventVendor, "
                    "EventProduct"
                )
            ),
        )

        result = VALIDATION.validate_ingest_time_parser(ingest_path)

        self.assertTrue(result["valid"], result["findings"])

    def test_defers_parser_operator_support_to_live_dcr(self):
        ingest_path = self.write_yaml(
            "Parsers/ASimAuthentication/IngestTimeParsers/"
            "ASimAuthenticationContoso.yaml",
            self.ingest_parser(
                parser_filter_query="source",
                parser_query=(
                    "source\n"
                    '| parse-where Data with ParsedKey ":" ParsedValue\n'
                    '| extend EventVendor = "Contoso", '
                    'EventProduct = "Contoso"\n'
                    "| project-reorder TimeGenerated, EventType\n"
                    "| project-keep TimeGenerated, EventType, EventVendor, "
                    "EventProduct"
                )
            ),
        )

        result = VALIDATION.validate_ingest_time_parser(ingest_path)

        self.assertTrue(result["valid"], result["findings"])

    def test_defers_other_ip_functions_to_live_dcr(self):
        ingest_path = self.write_yaml(
            "Parsers/ASimAuthentication/IngestTimeParsers/"
            "ASimAuthenticationContoso.yaml",
            self.ingest_parser(
                parser_query=(
                    'source\n| where EventType == "Login"\n'
                    '| extend Ipv6Match = ipv6_is_match(SourceIp, "::1"),\n'
                    "    NetmaskSuffix = ipv4_netmask_suffix(SourceIp),\n"
                    '    EventVendor = "Contoso", EventProduct = "Contoso"\n'
                    "| project TimeGenerated, EventType, Ipv6Match, "
                    "NetmaskSuffix, EventVendor, EventProduct"
                )
            ),
        )

        result = VALIDATION.validate_ingest_time_parser(ingest_path)

        self.assertTrue(result["valid"], result["findings"])

    def test_rejects_scalar_let_before_source_pipeline(self):
        query = (
            "let selectedType = 'Login';\n"
            "source\n"
            "| where EventType == selectedType\n"
            '| extend EventVendor = "Contoso", '
            'EventProduct = "Contoso"\n'
            "| project TimeGenerated, EventType, "
            "EventVendor, EventProduct"
        )
        ingest_path = self.write_yaml(
            "Parsers/ASimAuthentication/IngestTimeParsers/"
            "ASimAuthenticationContoso.yaml",
            self.ingest_parser(
                parser_filter_query=(
                    "let selectedType = 'Login';\n"
                    "source\n"
                    "| where EventType == selectedType"
                ),
                parser_query=query,
            ),
        )

        result = VALIDATION.validate_ingest_time_parser(ingest_path)

        self.assertFalse(result["valid"])
        self.assertEqual(
            2,
            sum(
                finding["code"] == "KQL039"
                for finding in result["findings"]
            ),
            result["findings"],
        )

    def test_defers_function_support_to_live_dcr(self):
        ingest_path = self.write_yaml(
            "Parsers/ASimAuthentication/IngestTimeParsers/"
            "ASimAuthenticationContoso.yaml",
            self.ingest_parser(
                parser_query=(
                    'source\n| where EventType == "Login"\n'
                    "| extend Result = coalesce\n"
                    "    (PrimaryResult, SecondaryResult)\n"
                    '| extend EventVendor = "Contoso", '
                    'EventProduct = "Contoso"\n'
                    "| project TimeGenerated, EventType, Result, "
                    "EventVendor, EventProduct"
                )
            ),
        )

        result = VALIDATION.validate_ingest_time_parser(ingest_path)

        self.assertTrue(result["valid"], result["findings"])

    def test_filter_query_keeps_its_stricter_operator_contract(self):
        filter_query = (
            "source\n"
            "| project EventType\n"
            '| where EventType == "Login"'
        )
        ingest_path = self.write_yaml(
            "Parsers/ASimAuthentication/IngestTimeParsers/"
            "ASimAuthenticationContoso.yaml",
            self.ingest_parser(
                parser_filter_query=filter_query,
                parser_query=(
                    f"{filter_query}\n"
                    '| extend EventVendor = "Contoso", '
                    'EventProduct = "Contoso"'
                ),
            ),
        )

        result = VALIDATION.validate_ingest_time_parser(ingest_path)

        self.assertIn(
            "KQL041",
            {
                finding["code"]
                for finding in result["findings"]
                if finding["field"] == "ParserFilterQuery"
            },
        )

    def test_rejects_second_external_table_statement(self):
        ingest_path = self.write_yaml(
            "Parsers/ASimAuthentication/IngestTimeParsers/"
            "ASimAuthenticationContoso.yaml",
            self.ingest_parser(
                parser_query=(
                    "source | project TimeGenerated, EventType;\n"
                    "OtherTable | project TimeGenerated, EventType"
                )
            ),
        )

        result = VALIDATION.validate_ingest_time_parser(ingest_path)

        codes = {finding["code"] for finding in result["findings"]}
        self.assertIn("KQL039", codes)

    def test_rejects_external_table_in_let_binding(self):
        ingest_path = self.write_yaml(
            "Parsers/ASimAuthentication/IngestTimeParsers/"
            "ASimAuthenticationContoso.yaml",
            self.ingest_parser(
                parser_query=(
                    "let enriched = OtherTable | project EventUid;\n"
                    "source | project TimeGenerated, EventType"
                )
            ),
        )

        result = VALIDATION.validate_ingest_time_parser(ingest_path)

        self.assertIn(
            "KQL039", {finding["code"] for finding in result["findings"]}
        )

    def test_rejects_non_lowercase_source_root(self):
        ingest_path = self.write_yaml(
            "Parsers/ASimAuthentication/IngestTimeParsers/"
            "ASimAuthenticationContoso.yaml",
            self.ingest_parser(
                parser_filter_query=(
                    'Source | where EventType == "Login"'
                ),
                parser_query=(
                    'Source | where EventType == "Login"\n'
                    '| extend EventVendor = "Contoso", '
                    'EventProduct = "Contoso"\n'
                    "| project TimeGenerated, EventType, "
                    "EventVendor, EventProduct"
                ),
            ),
        )

        result = VALIDATION.validate_ingest_time_parser(ingest_path)

        self.assertEqual(
            2,
            sum(
                finding["code"] == "KQL039"
                for finding in result["findings"]
            ),
            result["findings"],
        )

    def test_ignores_unsupported_words_in_strings_and_comments(self):
        ingest_path = self.write_yaml(
            "Parsers/ASimAuthentication/IngestTimeParsers/"
            "ASimAuthenticationContoso.yaml",
            self.ingest_parser(
                parser_query=(
                    'source\n| where EventType == "Login"\n'
                    '// | join OtherTable on EventUid\n'
                    '| extend Message = "coalesce(join)"\n'
                    '| extend EventVendor = "Contoso", '
                    'EventProduct = "Contoso"\n'
                    "| project TimeGenerated, EventType, Message, "
                    "EventVendor, EventProduct"
                )
            ),
        )

        result = VALIDATION.validate_ingest_time_parser(ingest_path)

        self.assertTrue(result["valid"], result["findings"])

    def test_rejects_duplicate_yaml_key(self):
        path = (
            self.repo_root
            / "Parsers/ASimAuthentication/IngestTimeParsers/"
            "ASimAuthenticationContoso.yaml"
        )
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(
            "ParserName: ASimAuthenticationContoso\n"
            "ParserName: ASimAuthenticationDuplicate\n",
            encoding="utf-8",
        )

        result = VALIDATION.validate_ingest_time_parser(path)

        self.assertFalse(result["valid"])
        self.assertIn(
            "Duplicate YAML key", result["findings"][0]["message"]
        )

    def test_rejects_yaml_over_size_limit(self):
        path = (
            self.repo_root
            / "Parsers/ASimAuthentication/IngestTimeParsers/"
            "ASimAuthenticationContoso.yaml"
        )
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("ParserName: oversized\n", encoding="utf-8")

        with unittest.mock.patch.object(
            VALIDATION.parser_common, "MAX_YAML_BYTES", 5
        ):
            result = VALIDATION.validate_ingest_time_parser(path)

        self.assertFalse(result["valid"])
        self.assertIn(
            "YAML limit", result["findings"][0]["message"]
        )


class CurrentRepositoryIngestionParserTests(unittest.TestCase):
    def test_websession_itp_falls_back_from_empty_dst_bytes(self):
        repo_root = Path(__file__).resolve().parents[5]
        query = VALIDATION.load_yaml_file(
            repo_root
            / "Parsers/ASimWebSession/IngestTimeParsers/"
            "ASimWebSessionSalesforceServiceCloud.yaml"
        )["ParserQuery"]

        self.assertIn(
            "DstBytes = tolong(iif(isnotempty(tostring(DstBytes)), "
            "DstBytes, ResponseSize))",
            query,
        )

    def test_authentication_pairs_emit_current_schema_version(self):
        repo_root = Path(__file__).resolve().parents[5]
        paths = (
            "Parsers/ASimAuthentication/Parsers/"
            "ASimAuthenticationOktaV2.yaml",
            "Parsers/ASimAuthentication/Parsers/"
            "vimAuthenticationOktaV2.yaml",
            "Parsers/ASimAuthentication/IngestTimeParsers/"
            "ASimAuthenticationOktaV2.yaml",
            "Parsers/ASimAuthentication/Parsers/"
            "ASimAuthenticationSalesforceSC.yaml",
            "Parsers/ASimAuthentication/Parsers/"
            "vimAuthenticationSalesforceSC.yaml",
            "Parsers/ASimAuthentication/IngestTimeParsers/"
            "ASimAuthenticationSalesforceServiceCloud.yaml",
        )
        for relative_path in paths:
            with self.subTest(path=relative_path):
                document = VALIDATION.load_yaml_file(
                    repo_root / relative_path
                )
                expected = document["Normalization"]["Version"]
                assignments = [
                    assignment["stringValue"]
                    for assignment in analyze_kql(
                        document["ParserQuery"]
                    )["assignments"]
                    if assignment["name"] == "EventSchemaVersion"
                ]
                self.assertTrue(assignments)
                self.assertEqual(
                    {expected},
                    set(assignments),
                )

    def test_current_ingestion_parsers_validate_and_pair(self):
        repo_root = Path(__file__).resolve().parents[5]
        pairs = {
            "Parsers/ASimAlertEvent/IngestTimeParsers/"
            "ASimAlertEventAWSGuardDuty.yaml":
                "Parsers/ASimAlertEvent/Parsers/"
                "ASimAlertEventAWSGuardDuty.yaml",
            "Parsers/ASimAlertEvent/IngestTimeParsers/"
            "ASimAlertEventCrowdStrikeFalcon.yaml":
                "Parsers/ASimAlertEvent/Parsers/"
                "ASimAlertEventCrowdStrikeFalcon.yaml",
            "Parsers/ASimAuthentication/IngestTimeParsers/"
            "ASimAuthenticationOktaV2.yaml":
                "Parsers/ASimAuthentication/Parsers/"
                "ASimAuthenticationOktaV2.yaml",
            "Parsers/ASimAuthentication/IngestTimeParsers/"
            "ASimAuthenticationSalesforceServiceCloud.yaml":
                "Parsers/ASimAuthentication/Parsers/"
                "ASimAuthenticationSalesforceSC.yaml",
            "Parsers/ASimNetworkSession/IngestTimeParsers/"
            "ASimNetworkSessionAWSVPC.yaml":
                "Parsers/ASimNetworkSession/Parsers/"
                "ASimNetworkSessionAWSVPC.yaml",
            "Parsers/ASimWebSession/IngestTimeParsers/"
            "ASimWebSessionSalesforceServiceCloud.yaml":
                "Parsers/ASimWebSession/Parsers/"
                "ASimWebSessionSalesforceServiceCloud.yaml",
        }
        manifest = VALIDATION.build_validation_manifest(
            repo_root, list(pairs.keys())
        )
        self.assertEqual(6, len(manifest["targets"]))
        manifest_pairs = {
            target["ingestTimeParserPath"]: target["queryTimeParserPath"]
            for target in manifest["targets"]
        }
        self.assertEqual(pairs, manifest_pairs)
        targets_by_path = {
            target["ingestTimeParserPath"]: target
            for target in manifest["targets"]
        }

        for ingest_path, query_path in pairs.items():
            result = VALIDATION.validate_ingest_time_parser(
                repo_root / ingest_path,
                query_time_path=repo_root / query_path,
            )
            self.assertTrue(
                result["valid"],
                f"{ingest_path}: {result['findings']}",
            )
            self.assertEqual(
                "resolved",
                targets_by_path[ingest_path]["fixtureStatus"],
            )


if __name__ == "__main__":
    unittest.main()
