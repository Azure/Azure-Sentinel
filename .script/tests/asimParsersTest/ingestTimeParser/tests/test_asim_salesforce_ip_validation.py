import ipaddress
import re
import unittest
from pathlib import Path

import yaml


REPO_ROOT = Path(__file__).resolve().parents[5]
PARSER_DIRECTORY = REPO_ROOT / "Parsers" / "ASimAuthentication" / "IngestTimeParsers"
PARSER_NAMES = (
    "ASimAuthenticationSalesforceLoginHistory",
    "ASimAuthenticationSalesforceLoginHistoryV2_CL",
)


class SalesforceIpValidationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.queries = {}
        cls.patterns = {}
        for name in PARSER_NAMES:
            document = yaml.safe_load(
                (PARSER_DIRECTORY / f"{name}.yaml").read_text(encoding="utf-8")
            )
            query = document["ParserQuery"]
            cls.queries[name] = query
            literals = re.findall(r'SourceIp matches regex @"([^"]+)"', query)
            # Python's strict end anchor is \Z; KQL uses \z.
            cls.patterns[name] = [
                re.compile(pattern.replace(r"\z", r"\Z")) for pattern in literals
            ]

    def assert_ip(self, value, expected):
        for name, patterns in self.patterns.items():
            with self.subTest(parser=name, ip=value):
                self.assertEqual(
                    expected,
                    any(pattern.search(value) is not None for pattern in patterns),
                )

    def test_source_rooted_inline_expression(self):
        for name, query in self.queries.items():
            with self.subTest(parser=name):
                executable = re.sub(r"//[^\n]*", "", query)
                self.assertTrue(executable.lstrip().startswith("source\n"))
                self.assertNotRegex(executable, r"\blet\b|;|IsValidIpAddress")
                self.assertNotRegex(executable, r"\bparse_ipv[46]\s*\(")
                self.assertEqual(3, len(self.patterns[name]))
                self.assertRegex(
                    executable,
                    r'NormalizedSourceIp = iff\([\s\S]+?,\s*SourceIp,\s*""\)',
                )
                for field in ("IpAddr", "Src", "SrcIpAddr"):
                    self.assertIn(f"{field} = NormalizedSourceIp", executable)
                self.assertIn('"SourceIp", SourceIp', executable)
        self.assertEqual(*self.queries.values())

    def test_standard_addresses_and_cidr(self):
        valid = (
            "0.0.0.0", "255.255.255.255", "192.0.2.1", "10.20.30.40",
            "::", "::1", "1::", "2001:db8::1", "2001:DB8:ABCD::EF01",
            "1:2:3:4:5:6:7:8", "ffff:ffff:ffff:ffff:ffff:ffff:ffff:ffff",
            "::192.0.2.1", "::ffff:192.0.2.1", "2001:db8::ffff:192.0.2.1",
            "1:2:3:4:5:6:192.0.2.1", "1:2:3:4:5::192.0.2.1",
        )
        for value in valid:
            address = ipaddress.ip_address(value)
            self.assert_ip(value, True)
            for prefix in range(address.max_prefixlen + 1):
                self.assert_ip(f"{value}/{prefix}", True)

    def test_all_ipv6_compression_positions(self):
        for group_count, suffix in ((8, ""), (6, ":192.0.2.1")):
            groups = [f"{index + 1:x}" for index in range(group_count)]
            self.assert_ip(":".join(groups) + suffix, True)
            for start in range(group_count):
                for end in range(start + 1, group_count + 1):
                    left = ":".join(groups[:start])
                    right = ":".join(groups[end:])
                    if suffix:
                        right = right + suffix if right else suffix[1:]
                    value = left + "::" + right
                    ipaddress.IPv6Address(value)
                    self.assert_ip(value, True)
                    self.assert_ip(f"{value}/128", True)

    def test_ipv4_octet_boundaries(self):
        for position in range(4):
            for octet in (0, 9, 10, 99, 100, 199, 200, 249, 250, 255):
                groups = ["192", "0", "2", "1"]
                groups[position] = str(octet)
                value = ".".join(groups)
                self.assert_ip(value, True)
                self.assert_ip(f"::ffff:{value}", True)
            for octet in ("256", "999", "-1", "+1", "00", "01"):
                groups = ["192", "0", "2", "1"]
                groups[position] = octet
                value = ".".join(groups)
                self.assert_ip(value, False)
                self.assert_ip(f"::ffff:{value}", False)

    def test_invalid_compressed_ipv6_group_counts(self):
        for maximum, embedded in ((7, False), (5, True)):
            for left_count in range(maximum + 3):
                for right_count in range(maximum + 3):
                    if left_count + right_count <= maximum:
                        continue
                    left = ":".join(["1"] * left_count)
                    right = ":".join(["2"] * right_count)
                    if embedded:
                        right = right + ":192.0.2.1" if right else "192.0.2.1"
                    value = left + "::" + right
                    with self.assertRaises(ipaddress.AddressValueError):
                        ipaddress.IPv6Address(value)
                    self.assert_ip(value, False)

    def test_invalid_addresses(self):
        invalid = (
            "", "unknown", "192.0.2", "192.0.2.1.5", "256.0.0.1",
            "192.0.2.-1", "+192.0.2.1", "192..2.1", "192.0.2.01",
            "192.0.2.1/33", "192.0.2.1/-1", "192.0.2.1/01",
            "192.0.2.1/", "192.0.2.1/24/1", "0xC0000201", "3221225985",
            ":", ":::1", "1:::2", "1::2::3", "1:2:3:4:5:6:7",
            "1:2:3:4:5:6:7:8:9", "1:2:3:4:5:6:7:8::",
            "1:2:3:4:5:6:7::8", "12345::1", "gggg::1", "::/129",
            "::/-1", "::/01", "::/128/1", "::ffff:256.0.0.1",
            "::ffff:192.0.2", "1:2:3:4:5:6:7:192.0.2.1",
            "1:2:3:4:5:6::192.0.2.1", "::1:2:3:4:5:6:192.0.2.1",
            "1::2:3:4:5:6:192.0.2.1", "1::2::192.0.2.1",
            "[2001:db8::1]", "fe80::1%eth0", "192.0.2.1:443",
        )
        for value in invalid:
            self.assert_ip(value, False)
        for value in ("192.0.2.1", "::1", "::ffff:192.0.2.1"):
            for padding in (" ", "\t", "\n", "\r", "\r\n", "\x00"):
                self.assert_ip(value + padding, False)
                self.assert_ip(padding + value, False)


