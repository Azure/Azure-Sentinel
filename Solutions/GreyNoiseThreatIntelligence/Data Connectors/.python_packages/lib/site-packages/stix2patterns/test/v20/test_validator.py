"""
Test cases for stix2patterns/validator.py.
"""
import os

import pytest

from stix2patterns.validator import validate

TEST_CASE_FILE = os.path.join(os.path.dirname(__file__), 'spec_examples.txt')
with open(TEST_CASE_FILE) as f:
    SPEC_CASES = [x.strip() for x in f.readlines()]


@pytest.mark.parametrize("test_input", SPEC_CASES)
def test_spec_patterns(test_input):
    """
    Validate patterns from STIX 2.0 Patterning spec.
    """
    pass_test = validate(test_input, stix_version='2.0', print_errs=True)
    assert pass_test is True


FAIL_CASES = [
    ("file:size = 1280",  # Does not use square brackets
        "FAIL: Error found at line 1:0. input is missing square brackets"),
    ("[file:size = ]",  # Missing value
        "FAIL: Error found at line 1:13. mismatched input ']'"),
    ("[file:hashes.MD5 = cead3f77f6cda6ec00f57d76c9a6879f]",  # No quotes around string
        "FAIL: Error found at line 1:19. mismatched input 'cead3f77f6cda6ec00f57d76c9a6879f'"),
    ("[file.size = 1280]",  # Use period instead of colon
        "FAIL: Error found at line 1:5. no viable alternative at input 'file.'"),
    ("[file:name MATCHES /.*\\.dll/]",  # Quotes around regular expression
        "FAIL: Error found at line 1:19. mismatched input '/' expecting StringLiteral"),
    ("[win-registry-key:key = 'hkey_local_machine\\\\foo\\\\bar'] WITHIN ]",  # Missing Qualifier value
        "FAIL: Error found at line 1:63. mismatched input ']' expecting {IntPosLiteral, FloatPosLiteral}"),
    ("[win-registry-key:key = 'hkey_local_machine\\\\foo\\\\bar'] WITHIN 5 HOURS]",  # SECONDS is the only valid time unit
        "FAIL: Error found at line 1:65. mismatched input 'HOURS' expecting 'SECONDS'"),
    ("[win-registry-key:key = 'hkey_local_machine\\\\foo\\\\bar'] WITHIN -5 SECONDS]",  # Negative integer is invalid
        "FAIL: Error found at line 1:63. mismatched input '-5' expecting {IntPosLiteral, FloatPosLiteral}"),
    ("[network-traffic:dst_ref.value ISSUBSET ]",  # Missing second Comparison operand
        "FAIL: Error found at line 1:40. missing StringLiteral at ']'"),
    ("[file:hashes.MD5 =? 'cead3f77f6cda6ec00f57d76c9a6879f']",  # '=?' isn't a valid operator
        "FAIL: Error found at line 1:18. extraneous input '?'"),
    ("[x_whatever:detected == t'2457-73-22T32:81:84.1Z']",  # Not a valid date
        "FAIL: Error found at line 1:24. extraneous input 't'"),
    ("[artifact:payload_bin = b'====']",  # Not valid Base64
        "FAIL: Error found at line 1:24. extraneous input 'b'"),
    ("[foo:bar=1] within 2 seconds",  # keywords must be uppercase
        "FAIL: Error found at line 1:12. mismatched input 'within' expecting <EOF>"),
    ("[file:hashes.'SHA-256' = 'f00']",  # Malformed hash value
        "FAIL: 'f00' is not a valid SHA-256 hash"),
    # TODO: add more failing test cases.
]


@pytest.mark.parametrize("test_input,test_output", FAIL_CASES)
def test_fail_patterns(test_input, test_output):
    """
    Validate that patterns fail as expected.
    """
    pass_test, errors = validate(test_input, stix_version='2.0', ret_errs=True, print_errs=True)
    assert errors[0].startswith(test_output)
    assert pass_test is False


PASS_CASES = [
    "[file:size = 1280]",
    "[file:size != 1280]",
    "[file:size < 1024]",
    "[file:size <= 1024]",
    "[file:size > 1024]",
    "[file:size >= 1024]",
    "[file:file_name = 'my_file_name']",
    "[file:extended_properties.'ntfs-ext'.sid = '234']",
    r"[emailaddr:value MATCHES '.+\\@ibm\\.com$' OR file:name MATCHES '^Final Report.+\\.exe$']",
    "[ipv4addr:value ISSUBSET '192.168.0.1/24']",
    "[ipv4addr:value NOT ISSUBSET '192.168.0.1/24']",
    "[user-account:value = 'Peter'] AND [user-account:value != 'Paul'] AND [user-account:value = 'Mary'] WITHIN 5 SECONDS",
    "[file:file_system_properties.file_name LIKE 'name%']",
    "[file:file_name IN ('test.txt', 'test2.exe', 'README')]",
    "[file:size IN (1024, 2048, 4096)]",
    "[network-connection:extended_properties[0].source_payload MATCHES 'dGVzdHRlc3R0ZXN0']",
    "[win-registry-key:key = 'hkey_local_machine\\\\foo\\\\bar'] WITHIN 5 SECONDS",
    "[x_whatever:detected == t'2018-03-22T12:11:14.1Z']",
    "[artifact:payload_bin = b'dGhpcyBpcyBhIHRlc3Q=']",
    "[foo:bar=1] REPEATS 9 TIMES",
    "[network-traffic:start = '2018-04-20T12:36:24.558Z']",
    "( [(network-traffic:dst_port IN(443,6443,8443) AND network-traffic:src_packets != 0) ])",  # Misplaced whitespace
    "[file:hashes[*] = '8665c8d477534008b3058b72e2dae8ae']",
]


@pytest.mark.parametrize("test_input", PASS_CASES)
def test_pass_patterns(test_input):
    """
    Validate that patterns pass as expected.
    """
    pass_test = validate(test_input, stix_version='2.0', print_errs=True)
    assert pass_test is True
