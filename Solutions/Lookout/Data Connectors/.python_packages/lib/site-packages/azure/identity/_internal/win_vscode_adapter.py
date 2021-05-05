# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import os
import json
import logging
import ctypes as ct
from .._constants import VSCODE_CREDENTIALS_SECTION

try:
    import ctypes.wintypes as wt
except (IOError, ValueError):
    pass

_LOGGER = logging.getLogger(__name__)

SUPPORTED_CREDKEYS = set(("Type", "TargetName", "Persist", "UserName", "Comment", "CredentialBlob"))

_PBYTE = ct.POINTER(ct.c_byte)


class _CREDENTIAL(ct.Structure):
    _fields_ = [
        ("Flags", wt.DWORD),
        ("Type", wt.DWORD),
        ("TargetName", ct.c_wchar_p),
        ("Comment", ct.c_wchar_p),
        ("LastWritten", wt.FILETIME),
        ("CredentialBlobSize", wt.DWORD),
        ("CredentialBlob", _PBYTE),
        ("Persist", wt.DWORD),
        ("AttributeCount", wt.DWORD),
        ("Attributes", ct.c_void_p),
        ("TargetAlias", ct.c_wchar_p),
        ("UserName", ct.c_wchar_p),
    ]


_PCREDENTIAL = ct.POINTER(_CREDENTIAL)

_advapi = ct.WinDLL("advapi32")
_advapi.CredReadW.argtypes = [wt.LPCWSTR, wt.DWORD, wt.DWORD, ct.POINTER(_PCREDENTIAL)]
_advapi.CredReadW.restype = wt.BOOL
_advapi.CredFree.argtypes = [_PCREDENTIAL]


def _read_credential(service_name, account_name):
    target = "{}/{}".format(service_name, account_name)
    cred_ptr = _PCREDENTIAL()
    if _advapi.CredReadW(target, 1, 0, ct.byref(cred_ptr)):
        cred_blob = cred_ptr.contents.CredentialBlob
        cred_blob_size = cred_ptr.contents.CredentialBlobSize
        cred = "".join(map(chr, cred_blob[:cred_blob_size]))
        _advapi.CredFree(cred_ptr)
        return cred
    return None


def _get_user_settings_path():
    app_data_folder = os.environ["APPDATA"]
    return os.path.join(app_data_folder, "Code", "User", "settings.json")


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
    return _read_credential(service_name, account_name)


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
