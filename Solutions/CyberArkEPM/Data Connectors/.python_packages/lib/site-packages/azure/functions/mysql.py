# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

import collections.abc
import typing

from azure.functions import _mysql as mysql

from . import meta
from ._jsonutils import json


class MySqlConverter(meta.InConverter, meta.OutConverter,
                     binding='mysql'):

    @classmethod
    def check_input_type_annotation(cls, pytype: type) -> bool:
        return issubclass(pytype, mysql.BaseMySqlRowList)

    @classmethod
    def check_output_type_annotation(cls, pytype: type) -> bool:
        return issubclass(pytype, (mysql.BaseMySqlRowList, mysql.BaseMySqlRow))

    @classmethod
    def decode(cls,
               data: meta.Datum,
               *,
               trigger_metadata) -> typing.Optional[mysql.MySqlRowList]:
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

        return mysql.MySqlRowList(
            (None if row is None else mysql.MySqlRow.from_dict(row))
            for row in rows)

    @classmethod
    def encode(cls, obj: typing.Any, *,
               expected_type: typing.Optional[type]) -> meta.Datum:
        if isinstance(obj, mysql.MySqlRow):
            data = mysql.MySqlRowList([obj])

        elif isinstance(obj, mysql.MySqlRowList):
            data = obj

        elif isinstance(obj, collections.abc.Iterable):
            data = mysql.MySqlRowList()

            for row in obj:
                if not isinstance(row, mysql.MySqlRow):
                    raise NotImplementedError(
                        f'Unsupported list type: {type(obj)}, \
                            lists must contain MySqlRow objects')
                else:
                    data.append(row)

        else:
            raise NotImplementedError(f'Unsupported type: {type(obj)}')

        return meta.Datum(
            type='json',
            value=json.dumps([dict(d) for d in data])
        )
