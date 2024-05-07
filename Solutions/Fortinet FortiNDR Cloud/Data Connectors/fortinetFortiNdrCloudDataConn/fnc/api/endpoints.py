from enum import Enum, auto

from requests import Response
from requests.exceptions import HTTPError, JSONDecodeError

from ..errors import ErrorMessages, ErrorType, FncClientError
from ..logger import FncClientLogger


class EndpointEnum(Enum):
    def _generate_next_value_(name, start, count, last_values):
        return name.title()


class EndpointKey (EndpointEnum):
    # Sensors API's Endpoints

    GET_SENSORS = auto()
    GET_DEVICES = auto()
    GET_TASK = auto()
    GET_TASKS = auto()
    CREATE_TASK = auto()
    GET_TELEMETRY_EVENTS = auto()
    GET_TELEMETRY_PACKETSTATS = auto()
    GET_TELEMETRY_NETWORK = auto()

    # Detections API's Endpoints

    GET_DETECTIONS = auto()
    RESOLVE_DETECTION = auto()
    GET_DETECTION_EVENTS = auto()
    GET_RULES = auto()
    GET_RULE = auto()
    CREATE_RULE = auto()
    GET_RULE_EVENTS = auto()

    # Entity API's Endpoints

    GET_ENTITY_SUMMARY = auto()
    GET_ENTITY_PDNS = auto()
    GET_ENTITY_DHCP = auto()
    GET_ENTITY_FILE = auto()


