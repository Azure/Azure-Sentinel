from utils.csv_parser import parse_csv, parse_domain_list


def test_parse_csv_strips_headers_and_values():
    rows = parse_csv(" domain_name , num\n example.com , 1\n")
    assert rows == [{"domain_name": "example.com", "num": "1"}]


def test_parse_domain_list_skips_header_row():
    rows, raw = parse_domain_list("domain_name\nexample.com\nexample.org\n")
    assert rows == [{"domain_name": "example.com"}, {"domain_name": "example.org"}]
    # raw includes the header line so pagination offset advances correctly
    assert raw == 3


def test_parse_domain_list_no_header():
    rows, raw = parse_domain_list("example.com\nexample.org\n")
    assert rows == [{"domain_name": "example.com"}, {"domain_name": "example.org"}]
    assert raw == 2


def test_parse_domain_list_rejects_non_domain_lines():
    rows, raw = parse_domain_list("not a domain\nexample.com\n")
    assert rows == [{"domain_name": "example.com"}]
    # raw counts the invalid line too — prevents early pagination stop
    assert raw == 2


def test_parse_domain_list_empty():
    rows, raw = parse_domain_list("")
    assert rows == []
    assert raw == 0
