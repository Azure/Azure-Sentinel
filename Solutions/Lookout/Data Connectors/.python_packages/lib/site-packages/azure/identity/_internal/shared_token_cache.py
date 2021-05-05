# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import abc
import platform
import time

from msal import TokenCache
import six
from six.moves.urllib_parse import urlparse

from azure.core.credentials import AccessToken
from .. import CredentialUnavailableError
from .._constants import KnownAuthorities
from .._internal import get_default_authority, normalize_authority, wrap_exceptions
from .._internal.persistent_cache import load_user_cache

try:
    ABC = abc.ABC
except AttributeError:  # Python 2.7, abc exists, but not ABC
    ABC = abc.ABCMeta("ABC", (object,), {"__slots__": ()})  # type: ignore

try:
    from typing import TYPE_CHECKING
except ImportError:
    TYPE_CHECKING = False

if TYPE_CHECKING:
    # pylint:disable=unused-import,ungrouped-imports
    from typing import Any, Iterable, List, Mapping, Optional
    from .._internal import AadClientBase

    CacheItem = Mapping[str, str]


MULTIPLE_ACCOUNTS = """SharedTokenCacheCredential authentication unavailable. Multiple accounts
were found in the cache. Use username and tenant id to disambiguate."""

MULTIPLE_MATCHING_ACCOUNTS = """SharedTokenCacheCredential authentication unavailable. Multiple accounts
matching the specified{}{} were found in the cache."""

NO_ACCOUNTS = """SharedTokenCacheCredential authentication unavailable. No accounts were found in the cache."""

NO_MATCHING_ACCOUNTS = """SharedTokenCacheCredential authentication unavailable. No account
matching the specified{}{} was found in the cache."""

NO_TOKEN = """Token acquisition failed for user '{}'. To fix, re-authenticate
through developer tooling supporting Azure single sign on"""

# build a dictionary {authority: {its known aliases}}, aliases taken from MSAL.NET's KnownMetadataProvider
KNOWN_ALIASES = {
    alias: aliases  # N.B. aliases includes alias itself
    for aliases in (
        frozenset((KnownAuthorities.AZURE_CHINA, "login.partner.microsoftonline.cn")),
        frozenset((KnownAuthorities.AZURE_PUBLIC_CLOUD, "login.windows.net", "login.microsoft.com", "sts.windows.net")),
        frozenset((KnownAuthorities.AZURE_GOVERNMENT, "login.usgovcloudapi.net")),
    )
    for alias in aliases
}


def _account_to_string(account):
    username = account.get("username")
    home_account_id = account.get("home_account_id", "").split(".")
    tenant_id = home_account_id[-1] if len(home_account_id) == 2 else ""
    return "(username: {}, tenant: {})".format(username, tenant_id)


def _filtered_accounts(accounts, username=None, tenant_id=None):
    """yield accounts matching username and/or tenant_id"""

    filtered_accounts = []
    for account in accounts:
        if username and account.get("username") != username:
            continue
        if tenant_id:
            try:
                _, tenant = account["home_account_id"].split(".")
                if tenant_id != tenant:
                    continue
            except Exception:  # pylint:disable=broad-except
                continue
        filtered_accounts.append(account)
    return filtered_accounts


