# Note: This docstring is also used by this script's command line help.
"""A one-stop helper for desktop app to acquire an authorization code.

It starts a web server to listen redirect_uri, waiting for auth code.
It optionally opens a browser window to guide a human user to manually login.
After obtaining an auth code, the web server will automatically shut down.
"""
import logging
import socket
from string import Template

try:  # Python 3
    from http.server import HTTPServer, BaseHTTPRequestHandler
    from urllib.parse import urlparse, parse_qs, urlencode
except ImportError:  # Fall back to Python 2
    from BaseHTTPServer import HTTPServer, BaseHTTPRequestHandler
    from urlparse import urlparse, parse_qs
    from urllib import urlencode


logger = logging.getLogger(__name__)


def obtain_auth_code(listen_port, auth_uri=None):  # Historically only used in testing
    with AuthCodeReceiver(port=listen_port) as receiver:
        return receiver.get_auth_response(
            auth_uri=auth_uri,
            welcome_template="""<html><body>
                Open this link to <a href='$auth_uri'>Sign In</a>
                (You may want to use incognito window)
                <hr><a href='$abort_uri'>Abort</a>
                </body></html>""",
            ).get("code")


def is_wsl():
    # "Official" way of detecting WSL: https://github.com/Microsoft/WSL/issues/423#issuecomment-221627364
    # Run `uname -a` to get 'release' without python
    #   - WSL 1: '4.4.0-19041-Microsoft'
    #   - WSL 2: '4.19.128-microsoft-standard'
    import platform
    uname = platform.uname()
    platform_name = getattr(uname, 'system', uname[0]).lower()
    release = getattr(uname, 'release', uname[2]).lower()
    return platform_name == 'linux' and 'microsoft' in release


def _browse(auth_uri):  # throws ImportError, possibly webbrowser.Error in future
    import webbrowser  # Lazy import. Some distro may not have this.
    browser_opened = webbrowser.open(auth_uri)  # Use default browser. Customizable by $BROWSER

    # In WSL which doesn't have www-browser, try launching browser with PowerShell
    if not browser_opened and is_wsl():
        try:
            import subprocess
            # https://docs.microsoft.com/en-us/powershell/module/microsoft.powershell.core/about/about_powershell_exe
            # Ampersand (&) should be quoted
            exit_code = subprocess.call(
                ['powershell.exe', '-NoProfile', '-Command', 'Start-Process "{}"'.format(auth_uri)])
            browser_opened = exit_code == 0
        except FileNotFoundError:  # WSL might be too old
            pass
    return browser_opened


def _qs2kv(qs):
    """Flatten parse_qs()'s single-item lists into the item itself"""
    return {k: v[0] if isinstance(v, list) and len(v) == 1 else v
        for k, v in qs.items()}


class _AuthCodeHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        # For flexibility, we choose to not check self.path matching redirect_uri
        #assert self.path.startswith('/THE_PATH_REGISTERED_BY_THE_APP')
        qs = parse_qs(urlparse(self.path).query)
        if qs.get('code') or qs.get("error"):  # So, it is an auth response
            self.server.auth_response = _qs2kv(qs)
            logger.debug("Got auth response: %s", self.server.auth_response)
            template = (self.server.success_template
                if "code" in qs else self.server.error_template)
            self._send_full_response(
                template.safe_substitute(**self.server.auth_response))
            # NOTE: Don't do self.server.shutdown() here. It'll halt the server.
        else:
            self._send_full_response(self.server.welcome_page)

    def _send_full_response(self, body, is_ok=True):
        self.send_response(200 if is_ok else 400)
        content_type = 'text/html' if body.startswith('<') else 'text/plain'
        self.send_header('Content-type', content_type)
        self.end_headers()
        self.wfile.write(body.encode("utf-8"))

    def log_message(self, format, *args):
        logger.debug(format, *args)  # To override the default log-to-stderr behavior


