import json
from typing import List

from azure.functions.decorators.utils import StringifyEnumJsonEncoder


class CollectionBytes:
    """The CollectionBytes class is used for generating a mock
    'collection_bytes' meta.Datum in testing. The common usage of it is
    new_datum = meta.Datum(type='collection_bytes',
                           value=CollectionBytes([b'1', b'2']))
    """
    def __init__(self, data: List[bytes]):
        self.bytes = data


class CollectionString:
    """The CollectionString class is used for generating a mock
    'collection_string' meta.Datum in testing. The common usage of it is
    new_datum = meta.Datum(type='collection_string',
                           value=CollectionString(['a', 'b']))
    """
    def __init__(self, data: List[str]):
        self.string = data


class CollectionSint64:
    """The CollectionSint64 class is used for generating a mock
    'collection_sint64' meta.Datum in testing. The common usage of it is
    new_datum = meta.Datum(type='collection_sint64',
                           value=CollectionSint64([1, 2]))
    """
    def __init__(self, data: List[int]):
        self.sint64 = data


def assert_json(self, func, expected_dict):
    self.assertEqual(json.dumps(json.loads(str(func)), sort_keys=True,
                                cls=StringifyEnumJsonEncoder),
                     json.dumps(expected_dict, sort_keys=True,
                                cls=StringifyEnumJsonEncoder))
