# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

from typing import (  # pylint: disable=unused-import
    Union, Optional, Any, TYPE_CHECKING
)

from ._shared import sign_string, url_quote
from ._shared.constants import X_MS_VERSION
from ._shared.models import Services
from ._shared.shared_access_signature import SharedAccessSignature, _SharedAccessHelper, \
    QueryStringConstants

if TYPE_CHECKING:
    from datetime import datetime
    from ..blob import (
        ResourceTypes,
        AccountSasPermissions,
        UserDelegationKey,
        ContainerSasPermissions,
        BlobSasPermissions
    )


class BlobQueryStringConstants(object):
    SIGNED_TIMESTAMP = 'snapshot'


class BlobSharedAccessSignature(SharedAccessSignature):
    '''
    Provides a factory for creating blob and container access
    signature tokens with a common account name and account key.  Users can either
    use the factory or can construct the appropriate service and use the
    generate_*_shared_access_signature method directly.
    '''

    def __init__(self, account_name, account_key=None, user_delegation_key=None):
        '''
        :param str account_name:
            The storage account name used to generate the shared access signatures.
        :param str account_key:
            The access key to generate the shares access signatures.
        :param ~azure.storage.blob.models.UserDelegationKey user_delegation_key:
            Instead of an account key, the user could pass in a user delegation key.
            A user delegation key can be obtained from the service by authenticating with an AAD identity;
            this can be accomplished by calling get_user_delegation_key on any Blob service object.
        '''
        super(BlobSharedAccessSignature, self).__init__(account_name, account_key, x_ms_version=X_MS_VERSION)
        self.user_delegation_key = user_delegation_key

    def generate_blob(self, container_name, blob_name, snapshot=None, version_id=None, permission=None,
                      expiry=None, start=None, policy_id=None, ip=None, protocol=None,
                      cache_control=None, content_disposition=None,
                      content_encoding=None, content_language=None,
                      content_type=None, **kwargs):
        '''
        Generates a shared access signature for the blob or one of its snapshots.
        Use the returned signature with the sas_token parameter of any BlobService.

        :param str container_name:
            Name of container.
        :param str blob_name:
            Name of blob.
        :param str snapshot:
            The snapshot parameter is an opaque DateTime value that,
            when present, specifies the blob snapshot to grant permission.
        :param BlobSasPermissions permission:
            The permissions associated with the shared access signature. The
            user is restricted to operations allowed by the permissions.
            Permissions must be ordered read, write, delete, list.
            Required unless an id is given referencing a stored access policy
            which contains this field. This field must be omitted if it has been
            specified in an associated stored access policy.
        :param expiry:
            The time at which the shared access signature becomes invalid.
            Required unless an id is given referencing a stored access policy
            which contains this field. This field must be omitted if it has
            been specified in an associated stored access policy. Azure will always
            convert values to UTC. If a date is passed in without timezone info, it
            is assumed to be UTC.
        :type expiry: datetime or str
        :param start:
            The time at which the shared access signature becomes valid. If
            omitted, start time for this call is assumed to be the time when the
            storage service receives the request. Azure will always convert values
            to UTC. If a date is passed in without timezone info, it is assumed to
            be UTC.
        :type start: datetime or str
        :param str policy_id:
            A unique value up to 64 characters in length that correlates to a
            stored access policy. To create a stored access policy, use
            set_blob_service_properties.
        :param str ip:
            Specifies an IP address or a range of IP addresses from which to accept requests.
            If the IP address from which the request originates does not match the IP address
            or address range specified on the SAS token, the request is not authenticated.
            For example, specifying sip=168.1.5.65 or sip=168.1.5.60-168.1.5.70 on the SAS
            restricts the request to those IP addresses.
        :param str protocol:
            Specifies the protocol permitted for a request made. The default value
            is https,http. See :class:`~azure.storage.common.models.Protocol` for possible values.
        :param str cache_control:
            Response header value for Cache-Control when resource is accessed
            using this shared access signature.
        :param str content_disposition:
            Response header value for Content-Disposition when resource is accessed
            using this shared access signature.
        :param str content_encoding:
            Response header value for Content-Encoding when resource is accessed
            using this shared access signature.
        :param str content_language:
            Response header value for Content-Language when resource is accessed
            using this shared access signature.
        :param str content_type:
            Response header value for Content-Type when resource is accessed
            using this shared access signature.
        '''
        resource_path = container_name + '/' + blob_name

        sas = _BlobSharedAccessHelper()
        sas.add_base(permission, expiry, start, ip, protocol, self.x_ms_version)
        sas.add_id(policy_id)

        resource = 'bs' if snapshot else 'b'
        resource = 'bv' if version_id else resource
        resource = 'd' if kwargs.pop("is_directory", None) else resource
        sas.add_resource(resource)

        sas.add_timestamp(snapshot or version_id)
        sas.add_override_response_headers(cache_control, content_disposition,
                                          content_encoding, content_language,
                                          content_type)
        sas.add_info_for_hns_account(**kwargs)
        sas.add_resource_signature(self.account_name, self.account_key, resource_path,
                                   user_delegation_key=self.user_delegation_key)

        return sas.get_token()

    def generate_container(self, container_name, permission=None, expiry=None,
                           start=None, policy_id=None, ip=None, protocol=None,
                           cache_control=None, content_disposition=None,
                           content_encoding=None, content_language=None,
                           content_type=None, **kwargs):
        '''
        Generates a shared access signature for the container.
        Use the returned signature with the sas_token parameter of any BlobService.

        :param str container_name:
            Name of container.
        :param ContainerSasPermissions permission:
            The permissions associated with the shared access signature. The
            user is restricted to operations allowed by the permissions.
            Permissions must be ordered read, write, delete, list.
            Required unless an id is given referencing a stored access policy
            which contains this field. This field must be omitted if it has been
            specified in an associated stored access policy.
        :param expiry:
            The time at which the shared access signature becomes invalid.
            Required unless an id is given referencing a stored access policy
            which contains this field. This field must be omitted if it has
            been specified in an associated stored access policy. Azure will always
            convert values to UTC. If a date is passed in without timezone info, it
            is assumed to be UTC.
        :type expiry: datetime or str
        :param start:
            The time at which the shared access signature becomes valid. If
            omitted, start time for this call is assumed to be the time when the
            storage service receives the request. Azure will always convert values
            to UTC. If a date is passed in without timezone info, it is assumed to
            be UTC.
        :type start: datetime or str
        :param str policy_id:
            A unique value up to 64 characters in length that correlates to a
            stored access policy. To create a stored access policy, use
            set_blob_service_properties.
        :param str ip:
            Specifies an IP address or a range of IP addresses from which to accept requests.
            If the IP address from which the request originates does not match the IP address
            or address range specified on the SAS token, the request is not authenticated.
            For example, specifying sip=168.1.5.65 or sip=168.1.5.60-168.1.5.70 on the SAS
            restricts the request to those IP addresses.
        :param str protocol:
            Specifies the protocol permitted for a request made. The default value
            is https,http. See :class:`~azure.storage.common.models.Protocol` for possible values.
        :param str cache_control:
            Response header value for Cache-Control when resource is accessed
            using this shared access signature.
        :param str content_disposition:
            Response header value for Content-Disposition when resource is accessed
            using this shared access signature.
        :param str content_encoding:
            Response header value for Content-Encoding when resource is accessed
            using this shared access signature.
        :param str content_language:
            Response header value for Content-Language when resource is accessed
            using this shared access signature.
        :param str content_type:
            Response header value for Content-Type when resource is accessed
            using this shared access signature.
        '''
        sas = _BlobSharedAccessHelper()
        sas.add_base(permission, expiry, start, ip, protocol, self.x_ms_version)
        sas.add_id(policy_id)
        sas.add_resource('c')
        sas.add_override_response_headers(cache_control, content_disposition,
                                          content_encoding, content_language,
                                          content_type)
        sas.add_info_for_hns_account(**kwargs)
        sas.add_resource_signature(self.account_name, self.account_key, container_name,
                                   user_delegation_key=self.user_delegation_key)
        return sas.get_token()


