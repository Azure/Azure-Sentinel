# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

import os
from os import urandom
from json import (
    dumps,
    loads,
)
from collections import OrderedDict

from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.ciphers import Cipher
from cryptography.hazmat.primitives.ciphers.algorithms import AES
from cryptography.hazmat.primitives.ciphers.modes import CBC
from cryptography.hazmat.primitives.padding import PKCS7

from azure.core.exceptions import HttpResponseError

from .._version import VERSION
from . import encode_base64, decode_base64_to_bytes


_ENCRYPTION_PROTOCOL_V1 = '1.0'
_ERROR_OBJECT_INVALID = \
    '{0} does not define a complete interface. Value of {1} is either missing or invalid.'


def _validate_not_none(param_name, param):
    if param is None:
        raise ValueError('{0} should not be None.'.format(param_name))


def _validate_key_encryption_key_wrap(kek):
    # Note that None is not callable and so will fail the second clause of each check.
    if not hasattr(kek, 'wrap_key') or not callable(kek.wrap_key):
        raise AttributeError(_ERROR_OBJECT_INVALID.format('key encryption key', 'wrap_key'))
    if not hasattr(kek, 'get_kid') or not callable(kek.get_kid):
        raise AttributeError(_ERROR_OBJECT_INVALID.format('key encryption key', 'get_kid'))
    if not hasattr(kek, 'get_key_wrap_algorithm') or not callable(kek.get_key_wrap_algorithm):
        raise AttributeError(_ERROR_OBJECT_INVALID.format('key encryption key', 'get_key_wrap_algorithm'))


class _EncryptionAlgorithm(object):
    '''
    Specifies which client encryption algorithm is used.
    '''
    AES_CBC_256 = 'AES_CBC_256'


class _WrappedContentKey:
    '''
    Represents the envelope key details stored on the service.
    '''

    def __init__(self, algorithm, encrypted_key, key_id):
        '''
        :param str algorithm:
            The algorithm used for wrapping.
        :param bytes encrypted_key:
            The encrypted content-encryption-key.
        :param str key_id:
            The key-encryption-key identifier string.
        '''

        _validate_not_none('algorithm', algorithm)
        _validate_not_none('encrypted_key', encrypted_key)
        _validate_not_none('key_id', key_id)

        self.algorithm = algorithm
        self.encrypted_key = encrypted_key
        self.key_id = key_id


class _EncryptionAgent:
    '''
    Represents the encryption agent stored on the service.
    It consists of the encryption protocol version and encryption algorithm used.
    '''

    def __init__(self, encryption_algorithm, protocol):
        '''
        :param _EncryptionAlgorithm encryption_algorithm:
            The algorithm used for encrypting the message contents.
        :param str protocol:
            The protocol version used for encryption.
        '''

        _validate_not_none('encryption_algorithm', encryption_algorithm)
        _validate_not_none('protocol', protocol)

        self.encryption_algorithm = str(encryption_algorithm)
        self.protocol = protocol


class _EncryptionData:
    '''
    Represents the encryption data that is stored on the service.
    '''

    def __init__(self, content_encryption_IV, encryption_agent, wrapped_content_key,
                 key_wrapping_metadata):
        '''
        :param bytes content_encryption_IV:
            The content encryption initialization vector.
        :param _EncryptionAgent encryption_agent:
            The encryption agent.
        :param _WrappedContentKey wrapped_content_key:
            An object that stores the wrapping algorithm, the key identifier,
            and the encrypted key bytes.
        :param dict key_wrapping_metadata:
            A dict containing metadata related to the key wrapping.
        '''

        _validate_not_none('content_encryption_IV', content_encryption_IV)
        _validate_not_none('encryption_agent', encryption_agent)
        _validate_not_none('wrapped_content_key', wrapped_content_key)

        self.content_encryption_IV = content_encryption_IV
        self.encryption_agent = encryption_agent
        self.wrapped_content_key = wrapped_content_key
        self.key_wrapping_metadata = key_wrapping_metadata


