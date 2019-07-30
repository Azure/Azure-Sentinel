# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
"""
log_utilities module:
This module provides help functions for logging
"""

import hashlib
import re
from SentinelExceptions import InputError


class LogUtilities:
    """ This class provides static methods to support logging """

    @staticmethod
    def generate_hash(text):
        """ Generate hash to replace user-related information """

        hash_val = hashlib.md5(text.encode())
        return hash_val.hexdigest()

    @staticmethod
    def validate_input(name, text):
        """ Validating input, no None or empty """

        if not text:
            raise InputError(name)

    @staticmethod
    def is_external_tenant(tenant_domain):
        """ Check if a tenant is external """

        if tenant_domain.strip().lower() == 'microsoft.onmicrosoft.com':
            return False
        return True

    @staticmethod
    def sanitize_input(text):
        """ Remove special chars, and limit size to 500 characters """
        if not text:
            return None

        replaced = re.sub('[^a-zA-Z0-9._,!-]', ' ', text)
        if not replaced:
            return None

        if len(replaced) > 500:
            return replaced[0:500]

        return replaced
