'''
Sessions
========

.. autoclass:: APISession
    :members:
    :private-members:
'''
import sys
import time
import warnings
import platform
import json
import logging
from typing import Union, Dict, List
from urllib.parse import urlparse
from requests import Response, Session
from requests.exceptions import (
    ConnectionError as RequestsConnectionError,
    RequestException as RequestsRequestException
)
from box import Box, BoxList
from .utils import dict_merge, redact_values
from . import errors
from .version import VERSION


class APISession:  # noqa: PLR0902
    '''
    The APISession class is the base model for APISessions for different
    products and applications.  This is the model that the APIEndpoints
    will be grafted onto and supports some basic wrapping of standard HTTP
    methods on it's own.

    Attributes:
        _box (bool):
            Should responses be converted to Box objects automatically by
            default?  If left unspecified, the default is `False`
        _build (str):
            The build number/version of the integration.
        _backoff (float):
            The default backoff timer to use when retrying.  The value is
            either a float or integer denoting the number of seconds to delay
            before the next retry attempt.  The number will be multiplied by
            the number of retries attempted.
        _base_error_map (dict):
            The error mapping detailing what HTTP response code should throw
            what kind of error.  As this is the base mapping, overloading this
            would remove any pre-set error mappings.
        _error_map (dict):
            The error mapping detailing what HTTP response code should throw
            what kind of error.  This error map will overload specific error
            mappings.
        _error_on_unexpected_input (bool):
            If unexpected keywords have been passed to the session constructor,
            should we raise an error?  Default is ``False``.
        _lib_name (str):
            The name of the library.
        _lib_version (str):
            The version of the library.
        _product (str):
            The product name for the integration.
        _proxies (dict):
            A dictionary detailing what proxy should be used for what transport
            protocol.  This value will be passed to the session object after it
            has been either attached or created.  For details on the structure
            of this dictionary, consult the
            :requests:`Requests documentation.<user/advanced/#proxies>`
        _restricted_paths (list[str]):
            A list of paths (not complete URIs) that if seen be the
            :obj:`_req` method will not pass the query params or the
            request body into the logging facility.  This should generally be
            used for paths that are sensitive in nature (such as logins).
        _retries (int):
            The number of retries to make before failing a request.  The
            default is 3.
        _session (requests.Session):
            Provide a pre-built session instead of creating a requests session
            at instantiation.
        _ssl_verify (bool):
            Should SSL verification be performed?  If not, then inform requests
            that we don't want to use SSL verification and suppress the SSL
            certificate warnings.
        _timeout (int):
            The number of seconds to wait with no data returned before
            declaring the request as stalled and timing-out the request.
        _url (str):
            The base URL path to use.  This should generally be a string value
            denoting the first half of the URI.  For example,
            ``https://httpbin.org`` or ``https://example.api.site/api/2``.  The
            :obj:`_req` method will join this string with the incoming path
            to construct the complete URI.  Note that the two strings will be
            joined with a backslash ``/``.
        _vendor (str):
            The vendor name for the integration.

    Args:
        adaptor (Object, optional):
            A Requests Session adaptor to bind to the session object.
        backoff (float, optional):
            If a 429 response is returned, how much do we want to backoff
            if the response didn't send a Retry-After header.
        build (str, optional):
            The build number to put into the User-Agent string.
        product (str, optional):
            The product name to put into the User-Agent string.
        proxies (dict, optional):
            A dictionary detailing what proxy should be used for what
            transport protocol.  This value will be passed to the session
            object after it has been either attached or created.  For
            details on the structure of this dictionary, consult the
            :requests:`proxies <user/advanced/#proxies>` section of the
            Requests documentation.
        retries (int, optional):
            The number of retries to make before failing a request.  The
            default is 3.
        session (requests.Session, optional):
            Provide a pre-built session instead of creating a requests
            session at instantiation.
        ssl_verify (bool, optional):
            If SSL Verification needs to be disabled (for example when using
            a self-signed certificate), then this parameter should be set to
            ``False`` to disable verification and mask the Certificate
            warnings.
        url (str, optional):
            The base URL that the paths will be appended onto.
        vendor (str, optional):
            The vendor name to put into the User-Agent string.
    '''
    _url = None
    _base_path = None
    _retries = 3
    _backoff = 1
    _proxies = None
    _ssl_verify = True
    _lib_name = 'Restfly'
    _lib_version = VERSION
    _restricted_paths = []
    _vendor = 'unknown'
    _product = 'unknown'
    _build = 'unknown'
    _adaptor = None
    _timeout = None
    _conv_json = False
    _box = False
    _box_attrs = {}
    _error_map = {}
    _error_on_unexpected_input = False
    _base_error_map = {
        400: errors.BadRequestError,
        401: errors.UnauthorizedError,
        403: errors.ForbiddenError,
        404: errors.NotFoundError,
        405: errors.InvalidMethodError,
        406: errors.NotAcceptableError,
        407: errors.ProxyAuthenticationError,
        408: errors.RequestTimeoutError,
        409: errors.RequestConflictError,
        410: errors.NoLongerExistsError,
        411: errors.LengthRequiredError,
        412: errors.PreconditionFailedError,
        413: errors.PayloadTooLargeError,
        414: errors.URITooLongError,
        415: errors.UnsupportedMediaTypeError,
        416: errors.RangeNotSatisfiableError,
        417: errors.ExpectationFailedError,
        418: errors.TeapotResponseError,
        420: errors.TooManyRequestsError,
        421: errors.MisdirectRequestError,
        425: errors.TooEarlyError,
        426: errors.UpgradeRequiredError,
        428: errors.PreconditionRequiredError,
        429: errors.TooManyRequestsError,
        431: errors.RequestHeaderFieldsTooLargeError,
        451: errors.UnavailableForLegalReasonsError,
        500: errors.ServerError,
        501: errors.MethodNotImplementedError,
        502: errors.BadGatewayError,
        503: errors.ServiceUnavailableError,
        504: errors.GatewayTimeoutError,
        510: errors.NotExtendedError,
        511: errors.NetworkAuthenticationRequiredError,
    }

    def __enter__(self):
        '''
        Context Manager __enter__ built-in method. See PEP-343 for more
        details.
        '''
        return self

    def __exit__(self, exc_type, exc_value, exc_traceback):
        '''
        Context Manager __exit__ built-in method. See PEP-343 for more details.
        '''
        return self._deauthenticate()

    def __init__(self, **kwargs):
        # Construct the error map from the base mapping, then overload the map
        # with anything specified in the error map parameter and then store the
        # final result in the error map parameter.  This allows for overloading
        # specific items if necessary without having to re-construct the whole
        # map.
        self._error_map = dict_merge(self._base_error_map, self._error_map)

        # Assign the kw arguments to the private attributes.
        self._url = kwargs.pop('url', self._url)
        self._base_path = kwargs.pop('base_path', self._base_path)
        self._retries = int(kwargs.pop('retries', self._retries))
        self._backoff = float(kwargs.pop('backoff', self._backoff))
        self._proxies = kwargs.pop('proxies', self._proxies)
        self._ssl_verify = kwargs.pop('ssl_verify', self._ssl_verify)
        self._adaptor = kwargs.pop('adaptor', self._adaptor)
        self._vendor = kwargs.pop('vendor', self._vendor)
        self._product = kwargs.pop('product', self._product)
        self._build = kwargs.pop('build', self._build)
        self._error_func = kwargs.pop('error_func', errors.api_error_func)
        self._timeout = kwargs.pop('timeout', self._timeout)
        self._box = kwargs.pop('box', self._box)
        self._box_attrs = kwargs.pop('box_attrs', self._box_attrs)
        self._conv_json = kwargs.pop('conv_json', self._conv_json)

        # Create the logging facility
        self._log = logging.getLogger(
            f'{self.__module__}.{self.__class__.__name__}'
        )

        # Initiate the session builder.
        self._build_session(**kwargs)
        self._authenticate(**kwargs)

        # if the _error_on_unexpected_input flag is set to True, then we will
        # check to see if any values remain in the kwargs dict, and if so, then
        # error to the caller with the remaining items.
        if self._error_on_unexpected_input and len(kwargs.keys()) > 0:
            raise errors.UnexpectedValueError(
                'The following keywords are invalid {kwargs.keys()}'
            )

    def _build_session(self, **kwargs) -> None:
        '''
        The session builder.  User-agent strings, cookies, headers, etc that
        should persist for the session should be initiated here.  The session
        builder is called as part of the APISession constructor.

        Args:
            session (requests.Session, optional):
                If a session object was passed to the constructor, then this
                would contain a session, otherwise a new one is created.

        Returns:
            :obj:`None`

        Examples:
            Extending the session builder to use basic auth:

            >>> class ExampleAPI(APISession):
            ...     def _build_session(self, session=None):
            ...         super(APISession, self)._build_session(**kwargs)
            ...         self._session.auth = (self._username, self._password)
        '''
        uname = platform.uname()
        # link up the session to either the one passed or create a new session.
        self._session = kwargs.pop('session', Session())

        # If proxy support is needed, update the proxies in the session.
        if self._proxies:
            self._session.proxies.update(self._proxies)

        # If the SSL verification is disabled then we will need to disable
        # verification in the requests session and we also want to mask the
        # certificate warnings.
        if self._ssl_verify is False:
            self._session.verify = self._ssl_verify
            warnings.filterwarnings('ignore', 'Unverified HTTPS request')

        # Update the User-Agent string with the information necessary.
        py_version = '.'.join([str(i) for i in sys.version_info][0:3])
        opsys = uname[0]
        arch = uname[-2]
        self._session.headers.update({
            'User-Agent': (
                # Integration/1.0 (VENDOR; PRODUCT; Build/BUILD)
                'Integration/1.0 '
                f'({self._vendor}; {self._product}; Build/{self._build}) '
                # LIB_NAME/LIB_VER (Restfly/VERSION; Python/VERSION; OS/ARCH)
                f'{self._lib_name}/{self._lib_version} '
                f'(Restfly/{VERSION}; Python/{py_version}; {opsys}/{arch})'
            )
        })

    def _authenticate(self, **kwargs):  # stub
        '''
        Authentication stub.  Overload this method with your authentication
        mechanism if you with to support authentication at creation and
        authentication as part of context management.  Note that this is run
        AFTER the session builder.

        Example:
            >>> class ExampleAPISession(APISession):
            ...     def _authenticate(self, username, password):
            ...         self._session.auth = (username, password)
        '''

    def _deauthenticate(self, **kwargs):  # stub
        '''
        De-authentication stub.  De-authentication is automatically run as part
        of leaving context within the context manager.

        Example:
            >>> class ExampleAPISession(APISession):
            ...     def _deauthenticate(self):
            ...         self.delete('session/token')
        '''

    def _resp_error_check(self, response: Response, **kwargs) -> Response:  # noqa: PLR0201,PLW0613,E501,PLC0301
        '''
        If there is a need for additional error checking (for example within
        the JSON response) then overload this method with the necessary
        checking.

        Args:
            response (request.Response):
                The response object.
            **kwargs (dict):
                The request keyword arguments.

        Returns:
            :obj:`requests.Response`:
                The response object.
        '''
        return response

    def _retry_request(self,                # noqa: PLR0201
                       response: Response,  # noqa: PLW0613
                       retries: int,        # noqa: PLW0613
                       **kwargs
                       ) -> dict:  # stub
        '''
        A method to be overloaded to return any modifications to the request
        upon retries.  By default just passes back what was send in the same
        order.

        Args:
            response (request.Response):
                The response object
            retries (int):
                The number of retries that have been performed.
            **kwargs (dict):
                The keyword arguments that were passed to the request.

        Returns:
            :obj:`dict`:
                The keyword arguments
        '''
        return kwargs

    # NOTE: This method is quite complex and should be refactored into smaller,
    #       more digestible methods.
    def _req(self,
             method: str,
             path: str,
             **kwargs
             ) -> Union[Box, BoxList, Response, Dict, List, None]:
        '''
        The requests session base request method.  This is considered internal
        as it's generally recommended to use the bespoke methods for each HTTP
        method.

        Args:
            method (str):
                The HTTP method
            path (str):
                The URI path to append to the base path.
            **kwargs (dict):
                The keyword arguments to pass to the requests lib.
            box (bool, optional):
                A request-specific override as to if the response should
                attempted to be converted into a Box object.
            box_attrs (dict, optional):
                A request-specific override with a list of key-values to
                pass to the box constructor.
            conv_json (bool, optional):
                A request-specific override to automatically convert the
                response fromJSON to native datatypes.
            redact_fields (list[str], optional):
                A list of keys to redact in the response.  Redaction is used
                for the requests to the API as all of the fields are sent to
                the debug logs.  Note that redaction should be used with care
                as it basically makes a copy fo the request in order to scrub
                the values.
            redact_value (str, optional):
                The value to use to replace the redacted values with.
            retry_on (list[int], optional):
                A list of numeric response status codes to attempt retry on.
                This behavior is additive to the retry parameter in the
                exceptions.
            use_base (bool, optional):
                Should the base path be appended to the URL?  if left
                unspecified the default is `True`.

        Returns:
            :obj:`requests.Response`:
                The default behavior is to return the requests Response object.
            :obj:`box.Box` or :obj:`box.BoxList`:
                If the `box` parameter is set, then the response object will
                be converted to a Box object if the response contains a the
                content type header of "application/json"
            :obj:`dict` or :obj:`list`:
                If the `conv_json` paramerter is set, then the response object
                will be converted using the Response objects baked-in `json()`
                method.
            :obj:`None`:
                If either `conv_json` or `box` has been set, however the
                response object has an empty response body, then `None` will
                be returned instead.

        Examples:
            >>> api = APISession()
            >>> resp = api._req('GET', '/')
        '''
        error_resp = None
        retries = 0
        kwargs['verify'] = kwargs.get('verify', self._ssl_verify)
        conv_json = kwargs.pop('conv_json', self._conv_json)

        # Ensure that the box variable is set to either Box or BoxList.  Then
        # we want to ensure that "box" is removed from the keyword list.
        box = kwargs.pop('box', self._box)
        if box is not False and box not in [Box, BoxList]:
            box = Box

        # Similarly to the box var, we will want to do the same thing with the
        # box_attrs keyword.
        box_attrs = kwargs.pop('box_attrs', self._box_attrs)

        # If retry_on is specified, then we will populate the retry_codes
        # variable with a list of numeric status codes to additionally retry
        # on.  This is helpful if the API in question doesn't always behave in
        # a consistent manner.
        retry_codes = kwargs.pop('retry_on', [])

        # While the number of retries is less than the retry limit, loop.  As
        # we will be returning from within the loop if we receive a successful
        # response or a non-retryable error, the loop should only be handling
        # the retries themselves.
        while retries <= self._retries:
            # Check to see if the path is a relative path or a full path  If
            # we were able to successfully parse a network location using
            # urlparse, then we will assume that this is a full path and pass
            # the URL as-is.  If it's a relative path, then we will append the
            # baseurl to the path.  In either case, the constructed uri string
            # is what we will be using for the rest of the method for making
            # the actual calls.
            if len(urlparse(path).netloc) > 0:
                uri = path
            elif kwargs.pop('use_base', True) and self._base_path:
                uri = f'{self._url}/{self._base_path}/{path}'
            else:
                uri = f'{self._url}/{path}'

            # Here we will generate the debug log.  As some of the values that
            # may be sent to us could be sensitive in nature, we have multiple
            # ways for the developer to inform us that the data may be
            # sensitive, and to screen out that data from the debug logs.  We
            # will be working through that below.
            rkeys = kwargs.pop('redact_fields', None)
            rval = kwargs.pop('redact_value', 'REDACTED')

            # if the path itself is in the _restricted_paths list, then we will
            # simply replace the body and params
            if path in self._restricted_paths:
                body, params = rval, rval

            # if the redact_fields keyword was passed, then we will make a
            # shallow copy of the body and params and pass those to the
            # redact_values utility function to replace the values for any
            # matching keys to the redact_value.
            elif rkeys:
                body = redact_values(kwargs.get('json', {}), rkeys, rval)
                params = redact_values(kwargs.get('params', {}), rkeys, rval)

            # if no redaction happens, then we will simply store the
            # reference of the body and params in the body and params vars.
            else:
                body = kwargs.get('json', {})
                params = kwargs.get('params', {})

            # And now we generate the log based on body and params that we have
            # sanitized (or not).
            self._log.debug('Request: %s' % json.dumps({'method': method,
                                                        'url': uri,
                                                        'params': params,
                                                        'body': body
                                                        }))

            # Make the call to the API and pull the status code.
            try:
                resp = self._session.request(method, uri,
                                             timeout=self._timeout, **kwargs)
                status = resp.status_code

            # Here we will catch any underlying exceptions thrown from the
            # requests library, log them, iterate the retry counter, then
            # release the attempt for the next iteration.
            except (RequestsConnectionError, RequestsRequestException) as ereq:
                self._log.error('Requests Library Error: %s',
                                str(ereq))
                time.sleep(1)
                retries += 1
                error_resp = ereq

            # The following code will run when a request successfully returned.
            else:
                if status in self._error_map:
                    # If a status code that we know about has returned, then we
                    # will want to raise the appropriate Error.
                    err = self._error_map[status]
                    error_resp = err(resp,
                                     retries=retries,
                                     func=self._error_func)
                    if err.retryable or status in retry_codes:  # noqa: PLR1724
                        # If the APIError fetched is retryable, we will want to
                        # attempt to retry our call.  If we see the
                        # "Retry-After" header, then we will respect that.  If
                        # no "Retry-After" header exists, then we will use the
                        # _backoff attribute to build a back-off timer based on
                        # the number of retries we have already performed.
                        retries += 1
                        time.sleep(
                            int(resp.headers.get('retry-after',
                                                 retries * self._backoff
                                                 )
                                )
                        )

                        # The need to potentially modify the request for
                        # subsequent calls is the whole reason that we aren't
                        # using the default Retry logic that urllib3 supports.
                        kwargs = self._retry_request(resp, retries, **kwargs)
                        continue
                    else:
                        raise error_resp

                elif status in range(200, 299):
                    # As everything looks ok, lets pass the response on to the
                    # error checker and then return the response.
                    resp = self._resp_error_check(resp, **kwargs)

                    # If boxification is enabled, then we will want to return
                    # JSON responses with Box objects.  If the content type
                    # isn't JSON, then return a regular Response object.  As we
                    # can't always trust that the content-type header has been
                    # set, if no content-type header is returned to us, we will
                    # assume that the caller is expecting the response to be
                    # a JSON body.
                    ctype = resp.headers.get('content-type',
                                             'application/json')
                    if box and 'application/json' in ctype:
                        # we want to make a quick check to ensure that there is
                        # actually some data to pass to Box.  If there isn't,
                        # then we should just return back a None response.
                        if len(resp.text) > 0:
                            if box_attrs.get('default_box'):
                                self._log.debug(
                                    'unknown attrs will return as %s' %
                                    box_attrs.get('default_box_attr', Box)
                                )
                            return box.from_json(resp.text, **box_attrs)
                    elif conv_json and 'application/json' in ctype:
                        if len(resp.text) > 0:
                            return resp.json()
                    else:
                        return resp

                else:
                    # If all else fails, raise an error stating that we don't
                    # even know whats happening.
                    raise errors.APIError(resp, retries=retries,
                                          func=self._error_func)
        raise error_resp

    def get(self,
            path: str,
            **kwargs
            ) -> Union[Box, BoxList, Response]:
        '''
        Initiates an HTTP GET request using the specified path.  Refer to
        :obj:`requests.request` for more detailed information on what
        keyword arguments can be passed:

        Args:
            path (str):
                The path to be appended onto the base URL for the request.
            **kwargs (dict):
                Keyword arguments to be passed to
                :py:meth:`restfly.session.APISession._req`.

        Returns:
            :obj:`requests.Response` or :obj:`box.Box`
                If the request was informed to attempt to "boxify" the response
                and the response was JSON data, then a Box will be returned.
                In all other scenarios, a Response object will be returned.

        Examples:
            >>> api = APISession()
            >>> resp = api.get('/')
        '''
        return self._req('GET', path, **kwargs)

    def post(self,
             path: str,
             **kwargs
             ) -> Union[Box, BoxList, Response]:
        '''
        Initiates an HTTP POST request using the specified path.  Refer to the
        :obj:`requests.request` for more detailed information on what
        keyword arguments can be passed:

        Args:
            path (str):
                The path to be appended onto the base URL for the request.
            **kwargs (dict):
                Keyword arguments to be passed to
                :py:meth:`restfly.session.APISession._req`.

        Returns:
            :obj:`requests.Response` or :obj:`box.Box`
                If the request was informed to attempt to "boxify" the response
                and the response was JSON data, then a Box will be returned.
                In all other scenarios, a Response object will be returned.

        Examples:
            >>> api = APISession()
            >>> resp = api.post('/')
        '''
        return self._req('POST', path, **kwargs)

    def put(self,
            path: str,
            **kwargs
            ) -> Union[Box, BoxList, Response]:
        '''
        Initiates an HTTP PUT request using the specified path.  Refer to the
        :obj:`requests.request` for more detailed information on what
        keyword arguments can be passed:

        Args:
            path (str):
                The path to be appended onto the base URL for the request.
            **kwargs (dict):
                Keyword arguments to be passed to
                :py:meth:`restfly.session.APISession._req`.

        Returns:
            :obj:`requests.Response` or :obj:`box.Box`
                If the request was informed to attempt to "boxify" the response
                and the response was JSON data, then a Box will be returned.
                In all other scenarios, a Response object will be returned.

        Examples:
            >>> api = APISession()
            >>> resp = api.put('/')
        '''
        return self._req('PUT', path, **kwargs)

    def patch(self,
              path: str,
              **kwargs
              ) -> Union[Box, BoxList, Response]:
        '''
        Initiates an HTTP PATCH request using the specified path.  Refer to the
        :obj:`requests.request` for more detailed information on what
        keyword arguments can be passed:

        Args:
            path (str):
                The path to be appended onto the base URL for the request.
            **kwargs (dict):
                Keyword arguments to be passed to
                :py:meth:`restfly.session.APISession._req`.

        Returns:
            :obj:`requests.Response` or :obj:`box.Box`
                If the request was informed to attempt to "boxify" the response
                and the response was JSON data, then a Box will be returned.
                In all other scenarios, a Response object will be returned.

        Examples:
            >>> api = APISession()
            >>> resp = api.patch('/')
        '''
        return self._req('PATCH', path, **kwargs)

    def delete(self,
               path: str,
               **kwargs
               ) -> Union[Box, BoxList, Response]:
        '''
        Initiates an HTTP DELETE request using the specified path.  Refer to
        the :obj:`requests.request` for more detailed information on what
        keyword arguments can be passed:

        Args:
            path (str):
                The path to be appended onto the base URL for the request.
            **kwargs (dict):
                Keyword arguments to be passed to
                :py:meth:`restfly.session.APISession._req`.

        Returns:
            :obj:`requests.Response` or :obj:`box.Box`
                If the request was informed to attempt to "boxify" the response
                and the response was JSON data, then a Box will be returned.
                In all other scenarios, a Response object will be returned.

        Examples:
            >>> api = APISession()
            >>> resp = api.delete('/')
        '''
        return self._req('DELETE', path, **kwargs)

    def head(self,
             path: str,
             **kwargs
             ) -> Union[Box, BoxList, Response]:
        '''
        Initiates an HTTP HEAD request using the specified path.  Refer to the
        :obj:`requests.request` for more detailed information on what
        keyword arguments can be passed:

        Args:
            path (str):
                The path to be appended onto the base URL for the request.
            **kwargs (dict):
                Keyword arguments to be passed to
                :py:meth:`restfly.session.APISession._req`.

        Returns:
            :obj:`requests.Response` or :obj:`box.Box`
                If the request was informed to attempt to "boxify" the response
                and the response was JSON data, then a Box will be returned.
                In all other scenarios, a Response object will be returned.

        Examples:
            >>> api = APISession()
            >>> resp = api.head('/')
        '''
        return self._req('HEAD', path, **kwargs)
