from enum import Enum, auto


class ErrorMessages:

    # Client related error's messages
    GENERIC_ERROR_MESSAGE = "FNC Client API failed with error [{error}]."
    CLIENT_API_TOKEN_VALIDATION_ERROR = "The API Token validation failed due to {error}."
    CLIENT_REQUIRED_ARGUMENT_MISSING = "Arguments {arguments} are required for the {client} creation."

    # Endpoint related error's messages

    ENDPOINT_NOT_SUPPORTED = "Endpoint {endpoint} is not currently supported."
    ENDPOINT_ARGUMENT_VALIDATION = "Endpoint {endpoint} validation failed. " + \
        "Some arguments are missing, unexpected or their value is invalid (missing: {missing}, unexpected: {unexpected}, invalid: {invalid})."
    ENDPOINT_URL_CANNOT_BE_FORMED = "The url for endpoint {endpoint} cannot be formed [Some attributes are missing. {error}]."
    ENDPOINT_MULTIPLE_SUPPORTED = "Endpoint {endpoint} is supported by multiples APIs.\n" +\
        "Ensure that each endpoint is supported by at most one API."
    ENDPOINT_RESPONSE_INVALID = "Invalid response for endpoint {endpoint} due to {error}"
    ENDPOINT_RESPONSE_INVALID_STATUS_CODE = "Request to endpoint {endpoint} failed with status code {status} [{error}]."

    # Continuous Polling related errors's messages

    POLLING_VALIDATION_ERROR = "Some of the arguments provided for the continuous polling are invalid:\n [{failed}]"
    POLLING_TIME_WINDOW_ERROR = "The search time window cannot be determined due to {error_message}.\n [{error}]."
    POLLING_INVERTED_TIME_WINDOW_ERROR = "The end_date is sooner than the start_date."
    POLLING_EMPTY_TIME_WINDOW_ERROR = "The start_date and end_date are equal."
    POLLING_LIMIT_OVERPASSED = "The specified limit ({limit}) is being overpassed [total_count= {count}]."
    POLLING_MISSING_CONTEXT = "The ApiContext is Missing. Ensure that the appropriate context for history or continuous polling is passed."
    # Request related error's messages

    REQUEST_URL_NOT_PROVIDED = "The REST request cannot be performed because no url was provided."
    REQUEST_METHOD_NOT_PROVIDED = "The REST request cannot be performed because no method was provided."
    REQUEST_CONNECTION_ERROR = "The request to {url} cannot be handled due to a connection error [{error}]."
    REQUEST_TIMEOUT_ERROR = "The request to {url} cannot be handled due to a timeout error [{error}]."
    REQUEST_HTTP_ERROR = "The request to {url} cannot be handled due to a HTTP error [{error}]."
    REQUEST_CLOSING_SESSION_ERROR = "The HTTP session cannot be closed due to: [{error}]."
    REQUEST_ERROR = "The request to {url} cannot be handled due to a Request exception [{error}]."

    # Metastream related error's messages

    METASTREAM_MISSING_CONTEXT = "The Context is Missing. Ensure that the appropriate context for fetching events."
    EVENTS_FETCH_VALIDATION_ERROR = "Some of the arguments provided for fetching events from metastream are invalid:\n [{failed}]"
    EVENTS_UNKNOWN_DATE_PREFIX_FORMAT = "The date format for the date_prefix {date_prefix} is unknown [{error}]."


class ErrorType(Enum):

    # Client related errors

    GENERIC_ERROR = auto()
    CLIENT_VALIDATION_ERROR = auto()
    CLIENT_API_TOKEN_VALIDATION_ERROR = auto()

    # Continuous Polling related errors

    POLLING_VALIDATION_ERROR = auto()
    POLLING_TIME_WINDOW_ERROR = auto()
    POLLING_INVERTED_TIME_WINDOW_ERROR = auto()
    POLLING_EMPTY_TIME_WINDOW_ERROR = auto()
    POLLING_LIMIT_OVERPASSED = auto()
    MISSING_CONTEXT = auto()
    # Endpoint related errors

    ENDPOINT_ERROR = auto()
    ENDPOINT_VALIDATION_ERROR = auto()
    ENDPOINT_RESPONSE_VALIDATION_ERROR = auto()

    # Request related errors

    REQUEST_VALIDATION_ERROR = auto()
    REQUEST_CONNECTION_ERROR = auto()
    REQUEST_TIMEOUT_ERROR = auto()
    REQUEST_HTTP_ERROR = auto()
    REQUEST_CLOSING_SESSION_ERROR = auto()
    REQUEST_ERROR = auto()

    # Metastream related errors

    EVENTS_FETCH_VALIDATION_ERROR = auto()
    EVENTS_UNKNOWN_DATE_PREFIX_FORMAT = auto()


class FncClientError(Exception):
    error_type: ErrorType
    error_message: str
    error_data: dict
    exception: Exception

    def __init__(self, error_type: ErrorType, error_message: str, error_data: dict = None, exception: Exception = None):
        self.error_data = error_data or {}
        self.error_message = error_message
        self.error_type = error_type
        self.exception = exception

    def __str__(self) -> str:
        str_object = f"{self.error_type.name} - {self.error_message}"
        try:
            str_object = str_object.format(**self.error_data)
        except Exception:
            pass

        return str_object

    def get_original_exception(self):
        return self.exception