class Endpoint:
    _logger: FncClientLogger = None
    version: str
    endpoint: str

    default_values: dict = {}

    def set_Logger(self, logger: FncClientLogger):
        self._logger = logger

    def get_endpoint_key(self) -> EndpointKey:
        return None

    def get_url(self) -> str:
        """
        This method return the endpoint's url (excluding host)

        Raises:
            KeyError: If any required field like the api vesion is missing

        Returns:
            str: Returns the endpoint's url excluding host.
        """
        missing = []
        if not self.version:
            missing.append("endpoint's version")
        if not self.endpoint:
            missing.append("endpoint's url")

        if missing:
            if self._logger:
                self._logger.error("Api's version or the endpoint url is missing.")
                self._logger.debug("If the endpoint is not in the form '<api_version>/<endpoint>" +
                                   " ensure that the get_url method is implemented for the specific endpoint."
                                   )
            raise KeyError(missing)
        else:
            return f'{self.version}/{self.endpoint}'

    def get_query_args(self) -> dict:
        """
        This method returns the definition for any argument expected in the query string.
        Must be implemented by the endpoint if any argument is expected in the query string.
        Returns:
            dict: Dictionary containing the arguments' definition
        """
        return {}

    def get_body_args(self) -> dict:
        """
        This method returns the definition for any argument expected in the body.
        Must be implemented by the endpoint if any argument is expected in the body.
        Returns:
            dict: Dictionary containing the arguments' definition
        """
        return {}

    def get_url_args(self) -> list:
        """
        This method returns the definition for any argument expected in the url.
        Must be implemented by the endpoint if any argument is expected on the url.
        Returns:
            dict: Dictionary containing the arguments' definition
        """
        return []

    def get_control_args(self) -> dict:
        """
        This method returns the required arguments that control the request such as the method.
        Must be implemented by each endpoint since at least the method need to be provided.

        Returns:
            dict: Dictionary containing the default control arguments
        """
        return {}

    def get_response_fields(self) -> list[str]:
        """
        This method returns a list of all the expected fields in a successful response.

        Returns:
            list[str]: list of expected fields.
        """
        return []

    def evaluate(self, args: dict) -> dict:
        """
        This method receive a dictionary with all the arguments' value and, using the endpoint definition,
        it split them according to where are they required (url, body, query string or control).

        Args:
            args (dict): Dictionary with all the arguments' values

        Returns:
            dict: A dictionary with the arguments splitted as: 'url_args', 'query_args', 'body_args' and 'control_args'
        """

        final_args: dict = {
            'url_args': None,
            'query_args': None,
            'body_args': None,
            'control_args': None,
            'unexpected_args': None,
        }

        if self._logger:
            self._logger.debug(f"Evaluating endpoint {self.get_endpoint_key().name}")

        # Get the args to be added in the query string
        to_evaluate = self.get_query_args()
        final_args['query_args'] = self._evaluate_arguments(
            to_evaluate=to_evaluate, args=args)

        # Get the args to be added in the body
        final_args['body_args'] = self._evaluate_arguments(
            to_evaluate=self.get_body_args(), args=args)

        # Get the args to be added in the url
        final_args['url_args'] = self._evaluate_arguments(
            to_evaluate=self.get_url_args(), args=args)

        # Get the control arguments defined in the endpoint
        final_args['control_args'] = self.get_control_args()

        # Any remaining args is unexpected
        final_args['unexpected_args'] = args

        # Return the all the arguments separated by where are they required url, body, query string or control
        return final_args

    def _evaluate_arguments(self, to_evaluate: dict | list, args: dict) -> dict:
        """
        This method filter the arguments (args) leaving only those that are included in the arguments definition (to_evaluate).
        If the expected argument allows multiple values, its value (comma separated str) is converted to a list.
        Any returned argument is removed from the original dictionary.

        Args:
            to_evaluate (dict): dictionary with the definition for all the expected arguments
            args (dict): dictionary with all the arguments that need to be filtered

        Returns:
            dict: Returns a dictionary containing only the arguments that are expected
        """
        res = {}
        is_list = isinstance(to_evaluate, list)
        for arg in to_evaluate:
            value = args.pop(arg, None)
            if value is not None:
                if is_list:
                    res[arg] = value
                else:
                    arg_def: ArgumentDefinition = to_evaluate[arg]

                    # if argument allow multiple we need to provide a list of values instead of a comma separated str
                    if arg_def.allow_multiple() and isinstance(value, str):
                        value = value.split(',')
                        value = list(v.strip() for v in value)
                    res[arg] = value

        return res

    def validate(self, to_validate: dict):
        """
        This method receive a dictionary with the arguments and verify that any required argument is present and
        that there is no unexpected argument.

        Args:
            to_validate (dict): The dictionary containing all the arguments to be validated.

        Raises:
            FncApiClientError: Error_Type ENDPOINT_VALIDATION_ERROR if there is any missing or unexpected argument.
        """
        if self._logger:
            self._logger.debug(f"Validating endpoint {self.get_endpoint_key().name}")

        # Assert any required argument is present and
        # all the arguments are expected
        missing = []
        unexpected = []
        invalid = []

        # Validate the query string's arguments
        if 'query_args' in to_validate:
            m, i = self._validate_argument(
                to_validate=to_validate['query_args'],
                args_definition=self.get_query_args()
            )
            missing.extend(m)
            invalid.extend(i)

        # Validate the body's arguments
        if 'body_args' in to_validate:
            m, i = self._validate_argument(
                to_validate=to_validate['body_args'],
                args_definition=self.get_body_args()
            )
            missing.extend(m)
            invalid.extend(i)

        # Validate the url's arguments
        if 'url_args' in to_validate:
            m, i = self._validate_argument(
                to_validate=to_validate['url_args'],
                args_definition=self.get_url_args(),
                requires_all=True
            )
            missing.extend(m)
            invalid.extend(i)

        # Control's arguments do not need validation since they are defined internally in the endpoint

        # If there is any unexpected argument add it to the list
        if 'unexpected_args' in to_validate:
            unexpected = list(to_validate['unexpected_args'].keys())

        if missing or unexpected or invalid:
            raise FncClientError(
                error_type=ErrorType.ENDPOINT_VALIDATION_ERROR,
                error_message=ErrorMessages.ENDPOINT_ARGUMENT_VALIDATION,
                error_data={'endpoint': self.get_endpoint_key().name, 'missing': missing, 'unexpected': unexpected, 'invalid': invalid}
            )

    def _validate_argument(self, to_validate: dict, args_definition: dict | list, requires_all: bool = False) -> tuple[list, list, list]:
        """
        This method take a dictionary of arguments and the arguments definitions to validate that
        any required argument is present and any existing argument is expected.

        Args:
            to_validate (dict): Dictionary of arguments to be validated
            args_definition (dict): The arguments' definition to be used during validation

        Returns:
            tuple[list, list]: return a tuple [missing, unexpected] containing the missing required arguments and those that were not expected.
        """
        # Assert any required argument is present
        is_list = isinstance(args_definition, list)
        missing = []

        # Verify any required argument that is missing
        for arg in args_definition:
            is_required = False
            if is_list:
                is_required = requires_all
            else:
                arg_def: ArgumentDefinition = args_definition[arg]
                is_required = arg_def.is_required()

            if arg not in to_validate and is_required:
                missing.append(arg)

        # Verify that any argument present is expected
        invalid = []
        for arg in to_validate:
            if arg not in args_definition:
                # This should never happened since we only add the argument if it is in the argument's definition
                if self._logger:
                    self._logger.error("Unexpected error: We are trying to validate an argument " +
                                       "that is not in the argument's definitions dictionary"
                                       )
                continue

            if not (is_list or args_definition[arg].is_valid(values=to_validate[arg])):
                invalid.append(arg)

        return missing, invalid

    def validate_response(self, response: Response) -> dict:
        """
        This method validate the received response ensuring that the status code is successful,
        the response is a valid json and any expected field is included in the response.
        The response json is returned if response is valid.

        Args:
            response (dict): received response

        Raises:
            FncApiClientError: Error Type ENDPOINT_RESPONSE_VALIDATION_ERROR if:
                - The status code is not successful
                - It is not a valid json
                - Any required field is missing from the response.

        Returns:
            dict: Returns the response json as dictionary
        """
        if self._logger:
            self._logger.debug(f"Validating response after calling endpoint {self.get_endpoint_key().name}")

        try:
            response.raise_for_status()
        except HTTPError as e:
            try:
                error = response.json()
            except JSONDecodeError:
                error = e
            status = response.status_code

            raise FncClientError(
                error_type=ErrorType.ENDPOINT_RESPONSE_VALIDATION_ERROR,
                error_message=ErrorMessages.ENDPOINT_RESPONSE_INVALID_STATUS_CODE,
                error_data={'endpoint': self.get_endpoint_key().name, 'status': status, 'error': error},
                exception=e
            ) from e

        if self.get_response_fields() is None:
            # Validate the response is empty as it was expected
            if response.text():
                error = f"An empty response was expected but '{response.text()}' was received."
                raise FncClientError(
                    error_type=ErrorType.ENDPOINT_RESPONSE_VALIDATION_ERROR,
                    error_message=ErrorMessages.ENDPOINT_RESPONSE_INVALID,
                    error_data={'endpoint': self.get_endpoint_key().name, 'error': error}
                )
            else:
                res_json = f"{response.status_code} - Empty Response"
        else:
            # Validate if any required field in the response is present
            try:
                res_json = response.json()
            except JSONDecodeError as e:
                error = f'Response is not a valid json [{e}].'
                raise FncClientError(
                    error_type=ErrorType.ENDPOINT_RESPONSE_VALIDATION_ERROR,
                    error_message=ErrorMessages.ENDPOINT_RESPONSE_INVALID,
                    error_data={'endpoint': self.get_endpoint_key().name, 'error': error},
                    exception=e
                ) from e

            missing = []
            for field in self.get_response_fields():
                if field not in res_json:
                    missing.append(field)

            if missing:
                error = f"Fields {missing} are missing from the response."
                raise FncClientError(
                    error_type=ErrorType.ENDPOINT_RESPONSE_VALIDATION_ERROR,
                    error_message=ErrorMessages.ENDPOINT_RESPONSE_INVALID,
                    error_data={"endpoint": self.get_endpoint_key().name, "error": error}
                )

        return res_json


