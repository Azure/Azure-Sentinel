import http.client
import json

from globalVariables import AUTH_URLS
from .errors import InputError

def _get_auth_url(env):
    auth_url = AUTH_URLS.get(env)
    if not auth_url:
        raise InputError(f"no auth url defined for environment '{env}'")
    return auth_url


class Auth:
    def __init__(self, token, env):
        self.token = token
        self.env = env

    def __enter__(self):
        self.connection = _Auth(self.token).connect(self.env)
        return self.connection

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.connection.conn.close()


class _Auth:
    def __init__(self, token):
        self.conn = None
        self._headers = {"Authorization": f"IBToken {token}"}

    def connect(self, env: str):
        auth_url = _get_auth_url(env)
        self.conn = http.client.HTTPSConnection(auth_url)
        return self

    def user(self) -> dict:
        url = "/v1/authenticate/self"
        user = self._get(url).get("user")
        if not user:
            raise InputError("unable to get user from auth")
        return user

    def account(self, account_uuid: str) -> dict:
        url = f"/v1/account/{account_uuid}"
        account = self._get(url).get("account")
        if not account:
            raise InputError("unable to get account from auth")
        return account

    def _get(self, url: str) -> dict:
        self.conn.request("GET", url, headers=self._headers)
        r = self.conn.getresponse()
        if 200 > r.status > 300:
            raise InputError(f"unable to contact auth: {r.status} {r.reason}")
        return json.loads(r.read())
