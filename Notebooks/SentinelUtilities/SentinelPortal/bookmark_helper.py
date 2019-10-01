# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
"""
Hunting Bookmark Helper:
This module provides helper methods to initialize and
manipulate Hunting Bookmark (create, read, and delete).
"""
# pylint: disable-msg=C0103
# pylint: disable-msg=E0401
# pylint: disable-msg=E0602
# pylint: disable-msg=R0902
# pylint: disable-msg=R0903
# pylint: disable-msg=R0913
# pylint: disable-msg=W0201
# pylint: disable=line-too-long

# BookmarkProperties
import uuid
# BookmarkHelper
import requests
import jsons
from SentinelUtils import InputValidation


class Constants():
    """ This class holds constants """
    TYPE = 'Microsoft.SecurityInsights/Bookmarks'
    ETAG = '*'
    BOOKMARK_RESOURCE_BASE = '/subscriptions/{0}/resourceGroups/{1}/providers/Microsoft.OperationalInsights/workspaces/{2}/providers/Microsoft.SecurityInsights/bookmarks'
    BOOKMARK_ID = '/{0}'
    BOOKMARK_RESOURCE_ID = BOOKMARK_RESOURCE_BASE + BOOKMARK_ID

class EntityType():
    """ This class holds entity type enums """
    BOOKMARK = 'Bookmark'
    SECURITYALERT = 'SecurityAlert'
    ACCOUNT = 'Account'
    HOST = 'Host'
    MALWARE = 'Malware'
    FILE = 'File'
    PROCESS = 'Process'
    CLOUDAPPLICATION = 'CloudApplication'
    DNSRESOLUTION = 'DnsResolution'
    AZURERESOURCE = 'AzureResource'
    FILEHASH = 'FileHash'
    REGISTRYKEY = 'RegistryKey'
    REGISTRYVALUE = 'RegistryValue'
    SECURITYGROUP = 'SecurityGroup'
    URL = 'Url'

class BookmarkProperties():
    """ This class holds properties for Hunting bookmark """

    def __init__(self,
                 display_name,
                 query,
                 query_result=None,
                 tag_list=None,
                 notes=None,
                 event_time=None,
                 query_start_time=None,
                 query_end_time=None):
        self.displayName = display_name
        self.labels = tag_list
        self.query = query
        self.queryResult = query_result
        self.notes = notes
        self.eventTime = event_time
        self.queryStartTime = query_start_time
        self.queryEndTime = query_end_time
        self.bookmarkId = str(uuid.uuid4())

    @property
    def bookmarkId(self):
        """ bookmarkId getter """
        return self._bookmarkId

    @bookmarkId.setter
    def bookmarkId(self, bookmark_id):
        """ bookmarkId setter """
        self._bookmarkId = bookmark_id

    @property
    def displayName(self):
        """ displayName getter """
        return self._displayName

    @displayName.setter
    def displayName(self, display_name):
        """ displayName setter """
        InputValidation.validate_input('display_name', display_name)
        self._displayName = display_name

    @property
    def labels(self):
        """ labels getter """
        return self._labels

    @labels.setter
    def labels(self, tag_list):
        """ labels setter """
        if tag_list:
            self._labels = tag_list
        else:
            self._labels = []

    @property
    def query(self):
        """ query """
        return self._query

    @query.setter
    def query(self, query):
        """ query setter """
        InputValidation.validate_input('query', query)
        self._query = query

    @property
    def queryResult(self):
        """ queryResult """
        return self._queryResult

    @queryResult.setter
    def queryResult(self, query_result):
        """ queryResult setter """
        if query_result:
            self._queryResult = query_result
        else:
            self._queryResult = '{}'

    @property
    def notes(self):
        """ notes getter """
        return self._notes

    @notes.setter
    def notes(self, notes):
        """ notes setter """
        self._notes = notes

    @property
    def eventTime(self):
        """ eventTime """
        return self._eventTime

    @eventTime.setter
    def eventTime(self, event_time):
        """ eventTime setter """
        self._eventTime = event_time

    @property
    def queryStartTime(self):
        """ queryStartTime """
        return self._queryStartTime

    @queryStartTime.setter
    def queryStartTime(self, query_start_time):
        """ queryStartTime setter """
        self._queryStartTime = query_start_time

    @property
    def queryEndTime(self):
        """ queryEndTime """
        return self._queryEndTime

    @queryEndTime.setter
    def queryEndTime(self, query_end_time):
        """ queryEndTime setter """
        self._queryEndTime = query_end_time

