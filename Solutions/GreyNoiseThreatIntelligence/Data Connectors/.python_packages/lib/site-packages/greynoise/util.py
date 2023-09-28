"""Utility functions."""
import logging
import os
from ipaddress import IPv6Address, ip_address

from six.moves.configparser import ConfigParser

CONFIG_FILE = os.path.expanduser(os.path.join("~", ".config", "greynoise", "config"))
LOGGER = logging.getLogger(__name__)

DEFAULT_CONFIG = {
    "api_key": "",
    "api_server": "https://api.greynoise.io",
    "timeout": 60,
    "proxy": "",
    "offering": "enterprise",
}


def load_config():
    """Load configuration.

    :returns:
        Current configuration based on configuration file and environment variables.
    :rtype: dict

    """
    config_parser = ConfigParser(
        {key: str(value) for key, value in DEFAULT_CONFIG.items()}
    )
    config_parser.add_section("greynoise")

    if os.path.isfile(CONFIG_FILE):
        LOGGER.debug("Parsing configuration file: %s...", CONFIG_FILE)
        with open(CONFIG_FILE) as config_file:
            config_parser.read_file(config_file)
    else:
        LOGGER.debug("Configuration file not found: %s", CONFIG_FILE)

    if "GREYNOISE_API_KEY" in os.environ:
        api_key = os.environ["GREYNOISE_API_KEY"]
        LOGGER.debug("API key found in environment variable: %s", api_key)
        # Environment variable takes precedence over configuration file content
        config_parser.set("greynoise", "api_key", api_key)

    if "GREYNOISE_API_SERVER" in os.environ:
        api_server = os.environ["GREYNOISE_API_SERVER"]
        LOGGER.debug("API server found in environment variable: %s", api_server)
        # Environment variable takes precedence over configuration file content
        config_parser.set("greynoise", "api_server", api_server)

    if "GREYNOISE_TIMEOUT" in os.environ:
        timeout = os.environ["GREYNOISE_TIMEOUT"]
        try:
            int(timeout)
        except ValueError:
            LOGGER.error(
                "GREYNOISE_TIMEOUT environment variable "
                "cannot be converted to an integer: %r",
                timeout,
            )
        else:
            LOGGER.debug("Timeout found in environment variable: %s", timeout)
            # Environment variable takes precedence over configuration file content
            config_parser.set("greynoise", "timeout", timeout)

    if "GREYNOISE_PROXY" in os.environ:
        proxy = os.environ["GREYNOISE_PROXY"]
        LOGGER.debug("Proxy found in environment variable: %s", proxy)
        # Environment variable takes precedence over configuration file content
        config_parser.set("greynoise", "proxy", proxy)

    if "GREYNOISE_OFFERING" in os.environ:
        offering = os.environ["GREYNOISE_OFFERING"]
        LOGGER.debug("Offering found in environment variable: %s", offering)
        # Environment variable takes precedence over configuration file content
        config_parser.set("greynoise", "offering", offering)

    return {
        "api_key": config_parser.get("greynoise", "api_key"),
        "api_server": config_parser.get("greynoise", "api_server"),
        "timeout": config_parser.getint("greynoise", "timeout"),
        "proxy": config_parser.get("greynoise", "proxy"),
        "offering": config_parser.get("greynoise", "offering"),
    }


def save_config(config):
    """Save configuration.

    :param config: Data to be written to the configuration file.
    :type config:  dict

    """
    config_parser = ConfigParser()
    config_parser.add_section("greynoise")
    config_parser.set("greynoise", "api_key", config["api_key"])
    config_parser.set("greynoise", "api_server", config["api_server"])
    config_parser.set("greynoise", "timeout", str(config["timeout"]))
    config_parser.set("greynoise", "proxy", config["proxy"])
    config_parser.set("greynoise", "offering", config["offering"])

    config_dir = os.path.dirname(CONFIG_FILE)
    if not os.path.isdir(config_dir):
        os.makedirs(config_dir)

    with open(CONFIG_FILE, "w") as config_file:
        config_parser.write(config_file)


def validate_ip(ip, strict=True, print_warning=True):
    """Check if the IPv4 address is valid.

    :param ip_address: IPv4 address value to validate.
    :type ip_address: str
    :param strict: Whether to raise exception if validation fails.
    :type strict: bool
    :raises ValueError: When validation fails and strict is set to True.
    :type print_warning: bool
    :raises ValueError: By default, otherwise returns nothing

    """
    is_valid = False
    error_message = ""

    try:
        ip_address(ip)
        is_valid = True
    except ValueError:
        if print_warning:
            error_message = "Invalid IP address: {!r}".format(ip)
            LOGGER.warning(error_message)
        if strict:
            raise ValueError(error_message)
        return False

    if is_valid:
        if type(ip_address(ip)) is IPv6Address:
            error_message = "IPv6 addresses are not supported: {!r}".format(ip)
            if print_warning:
                LOGGER.warning(error_message)
            if strict:
                raise ValueError(error_message)
            return False
        else:
            is_routable = ip_address(ip).is_global
            if is_routable:
                return True
            else:
                error_message = "Non-Routable IP address: {!r}".format(ip)
                if print_warning:
                    LOGGER.warning(error_message)
                if strict:
                    raise ValueError(error_message)
                return False


def validate_timeline_field_value(field):
    """Check if the Timeline Field value is valid.

    :param field: field value to validate.
    :type field: str

    """
    valid_field_names = [
        "destination_port",
        "http_path",
        "http_user_agent",
        "source_asn",
        "source_org",
        "source_rdns",
        "tag_ids",
        "classification",
    ]

    if field in valid_field_names:
        return True
    else:
        raise ValueError(
            f"Field must be one of the following values: {valid_field_names}"
        )


def validate_timeline_days(days):
    """Check if the Timeline Days value is valid.

    :param days: field value to validate.
    :type days: str

    """
    if isinstance(days, str):
        raise ValueError(
            "Days must be a valid integer between 1 and 90.  Current input is a "
            "string."
        )
    if isinstance(days, int) and 1 <= int(days) <= 90:
        return True
    else:
        raise ValueError("Days must be a valid integer between 1 and 90.")


def validate_timeline_granularity(granularity):
    """Check if the Timeline granularity value is valid.

    :param granularity: field value to validate.
    :type granularity: str

    """
    if granularity != "1h" and granularity != "1d":
        raise ValueError("Granularity currently only supports a value of 1d or 1h")
    else:
        return True


def validate_similar_min_score(min_score):
    """Check if the Similarity min_score value is valid.

    :param min_score: field value to validate.
    :type min_score: str

    """
    if isinstance(min_score, str):
        raise ValueError(
            "Min Score must be a valid integer between 0 and 100.  Current input is a "
            "string."
        )
    if isinstance(min_score, int) and 0 <= int(min_score) <= 100:
        return True
    else:
        raise ValueError("Min Score must be a valid integer between 0 and 100.")