class _BlobSharedAccessHelper(_SharedAccessHelper):

    def add_timestamp(self, timestamp):
        self._add_query(BlobQueryStringConstants.SIGNED_TIMESTAMP, timestamp)

    def add_info_for_hns_account(self, **kwargs):
        self._add_query(QueryStringConstants.SIGNED_DIRECTORY_DEPTH, kwargs.pop('sdd', None))
        self._add_query(QueryStringConstants.SIGNED_AUTHORIZED_OID, kwargs.pop('preauthorized_agent_object_id', None))
        self._add_query(QueryStringConstants.SIGNED_UNAUTHORIZED_OID, kwargs.pop('agent_object_id', None))
        self._add_query(QueryStringConstants.SIGNED_CORRELATION_ID, kwargs.pop('correlation_id', None))

    def get_value_to_append(self, query):
        return_value = self.query_dict.get(query) or ''
        return return_value + '\n'

    def add_resource_signature(self, account_name, account_key, path, user_delegation_key=None):
        # pylint: disable = no-member
        if path[0] != '/':
            path = '/' + path

        canonicalized_resource = '/blob/' + account_name + path + '\n'

        # Form the string to sign from shared_access_policy and canonicalized
        # resource. The order of values is important.
        string_to_sign = \
            (self.get_value_to_append(QueryStringConstants.SIGNED_PERMISSION) +
             self.get_value_to_append(QueryStringConstants.SIGNED_START) +
             self.get_value_to_append(QueryStringConstants.SIGNED_EXPIRY) +
             canonicalized_resource)

        if user_delegation_key is not None:
            self._add_query(QueryStringConstants.SIGNED_OID, user_delegation_key.signed_oid)
            self._add_query(QueryStringConstants.SIGNED_TID, user_delegation_key.signed_tid)
            self._add_query(QueryStringConstants.SIGNED_KEY_START, user_delegation_key.signed_start)
            self._add_query(QueryStringConstants.SIGNED_KEY_EXPIRY, user_delegation_key.signed_expiry)
            self._add_query(QueryStringConstants.SIGNED_KEY_SERVICE, user_delegation_key.signed_service)
            self._add_query(QueryStringConstants.SIGNED_KEY_VERSION, user_delegation_key.signed_version)

            string_to_sign += \
                (self.get_value_to_append(QueryStringConstants.SIGNED_OID) +
                 self.get_value_to_append(QueryStringConstants.SIGNED_TID) +
                 self.get_value_to_append(QueryStringConstants.SIGNED_KEY_START) +
                 self.get_value_to_append(QueryStringConstants.SIGNED_KEY_EXPIRY) +
                 self.get_value_to_append(QueryStringConstants.SIGNED_KEY_SERVICE) +
                 self.get_value_to_append(QueryStringConstants.SIGNED_KEY_VERSION) +
                 self.get_value_to_append(QueryStringConstants.SIGNED_AUTHORIZED_OID) +
                 self.get_value_to_append(QueryStringConstants.SIGNED_UNAUTHORIZED_OID) +
                 self.get_value_to_append(QueryStringConstants.SIGNED_CORRELATION_ID))
        else:
            string_to_sign += self.get_value_to_append(QueryStringConstants.SIGNED_IDENTIFIER)

        string_to_sign += \
            (self.get_value_to_append(QueryStringConstants.SIGNED_IP) +
             self.get_value_to_append(QueryStringConstants.SIGNED_PROTOCOL) +
             self.get_value_to_append(QueryStringConstants.SIGNED_VERSION) +
             self.get_value_to_append(QueryStringConstants.SIGNED_RESOURCE) +
             self.get_value_to_append(BlobQueryStringConstants.SIGNED_TIMESTAMP) +
             self.get_value_to_append(QueryStringConstants.SIGNED_CACHE_CONTROL) +
             self.get_value_to_append(QueryStringConstants.SIGNED_CONTENT_DISPOSITION) +
             self.get_value_to_append(QueryStringConstants.SIGNED_CONTENT_ENCODING) +
             self.get_value_to_append(QueryStringConstants.SIGNED_CONTENT_LANGUAGE) +
             self.get_value_to_append(QueryStringConstants.SIGNED_CONTENT_TYPE))

        # remove the trailing newline
        if string_to_sign[-1] == '\n':
            string_to_sign = string_to_sign[:-1]

        self._add_query(QueryStringConstants.SIGNED_SIGNATURE,
                        sign_string(account_key if user_delegation_key is None else user_delegation_key.value,
                                    string_to_sign))

    def get_token(self):
        # a conscious decision was made to exclude the timestamp in the generated token
        # this is to avoid having two snapshot ids in the query parameters when the user appends the snapshot timestamp
        exclude = [BlobQueryStringConstants.SIGNED_TIMESTAMP]
        return '&'.join(['{0}={1}'.format(n, url_quote(v))
                         for n, v in self.query_dict.items() if v is not None and n not in exclude])


