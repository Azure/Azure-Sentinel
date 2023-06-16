# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
from enum import Enum
from typing import TYPE_CHECKING, Any, Dict, List

from azure.core.exceptions import HttpResponseError
from azure.core.paging import PageIterator
# from azure.core import CaseInsensitiveEnumMeta
# from six import with_metaclass

from ._generated.models import TableServiceStats as GenTableServiceStats
from ._generated.models import AccessPolicy as GenAccessPolicy
from ._generated.models import Logging as GeneratedLogging
from ._generated.models import Metrics as GeneratedMetrics
from ._generated.models import RetentionPolicy as GeneratedRetentionPolicy
from ._generated.models import CorsRule as GeneratedCorsRule
from ._generated.models import QueryOptions
from ._deserialize import (
    _convert_to_entity,
    _return_context_and_deserialized,
    _extract_continuation_token,
)
from ._error import _process_table_error
from ._constants import NEXT_PARTITION_KEY, NEXT_ROW_KEY, NEXT_TABLE_NAME

if TYPE_CHECKING:
    from ._generated.models import TableQueryResponse
    from ._generated.models import TableServiceProperties as GenTableServiceProperties


class TableAccessPolicy(GenAccessPolicy):
    """Access Policy class used by the set and get access policy methods.

    A stored access policy can specify the start time, expiry time, and
    permissions for the Shared Access Signatures with which it's associated.
    Depending on how you want to control access to your resource, you can
    specify all of these parameters within the stored access policy, and omit
    them from the URL for the Shared Access Signature. Doing so permits you to
    modify the associated signature's behavior at any time, as well as to revoke
    it. Or you can specify one or more of the access policy parameters within
    the stored access policy, and the others on the URL. Finally, you can
    specify all of the parameters on the URL. In this case, you can use the
    stored access policy to revoke the signature, but not to modify its behavior.

    Together the Shared Access Signature and the stored access policy must
    include all fields required to authenticate the signature. If any required
    fields are missing, the request will fail. Likewise, if a field is specified
    both in the Shared Access Signature URL and in the stored access policy, the
    request will fail with status code 400 (Bad Request).

    :keyword str permission:
        The permissions associated with the shared access signature. The
        user is restricted to operations allowed by the permissions.
        Required unless an id is given referencing a stored access policy
        which contains this field. This field must be omitted if it has been
        specified in an associated stored access policy.
    :keyword expiry:
        The time at which the shared access signature becomes invalid.
        Required unless an id is given referencing a stored access policy
        which contains this field. This field must be omitted if it has
        been specified in an associated stored access policy. Azure will always
        convert values to UTC. If a date is passed in without timezone info, it
        is assumed to be UTC.
    :paramtype expiry: ~datetime.datetime or str
    :keyword start:
        The time at which the shared access signature becomes valid. If
        omitted, start time for this call is assumed to be the time when the
        storage service receives the request. Azure will always convert values
        to UTC. If a date is passed in without timezone info, it is assumed to
        be UTC.
    :paramtype start: ~datetime.datetime or str
    """
    def __init__(self, **kwargs):  # pylint: disable=super-init-not-called
        self.start = kwargs.get('start')
        self.expiry = kwargs.get('expiry')
        self.permission = kwargs.get('permission')

    def __repr__(self):
        # type: () -> str
        return "TableAccessPolicy(start={}, expiry={}, permission={})".format(
            self.start, self.expiry, self.permission
        )[1024:]


