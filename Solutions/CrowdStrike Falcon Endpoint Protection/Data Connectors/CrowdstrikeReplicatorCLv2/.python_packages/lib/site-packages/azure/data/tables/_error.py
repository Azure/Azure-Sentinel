# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
import sys
import re
from enum import Enum

from azure.core.exceptions import (
    HttpResponseError,
    ResourceNotFoundError,
    ResourceModifiedError,
    ResourceExistsError,
    ClientAuthenticationError,
    DecodeError,
)
from azure.core.pipeline.policies import ContentDecodePolicy


def _to_str(value):
    return str(value) if value is not None else None


_ERROR_TYPE_NOT_SUPPORTED = "Type not supported when sending data to the service: {0}."
_ERROR_VALUE_TOO_LARGE = "{0} is too large to be cast to type {1}."
_ERROR_UNKNOWN = "Unknown error ({0})"
_ERROR_VALUE_NONE = "{0} should not be None."
_ERROR_UNKNOWN_KEY_WRAP_ALGORITHM = "Unknown key wrap algorithm."

# Storage table validation regex breakdown:
# ^ Match start of string.
# [a-zA-Z]{1} Match any letter for exactly 1 character.
# [a-zA-Z0-9]{2,62} Match any alphanumeric character for between 2 and 62 characters.
# $ End of string
_STORAGE_VALID_TABLE = re.compile(r"^[a-zA-Z]{1}[a-zA-Z0-9]{2,62}$")

# Cosmos table validation regex breakdown:
# ^ Match start of string.
# [^/\#?]{0,254} Match any character that is not /\#? for between 0-253 characters.
# [^ /\#?]{1} Match any character that is not /\#? or a space for exactly 1 character.
# $ End of string
_COSMOS_VALID_TABLE = re.compile(r"^[^/\\#?]{0,253}[^ /\\#?]{1}$")

def _validate_not_none(param_name, param):
    if param is None:
        raise ValueError(_ERROR_VALUE_NONE.format(param_name))


def _wrap_exception(ex, desired_type):
    msg = ""
    if len(ex.args) > 0:
        msg = ex.args[0]
    if sys.version_info >= (3,):
        # Automatic chaining in Python 3 means we keep the trace
        return desired_type(msg)

    # There isn't a good solution in 2 for keeping the stack trace
    # in general, or that will not result in an error in 3
    # However, we can keep the previous error type and message
    # TODO: In the future we will log the trace
    return desired_type("{}: {}".format(ex.__class__.__name__, msg))


def _validate_storage_tablename(table_name):
    if _STORAGE_VALID_TABLE.match(table_name) is None:
        raise ValueError(
            "Storage table names must be alphanumeric, cannot begin with a number, and must be between 3-63 characters long."  # pylint: disable=line-too-long
        )


def _validate_cosmos_tablename(table_name):
    if _COSMOS_VALID_TABLE.match(table_name) is None:
        raise ValueError(
            "Cosmos table names must contain from 1-255 characters, and they cannot contain /, \\, #, ?, or a trailing space."  # pylint: disable=line-too-long
        )


def _validate_tablename_error(decoded_error, table_name):
    if (decoded_error.error_code == 'InvalidResourceName' and
        'The specified resource name contains invalid characters' in decoded_error.message):
        # This error is raised by Storage for any table/entity operations where the table name contains
        # forbidden characters.
        _validate_storage_tablename(table_name)
    elif (decoded_error.error_code == 'InvalidResourceName' and
        'The specifed resource name contains invalid characters' in decoded_error.message):
        # This error is raised by Storage for any table/entity operations where the table name contains
        # forbidden characters.
        _validate_storage_tablename(table_name)
    elif (decoded_error.error_code == 'OutOfRangeInput' and
          'The specified resource name length is not within the permissible limits' in decoded_error.message):
        # This error is raised by Storage for any table/entity operations where the table name is < 3 or > 63
        # characters long
        _validate_storage_tablename(table_name)
    elif (decoded_error.error_code == 'InternalServerError' and
          ('The resource name presented contains invalid character' in decoded_error.message or
           'The resource name can\'t end with space'in decoded_error.message)):
        # This error is raised by Cosmos during create_table if the table name contains forbidden
        # characters or ends in a space.
        _validate_cosmos_tablename(table_name)
    elif (decoded_error.error_code == 'BadRequest' and
          'The input name is invalid.' in decoded_error.message):
        # This error is raised by Cosmos specifically during create_table if the table name is 255 or more
        # characters. Entity operations on a too-long-table name simply result in a ResourceNotFoundError.
        _validate_cosmos_tablename(table_name)
    elif (decoded_error.error_code == 'InvalidInput' and
          ('Request url is invalid.' in decoded_error.message or
           'One of the input values is invalid.' in decoded_error.message or
           'The table name contains an invalid character' in decoded_error.message or
           'Table name cannot end with a space.' in decoded_error.message)):
        # This error is raised by Cosmos for any entity operations or delete_table if the table name contains
        # forbidden characters (except in the case of trailing space and backslash).
        _validate_cosmos_tablename(table_name)
    elif (decoded_error.error_code == 'Unauthorized' and
          ('The input authorization token can\'t serve the request.' in decoded_error.message or
           'The MAC signature found in the HTTP request' in decoded_error.message)):
        # This error is raised by Cosmos specifically on entity operations where the table name contains
        # some forbidden characters, and seems to be a bug in the service authentication.
        _validate_cosmos_tablename(table_name)


