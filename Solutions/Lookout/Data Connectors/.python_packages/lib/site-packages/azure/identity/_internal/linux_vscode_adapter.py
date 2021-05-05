# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import os
import json
import logging
import ctypes as ct
from .._constants import VSCODE_CREDENTIALS_SECTION

_LOGGER = logging.getLogger(__name__)


def _c_str(string):
    return ct.c_char_p(string.encode("utf-8"))


class _SECRET_SCHEMA_ATTRIBUTE(ct.Structure):
    _fields_ = [
        ("name", ct.c_char_p),
        ("type", ct.c_uint),
    ]


class _SECRET_SCHEMA(ct.Structure):
    _fields_ = [
        ("name", ct.c_char_p),
        ("flags", ct.c_uint),
        ("attributes", _SECRET_SCHEMA_ATTRIBUTE * 2),
    ]
_PSECRET_SCHEMA = ct.POINTER(_SECRET_SCHEMA)


try:
    _libsecret = ct.cdll.LoadLibrary("libsecret-1.so.0")
    _libsecret.secret_password_lookup_sync.argtypes = [
        ct.c_void_p,
        ct.c_void_p,
        ct.c_void_p,
        ct.c_char_p,
        ct.c_char_p,
        ct.c_char_p,
        ct.c_char_p,
        ct.c_void_p,
    ]
    _libsecret.secret_password_lookup_sync.restype = ct.c_char_p
    _libsecret.secret_password_free.argtypes = [ct.c_char_p]
except OSError:
    _libsecret = None


def _get_user_settings_path():
    app_data_folder = os.environ["HOME"]
    return os.path.join(app_data_folder, ".config", "Code", "User", "settings.json")


def _get_user_settings():
    path = _get_user_settings_path()
    try:
        with open(path) as file:
            data = json.load(file)
            environment_name = data.get("azure.cloud", "AzureCloud")
            return environment_name
    except IOError:
        return "AzureCloud"


def _get_refresh_token(service_name, account_name):
    if not _libsecret:
        return None

    err = ct.c_int()
    attributes = [_SECRET_SCHEMA_ATTRIBUTE(_c_str("service"), 0), _SECRET_SCHEMA_ATTRIBUTE(_c_str("account"), 0)]
    pattributes = (_SECRET_SCHEMA_ATTRIBUTE * 2)(*attributes)
    schema = _SECRET_SCHEMA()
    pschema = _PSECRET_SCHEMA(schema)
    ct.memset(pschema, 0, ct.sizeof(schema))
    schema.name = _c_str("org.freedesktop.Secret.Generic")  # pylint: disable=attribute-defined-outside-init
    schema.flags = 2    # pylint: disable=attribute-defined-outside-init
    schema.attributes = pattributes # pylint: disable=attribute-defined-outside-init
    p_str = _libsecret.secret_password_lookup_sync(
        pschema,
        None,
        ct.byref(err),
        _c_str("service"),
        _c_str(service_name),
        _c_str("account"),
        _c_str(account_name),
        None,
    )
    if err.value == 0:
        return p_str.decode("utf-8")

    return None


def get_credentials():
    try:
        environment_name = _get_user_settings()
        credentials = _get_refresh_token(VSCODE_CREDENTIALS_SECTION, environment_name)
        return credentials
    except Exception as ex:  # pylint: disable=broad-except
        _LOGGER.debug(
            'Exception retrieving VS Code credentials: "%s"', ex, exc_info=_LOGGER.isEnabledFor(logging.DEBUG)
        )
        return None
