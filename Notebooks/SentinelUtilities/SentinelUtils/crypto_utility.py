# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
"""
cryto_utility module:
This module provides encryption and decryption functionalities
"""

from cryptography.fernet import Fernet


class CryptoUtility():
    """ This class provides utility methods to encrypt and decrypt """
    def __init__(self, key):
        self.key = key

    @staticmethod
    def generate_key():
        """ Generate key """

        return Fernet.generate_key()

    def encrypt_text(self, text):
        """ Encrypt input text using key """

        fernet = Fernet(self.key)
        en_text = fernet.encrypt(text)
        return en_text

    def decrypt_text(self, en_text):
        """ Decrypt input text using key """

        fernet = Fernet(self.key)
        re_text = fernet.decrypt(en_text)
        return re_text.decode('utf-8')