def _generate_encryption_data_dict(kek, cek, iv):
    '''
    Generates and returns the encryption metadata as a dict.

    :param object kek: The key encryption key. See calling functions for more information.
    :param bytes cek: The content encryption key.
    :param bytes iv: The initialization vector.
    :return: A dict containing all the encryption metadata.
    :rtype: dict
    '''
    # Encrypt the cek.
    wrapped_cek = kek.wrap_key(cek)

    # Build the encryption_data dict.
    # Use OrderedDict to comply with Java's ordering requirement.
    wrapped_content_key = OrderedDict()
    wrapped_content_key['KeyId'] = kek.get_kid()
    wrapped_content_key['EncryptedKey'] = encode_base64(wrapped_cek)
    wrapped_content_key['Algorithm'] = kek.get_key_wrap_algorithm()

    encryption_agent = OrderedDict()
    encryption_agent['Protocol'] = _ENCRYPTION_PROTOCOL_V1
    encryption_agent['EncryptionAlgorithm'] = _EncryptionAlgorithm.AES_CBC_256

    encryption_data_dict = OrderedDict()
    encryption_data_dict['WrappedContentKey'] = wrapped_content_key
    encryption_data_dict['EncryptionAgent'] = encryption_agent
    encryption_data_dict['ContentEncryptionIV'] = encode_base64(iv)
    encryption_data_dict['KeyWrappingMetadata'] = {'EncryptionLibrary': 'Python ' + VERSION}

    return encryption_data_dict


def _dict_to_encryption_data(encryption_data_dict):
    '''
    Converts the specified dictionary to an EncryptionData object for
    eventual use in decryption.

    :param dict encryption_data_dict:
        The dictionary containing the encryption data.
    :return: an _EncryptionData object built from the dictionary.
    :rtype: _EncryptionData
    '''
    try:
        if encryption_data_dict['EncryptionAgent']['Protocol'] != _ENCRYPTION_PROTOCOL_V1:
            raise ValueError("Unsupported encryption version.")
    except KeyError:
        raise ValueError("Unsupported encryption version.")
    wrapped_content_key = encryption_data_dict['WrappedContentKey']
    wrapped_content_key = _WrappedContentKey(wrapped_content_key['Algorithm'],
                                             decode_base64_to_bytes(wrapped_content_key['EncryptedKey']),
                                             wrapped_content_key['KeyId'])

    encryption_agent = encryption_data_dict['EncryptionAgent']
    encryption_agent = _EncryptionAgent(encryption_agent['EncryptionAlgorithm'],
                                        encryption_agent['Protocol'])

    if 'KeyWrappingMetadata' in encryption_data_dict:
        key_wrapping_metadata = encryption_data_dict['KeyWrappingMetadata']
    else:
        key_wrapping_metadata = None

    encryption_data = _EncryptionData(decode_base64_to_bytes(encryption_data_dict['ContentEncryptionIV']),
                                      encryption_agent,
                                      wrapped_content_key,
                                      key_wrapping_metadata)

    return encryption_data


def _generate_AES_CBC_cipher(cek, iv):
    '''
    Generates and returns an encryption cipher for AES CBC using the given cek and iv.

    :param bytes[] cek: The content encryption key for the cipher.
    :param bytes[] iv: The initialization vector for the cipher.
    :return: A cipher for encrypting in AES256 CBC.
    :rtype: ~cryptography.hazmat.primitives.ciphers.Cipher
    '''

    backend = default_backend()
    algorithm = AES(cek)
    mode = CBC(iv)
    return Cipher(algorithm, mode, backend)


