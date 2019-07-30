# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
"""
log module:
This module provides log functionalities through Azure Application Insights
"""


from applicationinsights import TelemetryClient
from SentinelUtils.crypto_utility import CryptoUtility


class Log:
    """ The class performs log action """

    def __init__(self):
        self.key = b'IVnGT69i43R1i6qokpVxIx_tE2MyBlMebu4yJfJh1Ow='
        # pylint: disable=line-too-long
        self.ai_key = b'gAAAAABdN3UmwZJHHxTybj0KRbKNehSo55DZ5Bi2QtohQsrEgy-WZNWDQAETVnaeJbQ4S0ltZLkebi_hhueaxl_uxYE5HheuB0ZFobq1IzgE163jUsjSLqilcqzy_uLKkSTYHAxYNLxL'

    def log(self, telemetry_instance):
        """ Log Telemetry instance """

        crypto = CryptoUtility(self.key)
        client = TelemetryClient(crypto.decrypt_text(self.ai_key))
        client.track_trace(str(telemetry_instance))
        client.flush()

    def log_event(self, message):
        """ Log simple message in strinbg """

        crypto = CryptoUtility(self.key)
        client = TelemetryClient(crypto.decrypt_text(self.ai_key))
        client.track_event(message)
        client.flush()
