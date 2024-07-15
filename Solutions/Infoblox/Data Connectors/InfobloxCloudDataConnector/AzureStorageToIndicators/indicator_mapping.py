"""Mapping threat data to the required format for processing."""

import inspect
from ..SharedCode import consts
from ..SharedCode.logger import applogger
from ..SharedCode.infoblox_exception import InfobloxException


class Mapping:
    """Mapping class to map threat data to the required format for processing."""

    def __init__(self):
        """Initialize instance variable for class."""
        self.confidence = consts.CONFIDENCE_THRESHOLD
        self.threat_level = consts.THREAT_LEVEL

    def map_threat_data(self, item_list):
        """Map threat data to the required format for processing.

        Args:
            item_list (list): A list of threat data items to be processed.

        Returns:
            list: A list of mapped threat data items in the required format.
        """
        __method_name = inspect.currentframe().f_code.co_name
        try:
            applogger.info(
                consts.LOG_FORMAT.format(
                    consts.LOGS_STARTS_WITH,
                    __method_name,
                    consts.INDICATOR_FUNCTION_NAME,
                    "Mapping threat data, No. of records to map = {}".format(len(item_list)),
                )
            )
            mapped = []
            hash_map = {
                "SHA1": "SHA-1",
                "SHA256": "SHA-256",
                "MD5": "MD5",
                "SHA512": "SHA-512",
                "SHA384": "SHA-384",
                "SSDEEP": "SSDEEP",
                "MD6": "MD6",
                "RIPEMD160": "RIPEMD-160",
                "SHA224": "SHA-224",
                "SHA3224": "SHA3-224",
                "SHA3256": "SHA3-256",
                "SHA3384": "SHA3-384",
                "SHA3512": "SHA3-512",
                "SSDEEPWHIRLPOOL": "SSDEEPWHIRLPOOL",
            }
            temp = {
                "HOST": "[domain-name:value = '{}']",
                "IP": "[ipv4-addr:value = '{}']",
                "URL": "[url:value = '{}']",
                "HASH": "[file:hashes.'{}' = '{}']",
                "EMAIL": "{}",
            }
            for item in item_list:
                pattern = temp.get(item.get("type"))
                if item.get("type").upper() == "HASH":
                    hash_type = hash_map.get(item.get("hash_type"), "SHA256")
                    pattern = pattern.format(hash_type, item.get(item.get("type").lower()))
                else:
                    pattern = pattern.format(item.get(item.get("type").lower()))
                confidence_val = item.get("confidence", 0)
                threat_level_val = item.get("threat_level", 0)
                if threat_level_val >= self.threat_level and confidence_val >= self.confidence:
                    body = {
                        "name": "Infoblox - {} - {}".format(item.get("type"), item.get("id")),
                        "type": "indicator",
                        "spec_version": "2.1",
                        "id": "indicator--{}".format(item.get("id")),
                        "created": item.get("detected"),
                        "modified": item.get("detected"),
                        "revoked": item.get("up", False),
                        "labels": [
                            item.get("type"),
                            "Domain : {}".format(item.get("domain", "-")),
                            "TLD : {}".format(item.get("tld", "-")),
                            "Imported : {}".format(item.get("imported")),
                            "Profile : {}".format(item.get("profile")),
                            "Property : {}".format(item.get("property")),
                            "Dga: {}".format(item.get("dga", "-")),
                            "Threat Level : {}".format(item.get("threat_level")),
                            "Threat Score : {}".format(item.get("threat_score", "-")),
                            "Threat Score Rating : {}".format(item.get("threat_score_rating", "-")),
                            "Confidence Score : {}".format(item.get("confidence_score", "-")),
                            "Confidence Score Rating : {}".format(item.get("confidence_score_rating", "-")),
                            "Risk Score : {}".format(item.get("risk_score", "-")),
                            "Risk Score Rating : {}".format(item.get("risk_score_rating", "-")),
                            "Notes : {}".format(item.get("extended", {}).get("notes", "-")),
                        ],
                        "confidence": (item.get("confidence", 0)),
                        "description": "Infoblox - {} - {}".format(item.get("type"), item.get("class")),
                        "indicator_types": [item.get("class")],
                        "pattern": pattern,
                        "pattern_type": "stix",
                        "pattern_version": "2.1",
                        "valid_from": item.get("received"),
                        "valid_until": item.get("expiration"),
                    }
                    mapped.append(body)
            applogger.info(
                consts.LOG_FORMAT.format(
                    consts.LOGS_STARTS_WITH,
                    __method_name,
                    consts.INDICATOR_FUNCTION_NAME,
                    "No. of records after mapping = {}".format(len(mapped)),
                )
            )
            return mapped
        except KeyError as keyerror:
            applogger.error(
                "{} : {} (method={}), KeyError while mapping threat data :{}".format(
                    consts.LOGS_STARTS_WITH,
                    consts.INDICATOR_FUNCTION_NAME,
                    __method_name,
                    keyerror,
                )
            )
            raise InfobloxException()
        except Exception as error:
            applogger.error(
                "{} : {} (method={}), Error while mapping threat data :{}".format(
                    consts.LOGS_STARTS_WITH,
                    consts.INDICATOR_FUNCTION_NAME,
                    __method_name,
                    error,
                )
            )
            raise InfobloxException()

    def create_chunks(self, text, start_index):
        """Create chunk from text starting at a specific index.

        Args:
            text (str): The input text from which chunks will be created.
            start_index (int): The starting index to begin creating chunks from.

        Returns:
            list: A list of chunked data items.
        """
        __method_name = inspect.currentframe().f_code.co_name
        try:
            applogger.info(
                consts.LOG_FORMAT.format(
                    consts.LOGS_STARTS_WITH,
                    __method_name,
                    consts.INDICATOR_FUNCTION_NAME,
                    "Creating Chunks",
                )
            )
            chunk_size = consts.CHUNK_SIZE_INDICATOR
            chunked_data = [text[index: index + chunk_size] for index in range(start_index, len(text), chunk_size)]
            applogger.info(
                consts.LOG_FORMAT.format(
                    consts.LOGS_STARTS_WITH,
                    __method_name,
                    consts.INDICATOR_FUNCTION_NAME,
                    "Number of chunks : {}".format(len(chunked_data)),
                )
            )
            return chunked_data
        except Exception as error:
            applogger.error(
                consts.LOG_FORMAT.format(
                    consts.LOGS_STARTS_WITH,
                    __method_name,
                    consts.INDICATOR_FUNCTION_NAME,
                    "Unexpected error : Error-{}".format(error),
                )
            )
            raise InfobloxException()