class ArgumentDefinition:
    _required: bool
    _multiple: bool
    _allowed: list

    def __init__(self, required: bool, multiple: bool, allowed: list = None):
        self._required = required
        self._multiple = multiple
        self._allowed = allowed

    def is_valid(self, values) -> bool:
        return self.is_allowed(values)

    def is_required(self) -> bool:
        return self._required

    def allow_multiple(self) -> bool:
        return self._multiple

    def is_allowed(self, values) -> bool:
        if not isinstance(values, list):
            values = [values]

        return not self._allowed or all(v in self._allowed for v in values)

# Sensors API's Endpoints


class GetSensors(Endpoint):
    """_summary_

    Args:
        Endpoint (_type_): _description_

    Returns:
        _type_: _description_
    """
    version: str = 'v1'
    endpoint: str = 'sensors'

    default_values: dict = {}

    def get_endpoint_key(self) -> EndpointKey:
        return EndpointKey.GET_SENSORS

    def get_control_args(self) -> dict:
        return {
            'method': 'GET'
        }

    def get_query_args(self) -> dict:
        return {
            'account_uuid':   ArgumentDefinition(required=False, multiple=False),
            'account_code': ArgumentDefinition(required=False, multiple=False),
            'sensor_id':    ArgumentDefinition(required=False, multiple=False),
            'include':      ArgumentDefinition(required=False, multiple=True),
            'enabled':      ArgumentDefinition(required=False, multiple=False),
        }

    def get_response_fields(self) -> list[str]:
        return ['sensors']


