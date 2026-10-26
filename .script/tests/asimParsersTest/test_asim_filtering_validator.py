import ast
import importlib.util
import os
import re
import json
import unittest
from types import SimpleNamespace
from unittest.mock import Mock, patch


SCRIPT_PATH = os.path.join(os.path.dirname(__file__), "ASimFilteringTest.py")
SPEC = importlib.util.spec_from_file_location("asim_filtering_validator", SCRIPT_PATH)
validator = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(validator)

EXPECTED_EMAIL_EVENT_PARAMETERS = {
    "disabled": "",
    "starttime": "EventStartTime",
    "endtime": "EventEndTime",
    "ipaddr_has_any_prefix": "IpAddr",
    "emailfromaddress_has_any": "EmailFromAddress",
    "emailrecipient_has_any": (
        "EmailToRecipients",
        "EmailCCRecipients",
        "EmailBCCRecipients",
    ),
    "emailsubject_has_any": "EmailSubject",
    "emaildirection_in": "EmailDirection",
    "emaildeliverylocation_in": "EmailDeliveryLocation",
    "eventresult": "EventResult",
    "pack": "",
}


def response(rows):
    return SimpleNamespace(tables=[SimpleNamespace(rows=rows)])


def filtered_rows_for_query(query, parameter_name, rows):
    parameter_match = re.search(rf"{parameter_name}=dynamic\(\[([^\]]*)\]\)", query)
    if parameter_match is None:
        return rows
    values = re.findall(r"@'([^']*)'", parameter_match.group(1))
    if validator.DUMMY_VALUE.strip("'") in query:
        return []
    matches = []
    for row in rows:
        output_value = str(row[0]).casefold()
        normalized_values = [value.casefold() for value in values]
        if parameter_name.endswith("_has_any_prefix"):
            matched = any(output_value.startswith(value) for value in normalized_values)
        elif parameter_name.endswith("_has_any"):
            matched = any(value in output_value for value in normalized_values)
        else:
            matched = output_value in normalized_values
        if matched:
            matches.append(row)
    return matches


