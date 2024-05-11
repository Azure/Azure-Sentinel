
import traceback
from datetime import datetime, timedelta
from typing import Any, Iterator, List

from requests.exceptions import *

from ..errors import ErrorMessages, ErrorType, FncClientError
from ..global_variables import *
from ..logger import BasicLogger, FncClientLogger
from ..utils import *
from .endpoints import *
from .rest_clients import BasicRestClient, FncRestClient


class ApiContext:
    _polling_args: dict

    def __init__(self):
        self._checkpoint = ''
        self._history = {}
        self._polling_args = {}
        self._checkpoint = ''
        self._history = {}

    def update_history(self, history: dict):
        self._history = history or None

    def get_history(self):
        return self._history

    def update_checkpoint(self, checkpoint: str):
        self._checkpoint = checkpoint

    def get_checkpoint(self):
        return self._checkpoint

    def update_polling_args(self, args: dict):
        self._polling_args = args or None

    def get_polling_args(self):
        return self._polling_args

    def clear_args(self):
        self._polling_args = {}


class FncApiClient:

    supported_api: list[FncApi] = [SensorApi(), DetectionApi(), EntityApi()]

    domain: str
    protocol: str = CLIENT_PROTOCOL
    api_token: str
    user_agent: str
    rest_client: FncRestClient
    logger: FncClientLogger
    default_control_args: dict

    def __init__(
        self,
        name: str = None,
        api_token: str = None,
        domain: str = None,
        rest_client: FncRestClient = None,
        logger: FncClientLogger = None
    ):
        name = f'{name}-api'
        self.user_agent = f"{CLIENT_DEFAULT_USER_AGENT}-{name}"
        self.logger = logger or BasicLogger(name=self.user_agent)

        self.rest_client = rest_client or BasicRestClient()
        self.rest_client.set_logger(self.logger)

        self.logger.info(f"Initializing {CLIENT_NAME} version {CLIENT_VERSION}.")

        self.api_token = api_token
        self.domain = domain or CLIENT_DEFAULT_DOMAIN

        self.set_default_control_args()

        self.logger.info(f"User_Agent was set to: {self.user_agent}")
        self._validate_api_token()

    def _validate_api_token(self):
        """
        This method perform a call to the Get_Detections endpoint with limit =1 to validate
        the provided API Token
        """
        self.logger.info("Verifying API Token.")

        # Call Get_Detections endpoint with limit = 1
        try:
            _ = self.call_endpoint(EndpointKey.GET_DETECTIONS, {'limit': 1})
            self.logger.info("The API Token has been successfully validated.")
        except FncClientError as e:
            self.logger.error(f"API Token validation failed due to {e}.")
            raise FncClientError(
                error_type=ErrorType.CLIENT_API_TOKEN_VALIDATION_ERROR,
                error_message=ErrorMessages.CLIENT_API_TOKEN_VALIDATION_ERROR,
                error_data={'error': e},
                exception=e
            )

    def get_logger(self):
        return self.logger

    def get_url(self, e: Endpoint, api: FncApi, url_args: dict = {}) -> str:
        """
        This method construct the full url by gathering all the required information from the API and the endpoint
        and evaluating any existing argument in the url.

        Args:
            e (Endpoint): The definition of the endpoint that want to be reached with this url.
            api (FncApi): The definition of the API supporting the provided endpoint
            url_args (dict, optional): the values for any existing argument in the url. Defaults to {}.

        Raises:
            FncApiClientError: Error_Type.API_VALIDATION_ERROR is raised if the provided API does not have the attribute name defined.
            FncApiClientError: Error_Type.ENDPOINT_VALIDATION_ERROR is raised if the url part of the endpoint cannot be retrieved.

        Returns:
            str: Returns the full url to reach the provided endpoint after evaluate any existing argument.
        """
        try:
            api_name = api.get_name()

            # Verify that the API's name was defined
            if not api_name:
                self.logger.error(
                    f"The API supporting endpoint {e.get_endpoint_key().name} is missing its name. \n" +
                    "The API's name is required to form the endpoint url."
                )

                raise KeyError(["API's name"])

            # Verify that the endpoint's url was defined
            endpoint = e.get_url()

            # Prepare the url
            if self.domain.startswith('-uat'):
                # To allow use of uat environment
                url = f"{self.protocol}://{api_name}{self.domain}/{endpoint}"
            elif self.domain == CLIENT_DEFAULT_DOMAIN:
                url = f"{self.protocol}://{api_name}.{self.domain}/{endpoint}"
            else:
                url = f"{self.protocol}://{api_name}-api.{self.domain}/{endpoint}"

            full_url = ""

            # Evaluate any argument present in the url and return the resulted full url
            full_url = url.format(**url_args)
            self.logger.debug(f"URL successfully created: [{url}]")
        except KeyError as ex:
            # Some of the required arguments to format the url were not provided
            raise FncClientError(
                error_type=ErrorType.ENDPOINT_VALIDATION_ERROR,
                error_message=ErrorMessages.ENDPOINT_URL_CANNOT_BE_FORMED,
                error_data={'endpoint': e.get_endpoint_key().name,
                            'error': ex},
                exception=ex
            )
        return full_url

    def get_endpoint_if_supported(self, endpoint: str | EndpointKey) -> tuple[Endpoint, FncApi]:
        """
        This method verify if the endpoint is supported by any of the defined APIs.
        If the endpoint is supported the endpoint's definition and the API are returned.

        Args:
            endpoint (str | EndpointKey): The endpoint to be retrieved. It can be passed as the EndpointKey or just the name.

        Raises:
            FncApiClientError: Error_Type ENDPOINT_ERROR if the Endpoint was not provided, defined or it is not supported.
            FncApiClientError: Error_Type ENDPOINT_VALIDATION_ERROR if the provided endpoint is supported by most than one API.

        Returns:
            tuple[Endpoint, FncApi]: Returns the Endpoint's definition and the API that supports it
        """

        k = None
        api: FncApi = None

        # Raise unsupported Error if no endpoint was provided
        if not endpoint:
            self.logger.error("The endpoint was not provided")
            raise FncClientError(
                error_type=ErrorType.ENDPOINT_ERROR,
                error_message=ErrorMessages.ENDPOINT_NOT_SUPPORTED,
                error_data={'endpoint': ''}
            )

        # Get the EndpointKey if it was provided as str
        if isinstance(endpoint, str):
            endpoint = endpoint.title()
            self.logger.debug(f"Retrieving endpoint {endpoint}")

            try:
                # Verify the EndpointKey was defined for the received endpoint
                k = EndpointKey(endpoint)
            except:
                # Raise unsupported Error if the endpoint has not been defined
                self.logger.error(f"The endpoint ({endpoint}) is not defined. Verify that the spelling correspond with the EndpointKey.")
                raise FncClientError(
                    error_type=ErrorType.ENDPOINT_ERROR,
                    error_message=ErrorMessages.ENDPOINT_NOT_SUPPORTED,
                    error_data={'endpoint': endpoint}
                )
        else:
            self.logger.debug(f"Retrieving endpoint {endpoint.name}")
            k = endpoint

        # Get any API supporting the provided endpoint
        filtered: list = list(
            filter(lambda a: k in a.get_supported_endpoints(), self.supported_api))
        # filtered: list = [
        #     supported_endpoint for supported_api in self.supported_api
        #     for supported_endpoint in supported_api.get_supported_endpoints()
        # ]

        for a in filtered:
            if api:
                # Raise a Validation Error if the endpoint is supported by most than one API.
                raise FncClientError(
                    error_type=ErrorType.ENDPOINT_VALIDATION_ERROR,
                    error_message=ErrorMessages.ENDPOINT_MULTIPLE_SUPPORTED,
                    error_data={'endpoint': k}
                )
            api = a

        if api:
            e: Endpoint = api.get_supported_endpoints()[k]
            e.set_Logger(self.logger)
            return e, api
        else:
            # Raise Unsupported Error since the endpoint is not supported.
            raise FncClientError(
                error_type=ErrorType.ENDPOINT_ERROR,
                error_message=ErrorMessages.ENDPOINT_NOT_SUPPORTED,
                error_data={'endpoint': endpoint}
            )

    def _get_headers(self) -> dict:
        """
        This method returns the dictionary containing all the required headers.

        Returns:
            dict: Dictionary containing the headers
        """
        return {
            'Authorization': f'IBToken {self.api_token}',
            'User-Agent': self.user_agent,
            'Content-Type': 'application/json',
        }

    def set_default_control_args(self, args: dict = None):
        self.default_control_args: dict = {
            'method': 'GET',
            'verify': REQUEST_DEFAULT_VERIFY,
            'timeout': REQUEST_DEFAULT_TIMEOUT,
        }
        if args:
            self.default_control_args = {**self.default_control_args, **args}

    def get_default_control_args(self) -> dict:
        """
        This method returns a dictionary containing all the default control arguments used by the client.

        Returns:
            dict: Dictionary containing the default control arguments
        """
        args = self.default_control_args.copy()
        args.update({'headers': self._get_headers()})
        return args

    def _prepare_request(self, endpoint: str | EndpointKey, args: dict) -> tuple[Endpoint, dict]:
        """
        This method receive an endpoint and a dictionary of arguments it then verify that the endpoint is supported,
        that any required argument is present and that there is no unexpected argument. If the validation is passed,
        the arguments are separated as per where are they expected and the full url is computed replacing any argument
        with its value.

        Args:
            endpoint (str | EndpointKey): endpoint to be called
            args (dict): arguments to be passed with the request

        Raises:
            FncApiClientError: Reraise any exception raised during the endpoint validation or the calculation of the full url.

        Returns:
            tuple[Endpoint, dict]: Returns the definition of the endpoint to be called and a dictionary with the arguments splitted as:
            'url_args', 'query_args', 'body_args' and 'control_args'
        """
        e: Endpoint = None
        api: FncApi = None

        self.logger.debug(f'Preparing request to endpoint {endpoint}')
        # Verify the endpoint is supported
        try:
            e, api = self.get_endpoint_if_supported(endpoint)

            #  Evaluate and Validate the Endpoint
            e_args = e.evaluate(args=args.copy())

            e.validate(to_validate=e_args)

            # Gather all the request's control arguments
            control_args = self.get_default_control_args()
            if 'control_args' in e_args:
                # Adding the control's arguments received from the endpoint since they take precedence
                control_args.update(e_args['control_args'])
                e_args['control_args'] = control_args

            # Compute and update the url with api and endpoint information
            url_args = e_args.get('url_args', {})
            full_url = self.get_url(e=e, api=api, url_args=url_args)
            e_args['control_args']['url'] = full_url
        except FncClientError as ex:
            self.logger.error(f"Request preparation failed for endpoint {e.get_endpoint_key().name} due to {ex}")
            raise ex
        except Exception as ex:
            self.logger.error(
                f"Request preparation failed unexpectedly.\n [{str(ex)}]")
            raise FncClientError(
                error_type=ErrorType.GENERIC_ERROR,
                error_message=ErrorMessages.GENERIC_ERROR_MESSAGE,
                error_data={'error': ex},
                exception=ex
            )

        return (e, e_args)

    def _get_rest_client_arguments(self, req_args: dict = None, query_args: dict = None, body_args: Any = None) -> dict:
        """
        This method get the request arguments and create a new dictionary with the arguments as they are expected by the Rest Client.

        Args:
            req_args (dict, optional): Arguments that control the request. Defaults to None.
            query_args (dict, optional): Arguments to be passed in the query string. Defaults to None.
            body_args (Any, optional): Arguments to be passed in the body. Defaults to None.

        Returns:
            dict: New dictionary with the arguments as they are expected by the Rest Client
        """
        requests_args = {}
        requests_args.update(req_args)
        if query_args:
            requests_args['params'] = query_args
        if body_args:
            if isinstance(body_args, (dict, list)):
                requests_args['json'] = body_args
            else:
                requests_args['data'] = str(body_args)
        return requests_args

    def _map_error(self, error: Exception) -> FncClientError:
        masked_url = '???'

        if isinstance(error, FncClientError):
            return error
        elif isinstance(error, ConnectionError):
            return FncClientError(
                ErrorType.REQUEST_CONNECTION_ERROR,
                ErrorMessages.REQUEST_CONNECTION_ERROR,
                {'url': masked_url, 'error': error}
            )
        elif isinstance(error, Timeout):
            return FncClientError(
                ErrorType.REQUEST_TIMEOUT_ERROR,
                ErrorMessages.REQUEST_TIMEOUT_ERROR,
                {'url': masked_url, 'error': error}
            )
        elif isinstance(error, HTTPError):
            return FncClientError(
                ErrorType.REQUEST_HTTP_ERROR,
                ErrorMessages.REQUEST_HTTP_ERROR,
                {'url': masked_url, 'error': error}
            )
        elif isinstance(error, RequestException):
            return FncClientError(
                ErrorType.REQUEST_ERROR,
                ErrorMessages.REQUEST_ERROR,
                {'url': masked_url, 'error': error}
            )
        else:
            return FncClientError(
                ErrorType.GENERIC_ERROR,
                ErrorMessages.GENERIC_ERROR_MESSAGE,
                {'error': error}
            )

    def _is_retry_needed(self, error: Exception, attempt: int) -> bool:
        need_retry = False

        if error:
            if not isinstance(error, FncClientError):
                error = self._map_error(error)

            if error.error_type == ErrorType.ENDPOINT_RESPONSE_VALIDATION_ERROR:
                status = error.error_data.get('status', None)
                need_retry = not status or status >= 500
            else:
                need_retry: bool = error.error_type in [
                    ErrorType.REQUEST_CONNECTION_ERROR,
                    ErrorType.REQUEST_TIMEOUT_ERROR,
                    ErrorType.GENERIC_ERROR
                ]

        return need_retry and attempt <= REQUEST_MAXIMUM_RETRY_ATTEMPT

    def call_endpoint(self, endpoint: str | EndpointKey, args: dict) -> dict:
        """
        This method receives an endpoint and a dictionary of arguments. It will prepare
        and send the request to the received endpoint as well as validate the returned
        response returning the json response if it is valid

        Args:
            endpoint (str | EndpointKey): Endpoint to where to send the request
            args (dict): dictionary with all the argument's values that need to passed with the request

        Raises:
            FncApiClientError: If anything fails during the request

        Returns:
            dict:  Response's json
        """
        endpoint_key_name = endpoint if isinstance(endpoint, str) else endpoint.name
        need_retry = False
        attempt = 0

        args = args or {}
        args = args.copy()

        while attempt == 0 or need_retry:
            if need_retry:
                self.logger.info(f"Retrying...... [attempt #{attempt}]")

            response = None
            error = None

            e: Endpoint = None
            try:
                e, e_args = self._prepare_request(endpoint=endpoint, args=args)
                req_args = self._get_rest_client_arguments(
                    req_args=e_args['control_args'], body_args=e_args['body_args'], query_args=e_args['query_args']
                )

                self.logger.info(f"Sending request to {e.get_endpoint_key().name} endpoint.")

                self.rest_client.validate_request(req_args)
                response = self.rest_client.send_request(req_args=req_args)

                res_json = e.validate_response(response)
                self.logger.info("Response successfully validated.")

            except Exception as ex:
                self.logger.error(f"The request to {endpoint_key_name} endpoint failed due to:")
                self.logger.error("\n".join(traceback.format_exception(ex)))
                error = ex

            attempt += 1
            need_retry = self._is_retry_needed(error, attempt)

        if error:
            if attempt > REQUEST_MAXIMUM_RETRY_ATTEMPT:
                self.logger.error(
                    "Maximum number of retry attempts has been reached.")
            raise self._map_error(error)

        return res_json