class GetDevices(Endpoint):
    """
    List of devices for a particular cidr/prefix and Sensor with NS/EW true or false (limited to 10k ES default).
    Args:
        account_uuid (str): account's id to filter results,
        start_date (str):,
        end_date (str):,
        cidr/prefix (str): CIDR or an IP prefix is optionally accepted (prefix is converted to CIDR in the backend.
            The output subnet width is the 8bit subnet directly smaller than the filter CIDR/prefix. ,
        sensor_id (str): sensor's id to filter results,
        dedup_sensor_id (str): 'YES' or 'NO' (Default: 'YES').
        traffic_direction (str): 'internal' or 'external',
        sort_by (str): 'ip_address','internal' or 'external',
        sort_direction (str): 'asc' or 'desc',

    Returns:
        dict: A dictionary containing three fields (
            'device_list': list of returned devices,
            'result_count': total count of devices and
            'return_count': Amount of returned devices
        )
    """

    version: str = 'v1'
    endpoint: str = 'devices'

    default_values: dict = {}

    def get_endpoint_key(self) -> EndpointKey:
        return EndpointKey.GET_DEVICES

    def get_control_args(self) -> dict:
        return {
            'method': 'GET'
        }

    def get_query_args(self) -> dict:
        return {
            'account_uuid':        ArgumentDefinition(required=False, multiple=False),
            'start_date':        ArgumentDefinition(required=False, multiple=False),
            'end_date':          ArgumentDefinition(required=False, multiple=False),
            'cidr':              ArgumentDefinition(required=False, multiple=False),
            'sensor_id':         ArgumentDefinition(required=False, multiple=False),
            'dedup_sensor_id':    ArgumentDefinition(required=False, multiple=False, allowed=['YES', 'NO']),
            'traffic_direction': ArgumentDefinition(required=False, multiple=False, allowed=['internal', 'external']),
            'sort_by':           ArgumentDefinition(required=False, multiple=False, allowed=['ip_address', 'internal', 'external']),
            'sort_direction':    ArgumentDefinition(required=False, multiple=False, allowed=['desc', 'asc']),
        }

    def get_response_fields(self) -> list[str]:
        return ['devices']


class GetTask(Endpoint):
    version: str = 'v1'
    endpoint: str = 'pcaptasks/{task_id}'

    default_values: dict = {}

    def get_endpoint_key(self) -> EndpointKey:
        return EndpointKey.GET_TASK

    def get_control_args(self) -> dict:
        return {
            'method': 'GET'
        }

    def get_url_args(self) -> dict:
        return ['task_id']

    def get_response_fields(self) -> list[str]:
        return ['pcap_task']


class GetTasks(Endpoint):
    version: str = 'v1'
    endpoint: str = 'pcaptasks'

    default_values: dict = {}

    def get_endpoint_key(self) -> EndpointKey:
        return EndpointKey.GET_TASKS

    def get_control_args(self) -> dict:
        return {
            'method': 'GET'
        }

    def get_query_args(self) -> dict:
        return {
            'account_uuid':   ArgumentDefinition(required=False, multiple=False),
            'account_code': ArgumentDefinition(required=False, multiple=False),
            'sensor_id':    ArgumentDefinition(required=False, multiple=False),
            'include':      ArgumentDefinition(required=False, multiple=True),
            'enabled':      ArgumentDefinition(required=False, multiple=False),
        }

    def get_response_fields(self) -> list[str]:
        return ['pcaptasks']


class CreateTask(Endpoint):
    version: str = 'v1'
    endpoint: str = 'pcaptasks'

    default_values: dict = {}

    def get_endpoint_key(self) -> EndpointKey:
        return EndpointKey.CREATE_TASK

    def get_control_args(self) -> dict:
        return {
            'method': 'POST'
        }

    def get_body_args(self) -> dict:
        return {
            'description':          ArgumentDefinition(required=True, multiple=False),
            'name':                 ArgumentDefinition(required=True, multiple=False),
            'sensor_ids':           ArgumentDefinition(required=True, multiple=False),
            'account_uuid':         ArgumentDefinition(required=True, multiple=False),
            'bpf':                  ArgumentDefinition(required=True, multiple=False),
            'requested_start_date': ArgumentDefinition(required=True, multiple=False),
            'requested_end_date':   ArgumentDefinition(required=True, multiple=False),
        }

    def get_response_fields(self) -> list[str]:
        return ['pcaptask']