class TableAnalyticsLogging(GeneratedLogging):
    """Azure Analytics Logging settings.

    All required parameters must be populated in order to send to Azure.

    :keyword str version: Required. The version of Storage Analytics to configure.
    :keyword bool delete: Required. Indicates whether all delete requests should be logged.
    :keyword bool read: Required. Indicates whether all read requests should be logged.
    :keyword bool write: Required. Indicates whether all write requests should be logged.
    :keyword ~azure.data.tables.TableRetentionPolicy retention_policy: Required.
        The retention policy for the metrics.
    """

    def __init__(self, **kwargs):  # pylint: disable=super-init-not-called
        # type: (Any)-> None
        self.version = kwargs.get("version", u"1.0")
        self.delete = kwargs.get("delete", False)
        self.read = kwargs.get("read", False)
        self.write = kwargs.get("write", False)
        self.retention_policy = kwargs.get("retention_policy") or TableRetentionPolicy()

    @classmethod
    def _from_generated(cls, generated):
        if not generated:
            return cls()
        return cls(
            version=generated.version,
            delete=generated.delete,
            read=generated.read,
            write=generated.write,
            retention_policy=TableRetentionPolicy._from_generated(  # pylint: disable=protected-access
                generated.retention_policy
            )
        )

    def __repr__(self):
        # type: () -> str
        return "TableAnalyticsLogging(version={}, delete={}, read={}, write={}, retention_policy={})".format(
            self.version, self.delete, self.read, self.write, self.retention_policy
        )[1024:]


class TableMetrics(GeneratedMetrics):
    """A summary of request statistics grouped by API in hour or minute aggregates.

    All required parameters must be populated in order to send to Azure.

    :keyword str version: The version of Storage Analytics to configure.
    :keyword bool enabled: Required. Indicates whether metrics are enabled for the service.
    :keyword bool include_apis: Indicates whether metrics should generate summary
        statistics for called API operations.
    :keyword ~azure.data.tables.TableRetentionPolicy retention_policy: Required.
        The retention policy for the metrics.
    """

    def __init__(self, **kwargs):  # pylint: disable=super-init-not-called
        # type: (Any) -> None
        self.version = kwargs.get("version", u"1.0")
        self.enabled = kwargs.get("enabled", False)
        self.include_apis = kwargs.get("include_apis")
        self.retention_policy = kwargs.get("retention_policy") or TableRetentionPolicy()

    @classmethod
    def _from_generated(cls, generated):
        # type: (...) -> TableMetrics
        """A summary of request statistics grouped by API in hour or minute aggregates.

        :param TableMetrics generated: generated Metrics
        """
        if not generated:
            return cls()
        return cls(
            version=generated.version,
            enabled=generated.enabled,
            include_apis=generated.include_apis,
            retention_policy=TableRetentionPolicy._from_generated(  # pylint: disable=protected-access
                generated.retention_policy
            )
        )

    def __repr__(self):
        # type: () -> str
        return "TableMetrics(version={}, enabled={}, include_apis={}, retention_policy={})".format(
            self.version, self.enabled, self.include_apis, self.retention_policy
        )[1024:]


class TableRetentionPolicy(GeneratedRetentionPolicy):
    def __init__(self, **kwargs):  # pylint: disable=super-init-not-called
        # type: (Any) -> None
        """The retention policy which determines how long the associated data should
        persist.

        All required parameters must be populated in order to send to Azure.

        :keyword bool enabled: Required. Indicates whether a retention policy is enabled
            for the storage service. Default value is False.
        :keyword int days: Indicates the number of days that metrics or logging or
            soft-deleted data should be retained. All data older than this value will
            be deleted. Must be specified if policy is enabled.
        """
        self.enabled = kwargs.get('enabled', False)
        self.days = kwargs.get('days')
        if self.enabled and (self.days is None):
            raise ValueError("If policy is enabled, 'days' must be specified.")

    @classmethod
    def _from_generated(cls, generated, **kwargs):  # pylint: disable=unused-argument
        # type: (GeneratedRetentionPolicy, Dict[str, Any]) -> TableRetentionPolicy
        """The retention policy which determines how long the associated data should
        persist.

        All required parameters must be populated in order to send to Azure.

        :param TableRetentionPolicy generated: Generated Retention Policy
        """

        if not generated:
            return cls()
        return cls(
            enabled=generated.enabled,
            days=generated.days,
        )
    def __repr__(self):
        # type: () -> str
        return "TableRetentionPolicy(enabled={}, days={})".format(self.enabled, self.days)[1024:]


