from threading import Lock
from hashlib import sha256

from .individual_cache import _IndividualCache as IndividualCache
from .individual_cache import _ExpiringMapping as ExpiringMapping


# https://datatracker.ietf.org/doc/html/rfc8628#section-3.4
DEVICE_AUTH_GRANT = "urn:ietf:params:oauth:grant-type:device_code"


def _hash(raw):
    return sha256(repr(raw).encode("utf-8")).hexdigest()


def _parse_http_429_5xx_retry_after(result=None, **ignored):
    """Return seconds to throttle"""
    assert result is not None, """
        The signature defines it with a default value None,
        only because the its shape is already decided by the
        IndividualCache's.__call__().
        In actual code path, the result parameter here won't be None.
        """
    response = result
    lowercase_headers = {k.lower(): v for k, v in getattr(
        # Historically, MSAL's HttpResponse does not always have headers
        response, "headers", {}).items()}
    if not (response.status_code == 429 or response.status_code >= 500
            or "retry-after" in lowercase_headers):
        return 0  # Quick exit
    default = 60  # Recommended at the end of
        # https://identitydivision.visualstudio.com/devex/_git/AuthLibrariesApiReview?version=GBdev&path=%2FService%20protection%2FIntial%20set%20of%20protection%20measures.md&_a=preview
    retry_after = lowercase_headers.get("retry-after", default)
    try:
        # AAD's retry_after uses integer format only
        # https://stackoverflow.microsoft.com/questions/264931/264932
        delay_seconds = int(retry_after)
    except ValueError:
        delay_seconds = default
    return min(3600, delay_seconds)


def _extract_data(kwargs, key, default=None):
    data = kwargs.get("data", {})  # data is usually a dict, but occasionally a string
    return data.get(key) if isinstance(data, dict) else default


class ThrottledHttpClient(object):
    def __init__(self, http_client, http_cache):
        """Throttle the given http_client by storing and retrieving data from cache.

        This wrapper exists so that our patching post() and get() would prevent
        re-patching side effect when/if same http_client being reused.
        """
        expiring_mapping = ExpiringMapping(  # It will automatically clean up
            mapping=http_cache if http_cache is not None else {},
            capacity=1024,  # To prevent cache blowing up especially for CCA
            lock=Lock(),  # TODO: This should ideally also allow customization
            )

        _post = http_client.post  # We'll patch _post, and keep original post() intact

        _post = IndividualCache(
            # Internal specs requires throttling on at least token endpoint,
            # here we have a generic patch for POST on all endpoints.
            mapping=expiring_mapping,
            key_maker=lambda func, args, kwargs:
                "POST {} client_id={} scope={} hash={} 429/5xx/Retry-After".format(
                    args[0],  # It is the url, typically containing authority and tenant
                    _extract_data(kwargs, "client_id"),  # Per internal specs
                    _extract_data(kwargs, "scope"),  # Per internal specs
                    _hash(
                        # The followings are all approximations of the "account" concept
                        # to support per-account throttling.
                        # TODO: We may want to disable it for confidential client, though
                        _extract_data(kwargs, "refresh_token",  # "account" during refresh
                            _extract_data(kwargs, "code",  # "account" of auth code grant
                                _extract_data(kwargs, "username")))),  # "account" of ROPC
                    ),
            expires_in=_parse_http_429_5xx_retry_after,
            )(_post)

        _post = IndividualCache(  # It covers the "UI required cache"
            mapping=expiring_mapping,
            key_maker=lambda func, args, kwargs: "POST {} hash={} 400".format(
                args[0],  # It is the url, typically containing authority and tenant
                _hash(
                    # Here we use literally all parameters, even those short-lived
                    # parameters containing timestamps (WS-Trust or POP assertion),
                    # because they will automatically be cleaned up by ExpiringMapping.
                    #
                    # Furthermore, there is no need to implement
                    # "interactive requests would reset the cache",
                    # because acquire_token_silent()'s would be automatically unblocked
                    # due to token cache layer operates on top of http cache layer.
                    #
                    # And, acquire_token_silent(..., force_refresh=True) will NOT
                    # bypass http cache, because there is no real gain from that.
                    # We won't bother implement it, nor do we want to encourage
                    # acquire_token_silent(..., force_refresh=True) pattern.
                    str(kwargs.get("params")) + str(kwargs.get("data"))),
                ),
            expires_in=lambda result=None, kwargs=None, **ignored:
                60
                if result.status_code == 400
                    # Here we choose to cache exact HTTP 400 errors only (rather than 4xx)
                    # because they are the ones defined in OAuth2
                    # (https://datatracker.ietf.org/doc/html/rfc6749#section-5.2)
                    # Other 4xx errors might have different requirements e.g.
                    # "407 Proxy auth required" would need a key including http headers.
                and not(  # Exclude Device Flow whose retry is expected and regulated
                    isinstance(kwargs.get("data"), dict)
                    and kwargs["data"].get("grant_type") == DEVICE_AUTH_GRANT
                    )
                and "retry-after" not in set(  # Leave it to the Retry-After decorator
                    h.lower() for h in getattr(result, "headers", {}).keys())
                else 0,
            )(_post)

        self.post = _post

        self.get = IndividualCache(  # Typically those discovery GETs
            mapping=expiring_mapping,
            key_maker=lambda func, args, kwargs: "GET {} hash={} 2xx".format(
                args[0],  # It is the url, sometimes containing inline params
                _hash(kwargs.get("params", "")),
                ),
            expires_in=lambda result=None, **ignored:
                3600*24 if 200 <= result.status_code < 300 else 0,
            )(http_client.get)

        self._http_client = http_client

    # The following 2 methods have been defined dynamically by __init__()
    #def post(self, *args, **kwargs): pass
    #def get(self, *args, **kwargs): pass

    def close(self):
        """MSAL won't need this. But we allow throttled_http_client.close() anyway"""
        return self._http_client.close()