class GetTelemetryEvents(Endpoint):
    version: str = 'v1'
    endpoint: str = 'telemetry/events'

    default_values: dict = {}

    def get_endpoint_key(self) -> EndpointKey:
        return EndpointKey.GET_TELEMETRY_EVENTS

    def get_control_args(self) -> dict:
        return {
            'method': 'GET'
        }

    def get_query_args(self) -> dict:
        return {
            'interval':   ArgumentDefinition(required=False, multiple=False),
            'start_date': ArgumentDefinition(required=False, multiple=False),
            'end_date':    ArgumentDefinition(required=False, multiple=False),
            'account_uuid':      ArgumentDefinition(required=False, multiple=False),
            'account_code':      ArgumentDefinition(required=False, multiple=False),
            'sensor_id':    ArgumentDefinition(required=False, multiple=False),
            'event_type':      ArgumentDefinition(required=False, multiple=False),
            'group_by':      ArgumentDefinition(required=False, multiple=False, allowed=['event_type', 'sensor_id', 'account_code']),
        }

    def get_response_fields(self) -> list[str]:
        return ['columns', 'data']


class GetTelemetryPacketstats(Endpoint):
    version: str = 'v1'
    endpoint: str = 'telemetry/packetstats'

    default_values: dict = {}

    def get_endpoint_key(self) -> EndpointKey:
        return EndpointKey.GET_TELEMETRY_PACKETSTATS

    def get_control_args(self) -> dict:
        return {
            'method': 'GET'
        }

    def get_query_args(self) -> dict:
        return {
            'sensor_id':   ArgumentDefinition(required=False, multiple=False),
            'start_date': ArgumentDefinition(required=False, multiple=False),
            'end_date':    ArgumentDefinition(required=False, multiple=False),
            'interval':      ArgumentDefinition(required=False, multiple=False),
            'group_by':      ArgumentDefinition(required=False, multiple=False, allowed=['interface_name', 'sensor_id', 'account_code']),
        }

    def get_response_fields(self) -> list[str]:
        return ['data']


class GetTelemetryNetwork(Endpoint):
    version: str = 'v1'
    endpoint: str = 'telemetry/network_usage'

    default_values: dict = {}

    def get_endpoint_key(self) -> EndpointKey:
        return EndpointKey.GET_TELEMETRY_NETWORK

    def get_control_args(self) -> dict:
        return {
            'method': 'GET'
        }

    def get_query_args(self) -> dict:
        return {
            'account_code':      ArgumentDefinition(required=False, multiple=False),
            'interval':          ArgumentDefinition(required=False, multiple=False, allowed=['day', 'month_to-day']),
            'latest_each_month': ArgumentDefinition(required=False, multiple=False),
            'sort_order':        ArgumentDefinition(required=False, multiple=False, allowed=['desc', 'asc']),
            'limit':             ArgumentDefinition(required=False, multiple=False),
            'offset':            ArgumentDefinition(required=False, multiple=False),
            'start_date':        ArgumentDefinition(required=False, multiple=False),
            'end_date':          ArgumentDefinition(required=False, multiple=False),
        }

    def get_response_fields(self) -> list[str]:
        return ['network_usage']

# Entity API's Endpoints


class GetEntitySummary(Endpoint):
    version: str = 'v1'
    endpoint: str = 'entity/{entity}/summary'

    default_values: dict = {}

    def get_endpoint_key(self) -> EndpointKey:
        return EndpointKey.GET_ENTITY_SUMMARY

    def get_control_args(self) -> dict:
        return {
            'method': 'GET'
        }

    def get_url_args(self) -> list:
        return ['entity']

    def get_query_args(self) -> dict:
        return {
            'account_uuid':       ArgumentDefinition(required=False, multiple=True),
            'entity_type':      ArgumentDefinition(required=False, multiple=False, allowed=['domain', 'ip']),
        }

    def get_response_fields(self) -> list[str]:
        return ['summary']