class TableCorsRule(object):
    """CORS is an HTTP feature that enables a web application running under one
    domain to access resources in another domain. Web browsers implement a
    security restriction known as same-origin policy that prevents a web page
    from calling APIs in a different domain; CORS provides a secure way to
    allow one domain (the origin domain) to call APIs in another domain.

    All required parameters must be populated in order to send to Azure.

    :param list[str] allowed_origins:
        A list of origin domains that will be allowed via CORS, or "*" to allow
        all domains. The list of must contain at least one entry. Limited to 64
        origin domains. Each allowed origin can have up to 256 characters.
    :param list[str] allowed_methods:
        A list of HTTP methods that are allowed to be executed by the origin.
        The list of must contain at least one entry. For Azure Storage,
        permitted methods are DELETE, GET, HEAD, MERGE, POST, OPTIONS or PUT.
    :keyword int max_age_in_seconds:
        The number of seconds that the client/browser should cache a
        pre-flight response.
    :keyword list[str] exposed_headers:
        Defaults to an empty list. A list of response headers to expose to CORS
        clients. Limited to 64 defined headers and two prefixed headers. Each
        header can be up to 256 characters.
    :keyword list[str] allowed_headers:
        Defaults to an empty list. A list of headers allowed to be part of
        the cross-origin request. Limited to 64 defined headers and 2 prefixed
        headers. Each header can be up to 256 characters.
    """

    def __init__(
        self,
        allowed_origins,  # type: List[str]
        allowed_methods,  # type: List[str]
        **kwargs  # type: Any
    ):
        # type: (...)-> None
        self.allowed_origins = allowed_origins
        self.allowed_methods = allowed_methods
        self.allowed_headers = kwargs.get("allowed_headers", [])
        self.exposed_headers = kwargs.get("exposed_headers", [])
        self.max_age_in_seconds = kwargs.get("max_age_in_seconds", 0)

    def _to_generated(self):
        return GeneratedCorsRule(
            allowed_origins=",".join(self.allowed_origins),
            allowed_methods=",".join(self.allowed_methods),
            allowed_headers=",".join(self.allowed_headers),
            exposed_headers=",".join(self.exposed_headers),
            max_age_in_seconds=self.max_age_in_seconds
        )

    @classmethod
    def _from_generated(cls, generated):
        exposedheaders = generated.exposed_headers.split(',') if generated.exposed_headers else []
        allowedheaders = generated.allowed_headers.split(',') if generated.allowed_headers else []
        return cls(
            generated.allowed_origins.split(','),
            generated.allowed_methods.split(','),
            allowed_headers=allowedheaders,
            exposed_headers=exposedheaders,
            max_age_in_seconds=generated.max_age_in_seconds,
        )

    def __repr__(self):
        # type: () -> str
        return "TableCorsRules(allowed_origins={}, allowed_methods={}, allowed_headers={}, exposed_headers={}, max_age_in_seconds={})".format(  # pylint: disable=line-too-long
            self.allowed_origins, self.allowed_methods, self.allowed_headers, self.exposed_headers, self.max_age_in_seconds  # pylint: disable=line-too-long
        )[1024:]


class TablePropertiesPaged(PageIterator):
    """An iterable of Table properties.

    :param callable command: Function to retrieve the next page of items.
    :keyword int results_per_page: The maximum number of results retrieved per API call.
    :keyword str filter: The filter to apply to results.
    :keyword str continuation_token: An opaque continuation token.
    """

    def __init__(self, command, **kwargs):
        super(TablePropertiesPaged, self).__init__(
            self._get_next_cb,
            self._extract_data_cb,
            continuation_token=kwargs.get("continuation_token") or "",
        )
        self._command = command
        self._headers = None
        self._response = None
        self.results_per_page = kwargs.get("results_per_page")
        self.filter = kwargs.get("filter")
        self._location_mode = None

    def _get_next_cb(self, continuation_token, **kwargs):
        query_options = QueryOptions(top=self.results_per_page, filter=self.filter)
        try:
            return self._command(
                query_options=query_options,
                next_table_name=continuation_token or None,
                cls=kwargs.pop("cls", None) or _return_context_and_deserialized,
                use_location=self._location_mode,
            )
        except HttpResponseError as error:
            _process_table_error(error)

    def _extract_data_cb(self, get_next_return):
        self._location_mode, self._response, self._headers = get_next_return
        props_list = [
            TableItem._from_generated(t, **self._headers) for t in self._response.value  # pylint: disable=protected-access
        ]
        return self._headers[NEXT_TABLE_NAME] or None, props_list


