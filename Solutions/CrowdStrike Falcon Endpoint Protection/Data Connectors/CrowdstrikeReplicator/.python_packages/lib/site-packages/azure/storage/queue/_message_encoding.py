# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
# pylint: disable=unused-argument

import sys
from base64 import b64encode, b64decode

from azure.core.exceptions import DecodeError

from ._encryption import decrypt_queue_message, encrypt_queue_message, _ENCRYPTION_PROTOCOL_V1


class MessageEncodePolicy(object):

    def __init__(self):
        self.require_encryption = False
        self.encryption_version = None
        self.key_encryption_key = None
        self.resolver = None

    def __call__(self, content):
        if content:
            content = self.encode(content)
            if self.key_encryption_key is not None:
                content = encrypt_queue_message(content, self.key_encryption_key, self.encryption_version)
        return content

    def configure(self, require_encryption, key_encryption_key, resolver, encryption_version=_ENCRYPTION_PROTOCOL_V1):
        self.require_encryption = require_encryption
        self.encryption_version = encryption_version
        self.key_encryption_key = key_encryption_key
        self.resolver = resolver
        if self.require_encryption and not self.key_encryption_key:
            raise ValueError("Encryption required but no key was provided.")

    def encode(self, content):
        raise NotImplementedError("Must be implemented by child class.")


class MessageDecodePolicy(object):

    def __init__(self):
        self.require_encryption = False
        self.key_encryption_key = None
        self.resolver = None

    def __call__(self, response, obj, headers):
        for message in obj:
            if message.message_text in [None, "", b""]:
                continue
            content = message.message_text
            if (self.key_encryption_key is not None) or (self.resolver is not None):
                content = decrypt_queue_message(
                    content, response,
                    self.require_encryption,
                    self.key_encryption_key,
                    self.resolver)
            message.message_text = self.decode(content, response)
        return obj

    def configure(self, require_encryption, key_encryption_key, resolver):
        self.require_encryption = require_encryption
        self.key_encryption_key = key_encryption_key
        self.resolver = resolver

    def decode(self, content, response):
        raise NotImplementedError("Must be implemented by child class.")


class TextBase64EncodePolicy(MessageEncodePolicy):
    """Base 64 message encoding policy for text messages.

    Encodes text (unicode) messages to base 64. If the input content
    is not text, a TypeError will be raised. Input text must support UTF-8.
    """

    def encode(self, content):
        if not isinstance(content, str):
            raise TypeError("Message content must be text for base 64 encoding.")
        return b64encode(content.encode('utf-8')).decode('utf-8')


class TextBase64DecodePolicy(MessageDecodePolicy):
    """Message decoding policy for base 64-encoded messages into text.

    Decodes base64-encoded messages to text (unicode). If the input content
    is not valid base 64, a DecodeError will be raised. Message data must
    support UTF-8.
    """

    def decode(self, content, response):
        try:
            return b64decode(content.encode('utf-8')).decode('utf-8')
        except (ValueError, TypeError) as error:
            # ValueError for Python 3, TypeError for Python 2
            raise DecodeError(
                message="Message content is not valid base 64.",
                response=response,
                error=error)


class BinaryBase64EncodePolicy(MessageEncodePolicy):
    """Base 64 message encoding policy for binary messages.

    Encodes binary messages to base 64. If the input content
    is not bytes, a TypeError will be raised.
    """

    def encode(self, content):
        if not isinstance(content, bytes):
            raise TypeError("Message content must be bytes for base 64 encoding.")
        return b64encode(content).decode('utf-8')


class BinaryBase64DecodePolicy(MessageDecodePolicy):
    """Message decoding policy for base 64-encoded messages into bytes.

    Decodes base64-encoded messages to bytes. If the input content
    is not valid base 64, a DecodeError will be raised.
    """

    def decode(self, content, response):
        response = response.http_response
        try:
            return b64decode(content.encode('utf-8'))
        except (ValueError, TypeError) as error:
            # ValueError for Python 3, TypeError for Python 2
            raise DecodeError(
                message="Message content is not valid base 64.",
                response=response,
                error=error)


class NoEncodePolicy(MessageEncodePolicy):
    """Bypass any message content encoding."""

    def encode(self, content):
        if isinstance(content, bytes) and sys.version_info > (3,):
            raise TypeError(
                "Message content must not be bytes. Use the BinaryBase64EncodePolicy to send bytes."
            )
        return content


class NoDecodePolicy(MessageDecodePolicy):
    """Bypass any message content decoding."""

    def decode(self, content, response):
        return content
