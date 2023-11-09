from typing import Dict, Union, Optional

from azure.durable_functions.models.TokenSource import TokenSource
from azure.durable_functions.models.utils.json_utils import add_attrib, add_json_attrib


class DurableHttpRequest:
    """Data structure representing a durable HTTP request."""

    def __init__(self, method: str, uri: str, content: Optional[str] = None,
                 headers: Optional[Dict[str, str]] = None,
                 token_source: Optional[TokenSource] = None):
        self._method: str = method
        self._uri: str = uri
        self._content: Optional[str] = content
        self._headers: Optional[Dict[str, str]] = headers
        self._token_source: Optional[TokenSource] = token_source

    @property
    def method(self) -> str:
        """Get the HTTP request method."""
        return self._method

    @property
    def uri(self) -> str:
        """Get the HTTP request uri."""
        return self._uri

    @property
    def content(self) -> Optional[str]:
        """Get the HTTP request content."""
        return self._content

    @property
    def headers(self) -> Optional[Dict[str, str]]:
        """Get the HTTP request headers."""
        return self._headers

    @property
    def token_source(self) -> Optional[TokenSource]:
        """Get the source of OAuth token to add to the request."""
        return self._token_source

    def to_json(self) -> Dict[str, Union[str, int]]:
        """Convert object into a json dictionary.

        Returns
        -------
        Dict[str, Union[str, int]]
            The instance of the class converted into a json dictionary
        """
        json_dict: Dict[str, Union[str, int]] = {}
        add_attrib(json_dict, self, 'method')
        add_attrib(json_dict, self, 'uri')
        add_attrib(json_dict, self, 'content')
        add_attrib(json_dict, self, 'headers')
        add_json_attrib(json_dict, self, 'token_source', 'tokenSource')
        return json_dict