class TableEntityPropertiesPaged(PageIterator):
    """An iterable of TableEntity properties.

    :param callable command: Function to retrieve the next page of items.
    :param str table: The name of the table.
    :keyword int results_per_page: The maximum number of results retrieved per API call.
    :keyword str filter: The filter to apply to results.
    :keyword str select: The select filter to apply to results.
    :keyword str continuation_token: An opaque continuation token.
    """

    def __init__(self, command, table, **kwargs):
        super(TableEntityPropertiesPaged, self).__init__(
            self._get_next_cb,
            self._extract_data_cb,
            continuation_token=kwargs.get("continuation_token") or {},
        )
        self._command = command
        self._headers = None
        self._response = None
        self.table = table
        self.results_per_page = kwargs.get("results_per_page")
        self.filter = kwargs.get("filter")
        self.select = kwargs.get("select")
        self._location_mode = None

    def _get_next_cb(self, continuation_token, **kwargs):
        next_partition_key, next_row_key = _extract_continuation_token(
            continuation_token
        )
        query_options = QueryOptions(
            top=self.results_per_page, select=self.select, filter=self.filter
        )
        try:
            return self._command(
                query_options=query_options,
                next_row_key=next_row_key,
                next_partition_key=next_partition_key,
                table=self.table,
                cls=kwargs.pop("cls", None) or _return_context_and_deserialized,
                use_location=self._location_mode,
            )
        except HttpResponseError as error:
            _process_table_error(error)

    def _extract_data_cb(self, get_next_return):
        self._location_mode, self._response, self._headers = get_next_return
        props_list = [_convert_to_entity(t) for t in self._response.value]
        next_entity = {}
        if self._headers[NEXT_PARTITION_KEY] or self._headers[NEXT_ROW_KEY]:
            next_entity = {
                "PartitionKey": self._headers[NEXT_PARTITION_KEY],
                "RowKey": self._headers[NEXT_ROW_KEY],
            }
        return next_entity or None, props_list


class TableSasPermissions(object):
    def __init__(self, **kwargs):
        # type: (Any) -> None
        """
        :keyword bool read:
            Get entities and query entities.
        :keyword bool add:
            Add entities. Add and Update permissions are required for upsert operations.
        :keyword bool update:
            Update entities. Add and Update permissions are required for upsert operations.
        :keyword bool delete:
            Delete entities.
        """
        _str = kwargs.pop('_str', "") or ""
        self.read = kwargs.pop("read", False) or ("r" in _str)
        self.add = kwargs.pop("add", False) or ("a" in _str)
        self.update = kwargs.pop("update", False) or ("u" in _str)
        self.delete = kwargs.pop("delete", False) or ("d" in _str)

    def __or__(self, other):
        # type: (TableSasPermissions) -> TableSasPermissions
        """
        :param other:
        :type other: :class:`~azure.data.tables.TableSasPermissions`
        """
        return TableSasPermissions(_str=str(self) + str(other))

    def __add__(self, other):
        # type: (TableSasPermissions) -> TableSasPermissions
        """
        :param other:
        :type other: :class:`~azure.data.tables.TableSasPermissions`
        """
        return TableSasPermissions(_str=str(self) + str(other))

    def __str__(self):
        # type: () -> str
        return (
            ("r" if self.read else "")
            + ("a" if self.add else "")
            + ("u" if self.update else "")
            + ("d" if self.delete else "")
        )

    def __repr__(self):
        # type: () -> str
        return "TableSasPermissions(read={}, add={}, update={}, delete={})".format(
            self.read, self.add, self.update, self.delete
        )[1024:]

    @classmethod
    def from_string(
        cls,
        permission,
        **kwargs
    ):
        # Type: (str, Dict[str, Any]) -> AccountSasPermissions
        """Create AccountSasPermissions from a string.

        To specify read, write, delete, etc. permissions you need only to
        include the first letter of the word in the string. E.g. for read and write
        permissions you would provide a string "rw".

        :param str permission: Specify permissions in
            the string with the first letter of the word.
        :keyword callable cls: A custom type or function that will be passed the direct response
        :return: An AccountSasPermissions object
        :rtype: :class:`~azure.data.tables.AccountSasPermissions`
        """
        p_read = "r" in permission
        p_add = "a" in permission
        p_delete = "d" in permission
        p_update = "u" in permission

        parsed = cls(
            **dict(kwargs, read=p_read, add=p_add, delete=p_delete, update=p_update)
        )
        parsed._str = permission  # pylint: disable=protected-access,attribute-defined-outside-init
        return parsed


