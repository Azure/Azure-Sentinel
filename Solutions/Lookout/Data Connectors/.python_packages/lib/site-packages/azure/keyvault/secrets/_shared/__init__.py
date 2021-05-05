# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
from collections import namedtuple

try:
    import urllib.parse as parse
except ImportError:
    # pylint:disable=import-error
    import urlparse as parse  # type: ignore

from .challenge_auth_policy import ChallengeAuthPolicy, ChallengeAuthPolicyBase
from .client_base import KeyVaultClientBase
from .http_challenge import HttpChallenge
from . import http_challenge_cache as HttpChallengeCache


__all__ = [
    "ChallengeAuthPolicy",
    "ChallengeAuthPolicyBase",
    "HttpChallenge",
    "HttpChallengeCache",
    "KeyVaultClientBase",
]

_VaultId = namedtuple("VaultId", ["vault_url", "collection", "name", "version"])


def parse_vault_id(url):
    try:
        parsed_uri = parse.urlparse(url)
    except Exception:  # pylint: disable=broad-except
        raise ValueError("'{}' is not not a valid url".format(url))
    if not (parsed_uri.scheme and parsed_uri.hostname):
        raise ValueError("'{}' is not not a valid url".format(url))

    path = list(filter(None, parsed_uri.path.split("/")))

    if len(path) < 2 or len(path) > 3:
        raise ValueError("'{}' is not not a valid vault url".format(url))

    return _VaultId(
        vault_url="{}://{}".format(parsed_uri.scheme, parsed_uri.hostname),
        collection=path[0],
        name=path[1],
        version=path[2] if len(path) == 3 else None,
    )


try:
    # pylint:disable=unused-import
    from .async_challenge_auth_policy import AsyncChallengeAuthPolicy
    from .async_client_base import AsyncKeyVaultClientBase

    __all__.extend(["AsyncChallengeAuthPolicy", "AsyncKeyVaultClientBase"])
except (SyntaxError, ImportError):
    pass
