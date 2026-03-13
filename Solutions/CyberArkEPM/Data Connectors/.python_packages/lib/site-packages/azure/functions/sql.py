# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

import collections.abc
import typing

from azure.functions import _sql as sql

from . import meta
from ._jsonutils import json


class SqlConverter(meta.InConverter, meta.OutConverter,
                   binding='sql'):

    @classmethod
    def check_input_type_annotation(cls, pytype: type) -> bool:
        return issubclass(pytype, sql.BaseSqlRowList)

    @classmethod
    def check_output_type_annotation(cls, pytype: type) -> bool:
        return issubclass(pytype, (sql.BaseSqlRowList, sql.BaseSqlRow))

    @classmethod
    def decode(cls,
               data: meta.Datum,
               *,
               trigger_metadata) -> typing.Optional[sql.SqlRowList]:
        if data is None or data.type is None:
            return None

        data_type = data.type

        if data_type in ['string', 'json']:
            body = data.value

        elif data_type == 'bytes':
            body = data.value.decode('utf-8')

        else:
            raise NotImplementedError(
                f'Unsupported payload type: {data_type}')

        rows = json.loads(body)
        if not isinstance(rows, list):
            rows = [rows]

        return sql.SqlRowList(
            (None if row is None else sql.SqlRow.from_dict(row))
            for row in rows)

    @classmethod
    def encode(cls, obj: typing.Any, *,
               expected_type: typing.Optional[type]) -> meta.Datum:
        if isinstance(obj, sql.SqlRow):
            data = sql.SqlRowList([obj])

        elif isinstance(obj, sql.SqlRowList):
            data = obj

        elif isinstance(obj, collections.abc.Iterable):
            data = sql.SqlRowList()

            for row in obj:
                if not isinstance(row, sql.SqlRow):
                    raise NotImplementedError(
                        f'Unsupported list type: {type(obj)}, \
                            lists must contain SqlRow objects')
                else:
                    data.append(row)

        else:
            raise NotImplementedError(f'Unsupported type: {type(obj)}')

        return meta.Datum(
            type='json',
            value=json.dumps([dict(d) for d in data])
        )