def service_stats_deserialize(generated):
    # type: (GenTableServiceStats) -> Dict[str, Any]
    """Deserialize a ServiceStats objects into a dict."""
    return {
        "geo_replication": {
            "status": generated.geo_replication.status,  # type: ignore
            "last_sync_time": generated.geo_replication.last_sync_time,  # type: ignore
        }
    }


def service_properties_deserialize(generated):
    # type: (GenTableServiceProperties) -> Dict[str, Any]
    """Deserialize a ServiceProperties objects into a dict."""
    return {
        "analytics_logging": TableAnalyticsLogging._from_generated(generated.logging),  # pylint: disable=protected-access
        "hour_metrics": TableMetrics._from_generated(  # pylint: disable=protected-access
            generated.hour_metrics
        ),
        "minute_metrics": TableMetrics._from_generated(  # pylint: disable=protected-access
            generated.minute_metrics
        ),
        "cors": [
            TableCorsRule._from_generated(cors)  # pylint: disable=protected-access
            for cors in generated.cors  # type: ignore
        ],
    }


class TableItem(object):
    """
    Represents an Azure TableItem.
    Returned by TableServiceClient.list_tables and TableServiceClient.query_tables.

    :ivar str name: The name of the table.
    """

    def __init__(self, name):
        # type: (str) -> None
        """
        :param str name: Name of the Table
        """
        self.name = name

    # TODO: TableQueryResponse is not the correct type
    @classmethod
    def _from_generated(cls, generated, **kwargs):  # pylint: disable=unused-argument
        # type: (TableQueryResponse, Any) -> TableItem
        return cls(generated.table_name)  # type: ignore

    def __repr__(self):
        # type: () -> str
        return "TableItem(name={})".format(self.name)[1024:]


class TablePayloadFormat(object):
    """
    Specifies the accepted content type of the response payload. More information
    can be found here: https://msdn.microsoft.com/en-us/library/azure/dn535600.aspx
    """

    JSON_NO_METADATA = "application/json;odata=nometadata"
    """Returns no type information for the entity properties."""

    JSON_MINIMAL_METADATA = "application/json;odata=minimalmetadata"
    """Returns minimal type information for the entity properties."""

    JSON_FULL_METADATA = "application/json;odata=fullmetadata"
    """Returns minimal type information for the entity properties plus some extra odata properties."""


class UpdateMode(str, Enum): # pylint: disable=enum-must-inherit-case-insensitive-enum-meta
    REPLACE = "replace"
    MERGE = "merge"


class TransactionOperation(str, Enum): # pylint: disable=enum-must-inherit-case-insensitive-enum-meta
    CREATE = "create"
    UPSERT = "upsert"
    UPDATE = "update"
    DELETE = "delete"


class SASProtocol(str, Enum): # pylint: disable=enum-must-inherit-case-insensitive-enum-meta
    HTTPS = "https"
    HTTP = "http"


class LocationMode(str, Enum): # pylint: disable=enum-must-inherit-case-insensitive-enum-meta
    """
    Specifies the location the request should be sent to. This mode only applies
    for RA-GRS accounts which allow secondary read access. All other account types
    must use PRIMARY.
    """

    PRIMARY = "primary"  #: Requests should be sent to the primary location.
    SECONDARY = (
        "secondary"  #: Requests should be sent to the secondary location, if possible.
    )