def generate_account_sas(
        account_name,  # type: str
        account_key,  # type: str
        resource_types,  # type: Union[ResourceTypes, str]
        permission,  # type: Union[AccountSasPermissions, str]
        expiry,  # type: Optional[Union[datetime, str]]
        start=None,  # type: Optional[Union[datetime, str]]
        ip=None,  # type: Optional[str]
        **kwargs # type: Any
    ):  # type: (...) -> str
    """Generates a shared access signature for the blob service.

    Use the returned signature with the credential parameter of any BlobServiceClient,
    ContainerClient or BlobClient.

    :param str account_name:
        The storage account name used to generate the shared access signature.
    :param str account_key:
        The account key, also called shared key or access key, to generate the shared access signature.
    :param resource_types:
        Specifies the resource types that are accessible with the account SAS.
    :type resource_types: str or ~azure.storage.blob.ResourceTypes
    :param permission:
        The permissions associated with the shared access signature. The
        user is restricted to operations allowed by the permissions.
        Required unless an id is given referencing a stored access policy
        which contains this field. This field must be omitted if it has been
        specified in an associated stored access policy.
    :type permission: str or ~azure.storage.blob.AccountSasPermissions
    :param expiry:
        The time at which the shared access signature becomes invalid.
        Required unless an id is given referencing a stored access policy
        which contains this field. This field must be omitted if it has
        been specified in an associated stored access policy. Azure will always
        convert values to UTC. If a date is passed in without timezone info, it
        is assumed to be UTC.
    :type expiry: ~datetime.datetime or str
    :param start:
        The time at which the shared access signature becomes valid. If
        omitted, start time for this call is assumed to be the time when the
        storage service receives the request. Azure will always convert values
        to UTC. If a date is passed in without timezone info, it is assumed to
        be UTC.
    :type start: ~datetime.datetime or str
    :param str ip:
        Specifies an IP address or a range of IP addresses from which to accept requests.
        If the IP address from which the request originates does not match the IP address
        or address range specified on the SAS token, the request is not authenticated.
        For example, specifying ip=168.1.5.65 or ip=168.1.5.60-168.1.5.70 on the SAS
        restricts the request to those IP addresses.
    :keyword str protocol:
        Specifies the protocol permitted for a request made. The default value is https.
    :return: A Shared Access Signature (sas) token.
    :rtype: str

    .. admonition:: Example:

        .. literalinclude:: ../samples/blob_samples_authentication.py
            :start-after: [START create_sas_token]
            :end-before: [END create_sas_token]
            :language: python
            :dedent: 8
            :caption: Generating a shared access signature.
    """
    sas = SharedAccessSignature(account_name, account_key)
    return sas.generate_account(
        services=Services(blob=True),
        resource_types=resource_types,
        permission=permission,
        expiry=expiry,
        start=start,
        ip=ip,
        **kwargs
    ) # type: ignore