def _validate_and_unwrap_cek(encryption_data, key_encryption_key=None, key_resolver=None):
    '''
    Extracts and returns the content_encryption_key stored in the encryption_data object
    and performs necessary validation on all parameters.
    :param _EncryptionData encryption_data:
        The encryption metadata of the retrieved value.
    :param obj key_encryption_key:
        The key_encryption_key used to unwrap the cek. Please refer to high-level service object
        instance variables for more details.
    :param func key_resolver:
        A function used that, given a key_id, will return a key_encryption_key. Please refer
        to high-level service object instance variables for more details.
    :return: the content_encryption_key stored in the encryption_data object.
    :rtype: bytes[]
    '''

    _validate_not_none('content_encryption_IV', encryption_data.content_encryption_IV)
    _validate_not_none('encrypted_key', encryption_data.wrapped_content_key.encrypted_key)

    if _ENCRYPTION_PROTOCOL_V1 != encryption_data.encryption_agent.protocol:
        raise ValueError('Encryption version is not supported.')

    content_encryption_key = None

    # If the resolver exists, give priority to the key it finds.
    if key_resolver is not None:
        key_encryption_key = key_resolver(encryption_data.wrapped_content_key.key_id)

    _validate_not_none('key_encryption_key', key_encryption_key)
    if not hasattr(key_encryption_key, 'get_kid') or not callable(key_encryption_key.get_kid):
        raise AttributeError(_ERROR_OBJECT_INVALID.format('key encryption key', 'get_kid'))
    if not hasattr(key_encryption_key, 'unwrap_key') or not callable(key_encryption_key.unwrap_key):
        raise AttributeError(_ERROR_OBJECT_INVALID.format('key encryption key', 'unwrap_key'))
    if encryption_data.wrapped_content_key.key_id != key_encryption_key.get_kid():
        raise ValueError('Provided or resolved key-encryption-key does not match the id of key used to encrypt.')
    # Will throw an exception if the specified algorithm is not supported.
    content_encryption_key = key_encryption_key.unwrap_key(encryption_data.wrapped_content_key.encrypted_key,
                                                           encryption_data.wrapped_content_key.algorithm)
    _validate_not_none('content_encryption_key', content_encryption_key)

    return content_encryption_key


def _decrypt_message(message, encryption_data, key_encryption_key=None, resolver=None):
    '''
    Decrypts the given ciphertext using AES256 in CBC mode with 128 bit padding.
    Unwraps the content-encryption-key using the user-provided or resolved key-encryption-key (kek).
    Returns the original plaintex.

    :param str message:
        The ciphertext to be decrypted.
    :param _EncryptionData encryption_data:
        The metadata associated with this ciphertext.
    :param object key_encryption_key:
        The user-provided key-encryption-key. Must implement the following methods:
        unwrap_key(key, algorithm)
            - returns the unwrapped form of the specified symmetric key using the string-specified algorithm.
        get_kid()
            - returns a string key id for this key-encryption-key.
    :param function resolver(kid):
        The user-provided key resolver. Uses the kid string to return a key-encryption-key
        implementing the interface defined above.
    :return: The decrypted plaintext.
    :rtype: str
    '''
    _validate_not_none('message', message)
    content_encryption_key = _validate_and_unwrap_cek(encryption_data, key_encryption_key, resolver)

    if _EncryptionAlgorithm.AES_CBC_256 != encryption_data.encryption_agent.encryption_algorithm:
        raise ValueError('Specified encryption algorithm is not supported.')

    cipher = _generate_AES_CBC_cipher(content_encryption_key, encryption_data.content_encryption_IV)

    # decrypt data
    decrypted_data = message
    decryptor = cipher.decryptor()
    decrypted_data = (decryptor.update(decrypted_data) + decryptor.finalize())

    # unpad data
    unpadder = PKCS7(128).unpadder()
    decrypted_data = (unpadder.update(decrypted_data) + unpadder.finalize())

    return decrypted_data