#######################################
#
#
#   Continuous Polling Methods
#
#
########################################

    def _get_and_validate_search_window(
        self, start_date_str: str = None,
        end_date_str: str = None,
        polling_delay: int = None,
        checkpoint: str = None
    ) -> tuple[datetime, datetime]:

        # We try to get the start_date from the arguments or the checkpoint.
        # If none of them is provided we use the utc now - delay
        start_date_str = checkpoint or start_date_str or ""

        # If the polling_delay is not provided, we use the default polling delay
        polling_delay = polling_delay or POLLING_DEFAULT_DELAY

        now = datetime.now(tz=timezone.utc)
        end_date = now - timedelta(minutes=polling_delay)
        start_date = end_date

        sd = None
        ed = None
        if start_date_str:
            try:
                # If start_date >= now - delay we use now - delay
                sd = str_to_utc_datetime(start_date_str, DEFAULT_DATE_FORMAT)
                if sd < start_date:
                    start_date = sd
                else:
                    self.logger.warning(f"The provided start date {start_date_str} is to close or in the future. The default will be used.")

                # If end_date >= now - delay we use now - delay
                if end_date_str:
                    ed = str_to_utc_datetime(end_date_str, DEFAULT_DATE_FORMAT)
                    if ed < end_date:
                        end_date = ed
                    else:
                        self.logger.warning(f"The provided end date {end_date_str} is to close or in the future. The default will be used.")

            except ValueError as e:
                error_message = f"Provided start date {start_date_str} cannot be parsed."
                raise FncClientError(
                    error_type=ErrorType.POLLING_TIME_WINDOW_ERROR,
                    error_message=ErrorMessages.POLLING_TIME_WINDOW_ERROR,
                    error_data={'error_message': error_message, 'error': e},
                    exception=e
                )

        log_start_date = datetime_to_utc_str(start_date)
        log_end_date = datetime_to_utc_str(end_date)
        if not end_date_str:
            self.logger.debug(f"Getting search time window using start_date= {log_start_date} and polling_delay={polling_delay}")
        else:
            self.logger.debug(f"Using a fix search time window (start_date= {log_start_date} and end_date={log_end_date}")

        if end_date < start_date:
            raise FncClientError(
                error_type=ErrorType.POLLING_INVERTED_TIME_WINDOW_ERROR,
                error_message=ErrorMessages.POLLING_INVERTED_TIME_WINDOW_ERROR
            )

        if end_date == start_date:
            raise FncClientError(
                error_type=ErrorType.POLLING_EMPTY_TIME_WINDOW_ERROR,
                error_message=ErrorMessages.POLLING_EMPTY_TIME_WINDOW_ERROR,
                error_data={'start_date': start_date, 'end_date': end_date}
            )

        return start_date, end_date

        return start_date, end_date

    def get_default_polling_args(self) -> dict:
        """
        This method returns a dictionary containing all the default arguments for the continuous polling.

        Returns:
            dict: Dictionary containing the default arguments for the continuous polling
        """
        return {
            'status': 'active',
            'muted': False,
            'muted_rule': False,
            'muted_device': False,
            'sort_by': 'device_ip',
            'sort_order': 'asc',
            'include': 'rules, indicators',
            'limit': POLLING_MAX_DETECTIONS,
            'offset': 0
        }

    def _prepare_continuous_polling(self, context: ApiContext = None, args: dict = None, limit: int = 0) -> dict:
        self.logger.info(
            "Preparing arguments for continuously polling Detections.")

        args = args or {}
        polling_args: dict = None

        if context and context.get_polling_args():
            # Try to get polling arguments from the context and validate them
            try:
                polling_args = context.get_polling_args()
                self._validate_continuous_polling_args(args=polling_args)
                if 'offset' not in polling_args or polling_args['offset'] < 0:
                    polling_args['offset'] = 0
                self.logger.info(
                    "Using arguments received in the context.\n" +
                    "If this is not the expected behavior, ensure the context's args are cleared before polling."
                )
                return polling_args
            except FncClientError as e:
                self.logger.warning(
                    f'Arguments contained in the context will be ignored due to: \n [{e}]')

        # Getting arguments for the first call
        polling_args: dict = self.get_default_polling_args()

        if limit:
            lmt = limit if limit < POLLING_MAX_DETECTIONS else POLLING_MAX_DETECTIONS
            polling_args['limit'] = lmt

        polling_delay = args.get('polling_delay', POLLING_DEFAULT_DELAY)
        checkpoint = context.get_checkpoint() if context else None
        start_date_str = args.get('start_date', '')
        end_date_str = args.get('end_date', '')

        start_date, end_date = self._get_and_validate_search_window(
            start_date_str=start_date_str, end_date_str=end_date_str, polling_delay=polling_delay, checkpoint=checkpoint)

        polling_args['created_or_shared_start_date'] = datetime_to_utc_str(
            start_date, DEFAULT_DATE_FORMAT)
        polling_args['created_or_shared_end_date'] = datetime_to_utc_str(
            end_date, DEFAULT_DATE_FORMAT)

        if 'account_uuid' in args:
            polling_args['account_uuid'] = args['account_uuid'],

        muted_rules = str(args.get('pull_muted_rules',
                          polling_args['muted_rule'])).lower()
        if muted_rules == 'all':
            polling_args.pop('muted_rule')
        else:
            polling_args['muted_rule'] = muted_rules

        muted_devices = str(args.get('pull_muted_devices',
                            polling_args['muted_device'])).lower()
        if muted_devices == 'all':
            polling_args.pop('muted_device')
        else:
            polling_args['muted_device'] = muted_devices

        muted = str(args.get('pull_muted_detections',
                    polling_args['muted'])).lower()
        if muted == 'all':
            polling_args.pop('muted')
        else:
            polling_args['muted'] = muted

        status = str(args.get('status', polling_args['status'])).lower()
        if status == 'all':
            status = 'active,resolved'
        polling_args['status'] = status
        polling_args['offset'] = 0

        self._validate_continuous_polling_args(args=polling_args)

        return polling_args

    def _validate_continuous_polling_args(self, args: dict):
        self.logger.debug("Validating polling arguments.")
        failed = []
        # Verify Sort By is set to device_ip
        sort_by = args.get('sort_by', None)
        if not sort_by or sort_by != 'device_ip':
            failed.append("The sort_by field need to be set to 'device_ip.\n")

        muted_rule = args.get('muted_rule', None)
        if muted_rule and muted_rule not in ['true', 'false']:
            failed.append(
                "The muted_rule allowed values are ['true', 'false'].\n")

        muted_devices = args.get('muted_device', None)
        if muted_devices and muted_devices not in ['true', 'false']:
            failed.append(
                "The muted_devices allowed values are ['true', 'false'].\n")

        muted = args.get('muted', None)
        if muted and muted not in ['true', 'false']:
            failed.append("The muted allowed values are ['true', 'false'].\n")

        status: str = args.get('status', None)
        if not status:
            args['status'] = 'active,resolved'
        elif not all(s in ['active', 'resolved'] for s in status.split(',')):
            failed.append(
                "The status allowed values are ['active', 'resolved'].\n")

        if 'created_or_shared_start_date' not in args or 'created_or_shared_end_date' not in args:
            failed.append(
                "The created_or_shared_start_date and created_or_shared_end_date are required.\n")

        if failed:
            raise FncClientError(
                error_type=ErrorType.POLLING_VALIDATION_ERROR,
                error_message=ErrorMessages.POLLING_VALIDATION_ERROR,
                error_data={'failed': failed}
            )
        else:
            self.logger.info("Polling arguments successfully validated.")

    def _add_detection_rule(self, detection: dict, rules: dict, include_description: bool = False, include_signature: bool = False):
        rule = rules[detection['rule_uuid']]

        detection.update({'rule_name': rule['name']})
        detection.update({'rule_severity': rule['severity']})
        detection.update({'rule_confidence': rule['confidence']})
        detection.update({'rule_category': rule['category']})

        if include_description:
            detection.update({'rule_description': rule['description']})

        if include_signature:
            detection.update({'rule_signature': rule['query_signature']})

    def _get_entity_information(self, entity: str, fetch_pdns: bool = False, fetch_dhcp: bool = False, filter_training: bool = True) -> dict:
        result: dict = {}
        if not fetch_dhcp and not fetch_pdns:
            return result

        self.logger.debug(f'Retrieving information for entity {entity}.')

        # Get PDNS/VT/DHCP info if requested
        if fetch_pdns:
            self.logger.debug("Fetching entity's PDNS information.")
            try:
                pdns_data = self.call_endpoint(
                    endpoint=EndpointKey.GET_ENTITY_PDNS, args={'entity': entity})
                pdns: list = pdns_data.get('pdns_data', [])
                if filter_training:
                    pdns = list(filter(
                        lambda v: v.get('account_uuid', '') != POLLING_TRAINING_ACCOUNT_ID, pdns))

                result.update({"PDNS": pdns})

                self.logger.debug(
                    "Entity's pdns information successfully retrieved.")
            except FncClientError as e:
                # If the request fails for a particular entity, we log it but continue with the execution.
                self.logger.error(f"PDNS information for entity {entity} cannot be added due to:")
                self.logger.error("\n".join(traceback.format_exception(e)))

        if fetch_dhcp:
            self.logger.debug("Fetching entity's DHCP information.")
            try:
                dhcp_data = self.call_endpoint(
                    endpoint=EndpointKey.GET_ENTITY_DHCP, args={'entity': entity})
                dhcp: list = dhcp_data.get('dhcp', [])
                if filter_training:
                    dhcp = list(filter(
                        lambda v: v.get('customer_id', '') != POLLING_TRAINING_CUSTOMER_ID, dhcp))

                result.update({"dhcp": dhcp})

                self.logger.debug(
                    "Entity's DHCP information successfully retrieved.")
            except FncClientError as e:
                # If the request fails for a particular entity, we log it but continue with the execution.
                self.logger.error(f"DHCP information for entity {entity} cannot be added due to:")
                self.logger.error("\n".join(traceback.format_exception(e)))

        return result

    def _process_response(self, response: dict, entities_info: dict = {}, args: dict = None):
        # Getting instructions from the arguments
        include_description = args.get('include_description', False)
        include_signature = args.get('include_signature', False)
        fetch_pdns = args.get('include_pdns', False)
        fetch_dhcp = args.get('include_dhcp', False)
        include_events = args.get('include_events', False)
        filter_training = args.get('filter_training_detections', True)

        detection_events = {}

        dCount = len(response['detections']) if "detections" in response else 0
        if dCount == 0:
            return

        self.logger.info(f"Processing {dCount} retrieved detections.")

        # create a dictionary with the rules to find detection's rule easily
        response['rules'] = dict(
            map(lambda rule: (rule['uuid'], rule),  response['rules']))

        detection: dict

        self.logger.info(" Enriching detections.")

        # Adding rule's information to the detection
        self.logger.debug("Adding rule's information.")

        for detection in response['detections']:
            self._add_detection_rule(
                detection=detection,
                rules=response['rules'],
                include_description=include_description,
                include_signature=include_signature
            )
        self.logger.info(
            "Rules' information successfully added to the detections.")

        # Enrich detection with additional entity's information

        if fetch_dhcp or fetch_pdns:
            self.logger.debug(
                " Enriching detection with additional entity's information.")

            for detection in response['detections']:
                entity = detection['device_ip']
                if not entities_info.get(entity, {}):
                    # Add the PDNS and DHCP information if requested
                    entities_info[entity] = self._get_entity_information(
                        entity=entity,
                        fetch_dhcp=fetch_dhcp,
                        fetch_pdns=fetch_pdns,
                        filter_training=filter_training
                    )
                else:
                    self.logger.debug(f"Scaping {entity} since it was already requested.")

                detection.update(entities_info.get(entity))

            self.logger.info(
                "Entity's information successfully added to the detections.")

        # Add detection's associated events to the response
        if include_events:
            self.logger.debug("Adding Detection's associated events.")
            failed = 0
            total = 0
            for detection in response['detections']:
                total += 1
                try:
                    detection_events[detection['uuid']] = self._get_detection_events(
                        detection['uuid'])
                except FncClientError as e:
                    failed += 1
                    # If the request for associated events fails for a particular detection, we log it but continue with the execution.
                    self.logger.error(f"Detection's events request for {detection['uuid']} failed due to:")
                    self.logger.error("\n".join(traceback.format_exception(e)))

            self.logger.info(f"Associated events for ({total - failed} out of {total}) detections were successfully added to the response.")

        response['events'] = detection_events

    def _get_detection_events(self, detection_id: str) -> list:
        detection_events = []
        args = {
            'detection_uuid': detection_id,
            'offset': 0,
            'limit': POLLING_MAX_DETECTION_EVENTS
        }

        response = {}
        while 'events' not in response or response['events']:
            try:
                response = self.call_endpoint(
                    endpoint=EndpointKey.GET_DETECTION_EVENTS, args=args.copy())
                args['offset'] = args.get(
                    'offset', 0) + POLLING_MAX_DETECTION_EVENTS
                detection_events.extend(response['events'])
                count = len(detection_events)
                if count:
                    self.logger.debug(
                        f"{count} Detection's associated events successfully retrieved for detection {detection_id}.")
            except FncClientError as e:
                raise e
        return detection_events

    def _get_detections(self, args: dict) -> dict:
        start_date = args.get('created_or_shared_start_date', '')
        end_date = args.get('created_or_shared_end_date', '')
        offset = args.get('offset', 0)

        self.logger.info(
            f'Retrieving Detections between {start_date} and {end_date} and offset = {offset}.')

        response = {}

        # Retrieve detections
        response = self.call_endpoint(
            endpoint=EndpointKey.GET_DETECTIONS, args=args)

        return response

    def _check_if_limit_is_overpassed(self, polling_args: dict, limit):
        polling_args = polling_args.copy()
        polling_args['limit'] = 1

        self.logger.info("Verifying if limit will be overpassed.")

        response = self._get_detections(polling_args)
        if response['total_count'] > limit:
            raise FncClientError(
                error_type=ErrorType.POLLING_LIMIT_OVERPASSED,
                error_message=ErrorMessages.POLLING_LIMIT_OVERPASSED,
                error_data={'limit': limit, 'count': response['total_count']}
            )

    def continuous_polling(self, context: ApiContext = None, args: dict = None) -> Iterator[List[dict]]:
        self.logger.info("Starting continuous polling execution.")
        args = args.copy() or {}
        polling_args = {}

        if not context:
            self.logger.warning(
                "No context has been provided. The provided start date ( 7 days ago by default) will be used.")
            self.logger.info(
                "The context is required to keep track of the latest checkpoint to avoid missing or duplicated detections.")
        context = context or ApiContext()

        response = {}
        entities_info = {}

        limit = args.get('limit', 0)
        is_limited = limit > 0
        limit_checked = False

        while 'detections' not in response or response['detections']:
            try:
                # Prepare the arguments to be used for requesting detections
                polling_args = self._prepare_continuous_polling(
                    context=context, args=args)

                # Update context with the latest used arguments
                context.update_polling_args(args=polling_args)
                context.update_checkpoint(
                    polling_args['created_or_shared_end_date'])

                if is_limited and not limit_checked:
                    limit_checked = True
                    self._check_if_limit_is_overpassed(polling_args=polling_args, limit=limit)

                # Request detections
                response = self._get_detections(polling_args.copy())

                if len(response['detections']) > 0:
                    # Process the response enriching it if requested
                    self._process_response(response=response, entities_info=entities_info, args=args)

                    offset = polling_args.get('offset', 0)
                    polling_args['offset'] = offset + len(response['detections'])
                    context.update_polling_args(args=polling_args)
                else:
                    self.get_logger().info('No detection retrieved.')
                yield response

            except FncClientError as e:
                self.logger.error(
                    "Detections polling failed. " +
                    "If a context was provided, the arguments used for the latest call will be in the Context's polling_args field.")
                error_message = 'Detections cannot be pulled due to:'
                if e.error_type != ErrorType.POLLING_EMPTY_TIME_WINDOW_ERROR:
                    self.logger.error(f"{error_message} \n {str(e)}")
                    # self.logger.error("\n".join(traceback.format_exception(e)))
                    raise e
                else:
                    self.logger.info(f"{error_message} \n {str(e)}")
                    yield response
                    return
            except Exception as e:
                self.logger.error("Detections polling failed unexpectedly.")
                self.logger.error("\n".join(traceback.format_exception(e)))
                raise FncClientError(
                    error_type=ErrorType.GENERIC_ERROR,
                    error_message=ErrorMessages.GENERIC_ERROR_MESSAGE,
                    error_data={'error': e},
                    exception=e
                )

        self.logger.info(
            "Continuous polling execution successfully completed.")

    def get_splitted_context(self, args: dict = None) -> tuple[ApiContext, ApiContext]:
        polling_delay = args.get('polling_delay', POLLING_DEFAULT_DELAY)
        start_date_str = args.get('start_date', '')
        end_date_str = args.get('end_date', '')

        self.logger.info("Splitting the context to extract the history.")
        self.logger.debug(f"Start date= {start_date_str}, End date= {end_date_str}")

        ed = None
        if end_date_str:
            ed = str_to_utc_datetime(end_date_str)

        try:
            start_date, end_date = self._get_and_validate_search_window(
                start_date_str=start_date_str, end_date_str=end_date_str, polling_delay=polling_delay)
        except FncClientError as e:
            if e.error_type == ErrorType.POLLING_EMPTY_TIME_WINDOW_ERROR:
                start_date = e.error_data['start_date']
                end_date = e.error_data['end_date']
            else:
                raise e

        checkpoint = ''
        if not ed or ed > end_date:
            checkpoint = datetime_to_utc_str(
                end_date,
                DEFAULT_DATE_FORMAT
            )
        else:
            now = datetime.now(tz=timezone.utc)
            checkpoint = checkpoint or datetime_to_utc_str(
                now - timedelta(minutes=polling_delay),
                DEFAULT_DATE_FORMAT
            )

        history = {
            'start_date': datetime_to_utc_str(start_date, DEFAULT_DATE_FORMAT),
            'end_date': datetime_to_utc_str(end_date, DEFAULT_DATE_FORMAT),
        }

        self.logger.info("History set to")
        self.logger.debug(f"Start date= {history.get('start_date')}")
        self.logger.debug(f"End date= {history.get('end_date')}")

        history_context = ApiContext()
        history_context.update_history(history=history)

        context = ApiContext()
        context.update_checkpoint(checkpoint=checkpoint)
        self.logger.info(f"Start checkpoint set to: {checkpoint}")

        return history_context, context

    def poll_history(self, context: ApiContext = None, args: dict = None, interval: timedelta = timedelta(days=1)) -> Iterator[List[dict]]:
        # Raise Exception if No Context with History is passed
        if not context or not context.get_history():
            self.logger.error("A splitted context with the history time window is required to pull history")
            raise FncClientError(
                error_type=ErrorType.MISSING_CONTEXT,
                error_message=ErrorMessages.POLLING_MISSING_CONTEXT
            )

        # Copy the Arguments dictionary and update the history time window
        args = args.copy()
        history = context.get_history()

        now = datetime.now(tz=timezone.utc)
        start_date_str = context.get_checkpoint() or history.get('start_date', None)
        end_date_str = history.get('end_date', None)

        start_date = str_to_utc_datetime(start_date_str)
        end_date = str_to_utc_datetime(end_date_str)

        # If the there is no history to pull we return
        if end_date == start_date:
            self.get_logger().info(
                f"No history to be polled (start_date= {start_date_str} and end_date= {end_date_str}). ")
            return

        if (
            not start_date or not end_date or
            end_date > now or start_date > now or
            end_date < start_date
        ):
            self.get_logger().warning(
                f"Polling history was called with invalid data (start_date= {start_date_str} and end_date= {end_date_str}). The call will be ignored.")
            return

        self.get_logger().info(f"Polling history from {start_date_str} to {end_date_str}")

        args['start_date'] = start_date_str
        args['end_date'] = end_date_str

        # Required to check if enrichment is needed
        fetch_pdns = args.get('include_pdns', False)
        fetch_dhcp = args.get('include_dhcp', False)
        include_events = args.get('include_events', False)
        limit = 0

        # Start delta as the lesser of 1 day and the entire history time window
        delta = interval
        if delta > end_date - start_date:
            delta = end_date - start_date

        # If delta is less than 1 hour we do not care about the limit and pull the entire interval
        # otherwise get the limit and the end date for the first piece to pull
        need_enrichment = fetch_pdns or fetch_dhcp or include_events
        if delta > timedelta(hours=1) and need_enrichment:
            previous_checkpoint = start_date_str

            limit = args.get('limit', 0)
            ed = start_date + delta
            self.get_logger().debug(f"Enrichment is required so that the limit {limit} will be applied to every iteration.")
        else:
            self.get_logger().debug("Enrichment is not required or the interval is to short. The limit will be ignored.")
            delta = None
            ed = end_date
            args.pop('limit')

        # We pull detections one day at a time until we the limit is reached
        # If the limit is overpassed in the first piece of 1 day, we start
        # dividing the delta by 2 until we do not overpass the limit or delta
        # is less than 1 hour. At this moment, we pull everything regardless the
        # limit.

        d_count = 0
        is_done = False
        while not is_done:
            try:
                while not is_done and ed <= end_date:
                    # If we haven't yet pulled the entire history, We update the
                    # end_date to pull the next piece
                    context.clear_args()
                    args['end_date'] = datetime_to_utc_str(ed)

                    self.get_logger().info(f"Polling history from {context.get_checkpoint()} to {args['end_date']})")
                    count = 0
                    for detections in self.continuous_polling(context=context, args=args):
                        # we pull detections for the current piece and update the limit appropriately

                        count += len(detections.get('detections', []))
                        yield detections
                    d_count += count
                    limit = args.get('limit', 0)
                    if limit:
                        args['limit'] = limit - count

                    previous_checkpoint = context.get_checkpoint()
                    context.update_checkpoint(args['end_date'])

                    is_done = delta != interval
                    delta = interval

                    # If there remaining piece is less than delta we pull the entire remaining interval
                    if ed == end_date:
                        self.get_logger().info("Historical data has been fully retrieved")
                        is_done = True
                    elif end_date - ed <= delta:
                        ed = end_date
                    else:
                        ed = ed + delta

                is_done = True
            except FncClientError as e:
                context.update_checkpoint(previous_checkpoint)
                if e.error_type == ErrorType.POLLING_LIMIT_OVERPASSED:
                    if delta <= timedelta(hours=1):
                        # If the interval is less than 1h we do not split it and stop iteration
                        self.get_logger().info(
                            f"The limit of {limit} was overpassed but the interval is to short to split. The iteration will be ended.")
                        is_done = True
                    elif not d_count or delta == interval:
                        self.get_logger().info(f"The limit of {limit} was overpassed. Splitting the interval in half.")

                        # If we are not done yet and the limit was overpassed we divide the delta in half
                        delta = delta / 2
                        if delta < timedelta(hours=1):
                            # if delta becomes less than 1 hour, we fix it to 1 hour
                            delta = timedelta(hours=1)
                        sd = str_to_utc_datetime(context.get_checkpoint())
                        ed = sd + delta
                    else:
                        self.get_logger().info(
                            f"The limit of {limit} was overpassed with reduced interval. The iteration will be ended.")
                        is_done = True
                else:
                    raise e
        self.get_logger().info("Iteration completed for the history polling.")
