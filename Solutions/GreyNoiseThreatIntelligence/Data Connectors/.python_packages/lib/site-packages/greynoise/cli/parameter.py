"""Command line parameter types."""

import click

from greynoise.util import validate_ip


def ip_addresses_parameter(_context, _parameter, values):
    """IPv4 addresses passed from the command line.

    :param values: IPv4 address values
    :type value: list
    :raises click.BadParameter: when any IP address value is invalid

    """
    valid_ips = []
    for value in values:
        try:
            if "," in value:
                split_value = value.split(",")
                for item in split_value:
                    validate_ip(item, strict=False)
                    valid_ips.append(item)
            else:
                validate_ip(value)
                valid_ips.append(value)
        except ValueError:
            raise click.BadParameter(value)

    return valid_ips
