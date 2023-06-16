# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

from typing import (  # pylint: disable=unused-import
    Union, Optional, Any, List, TYPE_CHECKING
)

from ._shared import sign_string
from ._shared.constants import X_MS_VERSION
from ._shared.models import Services
from ._shared.shared_access_signature import SharedAccessSignature, _SharedAccessHelper, QueryStringConstants
from ._shared.parser import _str

if TYPE_CHECKING:
    from datetime import datetime
    from azure.storage.fileshare import (
        ResourceTypes,
        AccountSasPermissions,
        ShareSasPermissions,
        FileSasPermissions
    )

class FileSharedAccessSignature(SharedAccessSignature):
    '''
    Provides a factory for creating file and share access
    signature tokens with a common account name and account key.  Users can either
    use the factory or can construct the appropriate service and use the
    generate_*_shared_access_signature method directly.
    '''

    def __init__(self, account_name, account_key):
        '''
        :param str account_name:
            The storage account name used to generate the shared access signatures.
        :param str account_key:
            The access key to generate the shares access signatures.
        '''
        super(FileSharedAccessSignature, self).__init__(account_name, account_key, x_ms_version=X_MS_VERSION)

    def generate_file(self, share_name, directory_name=None, file_name=None,
                      permission=None, expiry=None, start=None, policy_id=None,
                      ip=None, protocol=None, cache_control=None,
                      content_disposition=None, content_encoding=None,
                      content_language=None, content_type=None):
        '''
        Generates a shared access signature for the file.
        Use the returned signature with the sas_token parameter of FileService.

        :param str share_name:
            Name of share.
        :param str directory_name:
            Name of directory. SAS tokens cannot be created for directories, so
            this parameter should only be present if file_name is provided.
        :param str file_name:
            Name of file.
        :param ~azure.storage.fileshare.FileSasPermissions permission:
            The permissions associated with the shared access signature. The
            user is restricted to operations allowed by the permissions.
            Permissions must be ordered read, create, write, delete, list.
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
            set_file_service_properties.
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
        resource_path = share_name
        if directory_name is not None:
            resource_path += '/' + _str(directory_name) if directory_name is not None else None
        resource_path += '/' + _str(file_name) if file_name is not None else None

        sas = _FileSharedAccessHelper()
        sas.add_base(permission, expiry, start, ip, protocol, self.x_ms_version)
        sas.add_id(policy_id)
        sas.add_resource('f')
        sas.add_override_response_headers(cache_control, content_disposition,
                                          content_encoding, content_language,
                                          content_type)
        sas.add_resource_signature(self.account_name, self.account_key, resource_path)

        return sas.get_token()

    def generate_share(self, share_name, permission=None, expiry=None,
                       start=None, policy_id=None, ip=None, protocol=None,
                       cache_control=None, content_disposition=None,
                       content_encoding=None, content_language=None,
                       content_type=None):
        '''
        Generates a shared access signature for the share.
        Use the returned signature with the sas_token parameter of FileService.

        :param str share_name:
            Name of share.
        :param ShareSasPermissions permission:
            The permissions associated with the shared access signature. The
            user is restricted to operations allowed by the permissions.
            Permissions must be ordered read, create, write, delete, list.
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
            set_file_service_properties.
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
        sas = _FileSharedAccessHelper()
        sas.add_base(permission, expiry, start, ip, protocol, self.x_ms_version)
        sas.add_id(policy_id)
        sas.add_resource('s')
        sas.add_override_response_headers(cache_control, content_disposition,
                                          content_encoding, content_language,
                                          content_type)
        sas.add_resource_signature(self.account_name, self.account_key, share_name)

        return sas.get_token()


class _FileSharedAccessHelper(_SharedAccessHelper):

    def add_resource_signature(self, account_name, account_key, path):
        def get_value_to_append(query):
            return_value = self.query_dict.get(query) or ''
            return return_value + '\n'

        if path[0] != '/':
            path = '/' + path

        canonicalized_resource = '/file/' + account_name + path + '\n'

        # Form the string to sign from shared_access_policy and canonicalized
        # resource. The order of values is important.
        string_to_sign = \
            (get_value_to_append(QueryStringConstants.SIGNED_PERMISSION) +
             get_value_to_append(QueryStringConstants.SIGNED_START) +
             get_value_to_append(QueryStringConstants.SIGNED_EXPIRY) +
             canonicalized_resource +
             get_value_to_append(QueryStringConstants.SIGNED_IDENTIFIER) +
             get_value_to_append(QueryStringConstants.SIGNED_IP) +
             get_value_to_append(QueryStringConstants.SIGNED_PROTOCOL) +
             get_value_to_append(QueryStringConstants.SIGNED_VERSION) +
             get_value_to_append(QueryStringConstants.SIGNED_CACHE_CONTROL) +
             get_value_to_append(QueryStringConstants.SIGNED_CONTENT_DISPOSITION) +
             get_value_to_append(QueryStringConstants.SIGNED_CONTENT_ENCODING) +
             get_value_to_append(QueryStringConstants.SIGNED_CONTENT_LANGUAGE) +
             get_value_to_append(QueryStringConstants.SIGNED_CONTENT_TYPE))

        # remove the trailing newline
        if string_to_sign[-1] == '\n':
            string_to_sign = string_to_sign[:-1]

        self._add_query(QueryStringConstants.SIGNED_SIGNATURE,
                        sign_string(account_key, string_to_sign))


