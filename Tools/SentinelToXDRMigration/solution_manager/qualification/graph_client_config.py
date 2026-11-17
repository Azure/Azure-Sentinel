from __future__ import annotations

import hashlib
import json
import os
import re
import stat
import threading
from contextlib import contextmanager
from pathlib import Path
from typing import Any, Iterator

DEFAULT_GRAPH_CLIENT_ID = "14d82eec-204b-4c2f-b7e8-296a70dab67e"
PRIVATE_AUTH_CONFIG_NAME = "private-auth-config.json"

_CLIENT_KEYS = {
    "appRegistration": "appRegistrationClientId",
    "appReadback": "appReadbackClientId",
    "advancedHunting": "advancedHuntingClientId",
    "customDetection": "customDetectionClientId",
}
_PROFILE_LOCK = threading.RLock()


def _private_state_root(state_root: str | Path) -> Path:
    root = Path(state_root).expanduser().resolve()
    if any(part.casefold() in {"logs", ".env"} for part in root.parts):
        raise ValueError(
            "private Graph authentication state must not be stored under Logs or .env"
        )
    return root


def ensure_private_state_root(state_root: str | Path) -> Path:
    root = _private_state_root(state_root)
    root.mkdir(parents=True, exist_ok=True)
    restrict_private_permissions(root, 0o700)
    return root


def restrict_private_permissions(path: str | Path, mode: int) -> None:
    target = Path(path)
    try:
        target.chmod(mode)
    except OSError as exc:
        if os.name == "posix":
            raise RuntimeError(
                f"could not restrict private authentication permissions on {target}"
            ) from exc
    if os.name == "posix" and stat.S_IMODE(target.stat().st_mode) != mode:
        raise RuntimeError(
            f"private authentication permissions are not restricted on {target}"
        )


def _valid_client_id(value: str, *, label: str = "Graph client ID") -> str:
    normalized = value.strip().lower()
    if not re.fullmatch(
        r"[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}",
        normalized,
    ):
        raise ValueError(f"{label} must be a GUID")
    return normalized


def _read_config(state_root: str | Path) -> dict[str, Any]:
    root = _private_state_root(state_root)
    path = root / PRIVATE_AUTH_CONFIG_NAME
    if not path.exists():
        return {"schemaVersion": 1, "graphClientIds": {}}
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError(f"private Graph client configuration is unreadable: {exc}") from exc
    if not isinstance(value, dict) or value.get("schemaVersion") != 1:
        raise ValueError("private Graph client configuration has an unsupported schema")
    clients = value.get("graphClientIds", {})
    if not isinstance(clients, dict):
        raise ValueError("private Graph client configuration has invalid graphClientIds")
    for purpose, client_id in clients.items():
        if purpose not in _CLIENT_KEYS:
            raise ValueError(f"unsupported Graph client purpose: {purpose}")
        if not isinstance(client_id, str):
            raise ValueError(f"Graph client ID for {purpose} must be a string")
        _valid_client_id(client_id)
    azure_config_dir = value.get("azureConfigDir")
    if azure_config_dir is not None:
        if not isinstance(azure_config_dir, str) or not Path(azure_config_dir).is_absolute():
            raise ValueError("azureConfigDir must be an absolute path")
        profile = Path(azure_config_dir).expanduser().resolve()
        if any(part.casefold() in {"logs", ".env"} for part in profile.parts):
            raise ValueError("azureConfigDir must not be stored under Logs or .env")
        if profile == (Path.home() / ".azure").resolve():
            raise ValueError("azureConfigDir must not replace the default Azure CLI profile")
    return value


def read_private_auth_config(state_root: str | Path) -> dict[str, Any]:
    config = _read_config(state_root)
    return {
        "schemaVersion": config["schemaVersion"],
        "graphClientIds": dict(config.get("graphClientIds", {})),
        "azureConfigDir": config.get("azureConfigDir"),
    }


