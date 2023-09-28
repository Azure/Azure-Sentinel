"""Helper functions to reduce subcommand duplication."""

import sys

import click

from greynoise.util import validate_ip


def get_ip_addresses(context, input_file, ip_address):
    """Get IP addresses passed as argument or via input file.

    :param context: Subcommand context
    :type context: click.Context
    :param input_file: Input file
    :type input_file: click.File | None
    :param ip_address: IP addresses passed via the ip address argument
    :type query: tuple(str, ...)

    """
    if input_file is None and not sys.stdin.isatty():
        input_file = click.open_file("-")

    if input_file is None and not ip_address:
        click.echo(context.get_help())
        context.exit(-1)

    ip_addresses = []
    if input_file is not None:
        lines = [line.strip() for line in input_file]
        ip_addresses.extend([line for line in lines if validate_ip(line, strict=False)])
    ip_addresses.extend(list(ip_address))

    if not ip_addresses:
        output = [
            context.command.get_usage(context),
            (
                "Error: at least one valid IP address must be passed either as an "
                "argument (IP_ADDRESS) or through the -i/--input_file option."
            ),
        ]
        click.echo("\n\n".join(output))
        context.exit(-1)

    return ip_addresses


def get_queries(context, input_file, query):
    """Get queries passed as argument or via input file.

    :param context: Subcommand context
    :type context: click.Context
    :param input_file: Input file
    :type input_file: click.File | None
    :param query: GNQL query
    :type query: str | None

    """
    if input_file is None and not sys.stdin.isatty():
        input_file = click.open_file("-")

    if input_file is None and not query:
        click.echo(context.get_help())
        context.exit(-1)

    queries = []
    if input_file is not None:
        queries.extend([line.strip() for line in input_file])
    if query:
        queries.append(query)

    if not queries:
        output = [
            context.command.get_usage(context),
            (
                "Error: at least one query must be passed either as an argument "
                "(QUERY) or through the -i/--input_file option."
            ),
        ]
        click.echo("\n\n".join(output))
        context.exit(-1)

    return queries
