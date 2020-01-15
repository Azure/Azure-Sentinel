# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
"""
input validation module:
This module validates user input, it throwes exceptions if validation fails
"""

from SentinelExceptions import InputError

# pylint: disable-msg=R0903
class InputValidation():
    """ This class validates user inputs """
    @staticmethod

    def validate_input(name, text):
        """ Validating input, no None or empty """
        if not text:
            raise InputError(name)
