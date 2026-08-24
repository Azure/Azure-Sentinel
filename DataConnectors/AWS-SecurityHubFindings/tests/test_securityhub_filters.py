import re
import sys
import unittest
from pathlib import Path


FUNCTION_DIRECTORY = Path(__file__).parents[1] / "AzFunAWSSecurityHubIngestion"
sys.path.insert(0, str(FUNCTION_DIRECTORY))

from securityhub_filters import INVALID_FILTER_MESSAGE, parse_securityhub_filters


class SecurityHubFiltersTests(unittest.TestCase):
    def test_accepts_supported_filter_shapes(self):
        filter_value = """{
            'SeverityLabel': [{'Value': 'HIGH', 'Comparison': 'EQUALS'}],
            'SeverityProduct': [{'Gte': 70}],
            'FirstObservedAt': [{'DateRange': {'Value': 7, 'Unit': 'DAYS'}}],
            'ProductFields': [
                {'Key': 'key', 'Value': 'value', 'Comparison': 'EQUALS'}
            ],
            'NetworkSourceIpV4': [{'Cidr': '10.0.0.0/8'}],
            'Keyword': [{'Value': 'threat'}],
            'Sample': [{'Value': True}],
        }"""

        filters = parse_securityhub_filters(filter_value)

        self.assertEqual(filters["SeverityProduct"], [{"Gte": 70}])
        self.assertEqual(filters["Sample"], [{"Value": True}])

    def test_sanitizes_literal_eval_errors(self):
        sensitive_values = (
            "{'SeverityLabel': ['customer-secret'",
            "{'SeverityLabel': customer_secret()}",
        )

        for sensitive_value in sensitive_values:
            with self.subTest(sensitive_value=sensitive_value):
                with self.assertRaisesRegex(
                    ValueError, f"^{re.escape(INVALID_FILTER_MESSAGE)}$"
                ) as error:
                    parse_securityhub_filters(sensitive_value)

                self.assertNotIn("customer", str(error.exception))
                self.assertIsNone(error.exception.__context__)

    def test_rejects_invalid_security_hub_shape_with_sanitized_error(self):
        sensitive_value = "{'customer-secret': [{'Value': 'secret'}]}"

        with self.assertRaisesRegex(
            ValueError, f"^{re.escape(INVALID_FILTER_MESSAGE)}$"
        ) as error:
            parse_securityhub_filters(sensitive_value)

        self.assertNotIn("customer-secret", str(error.exception))
        self.assertIsNone(error.exception.__context__)

    def test_rejects_empty_filter_entries(self):
        for filter_value in ("{'SeverityLabel': []}", "{'SeverityLabel': [{}]}"):
            with self.subTest(filter_value=filter_value):
                with self.assertRaisesRegex(
                    ValueError, f"^{re.escape(INVALID_FILTER_MESSAGE)}$"
                ):
                    parse_securityhub_filters(filter_value)


if __name__ == "__main__":
    unittest.main()