class EmailEventFilteringValidatorTests(unittest.TestCase):
    def make_test(self, query_responses):
        test = validator.FilteringTest()
        test.send_query = Mock(side_effect=query_responses)
        return test

    def test_email_event_catalog_maps_all_standard_parameters(self):
        self.assertEqual(
            validator.all_schemas_parameters["EmailEvent"],
            EXPECTED_EMAIL_EVENT_PARAMETERS,
        )

    def test_legacy_asim_tester_catalog_matches_shared_validator(self):
        legacy_path = os.path.join(
            os.path.dirname(__file__),
            "..",
            "..",
            "..",
            "ASIM",
            "dev",
            "ASimTester",
            "filteringTest",
            "ASimFilteringTest.py",
        )
        with open(legacy_path, encoding="utf-8") as legacy_file:
            syntax_tree = ast.parse(legacy_file.read())
        mapping_assignment = next(
            node
            for node in syntax_tree.body
            if isinstance(node, ast.Assign)
            and any(
                isinstance(target, ast.Name) and target.id == "all_schemas_parameters"
                for target in node.targets
            )
        )
        legacy_mapping = ast.literal_eval(mapping_assignment.value)
        self.assertEqual(legacy_mapping["EmailEvent"], EXPECTED_EMAIL_EVENT_PARAMETERS)

    def test_email_event_catalog_covers_the_unifier_parser_parameters(self):
        parser_path = os.path.join(
            os.path.dirname(__file__),
            "..",
            "..",
            "..",
            "Parsers",
            "ASimEmailEvent",
            "Parsers",
            "imEmailEvent.yaml",
        )
        parser = validator.get_parser(parser_path)
        self.assertLessEqual(
            {param["Name"] for param in parser["ParserParams"]},
            set(validator.all_schemas_parameters["EmailEvent"]),
        )
        self.assertIn("disabled", validator.all_schemas_parameters["EmailEvent"])

    def test_email_event_defaults_and_pack_control_preserve_rows(self):
        test = self.make_test(
            [
                response([[7]]),
                response([[7]]),
                response([[7]]),
                response([[7]]),
            ]
        )
        test.email_event_default_test(
            [
                {"Name": "ipaddr_has_any_prefix", "Type": "dynamic", "Default": "dynamic([])"},
                {"Name": "eventresult", "Type": "string", "Default": "*"},
            ],
            "let query=(ipaddr_has_any_prefix:dynamic=dynamic([]),eventresult:string='*') { Logs };\n",
        )
        test.pack_test("let query(pack:bool=false) { Logs };\n")
        self.assertIn("query(ipaddr_has_any_prefix=dynamic([]), eventresult='*')", test.send_query.call_args_list[1].args[0])
        self.assertIn("query(pack=true)", test.send_query.call_args_list[3].args[0])

    def test_existing_schema_mappings_and_disabled_control_remain_supported(self):
        self.assertEqual(
            validator.all_schemas_parameters["Authentication"]["eventtype_in"],
            "EventType",
        )
        self.assertEqual(
            validator.all_schemas_parameters["NetworkSession"]["srcipaddr_has_any_prefix"],
            "SrcIpAddr",
        )
        test = self.make_test([response([[0]]), response([[5]])])
        test.disabled_test("let query(disabled:bool=false) { Logs };\n")
        self.assertIn("query(disabled=true)", test.send_query.call_args_list[0].args[0])
        self.assertIn("query(disabled=false)", test.send_query.call_args_list[1].args[0])

    def test_datetime_filter_preserves_original_timegenerated_behavior(self):
        test = self.make_test(
            [
                response([["2026-10-21T00:00:00Z"], ["2026-10-22T00:00:00Z"]]),
                response([["2026-10-21T12:00:00Z", 2, 86400000000]]),
                response([["2026-10-22T00:00:00Z"]]),
            ]
        )
        test.datetime_test(
            {"Name": "starttime", "Type": "datetime"},
            "let query(starttime:datetime=datetime(null)) { Logs };\n",
            "EventStartTime",
        )
        query_text = "\n".join(call.args[0] for call in test.send_query.call_args_list)
        self.assertIn("max(TimeGenerated)", query_text)
        self.assertIn("project TimeGenerated", query_text)
        self.assertNotIn("EventStartTime", query_text)
        self.assertIn("query(starttime=datetime(2026-10-21T12:00:00Z))", query_text)
        self.assertEqual(test.send_query.call_count, 3)

    def test_sparse_maillog_filter_checks_match_and_absent_values(self):
        test = self.make_test(
            [
                response([["Delivered", 4]]),
                response([["Delivered", 4]]),
                response([]),
            ]
        )
        test.scalar_test(
            {"Name": "eventresult", "Type": "string"},
            "let query(eventresult:string='*') { MailLog };\n",
            "EventResult",
        )
        self.assertIn("query(eventresult='Delivered')", test.send_query.call_args_list[1].args[0])
        self.assertIn("!not_REAL_vAlUe", test.send_query.call_args_list[2].args[0])

    def test_sparse_dynamic_filter_checks_match_empty_and_absent_values(self):
        test = self.make_test(
            [
                response([["Inbound", 2]]),
                response([[2]]),
                response([[2]]),
                response([["Inbound", 2]]),
                response([]),
            ]
        )
        test.dynamic_test(
            {"Name": "emaildirection_in", "Type": "dynamic", "Default": "dynamic([])"},
            "let query(emaildirection_in:dynamic=dynamic([])) { MailLog };\n",
            "EmailDirection",
        )
        self.assertIn("emaildirection_in=dynamic([])", test.send_query.call_args_list[2].args[0])
        self.assertIn("emaildirection_in=dynamic", test.send_query.call_args_list[4].args[0])

    def test_message_sender_and_subject_has_any_filters(self):
        cases = [
            ("emailfromaddress_has_any", "EmailFromAddress", "alice@alpha.test", "bob@beta.test"),
            ("emailsubject_has_any", "EmailSubject", "Invoice 1042", "Reset access"),
        ]
        for parameter_name, column_name, first_value, second_value in cases:
            with self.subTest(parameter=parameter_name):
                baseline_rows = [[first_value, 2], [second_value, 1]]
                test = self.make_test([])

                def send_query(query):
                    if "| count" in query:
                        return response([[3]])
                    if f"query() | summarize count() by {column_name}" in query:
                        return response(baseline_rows)
                    return response(filtered_rows_for_query(query, parameter_name, baseline_rows))

                test.send_query.side_effect = send_query
                test.dynamic_test(
                    {"Name": parameter_name, "Type": "dynamic", "Default": "dynamic([])"},
                    f"let query({parameter_name}:dynamic=dynamic([])) {{ Message }};\n",
                    column_name,
                )
                self.assertTrue(
                    any(f"{parameter_name}=dynamic([" in call.args[0] for call in test.send_query.call_args_list)
                )

    def test_ip_prefix_filter_uses_distinct_network_prefixes(self):
        test = self.make_test([])

        def send_query(query):
            if "| count" in query:
                return response([[4]])
            if "query() | summarize count() by IpAddr" in query:
                rows = [["192.0.2.10", 2], ["198.51.100.3", 2]]
                return response(rows)
            return response(
                filtered_rows_for_query(
                    query,
                    "ipaddr_has_any_prefix",
                    [["192.0.2.10", 2], ["198.51.100.3", 2]],
                )
            )

        test.send_query.side_effect = send_query
        test.dynamic_test(
            {"Name": "ipaddr_has_any_prefix", "Type": "dynamic", "Default": "dynamic([])"},
            "let query(ipaddr_has_any_prefix:dynamic=dynamic([])) { Message };\n",
            "IpAddr",
        )
        self.assertTrue(
            any("192.0.2." in call.args[0] or "198.51.100." in call.args[0]
                for call in test.send_query.call_args_list)
        )

    def test_unavailable_column_still_checks_empty_and_absent_filters(self):
        test = self.make_test([response([[5]]), response([[5]]), response([[0]])])
        test.unavailable_column_test(
            {"Name": "emaildirection_in", "Type": "dynamic", "Default": "dynamic([])"},
            "let query(emaildirection_in:dynamic=dynamic([])) { MailLog };\n",
        )
        self.assertIn("query(emaildirection_in=dynamic([]))", test.send_query.call_args_list[1].args[0])
        self.assertIn("!not_REAL_vAlUe", test.send_query.call_args_list[2].args[0])

    def validator_classes(self):
        legacy_path = os.path.join(
            os.path.dirname(__file__), "..", "..", "..", "ASIM", "dev",
            "ASimTester", "filteringTest", "ASimFilteringTest.py"
        )
        with open(legacy_path, encoding="utf-8") as legacy_file:
            tree = ast.parse(legacy_file.read())
        class_node = next(node for node in tree.body
                          if isinstance(node, ast.ClassDef) and node.name == "FilteringTest")
        namespace = dict(vars(validator))
        exec(compile(ast.Module(body=[class_node], type_ignores=[]), legacy_path, "exec"), namespace)
        return (validator.FilteringTest, namespace["FilteringTest"])

    def test_recipient_filters_cover_each_array_and_reject_ignored_cc_bcc(self):
        columns = ("EmailToRecipients", "EmailCCRecipients", "EmailBCCRecipients")
        addresses = ("alice@alpha.test", "bob@beta.test", "carol@gamma.test")
        # The first row overlaps To/CC; the duplicate verifies multiset comparison.
        rows = [
            {"id": 1, "recipients": [addresses[0], addresses[1]]},
            {"id": 2, "recipients": [addresses[1]]},
            {"id": 3, "recipients": [addresses[2]]},
            {"id": 3, "recipients": [addresses[2]]},
        ]
        for test_class in self.validator_classes():
            for defect in (None, "cc", "bcc", "union", "duplicates"):
                with self.subTest(validator=test_class, defect=defect):
                    test = test_class()

                    def send_query(query):
                        for column, address in zip(columns, addresses):
                            if f"mv-expand recipient={column} " in query:
                                return response([[address]])
                        if "pack_all()" in query:
                            values = re.findall(r"@'([^']*)'", query)
                            filtered = "query(emailrecipient_has_any=" in query
                            if filtered and defect in ("cc", "bcc"):
                                ignored = addresses[1 if defect == "cc" else 2]
                                values = [value for value in values if value != ignored]
                            if filtered and defect == "union" and len(values) > 1:
                                values = values[:1]
                            matches = [row for row in rows if set(values) & set(row["recipients"])]
                            if filtered and defect == "duplicates" and addresses[2] in values:
                                matches = matches[:-1]
                            # Property ordering must not change row identity.
                            return response([[json.dumps(row, sort_keys="query() | where" in query)]
                                             for row in matches])
                        return response([[0 if "!not_REAL_vAlUe" in query else len(rows)]])

                    test.send_query = Mock(side_effect=send_query)
                    args = ("emailrecipient_has_any", "let query=() { Logs };\n", columns, set(columns))
                    if defect is None:
                        test.email_recipient_test(*args)
                        queries = "\n".join(call.args[0] for call in test.send_query.call_args_list)
                        for column in columns:
                            self.assertIn(f"mv-expand recipient={column}", queries)
                    else:
                        with self.assertRaisesRegex(AssertionError, "expected union"):
                            test.email_recipient_test(*args)

    def test_email_event_source_disabled_reaches_control_validation(self):
        for test_class in self.validator_classes():
            with self.subTest(validator=test_class):
                test = test_class()
                parser_path = os.path.join(os.path.dirname(__file__), "..", "..", "..",
                                           "Parsers", "ASimEmailEvent", "Parsers", "imEmailEvent.yaml")
                test.parser_file_path = parser_path
                test.check_required_fields = Mock()
                test.check_data_in_workspace = Mock()
                test.get_columns_of_parser_answer = Mock(return_value=set())
                test.email_event_default_test = Mock()
                test.legacy_eventtype_compatibility_test = Mock()
                test.send_query = Mock(side_effect=[response([[0]]), response([[5]])])
                parser = {
                    "Normalization": {"Schema": "EmailEvent"},
                    "ParserParams": [{"Name": "disabled", "Type": "bool", "Default": False}],
                }
                with patch.dict(test.tests_main_func.__globals__, {
                    "parser_file_path": parser_path,
                    "get_parser": Mock(return_value=parser),
                    "create_query_definition_string": Mock(return_value="let query=() { Logs };\n"),
                }):
                    test.tests_main_func()
                self.assertIn("query(disabled=true)", test.send_query.call_args_list[0].args[0])
                self.assertIn("query(disabled=false)", test.send_query.call_args_list[1].args[0])

    def test_recipient_filter_without_available_columns_checks_default_and_absent(self):
        for test_class in self.validator_classes():
            with self.subTest(validator=test_class):
                test = test_class()
                test.send_query = Mock(side_effect=[
                    response([[3]]), response([[3]]), response([[0]])
                ])
                test.email_recipient_test(
                    "emailrecipient_has_any", "let query=() { Logs };\n",
                    ("EmailToRecipients", "EmailCCRecipients", "EmailBCCRecipients"), set()
                )
                self.assertEqual(test.send_query.call_count, 3)
                self.assertIn("dynamic([])", test.send_query.call_args_list[1].args[0])
                self.assertIn("!not_REAL_vAlUe", test.send_query.call_args_list[2].args[0])

    def test_prefix_results_use_native_kql_for_embedded_ipv4_tokens(self):
        for test_class in self.validator_classes():
            with self.subTest(validator=test_class):
                test = test_class()
                rows = [["198.51.100.2;192.0.2.1", 2]]
                test.send_query = Mock(side_effect=[response(rows), response(rows)])
                result, _ = test.get_response_for_query_with_parameters(
                    "response_has_any_prefix", "", "DnsResponseName", ["192.0.2."]
                )
                test.dynamic_response_matches_filter("response_has_any_prefix", result, ["192.0.2."])
                self.assertIn("has_any_ipv4_prefix(tostring(DnsResponseName)",
                              test.send_query.call_args_list[1].args[0])
                test.send_query = Mock(side_effect=[response(rows), response([])])
                with self.assertRaisesRegex(AssertionError, "KQL IPv4-prefix"):
                    test.get_response_for_query_with_parameters(
                        "response_has_any_prefix", "", "DnsResponseName", ["203.0.113."]
                    )

    def test_multifield_aliases_do_not_reject_destination_only_matches(self):
        for test_class in self.validator_classes():
            with self.subTest(validator=test_class):
                test = test_class()
                test.send_query = Mock(return_value=response([["198.51.100.2", 1]]))
                result, _ = test.get_response_for_query_with_parameters(
                    "ipaddr_has_any_prefix", "", "IpAddr", ["192.0.2."]
                )
                test.dynamic_response_matches_filter("ipaddr_has_any_prefix", result, ["192.0.2."])
                self.assertEqual(test.send_query.call_count, 1)
                for parameter in ("hostname_has_any", "username_has_any", "hashes_has_any"):
                    test.dynamic_response_matches_filter(parameter, result, ["destination"])
                with self.assertRaisesRegex(AssertionError, "unrelated"):
                    test.dynamic_response_matches_filter(
                        "emailsubject_has_any", response([["unrelated", 1]]), ["invoice"]
                    )


if __name__ == "__main__":
    unittest.main()
