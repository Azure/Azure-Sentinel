# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
from collections import defaultdict
import functools
from typing import TYPE_CHECKING

from azure.core.exceptions import DecodeError, HttpResponseError, ResourceExistsError, ResourceNotFoundError
from azure.core.pipeline.policies import ContentDecodePolicy

if TYPE_CHECKING:
    # pylint:disable=unused-import,ungrouped-imports
    from typing import Optional, Type
    from azure.core.pipeline.transport import HttpResponse


def _get_exception_for_key_vault_error(cls, response):
    # type: (Type[HttpResponseError], HttpResponse) -> HttpResponseError
    """Construct cls (HttpResponseError or subclass thereof) with Key Vault's error message."""

    try:
        body = ContentDecodePolicy.deserialize_from_http_generics(response)
        message = "({}) {}".format(body["error"]["code"], body["error"]["message"])  # type: Optional[str]
    except (DecodeError, KeyError):
        # Key Vault error response bodies should have the expected shape and be deserializable.
        # If we somehow land here, we'll take HttpResponse's default message.
        message = None

    return cls(message=message, response=response)


# errors map to HttpResponseError...
_default = functools.partial(_get_exception_for_key_vault_error, HttpResponseError)

# ...unless this mapping specifies another type
_code_to_core_error = {404: ResourceNotFoundError, 409: ResourceExistsError}


class _ErrorMap(defaultdict):
    """A dict whose 'get' method returns a default value.

    defaultdict would be preferable but defaultdict.get returns None for keys having no value
    (azure.core.exceptions.map_error calls error_map.get)
    """

    def get(self, key, value=None):  # pylint:disable=unused-argument
        return self[key]


# map status codes to callables returning appropriate azure-core errors
error_map = _ErrorMap(lambda: _default,
    {
        status_code: functools.partial(_get_exception_for_key_vault_error, cls)
        for status_code, cls in _code_to_core_error.items()
    }
)