def _decode_error(response, error_message=None, error_type=None, **kwargs):  # pylint: disable=too-many-branches
    error_code = response.headers.get("x-ms-error-code")
    additional_data = {}
    try:
        error_body = ContentDecodePolicy.deserialize_from_http_generics(response)
        if isinstance(error_body, dict):
            for info in error_body.get("odata.error", {}):
                if info == "code":
                    error_code = error_body["odata.error"][info]
                elif info == "message":
                    error_message = error_body["odata.error"][info]["value"]
                else:
                    additional_data[info.tag] = info.text
        else:
            if error_body:
                for info in error_body.iter():
                    if info.tag.lower().find("code") != -1:
                        error_code = info.text
                    elif info.tag.lower().find("message") != -1:
                        error_message = info.text
                    else:
                        additional_data[info.tag] = info.text
    except DecodeError:
        pass

    try:
        if not error_type:
            error_code = TableErrorCode(error_code)
            if error_code in [
                TableErrorCode.condition_not_met,
                TableErrorCode.update_condition_not_satisfied
            ]:
                error_type = ResourceModifiedError
            elif error_code in [
                TableErrorCode.invalid_authentication_info,
                TableErrorCode.authentication_failed,
            ]:
                error_type = ClientAuthenticationError
            elif error_code in [
                TableErrorCode.resource_not_found,
                TableErrorCode.table_not_found,
                TableErrorCode.entity_not_found,
                ResourceNotFoundError,
            ]:
                error_type = ResourceNotFoundError
            elif error_code in [
                TableErrorCode.resource_already_exists,
                TableErrorCode.table_already_exists,
                TableErrorCode.account_already_exists,
                TableErrorCode.entity_already_exists,
                ResourceExistsError,
            ]:
                error_type = ResourceExistsError
            else:
                error_type = HttpResponseError
    except ValueError:
        # Got an unknown error code
        error_type = HttpResponseError

    try:
        error_message += "\nErrorCode:{}".format(error_code.value)
    except AttributeError:
        error_message += "\nErrorCode:{}".format(error_code)
    for name, info in additional_data.items():
        error_message += "\n{}:{}".format(name, info)

    error = error_type(message=error_message, response=response, **kwargs)
    error.error_code = error_code
    error.additional_info = additional_data
    return error


def _reraise_error(decoded_error):
    _, _, exc_traceback = sys.exc_info()
    try:
        raise decoded_error.with_traceback(exc_traceback)
    except AttributeError:
        decoded_error.__traceback__ = exc_traceback
        raise decoded_error


def _process_table_error(storage_error, table_name=None):
    try:
        decoded_error = _decode_error(storage_error.response, storage_error.message)
    except AttributeError:
        raise storage_error
    if table_name:
        _validate_tablename_error(decoded_error, table_name)
    _reraise_error(decoded_error)


def _reprocess_error(decoded_error, identifiers=None):
    error_code = decoded_error.error_code
    message = decoded_error.message
    authentication_failed = "Server failed to authenticate the request"
    invalid_input = "The number of keys specified in the URI does not match number of key properties for the resource"
    invalid_query_parameter_value = "Value for one of the query parameters specified in the request URI is invalid"
    invalid_url = "Request url is invalid"
    properties_need_value = "The values are not specified for all properties in the entity"
    table_does_not_exist = "The table specified does not exist"
    if (error_code == "AuthenticationFailed" and authentication_failed in message or # pylint: disable=too-many-boolean-expressions
        error_code == "InvalidInput" and invalid_input in message or
        error_code == "InvalidInput" and invalid_url in message or
        error_code == "InvalidQueryParameterValue" and invalid_query_parameter_value in message or
        error_code == "PropertiesNeedValue" and properties_need_value in message or
        error_code =="TableNotFound" and table_does_not_exist in message
        ):
        args_list = list(decoded_error.args)
        args_list[0] += "\nA possible cause of this error could be that the account URL used to"\
            "create the Client includes an invalid path, for example the table name. Please check your account URL."
        decoded_error.args = tuple(args_list)

    if (identifiers is not None and error_code == "InvalidXmlDocument" and len(identifiers) > 5):
        raise ValueError(
            "Too many access policies provided. The server does not support setting more than 5 access policies"\
                "on a single resource."
            )