def generate_container_sas(
        account_name,  # type: str
        container_name,  # type: str
        account_key=None,  # type: Optional[str]
        user_delegation_key=None,  # type: Optional[UserDelegationKey]
        permission=None,  # type: Optional[Union[ContainerSasPermissions, str]]
        expiry=None,  # type: Optional[Union[datetime, str]]
        start=None,  # type: Optional[Union[datetime, str]]
        policy_id=None,  # type: Optional[str]
        ip=None,  # type: Optional[str]
        **kwargs # type: Any
    ):
    # type: (...) -> Any
    """Generates a shared access signature for a container.

    Use the returned signature with the credential parameter of any BlobServiceClient,
    ContainerClient or BlobClient.

    :param str account_name:
        The storage account name used to generate the shared access signature.
    :param str container_name:
        The name of the container.
    :param str account_key:
        The account key, also called shared key or access key, to generate the shared access signature.
        Either `account_key` or `user_delegation_key` must be specified.
    :param ~azure.storage.blob.UserDelegationKey user_delegation_key:
        Instead of an account shared key, the user could pass in a user delegation key.
        A user delegation key can be obtained from the service by authenticating with an AAD identity;
        this can be accomplished by calling :func:`~azure.storage.blob.BlobServiceClient.get_user_delegation_key`.
        When present, the SAS is signed with the user delegation key instead.
    :param permission:
        The permissions associated with the shared access signature. The
        user is restricted to operations allowed by the permissions.
        Permissions must be ordered read, write, delete, list.
        Required unless an id is given referencing a stored access policy
        which contains this field. This field must be omitted if it has been
        specified in an associated stored access policy.
    :type permission: str or ~azure.storage.blob.ContainerSasPermissions
    :param expiry:
        The time at which the shared access signature becomes invalid.
        Required unless an id is given referencing a stored access policy
        which contains this field. This field must be omitted if it has
        been specified in an associated stored access policy. Azure will always
        convert values to UTC. If a date is passed in without timezone info, it
        is assumed to be UTC.
    :type expiry: ~datetime.datetime or str
    :param start:
        The time at which the shared access signature becomes valid. If
        omitted, start time for this call is assumed to be the time when the
        storage service receives the request. Azure will always convert values
        to UTC. If a date is passed in without timezone info, it is assumed to
        be UTC.
    :type start: ~datetime.datetime or str
    :param str policy_id:
        A unique value up to 64 characters in length that correlates to a
        stored access policy. To create a stored access policy, use
        :func:`~azure.storage.blob.ContainerClient.set_container_access_policy`.
    :param str ip:
        Specifies an IP address or a range of IP addresses from which to accept requests.
        If the IP address from which the request originates does not match the IP address
        or address range specified on the SAS token, the request is not authenticated.
        For example, specifying ip=168.1.5.65 or ip=168.1.5.60-168.1.5.70 on the SAS
        restricts the request to those IP addresses.
    :keyword str protocol:
        Specifies the protocol permitted for a request made. The default value is https.
    :keyword str cache_control:
        Response header value for Cache-Control when resource is accessed
        using this shared access signature.
    :keyword str content_disposition:
        Response header value for Content-Disposition when resource is accessed
        using this shared access signature.
    :keyword str content_encoding:
        Response header value for Content-Encoding when resource is accessed
        using this shared access signature.
    :keyword str content_language:
        Response header value for Content-Language when resource is accessed
        using this shared access signature.
    :keyword str content_type:
        Response header value for Content-Type when resource is accessed
        using this shared access signature.
    :return: A Shared Access Signature (sas) token.
    :rtype: str

    .. admonition:: Example:

        .. literalinclude:: ../samples/blob_samples_containers.py
            :start-after: [START generate_sas_token]
            :end-before: [END generate_sas_token]
            :language: python
            :dedent: 12
            :caption: Generating a sas token.
    """
    if not user_delegation_key and not account_key:
        raise ValueError("Either user_delegation_key or account_key must be provided.")

    if user_delegation_key:
        sas = BlobSharedAccessSignature(account_name, user_delegation_key=user_delegation_key)
    else:
        sas = BlobSharedAccessSignature(account_name, account_key=account_key)
    return sas.generate_container(
        container_name,
        permission=permission,
        expiry=expiry,
        start=start,
        policy_id=policy_id,
        ip=ip,
        **kwargs
    )


