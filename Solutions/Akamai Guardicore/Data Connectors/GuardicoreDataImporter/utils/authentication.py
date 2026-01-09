import datetime
from typing import Final

import jwt
import aiohttp


class GuardicoreAuth:
    AUTHENTICATION_ENDPOINT: Final[str] = 'api/v3.0/authenticate'
    AUTHENTICATION_EXPIRY_THRESHOLD_MINUTES: Final[int] = 5

    def __init__(self, url: str, user: str, password: str):
        self._url = url
        self._user = user
        self._password = password
        self._expiration_time = datetime.datetime.fromtimestamp(0,
                                                                tz=datetime.timezone.utc)
        self._jwt_token = None

    async def _refresh_token(self) -> None:
        body = {'username': self._user, 'password': self._password}
        async with aiohttp.ClientSession() as session:
            async with session.post(f'{self._url}/{GuardicoreAuth.AUTHENTICATION_ENDPOINT}', json=body) as response:
                self._jwt_token = (await response.json())['access_token']
                decoded_jwt = jwt.JWT().decode(self._jwt_token, do_verify=False)
                self._expiration_time = datetime.datetime.fromtimestamp(decoded_jwt['exp'],
                                                                        tz=datetime.timezone.utc)

    async def get_authorization_headers(self) -> dict[str, str]:
        if self._expiration_time < datetime.datetime.now(tz=datetime.timezone.utc) - datetime.timedelta(
                minutes=GuardicoreAuth.AUTHENTICATION_EXPIRY_THRESHOLD_MINUTES):
            await self._refresh_token()
        return {
            'Authorization': f'Bearer {self._jwt_token}'
        }
