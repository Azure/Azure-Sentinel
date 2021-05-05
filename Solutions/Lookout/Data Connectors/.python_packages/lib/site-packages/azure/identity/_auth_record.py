# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import json


class AuthenticationRecord(object):
    """A record which can initialize :class:`DeviceCodeCredential` or :class:`InteractiveBrowserCredential`"""

    def __init__(self, tenant_id, client_id, authority, home_account_id, username):
        # type: (str, str, str, str, str) -> None
        self._authority = authority
        self._client_id = client_id
        self._home_account_id = home_account_id
        self._tenant_id = tenant_id
        self._username = username

    @property
    def authority(self):
        # type: () -> str
        return self._authority

    @property
    def client_id(self):
        # type: () -> str
        return self._client_id

    @property
    def home_account_id(self):
        # type: () -> str
        return self._home_account_id

    @property
    def tenant_id(self):
        # type: () -> str
        return self._tenant_id

    @property
    def username(self):
        # type: () -> str
        """The authenticated user's username"""
        return self._username

    @classmethod
    def deserialize(cls, data):
        # type: (str) -> AuthenticationRecord
        """Deserialize a record.

        :param str data: a serialized record
        """

        deserialized = json.loads(data)

        return cls(
            authority=deserialized["authority"],
            client_id=deserialized["client_id"],
            home_account_id=deserialized["home_account_id"],
            tenant_id=deserialized["tenant_id"],
            username=deserialized["username"],
        )

    def serialize(self):
        # type: () -> str
        """Serialize the record.

        :rtype: str
        """

        record = {
            "authority": self._authority,
            "client_id": self._client_id,
            "home_account_id": self._home_account_id,
            "tenant_id": self._tenant_id,
            "username": self._username,
        }

        return json.dumps(record)