def generate_blob_sas(
        account_name,  # type: str
        container_name,  # type: str
        blob_name,  # type: str
        snapshot=None,  # type: Optional[str]
        account_key=None,  # type: Optional[str]
        user_delegation_key=None,  # type: Optional[UserDelegationKey]
        permission=None,  # type: Optional[Union[BlobSasPermissions, str]]
        expiry=None,  # type: Optional[Union[datetime, str]]
        start=None,  # type: Optional[Union[datetime, str]]
        policy_id=None,  # type: Optional[str]
        ip=None,  # type: Optional[str]
        **kwargs # type: Any
    ):
    # type: (...) -> Any
    """Generates a shared access signature for a blob.

    Use the returned signature with the credential parameter of any BlobServiceClient,
    ContainerClient or BlobClient.

    :param str account_name:
        The storage account name used to generate the shared access signature.
    :param str container_name:
        The name of the container.
    :param str blob_name:
        The name of the blob.
    :param str snapshot:
        An optional blob snapshot ID.
    :param str account_key:
        The account key, also called shared key or access key, to generate the shared access signature.
        Either `account_key` or `user_delegation_key` must be specified.
    :param ~azure.storage.blob.UserDelegationKey user_delegation_key:
        Instead of an account shared key, the user could pass in a user delegation key.
        A user delegation key can be obtained from the service by authenticating with an AAD identity;
        this can be accomplished by calling :func:`~azure.storage.blob.BlobServiceClient.get_user_delegation_key`.
        When present, the SAS is signed with the user delegation key instead.
    :param permission:
        The permissions associated with the shared access signature. The
        user is restricted to operations allowed by the permissions.
        Permissions must be ordered read, write, delete, list.
        Required unless an id is given referencing a stored access policy
        which contains this field. This field must be omitted if it has been
        specified in an associated stored access policy.
    :type permission: str or ~azure.storage.blob.BlobSasPermissions
    :param expiry:
        The time at which the shared access signature becomes invalid.
        Required unless an id is given referencing a stored access policy
        which contains this field. This field must be omitted if it has
        been specified in an associated stored access policy. Azure will always
        convert values to UTC. If a date is passed in without timezone info, it
        is assumed to be UTC.
    :type expiry: ~datetime.datetime or str
    :param start:
        The time at which the shared access signature becomes valid. If
        omitted, start time for this call is assumed to be the time when the
        storage service receives the request. Azure will always convert values
        to UTC. If a date is passed in without timezone info, it is assumed to
        be UTC.
    :type start: ~datetime.datetime or str
    :param str policy_id:
        A unique value up to 64 characters in length that correlates to a
        stored access policy. To create a stored access policy, use
        :func:`~azure.storage.blob.ContainerClient.set_container_access_policy()`.
    :param str ip:
        Specifies an IP address or a range of IP addresses from which to accept requests.
        If the IP address from which the request originates does not match the IP address
        or address range specified on the SAS token, the request is not authenticated.
        For example, specifying ip=168.1.5.65 or ip=168.1.5.60-168.1.5.70 on the SAS
        restricts the request to those IP addresses.
    :keyword str version_id:
        An optional blob version ID. This parameter is only for versioning enabled account

        .. versionadded:: 12.4.0
            This keyword argument was introduced in API version '2019-12-12'.
    :keyword str protocol:
        Specifies the protocol permitted for a request made. The default value is https.
    :keyword str cache_control:
        Response header value for Cache-Control when resource is accessed
        using this shared access signature.
    :keyword str content_disposition:
        Response header value for Content-Disposition when resource is accessed
        using this shared access signature.
    :keyword str content_encoding:
        Response header value for Content-Encoding when resource is accessed
        using this shared access signature.
    :keyword str content_language:
        Response header value for Content-Language when resource is accessed
        using this shared access signature.
    :keyword str content_type:
        Response header value for Content-Type when resource is accessed
        using this shared access signature.
    :return: A Shared Access Signature (sas) token.
    :rtype: str
    """
    if not user_delegation_key and not account_key:
        raise ValueError("Either user_delegation_key or account_key must be provided.")
    version_id = kwargs.pop('version_id', None)
    if version_id and snapshot:
        raise ValueError("snapshot and version_id cannot be set at the same time.")
    if user_delegation_key:
        sas = BlobSharedAccessSignature(account_name, user_delegation_key=user_delegation_key)
    else:
        sas = BlobSharedAccessSignature(account_name, account_key=account_key)
    return sas.generate_blob(
        container_name,
        blob_name,
        snapshot=snapshot,
        version_id=version_id,
        permission=permission,
        expiry=expiry,
        start=start,
        policy_id=policy_id,
        ip=ip,
        **kwargs
    )