def _write_config(state_root: str | Path, config: dict[str, Any]) -> Path:
    root = ensure_private_state_root(state_root)
    path = root / PRIVATE_AUTH_CONFIG_NAME
    path.write_text(
        json.dumps(config, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    restrict_private_permissions(path, 0o600)
    return path


def configure_graph_client(
    state_root: str | Path,
    purpose: str,
    client_id: str,
) -> dict[str, str]:
    if purpose not in _CLIENT_KEYS:
        raise ValueError(f"purpose must be one of {', '.join(sorted(_CLIENT_KEYS))}")
    normalized = _valid_client_id(client_id)
    config = _read_config(state_root)
    clients = config.setdefault("graphClientIds", {})
    clients[purpose] = normalized
    path = _write_config(state_root, config)
    return {"purpose": purpose, "clientId": normalized, "configPath": str(path)}


def configure_azure_cli_profile(
    state_root: str | Path,
    azure_config_dir: str | Path,
) -> dict[str, str]:
    path = Path(azure_config_dir).expanduser()
    if not path.is_absolute():
        raise ValueError("azure-config-dir must be an absolute path")
    normalized = str(path.resolve())
    protected_profiles = {str((Path.home() / ".azure").resolve())}
    current_profile = os.environ.get("AZURE_CONFIG_DIR")
    if current_profile:
        protected_profiles.add(str(Path(current_profile).expanduser().resolve()))
    if normalized in protected_profiles:
        raise ValueError(
            "azure-config-dir must be a separate profile and must not replace "
            "the current Azure CLI profile"
        )
    if any(part.casefold() in {"logs", ".env"} for part in path.parts):
        raise ValueError("azure-config-dir must not be stored in operational Logs or .env")
    config = _read_config(state_root)
    config["azureConfigDir"] = normalized
    config_path = _write_config(state_root, config)
    return {"azureConfigDir": normalized, "configPath": str(config_path)}


def read_delegated_app_registration(state_root: str | Path) -> dict[str, Any] | None:
    value = _read_config(state_root).get("delegatedAppRegistration")
    return dict(value) if isinstance(value, dict) else None


def write_delegated_app_registration(
    state_root: str | Path,
    registration: dict[str, Any],
    *,
    custom_detection_client_id: str | None = None,
    advanced_hunting_client_id: str | None = None,
) -> Path:
    config = _read_config(state_root)
    config["delegatedAppRegistration"] = registration
    if custom_detection_client_id:
        clients = config.setdefault("graphClientIds", {})
        clients["customDetection"] = _valid_client_id(custom_detection_client_id)
    if advanced_hunting_client_id:
        clients = config.setdefault("graphClientIds", {})
        clients["advancedHunting"] = _valid_client_id(advanced_hunting_client_id)
    return _write_config(state_root, config)


def resolve_graph_client_id(
    state_root: str | Path,
    purpose: str,
    client_id: str | None = None,
) -> str:
    if purpose not in _CLIENT_KEYS:
        raise ValueError(f"purpose must be one of {', '.join(sorted(_CLIENT_KEYS))}")
    if client_id is not None:
        return _valid_client_id(client_id)
    value = _read_config(state_root).get("graphClientIds", {}).get(purpose)
    return _valid_client_id(value) if value else DEFAULT_GRAPH_CLIENT_ID


def graph_auth_record_path(
    state_root: str | Path,
    purpose: str,
    client_id: str,
    legacy_name: str,
) -> Path:
    root = _private_state_root(state_root)
    normalized = _valid_client_id(client_id)
    base = root / legacy_name
    if normalized == DEFAULT_GRAPH_CLIENT_ID:
        return base
    suffix = hashlib.sha256(f"{purpose}:{normalized}".encode("utf-8")).hexdigest()[:12]
    return base.with_name(f"{base.stem}.{suffix}{base.suffix}")


def graph_token_cache_name(
    purpose: str,
    client_id: str,
    legacy_name: str,
) -> str:
    normalized = _valid_client_id(client_id)
    if normalized == DEFAULT_GRAPH_CLIENT_ID:
        return legacy_name
    suffix = hashlib.sha256(f"{purpose}:{normalized}".encode("utf-8")).hexdigest()[:12]
    return f"{legacy_name}_{suffix}"


def graph_auth_metadata_path(record_path: str | Path) -> Path:
    path = Path(record_path)
    return path.with_name(f"{path.name}.metadata.json")


def write_graph_auth_metadata(
    record_path: str | Path,
    *,
    purpose: str,
    client_id: str,
    tenant_id: str | None,
) -> None:
    path = Path(record_path)
    _private_state_root(path.parent)
    payload = {
        "schemaVersion": 1,
        "purpose": purpose,
        "clientId": _valid_client_id(client_id),
        "tenantId": tenant_id.strip().lower() if tenant_id else None,
    }
    metadata = graph_auth_metadata_path(path)
    metadata.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    restrict_private_permissions(metadata, 0o600)


def verify_graph_auth_binding(
    record_path: str | Path,
    record: Any,
    *,
    purpose: str,
    client_id: str,
    tenant_id: str | None,
) -> None:
    path = Path(record_path)
    expected_client = _valid_client_id(client_id)
    metadata_path = graph_auth_metadata_path(path)
    metadata: dict[str, Any] = {}
    if metadata_path.exists():
        try:
            value = json.loads(metadata_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            raise ValueError(f"Graph authentication binding metadata is unreadable: {exc}") from exc
        if not isinstance(value, dict) or value.get("schemaVersion") != 1:
            raise ValueError("Graph authentication binding metadata has an unsupported schema")
        metadata = value
        if metadata.get("purpose") != purpose:
            raise ValueError("cached Graph authentication purpose does not match the request")
        if _valid_client_id(str(metadata.get("clientId") or "")) != expected_client:
            raise ValueError("cached Graph authentication client does not match the request")
    elif expected_client != DEFAULT_GRAPH_CLIENT_ID:
        raise ValueError("custom Graph authentication record has no client binding metadata")

    record_client_id = getattr(record, "client_id", None)
    if record_client_id and _valid_client_id(str(record_client_id)) != expected_client:
        raise ValueError("cached Graph authentication client does not match the request")
    record_tenant = getattr(record, "tenant_id", None)
    bound_tenant = metadata.get("tenantId") or record_tenant
    if tenant_id:
        if not bound_tenant:
            raise ValueError(
                "cached Graph authentication has no verifiable tenant binding"
            )
        if str(tenant_id).casefold() != str(bound_tenant).casefold():
            raise ValueError(
                "cached Graph authentication tenant does not match the locked target"
            )
    if metadata.get("tenantId") and record_tenant and (
        str(metadata["tenantId"]).casefold() != str(record_tenant).casefold()
    ):
        raise ValueError("cached Graph authentication record conflicts with its tenant binding")


@contextmanager
def azure_cli_profile(azure_config_dir: str | Path | None) -> Iterator[None]:
    if azure_config_dir is None:
        yield
        return
    path = Path(azure_config_dir).expanduser()
    if not path.is_absolute():
        raise ValueError("AZURE_CONFIG_DIR must be an absolute path")
    normalized = str(path.resolve())
    with _PROFILE_LOCK:
        previous = os.environ.get("AZURE_CONFIG_DIR")
        os.environ["AZURE_CONFIG_DIR"] = normalized
        try:
            yield
        finally:
            if previous is None:
                os.environ.pop("AZURE_CONFIG_DIR", None)
            else:
                os.environ["AZURE_CONFIG_DIR"] = previous


def configured_azure_cli_profile(state_root: str | Path) -> str | None:
    value = _read_config(state_root).get("azureConfigDir")
    return str(value) if value else None


def azure_cli_credential(
    *,
    tenant_id: str | None = None,
    state_root: str | Path | None = None,
    subscription: str | None = None,
):
    from azure.identity import AzureCliCredential

    azure_config_dir = (
        configured_azure_cli_profile(state_root)
        if state_root is not None
        else None
    )
    credential = AzureCliCredential(
        tenant_id=tenant_id,
        subscription=subscription,
    )

    class ProfiledCredential:
        def get_token(self, *scopes: str, **kwargs: Any):
            with azure_cli_profile(azure_config_dir):
                try:
                    return credential.get_token(*scopes, **kwargs)
                except Exception:
                    if tenant_id and subscription:
                        return AzureCliCredential(tenant_id=tenant_id).get_token(
                            *scopes, **kwargs
                        )
                    raise

        def get_token_info(self, *scopes: str, **kwargs: Any):
            with azure_cli_profile(azure_config_dir):
                token_info_fn = getattr(
                    credential, "get_token_info", None
                ) or getattr(credential, "get_token")
                try:
                    return token_info_fn(*scopes, **kwargs)
                except Exception:
                    if tenant_id and subscription:
                        fallback = AzureCliCredential(tenant_id=tenant_id)
                        fallback_fn = getattr(
                            fallback, "get_token_info", None
                        ) or getattr(fallback, "get_token")
                        return fallback_fn(*scopes, **kwargs)
                    raise

        def __getattr__(self, name: str) -> Any:
            return getattr(credential, name)

    return ProfiledCredential()
