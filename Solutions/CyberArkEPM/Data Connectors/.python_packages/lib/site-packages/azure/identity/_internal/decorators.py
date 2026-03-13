# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import functools
import logging
import json
import base64

from azure.core.exceptions import ClientAuthenticationError

from .utils import within_credential_chain


_LOGGER = logging.getLogger(__name__)


def log_get_token(fn):

    @functools.wraps(fn)
    def wrapper(*args, **kwargs):
        try:
            token = fn(*args, **kwargs)
            _LOGGER.log(
                logging.DEBUG if within_credential_chain.get() else logging.INFO,
                "%s succeeded",
                fn.__qualname__,
            )
            if _LOGGER.isEnabledFor(logging.DEBUG):
                try:
                    base64_meta_data = token.token.split(".")[1]
                    padding_needed = -len(base64_meta_data) % 4
                    if padding_needed:
                        base64_meta_data += "=" * padding_needed
                    json_bytes = base64.urlsafe_b64decode(base64_meta_data)
                    json_string = json_bytes.decode("utf-8")
                    json_dict = json.loads(json_string)
                    upn = json_dict.get("upn", "unavailableUpn")
                    appid = json_dict.get("appid", "<unavailable>")
                    tid = json_dict.get("tid", "<unavailable>")
                    oid = json_dict.get("oid", "<unavailable>")
                    log_string = (
                        f"[Authenticated account] Client ID: {appid}. "
                        f"Tenant ID: {tid}. User Principal Name: {upn}. Object ID (user): {oid}"
                    )
                    _LOGGER.debug(log_string)
                except Exception as ex:  # pylint: disable=broad-except
                    _LOGGER.debug("Failed to log the account information: %s", ex, exc_info=True)
            return token
        except Exception as ex:
            _LOGGER.log(
                logging.DEBUG if within_credential_chain.get() else logging.WARNING,
                "%s failed: %s",
                fn.__qualname__,
                ex,
                exc_info=_LOGGER.isEnabledFor(logging.DEBUG),
            )
            raise

    return wrapper


def wrap_exceptions(fn):
    """Prevents leaking exceptions defined outside azure-core by raising ClientAuthenticationError from them.

    :param fn: The function to wrap.
    :type fn: ~typing.Callable
    :return: The wrapped function.
    :rtype: callable
    """

    @functools.wraps(fn)
    def wrapper(*args, **kwargs):
        try:
            return fn(*args, **kwargs)
        except ClientAuthenticationError:
            raise
        except Exception as ex:
            auth_error = ClientAuthenticationError(message="Authentication failed: {}".format(ex))
            raise auth_error from ex

    return wrapper
