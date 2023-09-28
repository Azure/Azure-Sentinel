"""CLI subcommands."""

import platform
import sys

import click

from greynoise.__version__ import __version__
from greynoise.cli.decorator import (
    echo_result,
    gnql_command,
    handle_exceptions,
    ip_lookup_command,
    not_implemented_command,
    pass_api_client,
)
from greynoise.cli.formatter import ANSI_MARKUP
from greynoise.cli.helper import get_ip_addresses, get_queries
from greynoise.cli.parameter import ip_addresses_parameter
from greynoise.util import CONFIG_FILE, DEFAULT_CONFIG, save_config


@not_implemented_command
def account():
    """View information about your GreyNoise account."""


@not_implemented_command
def alerts():
    """List, create, delete, and manage your GreyNoise alerts."""


@click.command()
@click.option("-k", "--api-key", help="Key to include in API requests")
@click.option("-i", "--input", "input_file", type=click.File(), help="Input file")
@click.option(
    "-o", "--output", "output_file", type=click.File(mode="w"), help="Output file"
)
@click.option(
    "-f",
    "--format",
    "output_format",
    type=click.Choice(["json", "txt", "xml"]),
    default="txt",
    help="Output format",
)
@click.option("-v", "--verbose", count=True, help="Verbose output")
@pass_api_client
@echo_result
@click.pass_context
@handle_exceptions
def analyze(
    context, api_client, api_key, input_file, output_file, output_format, verbose
):
    """Analyze the IP addresses in a log file, stdin, etc."""
    if input_file is None:
        if sys.stdin.isatty():
            output = [
                context.command.get_usage(context),
                (
                    "Error: at least one text file must be passed "
                    "either through the -i/--input_file option or through a shell pipe."
                ),
            ]
            click.echo("\n\n".join(output))
            context.exit(-1)
        else:
            input_file = click.open_file("-")
    if output_file is None:
        output_file = click.open_file("-", mode="w")

    result = api_client.analyze(input_file)
    return result


@not_implemented_command
def feedback():
    """Send feedback directly to the GreyNoise team."""


@click.command()
@click.option("-k", "--api-key", help="Key to include in API requests")
@click.option("-i", "--input", "input_file", type=click.File(), help="Input file")
@click.option(
    "-o", "--output", "output_file", type=click.File(mode="w"), help="Output file"
)
@click.option(
    "--noise-only", is_flag=True, help="Select lines containing noisy addresses"
)
@click.option(
    "--riot-only", is_flag=True, help="Select lines containing RIOT addresses"
)
@pass_api_client
@click.pass_context
@handle_exceptions
def filter(
    context, api_client, api_key, input_file, output_file, noise_only, riot_only
):
    """Filter the noise from a log file, stdin, etc."""
    if input_file is None:
        if sys.stdin.isatty():
            output = [
                context.command.get_usage(context),
                (
                    "Error: at least one text file must be passed "
                    "either through the -i/--input_file option or through a shell pipe."
                ),
            ]
            click.echo("\n\n".join(output))
            context.exit(-1)
        else:
            input_file = click.open_file("-")
    if output_file is None:
        output_file = click.open_file("-", mode="w")

    for chunk in api_client.filter(
        input_file, noise_only=noise_only, riot_only=riot_only
    ):
        output_file.write(ANSI_MARKUP(chunk))


@click.command(name="help")
@click.pass_context
def help_(context):
    """Show this message and exit."""
    click.echo(context.parent.get_help())


@click.command()
@click.argument("ip_address", callback=ip_addresses_parameter, nargs=-1)
@click.option("-k", "--api-key", help="Key to include in API requests")
@click.option("-i", "--input", "input_file", type=click.File(), help="Input file")
@pass_api_client
@click.pass_context
@handle_exceptions
def interesting(context, api_client, api_key, input_file, ip_address):
    """Report one or more IP addresses as "interesting"."""
    ip_addresses = get_ip_addresses(context, input_file, ip_address)
    results = [
        api_client.interesting(ip_address=ip_address) for ip_address in ip_addresses
    ]
    return results


@ip_lookup_command
@click.option("-v", "--verbose", count=True, help="Verbose output")
def ip(
    context,
    api_client,
    api_key,
    input_file,
    output_file,
    output_format,
    verbose,
    ip_address,
    offering,
):
    """Query GreyNoise for all information on a given IP."""
    ip_addresses = get_ip_addresses(context, input_file, ip_address)
    results = [api_client.ip(ip_address=ip_address) for ip_address in ip_addresses]
    return results


@ip_lookup_command
@click.option("-v", "--verbose", count=True, help="Verbose output")
def riot(
    context,
    api_client,
    api_key,
    input_file,
    output_file,
    output_format,
    verbose,
    ip_address,
    offering,
):
    """Query GreyNoise IP to see if it is in the RIOT dataset."""
    ip_addresses = get_ip_addresses(context, input_file, ip_address)
    results = [api_client.riot(ip_address=ip_address) for ip_address in ip_addresses]
    return results


@gnql_command
def query(
    context,
    api_client,
    api_key,
    input_file,
    output_file,
    output_format,
    verbose,
    query,
    size,
    scroll,
    offering,
):
    """Run a GNQL (GreyNoise Query Language) query."""
    queries = get_queries(context, input_file, query)
    results = [
        api_client.query(query=item, size=size, scroll=scroll) for item in queries
    ]
    return results