class ResourceTypes(object):
    """
    Specifies the resource types that are accessible with the account SAS.

    :keyword bool service:
        Access to service-level APIs (e.g., Get/Set Service Properties,
        Get Service Stats, List Tables)
    :keyword bool object:
        Access to object-level APIs for tables (e.g. Get/Create/Query Entity etc.)
    """

    def __init__(self, **kwargs):
        # type: (Any) -> None
        self.service = kwargs.get('service', False)
        self.object = kwargs.get('object', False)
        self._str = ("s" if self.service else "") + ("o" if self.object else "")

    def __str__(self):
        return self._str

    @classmethod
    def from_string(cls, string):
        # type: (str) -> ResourceTypes
        """Create a ResourceTypes from a string.

        To specify service, container, or object you need only to
        include the first letter of the word in the string. E.g. service and container,
        you would provide a string "sc".

        :param str string: Specify service, container, or object in
            in the string with the first letter of the word.
        :return: A ResourceTypes object
        :rtype: :class:`~azure.data.tables.ResourceTypes`
        """
        res_service = "s" in string
        res_object = "o" in string

        parsed = cls(service=res_service, object=res_object)
        parsed._str = string  # pylint: disable = protected-access
        return parsed


class AccountSasPermissions(object):
    """
    :class:`~AccountSasPermissions` class to be used with generate_account_sas

    :ivar bool read:
        Valid for all signed resources types (Service, Container, and Object).
        Permits read permissions to the specified resource type.
    :ivar bool write:
        Valid for all signed resources types (Service, Container, and Object).
        Permits write permissions to the specified resource type.
    :ivar bool delete:
        Valid for Container and Object resource types, except for queue messages.
    :ivar bool list:
        Valid for Service and Container resource types only.
    :ivar bool add:
        Valid for the following Object resource types only: queue messages, and append blobs.
    :ivar bool create:
        Valid for the following Object resource types only: blobs and files.
        Users can create new blobs or files, but may not overwrite existing
        blobs or files.
    :ivar bool update:
        Valid for the following Object resource types only: queue messages.
    :ivar bool process:
        Valid for the following Object resource type only: queue messages.
    """

    def __init__(self, **kwargs):
        self.read = kwargs.pop("read", False)
        self.write = kwargs.pop("write", False)
        self.delete = kwargs.pop("delete", False)
        self.list = kwargs.pop("list", False)
        self.add = kwargs.pop("add", False)
        self.create = kwargs.pop("create", False)
        self.update = kwargs.pop("update", False)
        self.process = kwargs.pop("process", False)
        self._str = (
            ("r" if self.read else "")
            + ("w" if self.write else "")
            + ("d" if self.delete else "")
            + ("l" if self.list else "")
            + ("a" if self.add else "")
            + ("c" if self.create else "")
            + ("u" if self.update else "")
            + ("p" if self.process else "")
        )

    def __str__(self):
        return self._str

    @classmethod
    def from_string(cls, permission, **kwargs):
        # type: (str, Dict[str, Any]) -> AccountSasPermissions
        """Create AccountSasPermissions from a string.

        To specify read, write, delete, etc. permissions you need only to
        include the first letter of the word in the string. E.g. for read and write
        permissions you would provide a string "rw".

        :param permission: Specify permissions in the string with the first letter of the word.
        :type permission: str
        :return: An AccountSasPermissions object
        :rtype: :class:`~azure.data.tables.AccountSasPermissions`
        """
        p_read = "r" in permission
        p_write = "w" in permission
        p_delete = "d" in permission
        p_list = "l" in permission
        p_add = "a" in permission
        p_create = "c" in permission
        p_update = "u" in permission
        p_process = "p" in permission

        parsed = cls(
            **dict(
                kwargs,
                read=p_read,
                write=p_write,
                delete=p_delete,
                list=p_list,
                add=p_add,
                create=p_create,
                update=p_update,
                process=p_process,
            )
        )
        parsed._str = permission  # pylint: disable = protected-access
        return parsed