def encrypt_blob(blob, key_encryption_key):
    '''
    Encrypts the given blob using AES256 in CBC mode with 128 bit padding.
    Wraps the generated content-encryption-key using the user-provided key-encryption-key (kek).
    Returns a json-formatted string containing the encryption metadata. This method should
    only be used when a blob is small enough for single shot upload. Encrypting larger blobs
    is done as a part of the upload_data_chunks method.

    :param bytes blob:
        The blob to be encrypted.
    :param object key_encryption_key:
        The user-provided key-encryption-key. Must implement the following methods:
        wrap_key(key)--wraps the specified key using an algorithm of the user's choice.
        get_key_wrap_algorithm()--returns the algorithm used to wrap the specified symmetric key.
        get_kid()--returns a string key id for this key-encryption-key.
    :return: A tuple of json-formatted string containing the encryption metadata and the encrypted blob data.
    :rtype: (str, bytes)
    '''

    _validate_not_none('blob', blob)
    _validate_not_none('key_encryption_key', key_encryption_key)
    _validate_key_encryption_key_wrap(key_encryption_key)

    # AES256 uses 256 bit (32 byte) keys and always with 16 byte blocks
    content_encryption_key = urandom(32)
    initialization_vector = urandom(16)

    cipher = _generate_AES_CBC_cipher(content_encryption_key, initialization_vector)

    # PKCS7 with 16 byte blocks ensures compatibility with AES.
    padder = PKCS7(128).padder()
    padded_data = padder.update(blob) + padder.finalize()

    # Encrypt the data.
    encryptor = cipher.encryptor()
    encrypted_data = encryptor.update(padded_data) + encryptor.finalize()
    encryption_data = _generate_encryption_data_dict(key_encryption_key, content_encryption_key,
                                                     initialization_vector)
    encryption_data['EncryptionMode'] = 'FullBlob'

    return dumps(encryption_data), encrypted_data


def generate_blob_encryption_data(key_encryption_key):
    '''
    Generates the encryption_metadata for the blob.

    :param bytes key_encryption_key:
        The key-encryption-key used to wrap the cek associate with this blob.
    :return: A tuple containing the cek and iv for this blob as well as the
        serialized encryption metadata for the blob.
    :rtype: (bytes, bytes, str)
    '''
    encryption_data = None
    content_encryption_key = None
    initialization_vector = None
    if key_encryption_key:
        _validate_key_encryption_key_wrap(key_encryption_key)
        content_encryption_key = urandom(32)
        initialization_vector = urandom(16)
        encryption_data = _generate_encryption_data_dict(key_encryption_key,
                                                         content_encryption_key,
                                                         initialization_vector)
        encryption_data['EncryptionMode'] = 'FullBlob'
        encryption_data = dumps(encryption_data)

    return content_encryption_key, initialization_vector, encryption_data


def decrypt_blob(require_encryption, key_encryption_key, key_resolver,
                 content, start_offset, end_offset, response_headers):
    '''
    Decrypts the given blob contents and returns only the requested range.

    :param bool require_encryption:
        Whether or not the calling blob service requires objects to be decrypted.
    :param object key_encryption_key:
        The user-provided key-encryption-key. Must implement the following methods:
        wrap_key(key)--wraps the specified key using an algorithm of the user's choice.
        get_key_wrap_algorithm()--returns the algorithm used to wrap the specified symmetric key.
        get_kid()--returns a string key id for this key-encryption-key.
    :param key_resolver(kid):
        The user-provided key resolver. Uses the kid string to return a key-encryption-key
        implementing the interface defined above.
    :return: The decrypted blob content.
    :rtype: bytes
    '''
    try:
        encryption_data = _dict_to_encryption_data(loads(response_headers['x-ms-meta-encryptiondata']))
    except:  # pylint: disable=bare-except
        if require_encryption:
            raise ValueError(
                'Encryption required, but received data does not contain appropriate metatadata.' + \
                'Data was either not encrypted or metadata has been lost.')

        return content

    if encryption_data.encryption_agent.encryption_algorithm != _EncryptionAlgorithm.AES_CBC_256:
        raise ValueError('Specified encryption algorithm is not supported.')

    blob_type = response_headers['x-ms-blob-type']

    iv = None
    unpad = False
    if 'content-range' in response_headers:
        content_range = response_headers['content-range']
        # Format: 'bytes x-y/size'

        # Ignore the word 'bytes'
        content_range = content_range.split(' ')

        content_range = content_range[1].split('-')
        content_range = content_range[1].split('/')
        end_range = int(content_range[0])
        blob_size = int(content_range[1])

        if start_offset >= 16:
            iv = content[:16]
            content = content[16:]
            start_offset -= 16
        else:
            iv = encryption_data.content_encryption_IV

        if end_range == blob_size - 1:
            unpad = True
    else:
        unpad = True
        iv = encryption_data.content_encryption_IV

    if blob_type == 'PageBlob':
        unpad = False

    content_encryption_key = _validate_and_unwrap_cek(encryption_data, key_encryption_key, key_resolver)
    cipher = _generate_AES_CBC_cipher(content_encryption_key, iv)
    decryptor = cipher.decryptor()

    content = decryptor.update(content) + decryptor.finalize()
    if unpad:
        unpadder = PKCS7(128).unpadder()
        content = unpadder.update(content) + unpadder.finalize()

    return content[start_offset: len(content) - end_offset]


