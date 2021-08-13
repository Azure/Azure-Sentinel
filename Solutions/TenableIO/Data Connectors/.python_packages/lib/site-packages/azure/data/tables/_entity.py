# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
from enum import Enum
from typing import Any, Dict, Union, NamedTuple


class TableEntity(dict):
    """
    An Entity dictionary with additional metadata

    """
    _metadata = {}  # type: Dict[str, Any]

    @property
    def metadata(self):
        # type: () -> Dict[str, Any]
        """Resets metadata to be a part of the entity
        :return Dict of entity metadata
        :rtype: Dict[str, Any]
        """
        return self._metadata


class EdmType(str, Enum):
    """
    Used by :class:`~.EntityProperty` to represent the type of the entity property
    to be stored by the Table service.
    """

    BINARY = "Edm.Binary"
    """ Represents byte data. This type will be inferred for Python bytes.. """

    INT64 = "Edm.Int64"
    """ Represents a number between -(2^31) and 2^31. This is the default type for Python numbers. """

    GUID = "Edm.Guid"
    """ Represents a GUID. This type will be inferred for uuid.UUID. """

    DATETIME = "Edm.DateTime"
    """ Represents a date. This type will be inferred for Python datetime objects. """

    STRING = "Edm.String"
    """ Represents a string. This type will be inferred for Python strings. """

    INT32 = "Edm.Int32"
    """ Represents a number between -(2^15) and 2^15. Must be specified or numbers will default to INT64. """

    DOUBLE = "Edm.Double"
    """ Represents a double. This type will be inferred for Python floating point numbers. """

    BOOLEAN = "Edm.Boolean"
    """ Represents a boolean. This type will be inferred for Python bools. """


EntityProperty = NamedTuple("EntityProperty", [("value", Any), ("edm_type", Union[str, EdmType])])
"""
An entity property. Used to explicitly set :class:`~EdmType` when necessary.

Values which require explicit typing are GUID, INT64, and BINARY. Other EdmTypes
may be explicitly create as EntityProperty objects but need not be. For example,
the below with both create STRING typed properties on the entity::
    entity = TableEntity()
    entity.a = 'b'
    entity.x = EntityProperty('y', EdmType.STRING)

:param value:
:type value: Any
:param edm_type: Type of the value
:type edm_type: str or :class:`~azure.data.tables.EdmType`
"""