class _AuthCodeHttpServer(HTTPServer):
    def handle_timeout(self):
        # It will be triggered when no request comes in self.timeout seconds.
        # See https://docs.python.org/3/library/socketserver.html#socketserver.BaseServer.handle_timeout
        raise RuntimeError("Timeout. No auth response arrived.")  # Terminates this server
            # We choose to not call self.server_close() here,
            # because it would cause a socket.error exception in handle_request(),
            # and likely end up the server being server_close() twice.


class _AuthCodeHttpServer6(_AuthCodeHttpServer):
    address_family = socket.AF_INET6


class AuthCodeReceiver(object):
    # This class has (rather than is) an _AuthCodeHttpServer, so it does not leak API
    def __init__(self, port=None):
        """Create a Receiver waiting for incoming auth response.

        :param port:
            The local web server will listen at http://...:<port>
            You need to use the same port when you register with your app.
            If your Identity Provider supports dynamic port, you can use port=0 here.
            Port 0 means to use an arbitrary unused port, per this official example:
            https://docs.python.org/2.7/library/socketserver.html#asynchronous-mixins
        """
        address = "127.0.0.1"  # Hardcode, for now, Not sure what to expose, yet.
            # Per RFC 8252 (https://tools.ietf.org/html/rfc8252#section-8.3):
            #   * Clients should listen on the loopback network interface only.
            #     (It is not recommended to use "" shortcut to bind all addr.)
            #   * the use of localhost is NOT RECOMMENDED.
            #     (Use) the loopback IP literal
            #     rather than localhost avoids inadvertently listening on network
            #     interfaces other than the loopback interface.
            # Note:
            #   When this server physically listens to a specific IP (as it should),
            #   you will still be able to specify your redirect_uri using either
            #   IP (e.g. 127.0.0.1) or localhost, whichever matches your registration.
        Server = _AuthCodeHttpServer6 if ":" in address else _AuthCodeHttpServer
            # TODO: But, it would treat "localhost" or "" as IPv4.
            # If pressed, we might just expose a family parameter to caller.
        self._server = Server((address, port or 0), _AuthCodeHandler)

    def get_port(self):
        """The port this server actually listening to"""
        # https://docs.python.org/2.7/library/socketserver.html#SocketServer.BaseServer.server_address
        return self._server.server_address[1]

    def get_auth_response(self, auth_uri=None, timeout=None, state=None,
            welcome_template=None, success_template=None, error_template=None,
            auth_uri_callback=None,
            ):
        """Wait and return the auth response. Raise RuntimeError when timeout.

        :param str auth_uri:
            If provided, this function will try to open a local browser.
        :param int timeout: In seconds. None means wait indefinitely.
        :param str state:
            You may provide the state you used in auth_uri,
            then we will use it to validate incoming response.
        :param str welcome_template:
            If provided, your end user will see it instead of the auth_uri.
            When present, it shall be a plaintext or html template following
            `Python Template string syntax <https://docs.python.org/3/library/string.html#template-strings>`_,
            and include some of these placeholders: $auth_uri and $abort_uri.
        :param str success_template:
            The page will be displayed when authentication was largely successful.
            Placeholders can be any of these:
            https://tools.ietf.org/html/rfc6749#section-5.1
        :param str error_template:
            The page will be displayed when authentication encountered error.
            Placeholders can be any of these:
            https://tools.ietf.org/html/rfc6749#section-5.2
        :param callable auth_uri_callback:
            A function with the shape of lambda auth_uri: ...
            When a browser was unable to be launch, this function will be called,
            so that the app could tell user to manually visit the auth_uri.
        :return:
            The auth response of the first leg of Auth Code flow,
            typically {"code": "...", "state": "..."} or {"error": "...", ...}
            See https://tools.ietf.org/html/rfc6749#section-4.1.2
            and https://openid.net/specs/openid-connect-core-1_0.html#AuthResponse
            Returns None when the state was mismatched, or when timeout occurred.
        """
        welcome_uri = "http://localhost:{p}".format(p=self.get_port())
        abort_uri = "{loc}?error=abort".format(loc=welcome_uri)
        logger.debug("Abort by visit %s", abort_uri)
        self._server.welcome_page = Template(welcome_template or "").safe_substitute(
            auth_uri=auth_uri, abort_uri=abort_uri)
        if auth_uri:  # Now attempt to open a local browser to visit it
            _uri = welcome_uri if welcome_template else auth_uri
            logger.info("Open a browser on this device to visit: %s" % _uri)
            browser_opened = False
            try:
                browser_opened = _browse(_uri)
            except:  # Had to use broad except, because the potential
                     # webbrowser.Error is purposely undefined outside of _browse().
                # Absorb and proceed. Because browser could be manually run elsewhere.
                logger.exception("_browse(...) unsuccessful")
            if not browser_opened:
                if not auth_uri_callback:
                    logger.warning(
                        "Found no browser in current environment. "
                        "If this program is being run inside a container "
                        "which has access to host network "
                        "(i.e. started by `docker run --net=host -it ...`), "
                        "you can use browser on host to visit the following link. "
                        "Otherwise, this auth attempt would either timeout "
                        "(current timeout setting is {timeout}) "
                        "or be aborted by CTRL+C. Auth URI: {auth_uri}".format(
                            auth_uri=_uri, timeout=timeout))
                else:  # Then it is the auth_uri_callback()'s job to inform the user
                    auth_uri_callback(_uri)

        self._server.success_template = Template(success_template or
            "Authentication completed. You can close this window now.")
        self._server.error_template = Template(error_template or
            "Authentication failed. $error: $error_description. ($error_uri)")

        self._server.timeout = timeout  # Otherwise its handle_timeout() won't work
        self._server.auth_response = {}  # Shared with _AuthCodeHandler
        while True:
            # Derived from
            # https://docs.python.org/2/library/basehttpserver.html#more-examples
            self._server.handle_request()
            if self._server.auth_response:
                if state and state != self._server.auth_response.get("state"):
                    logger.debug("State mismatch. Ignoring this noise.")
                else:
                    break
        return self._server.auth_response

    def close(self):
        """Either call this eventually; or use the entire class as context manager"""
        self._server.server_close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