def get_blob_encryptor_and_padder(cek, iv, should_pad):
    encryptor = None
    padder = None

    if cek is not None and iv is not None:
        cipher = _generate_AES_CBC_cipher(cek, iv)
        encryptor = cipher.encryptor()
        padder = PKCS7(128).padder() if should_pad else None

    return encryptor, padder


def encrypt_queue_message(message, key_encryption_key):
    '''
    Encrypts the given plain text message using AES256 in CBC mode with 128 bit padding.
    Wraps the generated content-encryption-key using the user-provided key-encryption-key (kek).
    Returns a json-formatted string containing the encrypted message and the encryption metadata.

    :param object message:
        The plain text messge to be encrypted.
    :param object key_encryption_key:
        The user-provided key-encryption-key. Must implement the following methods:
        wrap_key(key)--wraps the specified key using an algorithm of the user's choice.
        get_key_wrap_algorithm()--returns the algorithm used to wrap the specified symmetric key.
        get_kid()--returns a string key id for this key-encryption-key.
    :return: A json-formatted string containing the encrypted message and the encryption metadata.
    :rtype: str
    '''

    _validate_not_none('message', message)
    _validate_not_none('key_encryption_key', key_encryption_key)
    _validate_key_encryption_key_wrap(key_encryption_key)

    # AES256 uses 256 bit (32 byte) keys and always with 16 byte blocks
    content_encryption_key = os.urandom(32)
    initialization_vector = os.urandom(16)

    # Queue encoding functions all return unicode strings, and encryption should
    # operate on binary strings.
    message = message.encode('utf-8')

    cipher = _generate_AES_CBC_cipher(content_encryption_key, initialization_vector)

    # PKCS7 with 16 byte blocks ensures compatibility with AES.
    padder = PKCS7(128).padder()
    padded_data = padder.update(message) + padder.finalize()

    # Encrypt the data.
    encryptor = cipher.encryptor()
    encrypted_data = encryptor.update(padded_data) + encryptor.finalize()

    # Build the dictionary structure.
    queue_message = {'EncryptedMessageContents': encode_base64(encrypted_data),
                     'EncryptionData': _generate_encryption_data_dict(key_encryption_key,
                                                                      content_encryption_key,
                                                                      initialization_vector)}

    return dumps(queue_message)


def decrypt_queue_message(message, response, require_encryption, key_encryption_key, resolver):
    '''
    Returns the decrypted message contents from an EncryptedQueueMessage.
    If no encryption metadata is present, will return the unaltered message.
    :param str message:
        The JSON formatted QueueEncryptedMessage contents with all associated metadata.
    :param bool require_encryption:
        If set, will enforce that the retrieved messages are encrypted and decrypt them.
    :param object key_encryption_key:
        The user-provided key-encryption-key. Must implement the following methods:
        unwrap_key(key, algorithm)
            - returns the unwrapped form of the specified symmetric key usingthe string-specified algorithm.
        get_kid()
            - returns a string key id for this key-encryption-key.
    :param function resolver(kid):
        The user-provided key resolver. Uses the kid string to return a key-encryption-key
        implementing the interface defined above.
    :return: The plain text message from the queue message.
    :rtype: str
    '''

    try:
        message = loads(message)

        encryption_data = _dict_to_encryption_data(message['EncryptionData'])
        decoded_data = decode_base64_to_bytes(message['EncryptedMessageContents'])
    except (KeyError, ValueError):
        # Message was not json formatted and so was not encrypted
        # or the user provided a json formatted message.
        if require_encryption:
            raise ValueError('Message was not encrypted.')

        return message
    try:
        return _decrypt_message(decoded_data, encryption_data, key_encryption_key, resolver).decode('utf-8')
    except Exception as error:
        raise HttpResponseError(
            message="Decryption failed.",
            response=response,
            error=error)