class BookmarkModel():
    """ This class holds data model for Bookmark """

    def __init__(self,
                 bookmark_name,
                 subscription_id,
                 resource_group_name,
                 workspace_name,
                 bookmark_properties):
        self.name = bookmark_name
        self.type = Constants.TYPE
        self.etag = Constants.ETAG
        self.properties = bookmark_properties
        self.bookmark_resource_base = Constants.BOOKMARK_RESOURCE_BASE.format(subscription_id, resource_group_name, workspace_name)
        self.id = self.bookmark_resource_base + Constants.BOOKMARK_ID.format(bookmark_properties.bookmarkId)

    @property
    def id(self):
        """ id getter """
        return self._id

    @id.setter
    def id(self, bookmark_resource_id):
        """ id setter """
        self._id = bookmark_resource_id

    @property
    def name(self):
        """ name getter """
        return self._name

    @name.setter
    def name(self, bookmark_name):
        """ name setter """
        InputValidation.validate_input('bookmark_name', bookmark_name)
        self._name = bookmark_name

    @property
    def type(self):
        """ type getter """
        return self._type

    @type.setter
    def type(self, t):
        """ type setter """
        self._type = t

    @property
    def etag(self):
        """ etag getter """
        return self._etag

    @etag.setter
    def etag(self, etag):
        """ etag setter """
        self._etag = etag

    @property
    def properties(self):
        """ properties getter """
        return self._properties

    @properties.setter
    def properties(self, bookmark_properties):
        """ properties setter """
        InputValidation.validate_input('bookmark_properties', bookmark_properties)
        self._properties = bookmark_properties

# pylint: disable-msg=W0703
class BookmarkHelper:
    """ This class provides CRUD methods for bookmark """

    BOOKMARK_BASE_URL = 'https://management.azure.com'
    BOOKMARK_API_VERSION = '?api-version=2019-01-01-preview'

    def __init__(self, bookmark_model):
        self._bookmark_model = bookmark_model

    @staticmethod
    def __set_header(access_token):
        return {'Authorization': 'Bearer ' + access_token}

    def __set_rp_put_url(self):
        return self.BOOKMARK_BASE_URL + self._bookmark_model.id + self.BOOKMARK_API_VERSION

    def __set_rp_get_url(self):
        return self.BOOKMARK_BASE_URL + self._bookmark_model.bookmark_resource_base + self.BOOKMARK_API_VERSION

    def __set_rp_delete_url(self):
        return self.BOOKMARK_BASE_URL + self._bookmark_model.id + self.BOOKMARK_API_VERSION

    def __generate_bookmark_payload(self):
        items = jsons.dump(self._bookmark_model, strip_privates=True)
        return jsons.dump(self.__cleanup_json(items))

    def __cleanup_json(self, data):
        """
            Delete keys with the value ``None`` in a dictionary, recursively.
            This alters the input so you may wish to ``copy`` the dict first.
        """
        for key, value in list(data.items()):
            if key == 'bookmark_resource_base':
                del data[key]
            elif value is None:
                del data[key]
            elif isinstance(value, dict):
                self.__cleanup_json(value)

        return data

    def add_bookmark(self, access_token):
        """ Create a hunting bookmark """
        try:
            result = requests.put(
                self.__set_rp_put_url(),
                headers=BookmarkHelper.__set_header(access_token),
                json=self.__generate_bookmark_payload())
            print('Success')
            return result
        except Exception as e:
            print(str(e))

    def get_bookmarks(self, access_token):
        """ Retrieve hunting bookmarks for workspace """
        try:
            result = requests.get(
                self.__set_rp_get_url(),
                headers=BookmarkHelper.__set_header(access_token))
            print('Success')
            return result
        except Exception as e:
            print(str(e))

    def delete_bookmark(self, access_token):
        """ Delete a hunting bookmark """
        try:
            result = requests.delete(
                self.__set_rp_delete_url(),
                headers=BookmarkHelper.__set_header(access_token))
            print('Success')
            return result
        except Exception as e:
            print(str(e))

# end of the class
