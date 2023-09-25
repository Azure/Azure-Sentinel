import logging
import json
import zipfile
import io
from ..Models.Enum.mimecast_response_codes import MimecastResponseCodes

import re as regex

from ..Models.Error.errors import ParsingError, InvalidDataError


class ThreatIntelFeedResponseHelper:
    """ResponseHelper responsible for checking is token in response headers, also parsing and mapping responses."""

    next_token = ""
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
            logging.error(
                "Access is denied to the requested resource."
                "The user may not have enough permission to perform the action."
            )
        elif response.status_code == MimecastResponseCodes.not_found:
            logging.error("The requested resource does not exist.")
        elif response.status_code == MimecastResponseCodes.conflict:
            logging.error("The current status of the relying data does not match what is defined in the request.")
        elif response.status_code == MimecastResponseCodes.internal_server_error:
            logging.error("The request was not processed successfully or an issue has occurred on the Mimecast side.")
        else:
            logging.error("Unknown error.Please contact API administrator.")

    @staticmethod
    def get_next_token(response, next_token):
        """Extracting token from response headers."""
        has_more_data = False
        if response.headers.get("x-mc-threat-feed-next-token") != next_token:
            has_more_data = True
            next_token = response.headers.get("x-mc-threat-feed-next-token")
        else:
            next_token = ""

        return has_more_data, next_token

    @staticmethod
    def parser_threat_intel_feed_success_response(response, file_type, compress, mimecast_endpoint):
        """Parsing Threat Intel Feed responses depending on compress and file format parameters."""

        if response.headers.get("Content-Type") == "application/octet-stream":
            response = response.content
            if compress:
                try:
                    parsed_events = ThreatIntelFeedResponseHelper.parse_compressed_data(response, file_type)
                except Exception as exception:
                    exception.extra_message = "Parsing of Threat Intel Feed compressed data failed."
                    raise ParsingError("Parsing of Threat Intel Feed compressed data failed.")
            else:
                try:
                    parsed_events = ThreatIntelFeedResponseHelper.parse_uncompressed_data(response, file_type)
                except Exception as exception:
                    exception.extra_message = "Parsing of Threat Intel Feed uncompressed data failed."
                    raise ParsingError("Parsing of Threat Intel Feed uncompressed data failed.")
            return parsed_events
        else:
            try:
                response_text = json.loads(response.text)
            except json.JSONDecodeError:
                logging.error(mimecast_endpoint + ": Invalid content provided. Probably no more logs left.")
                return []
            else:
                if response_text["fail"]:
                    no_threat_intel_feed = ["No results found for threat intel feed.", "Unable to compress feeds."]
                    if any(x in response_text["fail"][0]["errors"][0]["message"] for x in no_threat_intel_feed):
                        return []
                    else:
                        logging.error(mimecast_endpoint + ": " + response_text["fail"][0]["errors"][0]["message"])
                        raise InvalidDataError(f'Unknown error: {response_text["fail"][0]["errors"][0]["message"]}')

    @staticmethod
    def parse_compressed_data(response, file_type):
        """Parsing compressed responses."""
        events = []
        byte_content = io.BytesIO(response)
        zip_file = zipfile.ZipFile(byte_content)
        for file_name in zip_file.namelist():
            content = zip_file.open(file_name).read()
            events += ThreatIntelFeedResponseHelper.parse_uncompressed_data(content, file_type)
        return events

    @staticmethod
    def parse_uncompressed_data(response, file_type):
        """Parsing uncompressed responses."""
        mapped_response = []
        if file_type == "csv":
            response_text = response.decode("utf-8")
            splitted_response_text = response_text.split("\n")
            pipes_num = splitted_response_text[0].count("|")
            splitted_keys = splitted_response_text[0].split("|")
            del splitted_response_text[0]
            mapped_keys = dict.fromkeys(splitted_keys)
            for response_text_line in splitted_response_text:
                #  Fix in case there are | characters in the FileName field
                if response_text_line.count("|") > pipes_num:
                    file_name = regex.search(r'".+?"', response_text_line).group()
                    new_file_name = file_name.replace("|", "<pipe>")
                    response_text_line = response_text_line.replace(file_name, new_file_name)
                splitted_values = response_text_line.split("|")
                mapped_dict = {key: value for key, value in zip(mapped_keys, splitted_values)}
                mapped_response.append(mapped_dict)
        elif file_type == "stix":
            response_text = json.loads(response)
            mapped_response = response_text["objects"]

        return mapped_response