class SalesforceDomainFallbackTests(unittest.TestCase):
    def test_optional_domain_and_fallbacks(self):
        cases = (
            ({"SalesforceDomain": "tenant.example", "LoginUrl": "https://login.example/path"}, "tenant.example"),
            ({"SalesforceDomain": "tenant.example", "LoginUrl": ""}, "tenant.example"),
            ({"SalesforceDomain": "", "LoginUrl": "https://login.example/path"}, "login.example"),
            ({"LoginUrl": "https://login.example/path"}, "login.example"),
            ({"SalesforceDomain": None, "LoginUrl": "https://login.example/path"}, "login.example"),
            ({"LoginUrl": "login.example/path"}, "login.example"),
            ({"SalesforceDomain": "", "LoginUrl": "http://user@login.example:443/path"}, "login.example"),
            ({"LoginUrl": "https:///path"}, "https:///path"),
            ({"SalesforceDomain": "", "LoginUrl": ""}, ""),
            ({"LoginUrl": ""}, ""),
        )
        for name in PARSER_NAMES:
            query = yaml.safe_load(
                (PARSER_DIRECTORY / f"{name}.yaml").read_text(encoding="utf-8")
            )["ParserQuery"]
            self.assertIn(
                '| extend _SalesforceDomain = tostring(columnifexists("SalesforceDomain", ""))',
                query,
            )
            self.assertLess(
                query.index("| extend _SalesforceDomain"),
                query.index("| extend TargetFQDN"),
            )
            self.assertEqual(1, len(re.findall(r'\bSalesforceDomain\b', query)))
            self.assertNotIn("column_ifexists", query)
            selection = re.search(
                r"TargetFQDN = case\(\s*"
                r"isnotempty\((\w+)\),\s*\1,\s*"
                r"isnotempty\((\w+)\),\s*\2,\s*(\w+)\)",
                query,
            )
            self.assertIsNotNone(selection)
            self.assertEqual(
                ("_SalesforceDomain", "LoginUrlFQDN", "LoginUrl"),
                selection.groups(),
            )
            host_pattern = re.search(
                r'LoginUrlFQDN = extract\(@"([^"]+)", 1, TargetUrl\)',
                query,
            ).group(1)
            for record, expected in cases:
                with self.subTest(parser=name, record=record):
                    # Local model of the asserted KQL selection, not live execution.
                    login_url = record["LoginUrl"]
                    target_url = (
                        login_url
                        if not login_url or login_url.startswith(("http://", "https://"))
                        else "https://" + login_url
                    )
                    match = re.search(host_pattern, target_url)
                    columns = {
                        "_SalesforceDomain": record.get("SalesforceDomain") or "",
                        "LoginUrlFQDN": match.group(1) if match else "",
                        "LoginUrl": login_url,
                    }
                    actual = next(
                        (columns[column] for column in selection.groups()[:2] if columns[column]),
                        columns[selection.group(3)],
                    )
                    self.assertEqual(expected, actual)


if __name__ == "__main__":
    unittest.main()
