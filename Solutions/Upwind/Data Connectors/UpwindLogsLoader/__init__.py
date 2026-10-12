"""
Upwind Catalog Loader - Azure Function

Timer-triggered function that fetches data from six Upwind API endpoints
(inventory/catalog assets, vulnerability findings, threat detections, threat
events, threat stories, and configuration findings) and uploads each to its
own stream on Azure Monitor via Data Collection Rules (DCR).

Each dataset is fetched and uploaded independently: if one Upwind endpoint is
unavailable (e.g. not entitled for a given organization) or fails, the others
still run to completion. The function raises only if every dataset failed.

Every dataset only looks back a fixed window (the gap between scheduled runs
plus a small overlap), so a run that never reaches one loses that window's data
for good. The run has a wall-clock budget below the host's functionTimeout, and
each dataset gets at most an even share of the time left, so one oversized
dataset can't starve the rest. Pages are uploaded as they are fetched, so
whatever was fetched before a failure or an early stop is kept.
"""

import logging
from datetime import datetime, timezone

import azure.functions as func
from azure.core.exceptions import HttpResponseError
from azure.identity import ManagedIdentityCredential
from azure.monitor.ingestion import LogsIngestionClient

from .config import load_configuration
from .upwind_catalog_client import UpwindCatalogClient
from .upwind_client import RunTimeBudget, RunTimeBudgetExceeded
from .upwind_configuration_findings_client import UpwindConfigurationFindingsClient
from .upwind_threat_detections_client import UpwindThreatDetectionsClient
from .upwind_threat_events_client import UpwindThreatEventsClient
from .upwind_threat_stories_client import UpwindThreatStoriesClient
from .upwind_vulnerability_client import UpwindVulnerabilityClient


def _make_page_uploader(config, stream_name: str):
    """
    Build a callable that uploads one page of records to Azure Monitor.

    The credential and ingestion client are created once and reused across every
    page, and each page is uploaded as it arrives rather than after the whole
    dataset has been fetched. That keeps memory flat regardless of dataset size,
    and means a run cut short by the function timeout still leaves the pages it
    already fetched in the workspace.

    :param config: ConfigStore with Azure DCR configuration.
    :param stream_name: The DCR stream name to upload to (e.g. "Custom-UpwindCatalogAssets_CL").
    :return: Tuple of (upload_page callable, stats dict with "uploaded" and "errors").
    """

    azure_client_id = config.get("azure_client_id")
    dce_endpoint = config.get("azure_dce_endpoint")
    dcr_immutableid = config.get("azure_dcr_immutableid")

    # No client_id means the Function App's system-assigned identity, which is
    # what the ARM template provisions. A client_id is only supplied when the
    # deployment was pointed at a user-assigned identity instead.
    credential = (
        ManagedIdentityCredential(client_id=azure_client_id)
        if azure_client_id
        else ManagedIdentityCredential()
    )
    client = LogsIngestionClient(endpoint=dce_endpoint, credential=credential)

    stats = {"uploaded": 0, "errors": []}

    def on_upload_error(error):
        """Callback for per-chunk upload failures."""
        logging.error(
            "Failed to upload chunk of %d logs to %s: %s",
            len(error.failed_logs),
            stream_name,
            error.error,
        )
        stats["errors"].append(error)

    def upload_page(records: list) -> None:
        """Upload a single page. Errors are collected so later pages still run."""
        if not records:
            return

        # The SDK handles 1MB chunking and gzip compression internally.
        client.upload(
            rule_id=dcr_immutableid,
            stream_name=stream_name,
            logs=records,
            on_error=on_upload_error,
        )
        stats["uploaded"] += len(records)
        logging.info(
            "Uploaded %d records to %s (%d so far).",
            len(records),
            stream_name,
            stats["uploaded"],
        )

    logging.info(
        "Streaming records to stream %s (DCR %s at %s)",
        stream_name,
        dcr_immutableid,
        dce_endpoint,
    )

    return upload_page, stats


