import logging
from collections.abc import Callable
from http import HTTPStatus

import aiohttp
from typing import Final, AsyncGenerator

from .authentication import GuardicoreAuth


class PaginatedResponse:
    ENTITIES_PER_PAGE: Final[int] = 1000
    METHOD_TYPE_TO_FUNCTION: Final[dict[str, Callable]] = {
        'GET': aiohttp.ClientSession.get,
        'POST': aiohttp.ClientSession.post,
        'PUT': aiohttp.ClientSession.put,
    }

    def __init__(self, endpoint: str, request_type: str, authentication: GuardicoreAuth,
                 headers: dict = None, body: dict = None, params: dict = None, chunk_size = ENTITIES_PER_PAGE):
        if headers is None:
            headers = {}
        if params is None:
            params = {}

        self._endpoint = endpoint
        self._authentication = authentication
        self._request_type = request_type
        self._params = params
        self._headers = headers
        self._body = body
        self._chunk_size = chunk_size

    async def items(self) -> AsyncGenerator[dict, None]:
        entities_found = 0
        if self._request_type not in PaginatedResponse.METHOD_TYPE_TO_FUNCTION:
            raise ValueError(f"Unsupported request type: {self._request_type}")
        async with aiohttp.ClientSession() as session:
            while True:
                self._headers.update(await self._authentication.get_authorization_headers())
                self._params.update({"offset": entities_found,
                                     "limit": self._chunk_size})

                async with PaginatedResponse.METHOD_TYPE_TO_FUNCTION[self._request_type](session, self._endpoint,
                                                                                         params=self._params,
                                                                                         headers=self._headers,
                                                                                         json=self._body) as response:
                    if response.status == HTTPStatus.OK:
                        resp = await response.json()
                        if 'objects' not in resp:
                            raise ValueError(f"Invalid response format: {resp}")
                        for item in resp['objects']:
                            yield item
                        entities_found += len(resp['objects'])
                        if len(resp['objects']) != self._chunk_size:
                            logging.info(f"End of pagination reached for {self._endpoint}")
                            break
                    elif response.status == HTTPStatus.NO_CONTENT:
                        logging.info(f"No content found in the response for {self._endpoint}")
                        break
                    else:
                        logging.error(f"Failed to fetch data from {self._endpoint}. Status code: {response.status}")
                        logging.error(f"Response: {await response.text()}")
                        break