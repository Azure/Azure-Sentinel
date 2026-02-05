from ..Models.Enum.mimecast_response_codes import MimecastResponseCodes
import logging
import json

from ..Models.Error.errors import InvalidDataError


class ResponseHelper:
    """ResponseHelper responsible for checking is token in response headers, also parsing and mapping responses."""

    next_token = ''
    response = []

    def __init__(self):
        """Initial setup of logger and default value for Mimecast endpoint."""
        self.mimecast_endpoint = None

    def check_response_codes(self, response, mimecast_endpoint):
        """Checking all response codes from Mimecast documentation and logging errors."""
        self.mimecast_endpoint = mimecast_endpoint
        if response.status_code == MimecastResponseCodes.success:
            return response
        elif response.status_code == MimecastResponseCodes.bad_request:
            logging.error("Request cannot be processed because it is either malformed or not correct.")
        elif response.status_code == MimecastResponseCodes.unauthorized:
            logging.error("Authorization information is either missing, incomplete or incorrect.")
        elif response.status_code == MimecastResponseCodes.forbidden:
            logging.error("Access is denied to the requested resource."
                          "The user may not have enough permission to perform the action.")
        elif response.status_code == MimecastResponseCodes.not_found:
            logging.error("The requested resource does not exist.")
        elif response.status_code == MimecastResponseCodes.conflict:
            logging.error("The current status of the relying data does not match what is defined in the request.")
        elif response.status_code == MimecastResponseCodes.internal_server_error:
            logging.error("The request was not processed successfully or an issue has occurred on the Mimecast side.")
        else:
            logging.error("Unknown error.Please contact API administrator.")

    def parse_success_response(self, response):
        """Logging and checking response body for errors."""
        try:
            response_text = json.loads(response.text)
        except json.JSONDecodeError:
            logging.error(self.mimecast_endpoint + ": Invalid content provided. Probably no more logs left.")
            raise InvalidDataError('Invalid content provided. Probably no more logs.')

        if response_text['fail']:
            logging.error(self.mimecast_endpoint + ": " + response_text['fail'][0]['errors'][0]['message'])
        else:
            return response_text['data']

    @staticmethod
    def get_next_token(response):
        """Extracting token from response headers."""
        has_more_data = False
        dictionary_response = json.loads(response.text)
        if 'pagination' in dictionary_response['meta']:
            if 'next' in dictionary_response['meta']['pagination']:
                has_more_data = True
                ResponseHelper.next_token = dictionary_response['meta']['pagination']['next']
            else:
                ResponseHelper.next_token = ''
        return has_more_data, ResponseHelper.next_token