class GetEntityPdns(Endpoint):
    version: str = 'v1'
    endpoint: str = 'entity/{entity}/pdns'

    default_values: dict = {}

    def get_endpoint_key(self) -> EndpointKey:
        return EndpointKey.GET_ENTITY_PDNS

    def get_control_args(self) -> dict:
        return {
            'method': 'GET'
        }

    def get_url_args(self) -> list:
        return ['entity']

    def get_query_args(self) -> dict:
        return {
            'account_uuid':       ArgumentDefinition(required=False, multiple=True),
            'record_type':      ArgumentDefinition(required=False, multiple=True),
            'source':           ArgumentDefinition(required=False, multiple=True),
            'resolve_external': ArgumentDefinition(required=False, multiple=False),
            'start_date':       ArgumentDefinition(required=False, multiple=False),
            'end_date':         ArgumentDefinition(required=False, multiple=False),
            'limit':            ArgumentDefinition(required=False, multiple=False),
        }

    def get_response_fields(self) -> list[str]:
        return ['passivedns']


class GetEntityDhcp(Endpoint):
    version: str = 'v1'
    endpoint: str = 'entity/{entity}/dhcp'

    default_values: dict = {}

    def get_endpoint_key(self) -> EndpointKey:
        return EndpointKey.GET_ENTITY_DHCP

    def get_control_args(self) -> dict:
        return {
            'method': 'GET'
        }

    def get_url_args(self) -> list:
        return ['entity']

    def get_query_args(self) -> dict:
        return {
            'account_uuid':       ArgumentDefinition(required=False, multiple=True),
            'sensor_id':      ArgumentDefinition(required=False, multiple=False),
            'start_date':       ArgumentDefinition(required=False, multiple=False),
            'end_date':         ArgumentDefinition(required=False, multiple=False),
        }

    def get_response_fields(self) -> list[str]:
        return ['dhcp']


class GetEntityFile(Endpoint):
    version: str = 'v1'
    endpoint: str = 'entity/{entity}/file'

    default_values: dict = {}

    def get_endpoint_key(self) -> EndpointKey:
        return EndpointKey.GET_ENTITY_FILE

    def get_control_args(self) -> dict:
        return {
            'method': 'GET'
        }

    def get_url_args(self) -> list:
        return ['entity']

    def get_query_args(self) -> dict:
        return {
            'account_uuid':       ArgumentDefinition(required=False, multiple=True),
        }

    def get_response_fields(self) -> list[str]:
        return ['file']

# Detection API's Endpoints


class GetDetections(Endpoint):
    version: str = 'v1'
    endpoint: str = 'detections'

    default_values: dict = {}

    def get_endpoint_key(self) -> EndpointKey:
        return EndpointKey.GET_DETECTIONS

    def get_control_args(self) -> dict:
        return {
            'method': 'GET'
        }

    def get_query_args(self) -> dict:
        return {
            'account_uuid':                   ArgumentDefinition(required=False, multiple=False),
            'rule_uuid':                    ArgumentDefinition(required=False, multiple=True),
            'status':                       ArgumentDefinition(required=False, multiple=True, allowed=['active', 'resolved']),
            'device_ip':                    ArgumentDefinition(required=False, multiple=False),
            'indicator_value':              ArgumentDefinition(required=False, multiple=False),
            'sensor_id':                    ArgumentDefinition(required=False, multiple=False),
            'muted':                        ArgumentDefinition(required=False, multiple=False),
            'muted_device':                 ArgumentDefinition(required=False, multiple=False),
            'muted_rule':                   ArgumentDefinition(required=False, multiple=False),
            'include':                      ArgumentDefinition(required=False, multiple=True, allowed=['rules', 'indicators']),
            'sort_by':                      ArgumentDefinition(
                required=False, multiple=False,
                allowed=['first_seen', 'last_seen', 'status', 'device_ip', 'indicator_count']),
            'sort_order':                   ArgumentDefinition(required=False, multiple=False, allowed=['desc', 'asc']),
            'offset':                       ArgumentDefinition(required=False, multiple=False),
            'limit':                        ArgumentDefinition(required=False, multiple=False),
            'created_start_date':           ArgumentDefinition(required=False, multiple=False),
            'created_end_date':             ArgumentDefinition(required=False, multiple=False),
            'created_or_shared_start_date': ArgumentDefinition(required=False, multiple=False),
            'created_or_shared_end_date':   ArgumentDefinition(required=False, multiple=False),
            'active_start_date':            ArgumentDefinition(required=False, multiple=False),
            'active_end_date':              ArgumentDefinition(required=False, multiple=False),
            'resolved_start_date':          ArgumentDefinition(required=False, multiple=False),
            'resolved_end_date':            ArgumentDefinition(required=False, multiple=False),
            'resolution':                   ArgumentDefinition(required=False, multiple=True),
            'resolution_user_uuid':         ArgumentDefinition(required=False, multiple=True),
            'has_resolution_user_uuid':     ArgumentDefinition(required=False, multiple=False),
            'is_muted':                     ArgumentDefinition(required=False, multiple=False),
        }

    def get_response_fields(self) -> list[str]:
        return ['detections', 'rules']


