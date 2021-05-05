# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import threading

try:
    import urllib.parse as parse
except ImportError:
    import urlparse as parse  # type: ignore

try:
    from typing import TYPE_CHECKING
except ImportError:
    TYPE_CHECKING = False

if TYPE_CHECKING:
    # pylint: disable=unused-import
    from typing import Dict
    from .http_challenge import HttpChallenge


_cache = {}  # type: Dict[str, HttpChallenge]
_lock = threading.Lock()


def get_challenge_for_url(url):
    """ Gets the challenge for the cached URL.
    :param url: the URL the challenge is cached for.
    :rtype: HttpBearerChallenge """

    if not url:
        raise ValueError("URL cannot be None")

    key = _get_cache_key(url)

    with _lock:
        return _cache.get(key)


def _get_cache_key(url):
    """Use the URL's netloc as cache key except when the URL specifies the default port for its scheme. In that case
    use the netloc without the port. That is to say, https://foo.bar and https://foo.bar:443 are considered equivalent.

    This equivalency prevents an unnecessary challenge when using Key Vault's paging API. The Key Vault client doesn't
    specify ports, but Key Vault's next page links do, so a redundant challenge would otherwise be executed when the
    client requests the next page."""

    parsed = parse.urlparse(url)
    if parsed.scheme == "https" and parsed.port == 443:
        return parsed.netloc[:-4]
    return parsed.netloc


def remove_challenge_for_url(url):
    """ Removes the cached challenge for the specified URL.
    :param url: the URL for which to remove the cached challenge """
    if not url:
        raise ValueError("URL cannot be empty")

    url = parse.urlparse(url)

    with _lock:
        del _cache[url.netloc]


def set_challenge_for_url(url, challenge):
    """ Caches the challenge for the specified URL.
    :param url: the URL for which to cache the challenge
    :param challenge: the challenge to cache """
    if not url:
        raise ValueError("URL cannot be empty")

    if not challenge:
        raise ValueError("Challenge cannot be empty")

    src_url = parse.urlparse(url)
    if src_url.netloc != challenge.source_authority:
        raise ValueError("Source URL and Challenge URL do not match")

    with _lock:
        _cache[src_url.netloc] = challenge


def clear():
    """ Clears the cache. """

    with _lock:
        _cache.clear()
