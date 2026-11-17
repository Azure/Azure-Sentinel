from __future__ import annotations

import json
from pathlib import Path

import pytest

from azure_monitor_logs_ingestion.azure import AzureClient
from azure_monitor_logs_ingestion.contract import (
    load_contract,
    load_records,
    validate_records,
)


def write_contract(tmp_path, value):
    path = tmp_path / "contract.yaml"
    import yaml

    path.write_text(yaml.safe_dump(value, sort_keys=False), encoding="utf-8")
    return path


def base_contract():
    return {
        "version": 1,
        "name": "sample",
        "workspace": "workspace",
        "inputStream": "Custom-SampleRaw",
        "inputColumns": [{"name": "EventTime", "type": "datetime"}],
        "transformKql": "source | project TimeGenerated=todatetime(EventTime)",
        "destination": {
            "kind": "custom",
            "table": "Sample_CL",
            "outputStream": "Custom-Sample_CL",
            "columns": [{"name": "TimeGenerated", "type": "datetime"}],
        },
    }


def test_loads_custom_contract_with_default_resource_names(tmp_path):
    contract = load_contract(write_contract(tmp_path, base_contract()))

    assert contract.resources.dce == "sample-dce"
    assert contract.resources.dcr == "sample-dcr"
    assert contract.destination.table == "Sample_CL"


def test_requires_custom_input_stream(tmp_path):
    value = base_contract()
    value["inputStream"] = "Microsoft-Sample"

    with pytest.raises(ValueError, match="Custom-"):
        load_contract(write_contract(tmp_path, value))


def test_requires_matching_custom_output_stream(tmp_path):
    value = base_contract()
    value["destination"]["outputStream"] = "Custom-Wrong_CL"

    with pytest.raises(ValueError, match="Custom-Sample_CL"):
        load_contract(write_contract(tmp_path, value))


def test_accepts_standard_destination_without_destination_columns(tmp_path):
    value = base_contract()
    value["destination"] = {
        "kind": "standard",
        "table": "CommonSecurityLog",
        "outputStream": "Microsoft-CommonSecurityLog",
    }

    contract = load_contract(write_contract(tmp_path, value))

    assert contract.destination.kind == "standard"
    assert contract.destination.columns == ()


def test_registered_standard_contracts_are_valid():
    root = Path(__file__).resolve().parents[1] / "contracts"

    for name in ("Event.yaml", "Syslog.yaml"):
        contract = load_contract(root / name)
        assert contract.destination.kind == "standard"
        assert contract.input_stream.startswith("Custom-")
        assert contract.destination.output_stream.startswith("Microsoft-")
        assert contract.resources.dce != contract.resources.dcr


def test_accepts_vendor_raw_input_column_names(tmp_path):
    value = base_contract()
    value["inputColumns"] = [
        {"name": "cs-username", "type": "string"},
        {"name": "event.timestamp", "type": "datetime"},
    ]

    contract = load_contract(write_contract(tmp_path, value))

    assert [column.name for column in contract.input_columns] == [
        "cs-username",
        "event.timestamp",
    ]


def test_rejects_vendor_raw_names_for_destination_columns(tmp_path):
    value = base_contract()
    value["destination"]["columns"] = [
        {"name": "TimeGenerated", "type": "datetime"},
        {"name": "invalid-name", "type": "string"},
    ]

    with pytest.raises(ValueError, match="valid column name"):
        load_contract(write_contract(tmp_path, value))


def test_accepts_case_distinct_destination_columns(tmp_path):
    value = base_contract()
    value["destination"]["columns"] = [
        {"name": "TimeGenerated", "type": "datetime"},
        {"name": "FilePath", "type": "string"},
        {"name": "Filepath", "type": "string"},
    ]

    contract = load_contract(write_contract(tmp_path, value))

    assert [column.name for column in contract.destination.columns[-2:]] == [
        "FilePath",
        "Filepath",
    ]


def test_loads_array_single_object_and_ndjson(tmp_path):
    array_path = tmp_path / "array.json"
    object_path = tmp_path / "object.json"
    ndjson_path = tmp_path / "records.ndjson"
    array_path.write_text('[{"a": 1}, {"a": 2}]', encoding="utf-8")
    object_path.write_text('{"a": 1}', encoding="utf-8")
    ndjson_path.write_text('{"a": 1}\n{"a": 2}\n', encoding="utf-8")

    assert len(load_records(array_path)) == 2
    assert len(load_records(object_path)) == 1
    assert len(load_records(ndjson_path)) == 2


def test_rejects_undeclared_fields(tmp_path):
    contract = load_contract(write_contract(tmp_path, base_contract()))

    with pytest.raises(ValueError, match="undeclared fields: Extra"):
        validate_records(contract, [{"EventTime": "now", "Extra": 1}])


def test_rejects_values_that_do_not_match_input_type(tmp_path):
    contract = load_contract(write_contract(tmp_path, base_contract()))

    with pytest.raises(ValueError, match="does not match"):
        validate_records(contract, [{"EventTime": 123}])


def test_batches_respect_count_limit():
    records = [{"value": index} for index in range(5)]

    batches = AzureClient.batches(records, max_records=2)

    assert [len(batch) for batch in batches] == [2, 2, 1]


def test_batches_reject_oversized_record():
    with pytest.raises(ValueError, match="single record"):
        AzureClient.batches([{"value": "x" * 100}], max_bytes=50)


def test_batches_respect_encoded_byte_limit():
    records = [{"value": "a" * 20}, {"value": "b" * 20}]
    single_size = len(json.dumps(records[0], separators=(",", ":")).encode("utf-8"))

    batches = AzureClient.batches(records, max_bytes=single_size + 3)

    assert [len(batch) for batch in batches] == [1, 1]