class TableTransactionError(HttpResponseError):
    """There is a failure in the transaction operations.

    :ivar int index: If available, the index of the operation in the transaction that caused the error.
     Defaults to 0 in the case where an index was not provided, or the error applies across operations.
    :ivar ~azure.data.tables.TableErrorCode error_code: The error code.
    :ivar str message: The error message.
    :ivar additional_info: Any additional data for the error.
    :vartype additional_info: Mapping[str, Any]
    """

    def __init__(self, **kwargs):
        super(TableTransactionError, self).__init__(**kwargs)
        self.index = kwargs.get('index', self._extract_index())

    def _extract_index(self):
        try:
            message_sections = self.message.split(':', 1)
            return int(message_sections[0])
        except:  # pylint: disable=bare-except
            return 0


class RequestTooLargeError(TableTransactionError):
    """An error response with status code 413 - Request Entity Too Large"""

# pylint: disable=enum-must-be-uppercase
class TableErrorCode(str, Enum): # pylint: disable=enum-must-inherit-case-insensitive-enum-meta
    # Generic storage values
    account_already_exists = "AccountAlreadyExists"
    account_being_created = "AccountBeingCreated"
    account_is_disabled = "AccountIsDisabled"
    authentication_failed = "AuthenticationFailed"
    authorization_failure = "AuthorizationFailure"
    no_authentication_information = "NoAuthenticationInformation"
    condition_headers_not_supported = "ConditionHeadersNotSupported"
    condition_not_met = "ConditionNotMet"
    empty_metadata_key = "EmptyMetadataKey"
    insufficient_account_permissions = "InsufficientAccountPermissions"
    internal_error = "InternalError"
    invalid_authentication_info = "InvalidAuthenticationInfo"
    invalid_header_value = "InvalidHeaderValue"
    invalid_http_verb = "InvalidHttpVerb"
    invalid_input = "InvalidInput"
    invalid_md5 = "InvalidMd5"
    invalid_metadata = "InvalidMetadata"
    invalid_query_parameter_value = "InvalidQueryParameterValue"
    invalid_range = "InvalidRange"
    invalid_resource_name = "InvalidResourceName"
    invalid_uri = "InvalidUri"
    invalid_xml_document = "InvalidXmlDocument"
    invalid_xml_node_value = "InvalidXmlNodeValue"
    md5_mismatch = "Md5Mismatch"
    metadata_too_large = "MetadataTooLarge"
    missing_content_length_header = "MissingContentLengthHeader"
    missing_required_query_parameter = "MissingRequiredQueryParameter"
    missing_required_header = "MissingRequiredHeader"
    missing_required_xml_node = "MissingRequiredXmlNode"
    multiple_condition_headers_not_supported = "MultipleConditionHeadersNotSupported"
    operation_timed_out = "OperationTimedOut"
    out_of_range_input = "OutOfRangeInput"
    out_of_range_query_parameter_value = "OutOfRangeQueryParameterValue"
    request_body_too_large = "RequestBodyTooLarge"
    resource_type_mismatch = "ResourceTypeMismatch"
    request_url_failed_to_parse = "RequestUrlFailedToParse"
    resource_already_exists = "ResourceAlreadyExists"
    resource_not_found = "ResourceNotFound"
    server_busy = "ServerBusy"
    unsupported_header = "UnsupportedHeader"
    unsupported_xml_node = "UnsupportedXmlNode"
    unsupported_query_parameter = "UnsupportedQueryParameter"
    unsupported_http_verb = "UnsupportedHttpVerb"

    # table error codes
    duplicate_properties_specified = "DuplicatePropertiesSpecified"
    entity_not_found = "EntityNotFound"
    entity_already_exists = "EntityAlreadyExists"
    entity_too_large = "EntityTooLarge"
    host_information_not_present = "HostInformationNotPresent"
    invalid_duplicate_row = "InvalidDuplicateRow"
    invalid_value_type = "InvalidValueType"
    json_format_not_supported = "JsonFormatNotSupported"
    method_not_allowed = "MethodNotAllowed"
    not_implemented = "NotImplemented"
    properties_need_value = "PropertiesNeedValue"
    property_name_invalid = "PropertyNameInvalid"
    property_name_too_long = "PropertyNameTooLong"
    property_value_too_large = "PropertyValueTooLarge"
    table_already_exists = "TableAlreadyExists"
    table_being_deleted = "TableBeingDeleted"
    table_not_found = "TableNotFound"
    too_many_properties = "TooManyProperties"
    update_condition_not_satisfied = "UpdateConditionNotSatisfied"
    x_method_incorrect_count = "XMethodIncorrectCount"
    x_method_incorrect_value = "XMethodIncorrectValue"
    x_method_not_using_post = "XMethodNotUsingPost"
