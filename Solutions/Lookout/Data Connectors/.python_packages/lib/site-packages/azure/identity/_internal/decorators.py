# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import functools
import logging

from six import raise_from
from azure.core.exceptions import ClientAuthenticationError

_LOGGER = logging.getLogger(__name__)


def log_get_token(class_name):
    """Adds logging around get_token calls.

    :param str class_name: required for the sake of Python 2.7, which lacks an easy way to get the credential's class
        name from the decorated function
    """

    def decorator(fn):
        qualified_name = class_name + ".get_token"

        @functools.wraps(fn)
        def wrapper(*args, **kwargs):
            try:
                token = fn(*args, **kwargs)
                _LOGGER.info("%s succeeded", qualified_name)
                return token
            except Exception as ex:
                _LOGGER.warning("%s failed: %s", qualified_name, ex, exc_info=_LOGGER.isEnabledFor(logging.DEBUG))
                raise

        return wrapper

    return decorator


def wrap_exceptions(fn):
    """Prevents leaking exceptions defined outside azure-core by raising ClientAuthenticationError from them."""

    @functools.wraps(fn)
    def wrapper(*args, **kwargs):
        try:
            return fn(*args, **kwargs)
        except ClientAuthenticationError:
            raise
        except Exception as ex:  # pylint:disable=broad-except
            auth_error = ClientAuthenticationError(message="Authentication failed: {}".format(ex))
            raise_from(auth_error, ex)

    return wrapper
