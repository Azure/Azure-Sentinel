# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
import sys
from re import match
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

if sys.version_info < (3,):

    def _str(value):
        if isinstance(value, unicode):  # pylint: disable=undefined-variable
            return value.encode("utf-8")

        return str(value)
else:
    _str = str



def _to_str(value):
    return _str(value) if value is not None else None


_ERROR_TYPE_NOT_SUPPORTED = "Type not supported when sending data to the service: {0}."
_ERROR_VALUE_TOO_LARGE = "{0} is too large to be cast to type {1}."
_ERROR_UNKNOWN = "Unknown error ({0})"
_ERROR_VALUE_NONE = "{0} should not be None."
_ERROR_UNKNOWN_KEY_WRAP_ALGORITHM = "Unknown key wrap algorithm."


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


def _validate_table_name(table_name):
    if match("^[a-zA-Z]{1}[a-zA-Z0-9]{2,62}$", table_name) is None:
        raise ValueError(
            "Table names must be alphanumeric, cannot begin with a number, and must be between 3-63 characters long."
        )


def _decode_error(response, error_message=None, error_type=None, **kwargs):
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


def _process_table_error(storage_error):
    decoded_error = _decode_error(storage_error.response, storage_error.message)
    _reraise_error(decoded_error)


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


class TableErrorCode(str, Enum):
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
