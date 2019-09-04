# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
"""
obfuscation_utility module:
This module provides obfuscation functionalities
"""

from cryptography.fernet import Fernet


class ObfuscationUtility():
    """ This class provides utility methods for obfuscation """
    def __init__(self, seed):
        self.seed = seed

    @staticmethod
    def generate_seed():
        """ Generate seed """

        return Fernet.generate_key()

    def obfuscate_text(self, text):
        """ Obfuscate input text using key """

        fernet = Fernet(self.seed)
        en_text = fernet.encrypt(text)
        return en_text

    def deobfuscate_text(self, en_text):
        """ De-obfuscate input text using key """

        fernet = Fernet(self.seed)
        re_text = fernet.decrypt(en_text)
        return re_text.decode('utf-8')
