import importlib.util
import json
import sys
import tempfile
import unittest
from pathlib import Path

import yaml


MODULE_PATH = Path(__file__).resolve().parents[1] / "asim_ingest_time_validation.py"
SPEC = importlib.util.spec_from_file_location(
    "asim_ingest_time_validation", MODULE_PATH
)
VALIDATION = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = VALIDATION
SPEC.loader.exec_module(VALIDATION)


class AsimIngestTimeValidationTests(unittest.TestCase):
    def setUp(self):
        self.temp_directory = tempfile.TemporaryDirectory()
        self.repo_root = Path(self.temp_directory.name)
        self.write_dcr_output_stream("Custom-Contoso_CL")

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

    def write_dcr_output_stream(self, output_stream):
        safe_name = output_stream.replace("-", "_")
        path = (
            self.repo_root
            / "Solutions/Test Solution/Data Connectors/"
            f"{safe_name}_DCR.json"
        )
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(
            json.dumps(
                {
                    "name": f"{safe_name}DCR",
                    "type": "Microsoft.Insights/dataCollectionRules",
                    "properties": {
                        "dataFlows": [
                            {
                                "streams": ["Custom-Input"],
                                "destinations": ["workspace"],
                                "outputStream": output_stream,
                            }
                        ]
                    },
                }
            ),
            encoding="utf-8",
        )
        return path

    def query_parser(
        self,
        parser_name="ASimAuthenticationContoso",
        product="Contoso",
        schema="Authentication",
        schema_version="1.0.0",
        source_table="Contoso_CL",
    ):
        parser_suffix = parser_name.removeprefix(f"ASim{schema}")
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
                {"Name": "disabled", "Type": "bool", "Default": False}
            ],
            "ParserQuery": (
                "let parser=(disabled:bool=false) {\n"
                f"  {source_table}\n"
                "  | where not(disabled)\n"
                '  | where EventType == "Login"\n'
                "  | project TimeGenerated, EventType\n"
                "};\n"
                "parser(disabled=false)"
            ),
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
        parser_query=(
            'source\n| where EventType == "Login"\n'
            "| project TimeGenerated, EventType"
        ),
        dcr_type="Standard",
        input_stream="Custom-Contoso_CL",
    ):
        return {
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
            "InputStream": input_stream,
            "SourceRawTable": source_table,
            "TargetASIMTable": target_table,
            "ParserFilterQuery": parser_filter_query,
            "ParserQuery": parser_query,
            "Change": {
                "Date": "2026-10-14",
                "Description": "Initial ingestion-time parser.",
            },
        }

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

    def test_query_time_parser_without_ingestion_counterpart_is_query_only(self):
        query_path = (
            "Parsers/ASimAuthentication/Parsers/"
            "ASimAuthenticationContoso.yaml"
        )
        self.write_yaml(query_path, self.query_parser())

        target = VALIDATION.build_validation_manifest(
            self.repo_root, [query_path]
        )["targets"][0]

        self.assertEqual("query-only", target["validationKind"])
        self.assertEqual("unpaired", target["pairStatus"])
        self.assertIsNone(target["ingestTimeParserPath"])

    def test_invalid_changed_query_parser_is_preserved_in_manifest(self):
        query_path = (
            "Parsers/ASimAuthentication/Parsers/"
            "ASimAuthenticationBroken.yaml"
        )
        path = self.repo_root / query_path
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("ParserName: Broken\nParserName: Duplicate\n")

        target = VALIDATION.build_validation_manifest(
            self.repo_root, [query_path]
        )["targets"][0]

        self.assertEqual("invalid", target["pairStatus"])
        self.assertEqual(query_path, target["queryTimeParserPath"])
        self.assertTrue(target["discoveryErrors"])

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
        self.assertTrue(result["connectorEvidence"])

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

    def test_rejects_standard_parser_without_input_stream(self):
        ingest_path = self.write_yaml(
            "Parsers/ASimAuthentication/IngestTimeParsers/"
            "ASimAuthenticationContoso.yaml",
            self.ingest_parser(input_stream="none"),
        )

        result = VALIDATION.validate_ingest_time_parser(ingest_path)

        self.assertIn(
            "META008", {finding["code"] for finding in result["findings"]}
        )

    def test_rejects_syntactically_valid_but_incorrect_input_stream(self):
        ingest_path = self.write_yaml(
            "Parsers/ASimAuthentication/IngestTimeParsers/"
            "ASimAuthenticationContoso.yaml",
            self.ingest_parser(input_stream="Custom-Bogus_CL"),
        )

        result = VALIDATION.validate_ingest_time_parser(ingest_path)

        codes = {finding["code"] for finding in result["findings"]}
        self.assertIn("SOURCE001", codes)
        self.assertIn("SOURCE002", codes)

    def test_workspace_parser_accepts_none_without_dcr_evidence(self):
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

    def test_workspace_parser_rejects_contradictory_dcr_evidence(self):
        ingest_path = self.write_yaml(
            "Parsers/ASimAuthentication/IngestTimeParsers/"
            "ASimAuthenticationContoso.yaml",
            self.ingest_parser(dcr_type="Workspace", input_stream="none"),
        )

        result = VALIDATION.validate_ingest_time_parser(ingest_path)

        self.assertIn(
            "SOURCE004", {finding["code"] for finding in result["findings"]}
        )

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

    def test_rejects_unsupported_kql_construct(self):
        ingest_path = self.write_yaml(
            "Parsers/ASimAuthentication/IngestTimeParsers/"
            "ASimAuthenticationContoso.yaml",
            self.ingest_parser(
                parser_query=(
                    'source\n| where EventType == "Login"\n'
                    "| join kind=inner OtherTable on EventUid"
                )
            ),
        )

        result = VALIDATION.validate_ingest_time_parser(ingest_path)

        codes = {finding["code"] for finding in result["findings"]}
        self.assertIn("KQL031", codes)
        self.assertIn("KQL041", codes)

    def test_allows_supported_scalar_let_statement(self):
        query = (
            "let selectedType = 'Login';\n"
            "source\n"
            "| where EventType == selectedType\n"
            "| project TimeGenerated, EventType"
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

        self.assertTrue(result["valid"], result["findings"])

    def test_detects_multiline_unsupported_function(self):
        ingest_path = self.write_yaml(
            "Parsers/ASimAuthentication/IngestTimeParsers/"
            "ASimAuthenticationContoso.yaml",
            self.ingest_parser(
                parser_query=(
                    'source\n| where EventType == "Login"\n'
                    "| extend Result = coalesce\n"
                    "    (PrimaryResult, SecondaryResult)\n"
                    "| project TimeGenerated, EventType, Result"
                )
            ),
        )

        result = VALIDATION.validate_ingest_time_parser(ingest_path)

        self.assertIn(
            "KQL013", {finding["code"] for finding in result["findings"]}
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
        self.assertIn("KQL042", codes)

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
            "KQL043", {finding["code"] for finding in result["findings"]}
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
                    "| project TimeGenerated, EventType, Message"
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


class CurrentRepositoryIngestionParserTests(unittest.TestCase):
    def test_current_ingestion_parsers_validate_and_pair(self):
        repo_root = Path(__file__).resolve().parents[4]
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

        for ingest_path, query_path in pairs.items():
            result = VALIDATION.validate_ingest_time_parser(
                repo_root / ingest_path,
                query_time_path=repo_root / query_path,
            )
            self.assertTrue(
                result["valid"],
                f"{ingest_path}: {result['findings']}",
            )


if __name__ == "__main__":
    unittest.main()
