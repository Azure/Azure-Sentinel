import ast
import importlib.util
import os
import re
import unittest
from types import SimpleNamespace
from unittest.mock import Mock


SCRIPT_PATH = os.path.join(os.path.dirname(__file__), "ASimFilteringTest.py")
SPEC = importlib.util.spec_from_file_location("asim_filtering_validator", SCRIPT_PATH)
validator = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(validator)

EXPECTED_EMAIL_EVENT_PARAMETERS = {
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
        self.assertEqual(
            set(validator.all_schemas_parameters["EmailEvent"]),
            {param["Name"] for param in parser["ParserParams"]},
        )

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

    def test_datetime_filter_uses_schema_event_time_and_checks_out_of_range(self):
        test = self.make_test(
            [
                response([["2026-10-21T00:00:00Z"], ["2026-10-22T00:00:00Z"]]),
                response([["2026-10-21T12:00:00Z", "2026-10-21T00:00:00Z", "2026-10-22T00:00:00Z", 2, 86400000000]]),
                response([[1]]),
                response([[0]]),
            ]
        )
        test.datetime_test(
            {"Name": "starttime", "Type": "datetime"},
            "let query(starttime:datetime=datetime(null)) { Logs };\n",
            "EventStartTime",
        )
        query_text = "\n".join(call.args[0] for call in test.send_query.call_args_list)
        self.assertIn("max(EventStartTime)", query_text)
        self.assertIn("project EventStartTime", query_text)
        self.assertNotIn("TimeGenerated", query_text)
        self.assertIn("datetime_add('microsecond', 1, filter_boundary)", query_text)

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

    def test_recipient_filter_searches_all_recipient_arrays(self):
        test = self.make_test(
            [
                response([[3]]),
                response([[3]]),
                response([["alice@example.test"], ["bob@example.test"]]),
                response([[1]]),
                response([[2]]),
                response([[0]]),
            ]
        )
        test.email_recipient_test(
            "emailrecipient_has_any",
            "let query(emailrecipient_has_any:dynamic=dynamic([])) { EmailLogs };\n",
            ("EmailToRecipients", "EmailCCRecipients", "EmailBCCRecipients"),
            {"EmailToRecipients", "EmailCCRecipients", "EmailBCCRecipients"},
        )
        value_query = test.send_query.call_args_list[2].args[0]
        self.assertIn("array_concat(coalesce(EmailToRecipients, dynamic([])), coalesce(EmailCCRecipients, dynamic([])), coalesce(EmailBCCRecipients, dynamic([])))", value_query)
        self.assertIn("mv-expand recipient=recipient_values", value_query)
        self.assertIn("emailrecipient_has_any=dynamic", test.send_query.call_args_list[3].args[0])
        self.assertIn("emailrecipient_has_any=dynamic", test.send_query.call_args_list[5].args[0])


if __name__ == "__main__":
    unittest.main()