# Note: Manually use or test this module by:
#       python -m path.to.this.file -h
if __name__ == '__main__':
    import argparse, json
    from .oauth2 import Client
    logging.basicConfig(level=logging.INFO)
    p = parser = argparse.ArgumentParser(
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        description=__doc__ + "The auth code received will be shown at stdout.")
    p.add_argument(
        '--endpoint', help="The auth endpoint for your app.",
        default="https://login.microsoftonline.com/common/oauth2/v2.0/authorize")
    p.add_argument('client_id', help="The client_id of your application")
    p.add_argument('--port', type=int, default=0, help="The port in redirect_uri")
    p.add_argument('--host', default="127.0.0.1", help="The host of redirect_uri")
    p.add_argument('--scope', default=None, help="The scope list")
    args = parser.parse_args()
    client = Client({"authorization_endpoint": args.endpoint}, args.client_id)
    with AuthCodeReceiver(port=args.port) as receiver:
        flow = client.initiate_auth_code_flow(
            scope=args.scope.split() if args.scope else None,
            redirect_uri="http://{h}:{p}".format(h=args.host, p=receiver.get_port()),
            )
        print(json.dumps(receiver.get_auth_response(
            auth_uri=flow["auth_uri"],
            welcome_template=
                "<a href='$auth_uri'>Sign In</a>, or <a href='$abort_uri'>Abort</a",
            error_template="Oh no. $error",
            success_template="Oh yeah. Got $code",
            timeout=60,
            state=flow["state"],  # Optional
            ), indent=4))
