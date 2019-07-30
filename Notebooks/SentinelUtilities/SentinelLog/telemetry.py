# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
"""
telemetry module:
This module data object classes based on Telemetry, including TraceTelemetry
"""

import json
from .log_utilities import LogUtilities


# pylint: disable=too-many-instance-attributes
class Telemetry:
    """ This is the base property class for logs """

    def __init__(self, title, tenant_domain, user_id):
        self.title = title
        self.tenant_domain = tenant_domain
        self.tenant_domain_hash = ''
        self.is_external_tenant = False
        self.user_id = user_id
        self.user_hash = ''
        self.__title = ''
        self.__tenant_domain_hash = ''
        self.__user_hash = ''
        self.__is_external_tenant = False

    def __repr__(self):
        """ ToString  method """
        filtered_dict = {k:v for (k, v) in self.__dict__.items() \
            if k not in ('tenant_domain', 'user_id')}
        return json.dumps(filtered_dict)

    @property
    def title(self):
        """ title getter """
        return self.__title

    @title.setter
    def title(self, title):
        """ title setter """
        LogUtilities.validate_input('title', title)
        self.__title = title

    @property
    def tenant_domain_hash(self):
        """ tenant_domain_hash getter """
        return self.__tenant_domain_hash

    @tenant_domain_hash.setter
    def tenant_domain_hash(self):
        """ tenant_domain_hash setter """
        self.__tenant_domain_hash = LogUtilities.generate_hash(self.tenant_domain)

    @property
    def is_external_tenant(self):
        """ is_external_tenant getter """
        return self.__is_external_tenant

    @is_external_tenant.setter
    def is_external_tenant(self):
        """ is_external_tenant setter """
        self.__is_external_tenant = LogUtilities.is_external_tenant(self.tenant_domain)

    @property
    def user_hash(self):
        """ user_hash getter """
        return self.__user_hash

    @user_hash.setter
    def user_hash(self):
        """ user_hash setter """
        LogUtilities.validate_input('user id', self.user_id)
        self.__user_hash = LogUtilities.generate_hash(self.user_id)

class TraceTelemetry(Telemetry):
    """ This is a class providing properties for handling trace """

    # pylint: disable=too-many-arguments
    def __init__(self, title, tenant_domain, user_id, value, extension):
        super().__init__(title, tenant_domain, user_id)
        self.value = value
        self.extension = extension
        self.__value = ''
        self.__extension = ''

    @property
    def value(self):
        """ value getter """
        return self.__value

    @value.setter
    def value(self, value):
        """ value setter """
        self.__value = value

    @property
    def extension(self):
        """ extension getter """
        return self.__extension

    @extension.setter
    def extension(self, extension):
        """ extension setter """
        self.__extension = extension