def _run_dataset(name: str, fetch_fn, config, stream_name, time_budget) -> bool:
    """
    Fetch one Upwind dataset and upload it page by page, isolating failures so
    one bad dataset doesn't block the others.

    :param fetch_fn: Callable taking a single ``on_page`` callback, which it
        invokes with each page of records as they are fetched.
    :param time_budget: The run's RunTimeBudget, shared across datasets.
    :return: True if the dataset succeeded (including "no records") or the time
        budget ran out after some records were uploaded; False on failure or
        when the budget ran out before anything was uploaded.
    """

    if not stream_name:
        logging.info(
            "Skipping %s: no stream name configured (set the corresponding "
            "STREAM_NAME_* app setting to enable it).",
            name,
        )
        return True

    if time_budget.is_exhausted():
        logging.warning("Skipping %s: run time budget already exhausted.", name)
        return False

    stats = {"uploaded": 0}
    try:
        upload_page, stats = _make_page_uploader(config, stream_name)
        fetched = fetch_fn(upload_page)

        if not fetched:
            logging.info("%s: no records returned from Upwind API. Nothing to upload.", name)
            return True

        if stats["errors"]:
            total_failed = sum(len(e.failed_logs) for e in stats["errors"])
            logging.error(
                "%s: upload to %s completed with errors: %d chunks failed, %d records lost.",
                name,
                stream_name,
                len(stats["errors"]),
                total_failed,
            )
            raise RuntimeError(
                f"Upload to {stream_name} partially failed: {len(stats['errors'])} "
                f"chunk(s) failed, {total_failed} record(s) not uploaded."
            )

        logging.info(
            "All %d records uploaded successfully to %s.", stats["uploaded"], stream_name
        )
        return True
    except RunTimeBudgetExceeded:
        # Running out of time after uploading data is a partial result, not a
        # failure: the uploaded pages are valid. Records this run didn't reach
        # are only picked up by a later run if they fall inside its window.
        logging.warning(
            "%s: partial - stopped early because the run time budget ran out; "
            "%d records were uploaded before the stop.",
            name,
            stats["uploaded"],
        )
        return stats["uploaded"] > 0
    except HttpResponseError as e:
        logging.error("%s: Azure Monitor upload failed: %s", name, e.message)
        if hasattr(e, "response") and e.response:
            logging.error(
                "%s: response status: %s, body: %s", name, e.response.status_code, e.response.text
            )
        return False
    except Exception as e:
        logging.error(
            "%s: failed after uploading %d records (those are kept): %s",
            name,
            stats["uploaded"],
            e,
            exc_info=True,
        )
        return False


def main(mytimer: func.TimerRequest = None) -> None:
    """
    Azure Function entry point (timer-triggered).

    Fetches all configured Upwind datasets and uploads each to its own DCR
    stream via the Logs Ingestion API.
    """

    utc_timestamp_start = datetime.now(timezone.utc)
    logging.info(
        "Upwind Catalog Loader: function started at %s",
        utc_timestamp_start.isoformat(),
    )

    if mytimer and mytimer.past_due:
        logging.warning("Upwind Catalog Loader: timer trigger is past due.")

    config = load_configuration()
    lookback_minutes = config.get("upwind_lookback_minutes")
    run_budget = RunTimeBudget(config.get("upwind_run_time_budget_seconds"))

    # Ordered smallest to least predictable: configuration findings come last
    # because a single evaluation sweep can make them the largest dataset by far.
    datasets = [
        ("vulnerability_findings", "azure_stream_name_vulnerability",
         lambda budget, on_page: UpwindVulnerabilityClient(config, budget).fetch_vulnerability_findings(lookback_minutes, on_page)),
        ("threat_detections", "azure_stream_name_threat_detections",
         lambda budget, on_page: UpwindThreatDetectionsClient(config, budget).fetch_threat_detections(lookback_minutes, on_page)),
        ("threat_events", "azure_stream_name_threat_events",
         lambda budget, on_page: UpwindThreatEventsClient(config, budget).fetch_threat_events(lookback_minutes, on_page)),
        ("threat_stories", "azure_stream_name_threat_stories",
         lambda budget, on_page: UpwindThreatStoriesClient(config, budget).fetch_threat_stories(lookback_minutes, on_page)),
        ("inventory_assets", "azure_stream_name_inventory",
         lambda budget, on_page: UpwindCatalogClient(config, budget).fetch_catalog_assets(lookback_minutes, on_page)),
        ("configuration_findings", "azure_stream_name_config_findings",
         lambda budget, on_page: UpwindConfigurationFindingsClient(config, budget).fetch_configuration_findings(lookback_minutes, on_page)),
    ]
    configured = [(name, config.get(stream_key), fetch) for name, stream_key, fetch in datasets]
    datasets_left = sum(1 for _, stream_name, _ in configured if stream_name)

    results = {}
    for name, stream_name, fetch in configured:
        # Each dataset gets at most an even share of the time left, so one
        # oversized dataset can't starve the ones after it. Time a dataset
        # doesn't use carries over to the rest.
        dataset_budget = run_budget.share(max(datasets_left, 1))
        results[name] = _run_dataset(
            name,
            lambda on_page, fetch=fetch, budget=dataset_budget: fetch(budget, on_page),
            config,
            stream_name,
            dataset_budget,
        )
        if stream_name:
            datasets_left -= 1

    utc_timestamp_end = datetime.now(timezone.utc)
    duration = (utc_timestamp_end - utc_timestamp_start).total_seconds()
    logging.info(
        "Upwind Catalog Loader: completed in %.2fs. Results: %s",
        duration,
        results,
    )

    if not any(results.values()):
        raise RuntimeError(f"All Upwind datasets failed this run: {results}")