def generate_account_sas(
        account_name,  # type: str
        account_key,  # type: str
        resource_types,  # type: Union[ResourceTypes, str]
        permission,  # type: Union[AccountSasPermissions, str]
        expiry,  # type: Optional[Union[datetime, str]]
        start=None,  # type: Optional[Union[datetime, str]]
        ip=None,  # type: Optional[str]
        **kwargs  # type: Any
    ):
    # type: (...) -> str
    """Generates a shared access signature for the file service.

    Use the returned signature with the credential parameter of any ShareServiceClient,
    ShareClient, ShareDirectoryClient, or ShareFileClient.

    :param str account_name:
        The storage account name used to generate the shared access signature.
    :param str account_key:
        The account key, also called shared key or access key, to generate the shared access signature.
    :param ~azure.storage.fileshare.ResourceTypes resource_types:
        Specifies the resource types that are accessible with the account SAS.
    :param ~azure.storage.fileshare.AccountSasPermissions permission:
        The permissions associated with the shared access signature. The
        user is restricted to operations allowed by the permissions.
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
        For example, specifying sip=168.1.5.65 or sip=168.1.5.60-168.1.5.70 on the SAS
        restricts the request to those IP addresses.
    :keyword str protocol:
        Specifies the protocol permitted for a request made. The default value is https.
    :return: A Shared Access Signature (sas) token.
    :rtype: str

    .. admonition:: Example:

        .. literalinclude:: ../samples/file_samples_authentication.py
            :start-after: [START generate_sas_token]
            :end-before: [END generate_sas_token]
            :language: python
            :dedent: 8
            :caption: Generate a sas token.
    """
    sas = SharedAccessSignature(account_name, account_key)
    return sas.generate_account(
        services=Services(fileshare=True),
        resource_types=resource_types,
        permission=permission,
        expiry=expiry,
        start=start,
        ip=ip,
        **kwargs
    ) # type: ignore


def generate_share_sas(
        account_name,  # type: str
        share_name,  # type: str
        account_key,  # type: str
        permission=None,  # type: Optional[Union[ShareSasPermissions, str]]
        expiry=None,  # type: Optional[Union[datetime, str]]
        start=None,  # type: Optional[Union[datetime, str]]
        policy_id=None,  # type: Optional[str]
        ip=None,  # type: Optional[str]
        **kwargs # type: Any
    ):  # type: (...) -> str
    """Generates a shared access signature for a share.

    Use the returned signature with the credential parameter of any ShareServiceClient,
    ShareClient, ShareDirectoryClient, or ShareFileClient.

    :param str account_name:
        The storage account name used to generate the shared access signature.
    :param str share_name:
        The name of the share.
    :param str account_key:
        The account key, also called shared key or access key, to generate the shared access signature.
    :param ~azure.storage.fileshare.ShareSasPermissions permission:
        The permissions associated with the shared access signature. The
        user is restricted to operations allowed by the permissions.
        Permissions must be ordered read, create, write, delete, list.
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
        :func:`~azure.storage.fileshare.ShareClient.set_share_access_policy`.
    :param str ip:
        Specifies an IP address or a range of IP addresses from which to accept requests.
        If the IP address from which the request originates does not match the IP address
        or address range specified on the SAS token, the request is not authenticated.
        For example, specifying sip=168.1.5.65 or sip=168.1.5.60-168.1.5.70 on the SAS
        restricts the request to those IP addresses.
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
    :keyword str protocol:
        Specifies the protocol permitted for a request made. The default value is https.
    :return: A Shared Access Signature (sas) token.
    :rtype: str
    """
    sas = FileSharedAccessSignature(account_name, account_key)
    return sas.generate_share(
        share_name=share_name,
        permission=permission,
        expiry=expiry,
        start=start,
        policy_id=policy_id,
        ip=ip,
        **kwargs
    )


def generate_file_sas(
        account_name,  # type: str
        share_name,  # type: str
        file_path,  # type: List[str]
        account_key,  # type: str
        permission=None,  # type: Optional[Union[FileSasPermissions, str]]
        expiry=None,  # type: Optional[Union[datetime, str]]
        start=None,  # type: Optional[Union[datetime, str]]
        policy_id=None,  # type: Optional[str]
        ip=None,  # type: Optional[str]
        **kwargs # type: Any
    ):
    # type: (...) -> str
    """Generates a shared access signature for a file.

    Use the returned signature with the credential parameter of any ShareServiceClient,
    ShareClient, ShareDirectoryClient, or ShareFileClient.

    :param str account_name:
        The storage account name used to generate the shared access signature.
    :param str share_name:
        The name of the share.
    :param file_path:
        The file path represented as a list of path segments, including the file name.
    :type file_path: List[str]
    :param str account_key:
        The account key, also called shared key or access key, to generate the shared access signature.
    :param ~azure.storage.fileshare.FileSasPermissions permission:
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
        stored access policy.
    :param str ip:
        Specifies an IP address or a range of IP addresses from which to accept requests.
        If the IP address from which the request originates does not match the IP address
        or address range specified on the SAS token, the request is not authenticated.
        For example, specifying sip=168.1.5.65 or sip=168.1.5.60-168.1.5.70 on the SAS
        restricts the request to those IP addresses.
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
    :keyword str protocol:
        Specifies the protocol permitted for a request made. The default value is https.
    :return: A Shared Access Signature (sas) token.
    :rtype: str
    """
    sas = FileSharedAccessSignature(account_name, account_key)
    if len(file_path) > 1:
        dir_path = '/'.join(file_path[:-1])
    else:
        dir_path = None # type: ignore
    return sas.generate_file( # type: ignore
        share_name=share_name,
        directory_name=dir_path,
        file_name=file_path[-1],
        permission=permission,
        expiry=expiry,
        start=start,
        policy_id=policy_id,
        ip=ip,
        **kwargs
    )