class SharedTokenCacheBase(ABC):
    def __init__(self, username=None, **kwargs):  # pylint:disable=unused-argument
        # type: (Optional[str], **Any) -> None
        authority = kwargs.pop("authority", None)
        self._authority = normalize_authority(authority) if authority else get_default_authority()
        environment = urlparse(self._authority).netloc
        self._environment_aliases = KNOWN_ALIASES.get(environment) or frozenset((environment,))
        self._username = username
        self._tenant_id = kwargs.pop("tenant_id", None)
        self._cache = kwargs.pop("_cache", None)
        self._client = None  # type: Optional[AadClientBase]
        self._client_kwargs = kwargs
        self._client_kwargs["tenant_id"] = "organizations"
        self._initialized = False

    def _initialize(self):
        if self._initialized:
            return

        self._load_cache()
        if self._cache:
            self._client = self._get_auth_client(authority=self._authority, cache=self._cache, **self._client_kwargs)

        self._initialized = True

    def _load_cache(self):
        if not self._cache and self.supported():
            allow_unencrypted = self._client_kwargs.get("_allow_unencrypted_cache", True)
            try:
                self._cache = load_user_cache(allow_unencrypted)
            except Exception:  # pylint:disable=broad-except
                pass

    @abc.abstractmethod
    def _get_auth_client(self, **kwargs):
        # type: (**Any) -> AadClientBase
        pass

    def _get_cache_items_for_authority(self, credential_type):
        # type: (TokenCache.CredentialType) -> List[CacheItem]
        """yield cache items matching this credential's authority or one of its aliases"""

        items = []
        for item in self._cache.find(credential_type):
            environment = item.get("environment")
            if environment in self._environment_aliases:
                items.append(item)
        return items

    def _get_accounts_having_matching_refresh_tokens(self):
        # type: () -> Iterable[CacheItem]
        """returns an iterable of cached accounts which have a matching refresh token"""

        refresh_tokens = self._get_cache_items_for_authority(TokenCache.CredentialType.REFRESH_TOKEN)
        all_accounts = self._get_cache_items_for_authority(TokenCache.CredentialType.ACCOUNT)

        accounts = {}
        for refresh_token in refresh_tokens:
            home_account_id = refresh_token.get("home_account_id")
            if not home_account_id:
                continue
            for account in all_accounts:
                # When the token has no family, msal.net falls back to matching client_id,
                # which won't work for the shared cache because we don't know the IDs of
                # all contributing apps. It should be unnecessary anyway because the
                # apps should all belong to the family.
                if home_account_id == account.get("home_account_id") and "family_id" in refresh_token:
                    accounts[account["home_account_id"]] = account
        return accounts.values()

    @wrap_exceptions
    def _get_account(self, username=None, tenant_id=None):
        # type: (Optional[str], Optional[str]) -> CacheItem
        """returns exactly one account which has a refresh token and matches username and/or tenant_id"""

        accounts = self._get_accounts_having_matching_refresh_tokens()
        if not accounts:
            # cache is empty or contains no refresh token -> user needs to sign in
            raise CredentialUnavailableError(message=NO_ACCOUNTS)

        filtered_accounts = _filtered_accounts(accounts, username, tenant_id)
        if len(filtered_accounts) == 1:
            return filtered_accounts[0]

        # no, or multiple, accounts after filtering -> choose the best error message
        cached_accounts = ", ".join(_account_to_string(account) for account in accounts)
        if username or tenant_id:
            username_string = " username: {}".format(username) if username else ""
            tenant_string = " tenant: {}".format(tenant_id) if tenant_id else ""
            if filtered_accounts:
                message = MULTIPLE_MATCHING_ACCOUNTS.format(username_string, tenant_string)
            else:
                message = NO_MATCHING_ACCOUNTS.format(username_string, tenant_string)
        else:
            message = MULTIPLE_ACCOUNTS.format(cached_accounts)

        raise CredentialUnavailableError(message=message)

    def _get_cached_access_token(self, scopes, account):
        # type: (Iterable[str], CacheItem) -> Optional[AccessToken]
        if "home_account_id" not in account:
            return None

        try:
            cache_entries = self._cache.find(
                TokenCache.CredentialType.ACCESS_TOKEN,
                target=list(scopes),
                query={"home_account_id": account["home_account_id"]},
            )
            for token in cache_entries:
                expires_on = int(token["expires_on"])
                if expires_on - 300 > int(time.time()):
                    return AccessToken(token["secret"], expires_on)
        except Exception as ex:  # pylint:disable=broad-except
            message = "Error accessing cached data: {}".format(ex)
            six.raise_from(CredentialUnavailableError(message=message), ex)

        return None

    def _get_refresh_tokens(self, account):
        if "home_account_id" not in account:
            return None

        try:
            cache_entries = self._cache.find(
                TokenCache.CredentialType.REFRESH_TOKEN, query={"home_account_id": account["home_account_id"]}
            )
            return [token["secret"] for token in cache_entries if "secret" in token]
        except Exception as ex:  # pylint:disable=broad-except
            message = "Error accessing cached data: {}".format(ex)
            six.raise_from(CredentialUnavailableError(message=message), ex)

    @staticmethod
    def supported():
        # type: () -> bool
        """Whether the shared token cache is supported on the current platform.

        :rtype: bool
        """
        return platform.system() in {"Darwin", "Linux", "Windows"}