class ResolveDetection(Endpoint):
    version: str = 'v1'
    endpoint: str = 'detections/{detection_id}/resolve'

    default_values: dict = {}

    def get_endpoint_key(self) -> EndpointKey:
        return EndpointKey.RESOLVE_DETECTION

    def get_control_args(self) -> dict:
        return {
            'method': 'PUT'
        }

    def get_url_args(self) -> dict:
        return ['detection_id']

    def get_body_args(self) -> dict:
        return {
            'resolution':         ArgumentDefinition(
                required=True,
                multiple=False,
                allowed=['true_positive_mitigated', 'true_positive_no_action', 'false_positive', 'unknown']
            ),
            'resolution_comment': ArgumentDefinition(required=False, multiple=False),
        }

    def get_response_fields(self) -> list[str]:
        return None


class GetDetectionEvents(Endpoint):
    version: str = 'v1'
    endpoint: str = 'events'

    default_values: dict = {}

    def get_endpoint_key(self) -> EndpointKey:
        return EndpointKey.GET_DETECTION_EVENTS

    def get_control_args(self) -> dict:
        return {
            'method': 'GET'
        }

    def get_query_args(self) -> dict:
        return {
            'detection_uuid': ArgumentDefinition(required=True, multiple=False),
            'offset':         ArgumentDefinition(required=False, multiple=False),
            'limit':          ArgumentDefinition(required=False, multiple=False),
        }

    def get_response_fields(self) -> list[str]:
        return ['events']


class GetRules(Endpoint):
    version: str = 'v1'
    endpoint: str = 'rules'

    default_values: dict = {}

    def get_endpoint_key(self) -> EndpointKey:
        return EndpointKey.GET_RULES

    def get_control_args(self) -> dict:
        return {
            'method': 'GET'
        }

    def get_query_args(self) -> dict:
        return {
            'account_uuid':          ArgumentDefinition(required=False, multiple=False),
            'rule_account_uuid':   ArgumentDefinition(required=False, multiple=False),
            'search':              ArgumentDefinition(required=False, multiple=False, allowed=['name', 'category', 'description']),
            'has_detections':      ArgumentDefinition(required=False, multiple=False),
            'detection_device_ip': ArgumentDefinition(required=False, multiple=False),
            'indicator_value':     ArgumentDefinition(required=False, multiple=False),
            'severity':            ArgumentDefinition(required=False, multiple=True, allowed=['low', 'moderate', 'high']),
            'confidence':          ArgumentDefinition(required=False, multiple=True, allowed=['low', 'moderate', 'high']),
            'category':            ArgumentDefinition(required=False, multiple=True),
            'rule_account_muted':  ArgumentDefinition(required=False, multiple=False),
            'enabled':             ArgumentDefinition(required=False, multiple=False),
            'attack_id':           ArgumentDefinition(required=False, multiple=True),
            'sort_by':             ArgumentDefinition(required=False, multiple=False,
                                                      allowed=[
                                                          'created', 'updated', 'detections',
                                                          'severity', 'confidence', 'category',
                                                          'last_seen', 'detections_muted'
                                                      ]),
            'sort_order':          ArgumentDefinition(required=False, multiple=False, allowed=['desc', 'asc']),
            'offset':              ArgumentDefinition(required=False, multiple=False),
            'limit':               ArgumentDefinition(required=False, multiple=False),
        }

    def get_response_fields(self) -> list[str]:
        return ['accounts', 'rules']


class GetRule(Endpoint):
    version: str = 'v1'
    endpoint: str = 'rules/{rule_id}'

    default_values: dict = {}

    def get_endpoint_key(self) -> EndpointKey:
        return EndpointKey.GET_RULE

    def get_control_args(self) -> dict:
        return {
            'method': 'GET'
        }

    def get_url_args(self) -> dict:
        return ['rule_id']

    def get_response_fields(self) -> list[str]:
        return ['rule']


