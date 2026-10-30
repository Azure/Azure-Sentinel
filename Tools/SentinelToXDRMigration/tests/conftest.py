from __future__ import annotations

import atexit
from contextlib import ExitStack, contextmanager
import importlib
import os
from pathlib import Path
import tempfile
from typing import Iterator
import unittest
from unittest import mock


_GUARDED_TARGETS: tuple[tuple[str, str, tuple[str, ...]], ...] = (
    (
        "azure.identity",
        "InteractiveBrowserCredential",
        ("get_token", "get_token_info", "authenticate"),
    ),
    (
        "azure.identity",
        "DeviceCodeCredential",
        ("get_token", "get_token_info", "authenticate"),
    ),
    (
        "azure.identity",
        "AzureCliCredential",
        ("get_token", "get_token_info"),
    ),
    (
        "msal",
        "PublicClientApplication",
        (
            "acquire_token_interactive",
            "acquire_token_by_device_flow",
            "initiate_device_flow",
            "acquire_token_silent",
        ),
    ),
    (
        "msal",
        "ConfidentialClientApplication",
        (
            "acquire_token_for_client",
            "acquire_token_silent",
        ),
    ),
)

_UNITTEST_GUARD_INSTALLED = False
_PROCESS_GUARD_STACK: ExitStack | None = None


def _blocked_auth_method(qualname: str):
    def _blocker(*_args, **_kwargs):
        raise RuntimeError(
            f"Unmocked live authentication call blocked by test isolation guard: {qualname}"
        )

    return _blocker


@contextmanager
def isolated_auth_guard() -> Iterator[Path]:
    """Block unmocked live authentication calls and isolate AZURE_CONFIG_DIR."""
    with ExitStack() as stack:
        temp_dir = stack.enter_context(
            tempfile.TemporaryDirectory(prefix="sentinel-xdr-test-azure-cli-")
        )
        isolated_profile = (Path(temp_dir) / "azure-cli-profile").resolve()
        isolated_profile.mkdir(parents=True, exist_ok=True)
        stack.enter_context(
            mock.patch.dict(
                os.environ,
                {"AZURE_CONFIG_DIR": str(isolated_profile)},
                clear=False,
            )
        )
        for module_name, class_name, methods in _GUARDED_TARGETS:
            try:
                module = importlib.import_module(module_name)
            except ImportError:
                continue
            target_cls = getattr(module, class_name, None)
            if target_cls is None:
                continue
            for method_name in methods:
                if hasattr(target_cls, method_name):
                    qualname = f"{class_name}.{method_name}"
                    stack.enter_context(
                        mock.patch.object(
                            target_cls,
                            method_name,
                            side_effect=_blocked_auth_method(qualname),
                        )
                    )
        yield isolated_profile


def install_unittest_auth_guard() -> None:
    """Install isolated_auth_guard around unittest.TestCase.run and process default."""
    global _UNITTEST_GUARD_INSTALLED, _PROCESS_GUARD_STACK
    if _PROCESS_GUARD_STACK is None:
        stack = ExitStack()
        stack.enter_context(isolated_auth_guard())
        _PROCESS_GUARD_STACK = stack
        atexit.register(stack.close)

    if _UNITTEST_GUARD_INSTALLED:
        return

    original_run = unittest.TestCase.run

    def _guarded_run(self: unittest.TestCase, result=None):
        with isolated_auth_guard():
            return original_run(self, result=result)

    unittest.TestCase.run = _guarded_run  # type: ignore[method-assign]
    _UNITTEST_GUARD_INSTALLED = True


install_unittest_auth_guard()

try:
    import pytest
except ImportError:  # pragma: no cover
    pytest = None  # type: ignore[assignment]

if pytest is not None:

    @pytest.fixture(autouse=True)
    def _enforce_isolated_auth_and_cli_profile() -> Iterator[Path]:
        with isolated_auth_guard() as profile_dir:
            yield profile_dir
