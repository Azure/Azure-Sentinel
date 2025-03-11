from zipfile import ZipFile, BadZipfile
import logging
import json
import io

from ..Models.Enum.mimecast_response_codes import MimecastResponseCodes
from ..Models.Error.errors import InvalidDataError, ParsingError, MimecastRequestError


class SIEMResponseHelper:
    """SIEMResponseHelper responsible for checking is token in response headers and parsing responses."""

    next_token = ''
    mimecast_endpoint = None

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

    def parse_siem_success_response(self, response, file_format):
        """Parsing SIEM responses depending on file format parameter."""
        if response.headers.get('Content-Type') == 'application/octet-stream':
            parsed_events = SIEMResponseHelper.parse_compressed_data(response, file_format)
            return parsed_events
        else:
            try:
                response_text = json.loads(response.text)
            except json.JSONDecodeError:
                logging.error(self.mimecast_endpoint + ": Invalid content provided. Probably no more logs left.")
                raise InvalidDataError('No more logs.')
            else:
                if response_text['fail']:
                    logging.error(self.mimecast_endpoint + ": " + response_text['fail'][0]['errors'][0]['message'])
                    raise MimecastRequestError(self.mimecast_endpoint + ": " + response_text['fail'][0]['errors'][0]['message'])

    @staticmethod
    def parse_compressed_data(response, file_format):
        """Parsing compressed responses."""
        events = []
        try:
            byte_content = io.BytesIO(response.content)
            zip_file = ZipFile(byte_content)
        except TypeError:
            raise ParsingError(
                "Parsing of SIEM compressed data failed. Invalid content provided. Probably no more logs left.")
        except BadZipfile:
            raise ParsingError(
                "Parsing of SIEM compressed data failed. Invalid zip file provided. Probably no more logs left.")

        for file_name in zip_file.namelist():
            content = zip_file.open(file_name).read()
            splitted_filename = file_name.split('_')
            if splitted_filename[0] == 'ttp':
                log_type = '{0}_{1}'.format(splitted_filename[0], splitted_filename[1])
            else:
                log_type = splitted_filename[0]
            if file_format == 'key_value':
                raw_events = SIEMResponseHelper.parse_key_value_response(content)
            else:
                raw_events = json.loads(content, encoding='utf-8')['data']
            for raw_event in raw_events:
                raw_event.update({'logType': log_type})
            events += raw_events
        return events

    @staticmethod
    def parse_key_value_response(file):
        """Parsing key_value file format responses."""
        events = []
        raw_events = file.decode('utf-8')
        string_events = raw_events.split('datetime=')
        for string_event in string_events:
            if string_event != '':
                event = "datetime={0}".format(string_event)
                dict_string = dict(item.split("=", 1) for item in event.rstrip().split("|"))
                events.append(dict_string)
        return events

    @staticmethod
    def get_siem_next_token(response):
        """Extracting SIEM token from response headers."""
        has_more_logs = False
        if 'mc-siem-token' in response.headers:
            has_more_logs = True
            SIEMResponseHelper.next_token = response.headers['mc-siem-token']
        else:
            SIEMResponseHelper.next_token = ''
        return has_more_logs, SIEMResponseHelper.next_token