@ip_lookup_command
def quick(
    context,
    api_client,
    api_key,
    input_file,
    output_file,
    output_format,
    ip_address,
    offering,
):
    """Quickly check whether or not one or many IPs are "noise"."""
    ip_addresses = get_ip_addresses(context, input_file, ip_address)
    results = []
    if ip_addresses:
        results.extend(api_client.quick(ip_addresses=ip_addresses))
    return results


@ip_lookup_command
def ip_multi(
    context,
    api_client,
    api_key,
    input_file,
    output_file,
    output_format,
    ip_address,
    offering,
):
    """
    Perform Context lookup for multiple IPs at once.\n
    Example: greynoise ip-multi 1.1.1.1 2.2.2.2 3.3.3.3\n
    Example: greynoise ip-multi 1.1.1.1,2.2.2.2,3.3.3.3\n
    Example: greynoise ip-multi -i <filename>
    """
    ip_addresses = get_ip_addresses(context, input_file, ip_address)
    results = []
    if ip_addresses:
        results.extend(api_client.ip_multi(ip_addresses=ip_addresses))
    return results


@click.command()
@click.option("-k", "--api-key", required=True, help="Key to include in API requests")
@click.option(
    "-O",
    "--offering",
    help="Which API offering to use, enterprise or community, "
    "defaults to enterprise",
)
@click.option("-t", "--timeout", type=click.INT, help="API client request timeout")
@click.option("-s", "--api-server", help="API server")
@click.option("-p", "--proxy", help="Proxy URL")
def setup(api_key, timeout, api_server, proxy, offering):
    """Configure API key."""
    config = {"api_key": api_key}

    if timeout is None:
        config["timeout"] = DEFAULT_CONFIG["timeout"]
    else:
        config["timeout"] = timeout

    if api_server is None:
        config["api_server"] = DEFAULT_CONFIG["api_server"]
    else:
        config["api_server"] = api_server

    if proxy is None:
        config["proxy"] = DEFAULT_CONFIG["proxy"]
    else:
        config["proxy"] = proxy

    if offering is None:
        config["offering"] = DEFAULT_CONFIG["offering"]
    else:
        config["offering"] = offering

    save_config(config)
    click.echo("Configuration saved to {!r}".format(CONFIG_FILE))


@not_implemented_command
def signature():
    """Submit an IDS signature to GreyNoise to be deployed to all GreyNoise nodes."""


@gnql_command
def stats(
    context,
    api_client,
    api_key,
    input_file,
    output_file,
    output_format,
    verbose,
    query,
    size,
    scroll,
    offering,
):
    """Get aggregate stats from a given GNQL query."""
    queries = get_queries(context, input_file, query)
    results = [api_client.stats(query=query) for query in queries]
    return results


@click.command()
def version():
    """Get version and OS information for your GreyNoise commandline installation."""
    click.echo(
        "greynoise {}\n"
        "  Python {}\n"
        "  {}\n".format(__version__, platform.python_version(), platform.platform())
    )


@ip_lookup_command
@click.option("-v", "--verbose", count=True, help="Verbose output")
@click.option("-l", "--limit", help="Limit the number of results")
@click.option(
    "-s", "--min_score", type=int, help="Return results where score is above min"
)
def similar(
    context,
    api_client,
    api_key,
    input_file,
    output_file,
    output_format,
    verbose,
    ip_address,
    offering,
    limit,
    min_score,
):
    """Query GreyNoise IP to identify Similar IPs."""
    ip_addresses = get_ip_addresses(context, input_file, ip_address)
    results = [
        api_client.similar(ip_address=ip_address, limit=limit, min_score=min_score)
        for ip_address in ip_addresses
    ]
    return results


@ip_lookup_command
@click.option("-v", "--verbose", count=True, help="Verbose output")
@click.option("-d", "--days", type=int, help="Number of Days to display")
@click.option("-F", "--field_name", help="Field name to display data for")
def timeline(
    context,
    api_client,
    api_key,
    input_file,
    output_file,
    output_format,
    verbose,
    ip_address,
    offering,
    field_name,
    days,
):
    """Query GreyNoise IP Timeline for events based on a single field."""
    ip_addresses = get_ip_addresses(context, input_file, ip_address)
    results = [
        api_client.timeline(ip_address=ip_address, days=days, field=field_name)
        for ip_address in ip_addresses
    ]
    return results


@ip_lookup_command
@click.option("-v", "--verbose", count=True, help="Verbose output")
@click.option("-d", "--days", type=int, help="Number of Days to display")
@click.option("-F", "--field_name", help="Field name to display data for")
def timelinehourly(
    context,
    api_client,
    api_key,
    input_file,
    output_file,
    output_format,
    verbose,
    ip_address,
    offering,
    field_name,
    days,
):
    """Query GreyNoise IP Timeline to get hourly event details."""
    ip_addresses = get_ip_addresses(context, input_file, ip_address)
    results = [
        api_client.timelinehourly(ip_address=ip_address, days=days)
        for ip_address in ip_addresses
    ]
    return results


@ip_lookup_command
@click.option("-v", "--verbose", count=True, help="Verbose output")
@click.option("-d", "--days", type=int, help="Number of Days to display")
@click.option("-F", "--field_name", help="Field name to display data for")
def timelinedaily(
    context,
    api_client,
    api_key,
    input_file,
    output_file,
    output_format,
    verbose,
    ip_address,
    offering,
    field_name,
    days,
):
    """Query GreyNoise IP Timeline to get daily event details."""
    ip_addresses = get_ip_addresses(context, input_file, ip_address)
    results = [
        api_client.timelinedaily(ip_address=ip_address, days=days)
        for ip_address in ip_addresses
    ]
    return results