class CreateRule(Endpoint):
    version: str = 'v1'
    endpoint: str = 'rules'

    default_values: dict = {}

    def get_endpoint_key(self) -> EndpointKey:
        return EndpointKey.CREATE_RULE

    def get_control_args(self) -> dict:
        return {
            'method': 'POST'
        }

    def get_body_args(self) -> dict:
        return {
            'account_uuid':            ArgumentDefinition(required=True, multiple=False),
            'name':                    ArgumentDefinition(required=True, multiple=False),
            'category':                ArgumentDefinition(required=True, multiple=False),
            'query_signature':         ArgumentDefinition(required=True, multiple=False),
            'description':             ArgumentDefinition(required=False, multiple=False),
            'severity':                ArgumentDefinition(required=True, multiple=False),
            'confidence':              ArgumentDefinition(required=True, multiple=False),
            'primary_attack_id':       ArgumentDefinition(required=False, multiple=False),
            'secondary_attack_id':     ArgumentDefinition(required=False, multiple=False),
            'specificity':             ArgumentDefinition(required=False, multiple=False),
            'device_ip_fields':        ArgumentDefinition(required=True, multiple=False),
            'indicator_fields':        ArgumentDefinition(required=False, multiple=False),
            'run_account_uuids':       ArgumentDefinition(required=True, multiple=False),
            'auto_resolution_minutes': ArgumentDefinition(required=False, multiple=False),
        }

    def get_response_fields(self) -> list[str]:
        return ['rule']


class GetRuleEvents(Endpoint):
    version: str = 'v1'
    endpoint: str = 'rules/{rule_id}/events'

    default_values: dict = {}

    def get_endpoint_key(self) -> EndpointKey:
        return EndpointKey.GET_RULE_EVENTS

    def get_control_args(self) -> dict:
        return {
            'method': 'GET'
        }

    def get_url_args(self) -> dict:
        return ['rule_id']

    def get_query_args(self) -> dict:
        return {
            'account_uuid': ArgumentDefinition(required=False, multiple=False),
            'offset':       ArgumentDefinition(required=False, multiple=False),
            'limit':        ArgumentDefinition(required=False, multiple=False),
        }

    def get_response_fields(self) -> list[str]:
        return ['events']


class FncApi:
    _logger: FncClientLogger = None
    _api_name: str = None

    def get_name(self) -> str:
        return self._api_name

    def get_supported_endpoints(self) -> dict:
        raise NotImplementedError()

    def get_endpoint_if_supported(self, endpoint: str | EndpointKey) -> Endpoint:
        k = None
        if isinstance(endpoint, str):
            try:
                k = EndpointKey(endpoint)
            except:
                return None
        else:
            k = endpoint
        return self.get_supported_endpoints()[k]


class SensorApi(FncApi):
    _api_name = "sensor"

    def get_supported_endpoints(self) -> dict:
        return {
            EndpointKey.GET_SENSORS: GetSensors(),
            EndpointKey.GET_DEVICES: GetDevices(),
            EndpointKey.GET_TASKS: GetTasks(),
            EndpointKey.GET_TASK: GetTask(),
            EndpointKey.CREATE_TASK: CreateTask(),
            EndpointKey.GET_TELEMETRY_EVENTS: GetTelemetryEvents(),
            EndpointKey.GET_TELEMETRY_PACKETSTATS: GetTelemetryPacketstats(),
            EndpointKey.GET_TELEMETRY_NETWORK: GetTelemetryNetwork(),
        }


class DetectionApi(FncApi):
    _api_name = "detections"

    def get_supported_endpoints(self) -> dict:
        return {
            EndpointKey.GET_DETECTIONS: GetDetections(),
            EndpointKey.GET_DETECTION_EVENTS: GetDetectionEvents(),
            EndpointKey.RESOLVE_DETECTION: ResolveDetection(),
            EndpointKey.GET_RULES: GetRules(),
            EndpointKey.GET_RULE: GetRule(),
            EndpointKey.CREATE_RULE: CreateRule(),
            EndpointKey.GET_RULE_EVENTS: GetRuleEvents(),
        }


class EntityApi(FncApi):
    _api_name = "entity"

    def get_supported_endpoints(self) -> dict:
        return {
            EndpointKey.GET_ENTITY_SUMMARY: GetEntitySummary(),
            EndpointKey.GET_ENTITY_PDNS: GetEntityPdns(),
            EndpointKey.GET_ENTITY_DHCP: GetEntityDhcp(),
            EndpointKey.GET_ENTITY_FILE: GetEntityFile(),
        }
