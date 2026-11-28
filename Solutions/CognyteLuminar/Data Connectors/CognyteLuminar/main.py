"""
main.py

Timer-triggered Azure Function: pulls STIX objects from the Cognyte Luminar
TAXII collections and uploads them to Microsoft Sentinel threat intelligence
through the STIX objects upload API.

    Luminar TAXII  --(luminar_manager)-->  batches
      --(stix_transform)-->  supported STIX objects
      --(sentinel_client)-->  ThreatIntelIndicators / ThreatIntelObjects

Checkpointing is per collection and committed only after the batch has been
uploaded, so a failure never advances past data that did not reach Sentinel.
"""

from __future__ import annotations

import logging
import time
from datetime import datetime, timedelta
from typing import Dict, Optional

import azure.functions as func  # type: ignore

from .config import LUMINAR_DATE_FORMAT, ConfigError, Settings
from .luminar_manager import LuminarAPIError, LuminarManager
from .sentinel_client import SentinelAuthError, SentinelTIClient, SentinelUploadError
from .state_manager import StateManager
from .stix_transform import TransformOptions, transform_batch

logger = logging.getLogger(__name__)

# Identifies this integration to the Luminar API.
LUMINAR_USER_AGENT = "Sentinel"


def subtract_seconds(timestamp: str, seconds: int) -> str:
    """Overlap guard applied when resuming from a saved checkpoint.

    `added_after` is exclusive on the Luminar server, so resuming from the
    exact `X-TAXII-Date-Added-Last` value is already safe unless two objects
    share one microsecond across a page boundary. Re-reading a second of
    history costs nothing because Sentinel upserts by STIX id.
    """
    if seconds <= 0:
        return timestamp
    parsed = datetime.strptime(timestamp, LUMINAR_DATE_FORMAT)
    return (parsed - timedelta(seconds=seconds)).strftime(LUMINAR_DATE_FORMAT)


class Runner:
    def __init__(
        self,
        settings: Settings,
        luminar: LuminarManager,
        sentinel: SentinelTIClient,
        state: StateManager,
    ) -> None:
        self.settings = settings
        self.luminar = luminar
        self.sentinel = sentinel
        self.state = state
        self.deadline = time.monotonic() + settings.max_run_minutes * 60

    def out_of_time(self) -> bool:
        return time.monotonic() >= self.deadline

    def run(self) -> Dict[str, Dict[str, int]]:
        checkpoints = self.state.load()
        summary: Dict[str, Dict[str, int]] = {}
        for alias in self.settings.collections:
            if self.out_of_time():
                logger.warning("Run time budget exhausted before collection %s", alias)
                break
            try:
                summary[alias] = self.run_collection(alias, checkpoints)
            except (
                LuminarAPIError,
                SentinelAuthError,
                SentinelUploadError,
                ValueError,
            ) as err:
                # Checkpoints already saved for this alias stay valid; move on
                # so one failing feed does not block the others.
                logger.error("Collection %s stopped with error: %s", alias, err)
                summary.setdefault(alias, {})["error"] = 1
        logger.info("Run summary: %s", summary)
        return summary

    def run_collection(self, alias: str, checkpoints: Dict[str, str]) -> Dict[str, int]:
        saved = checkpoints.get(alias)
        if saved:
            start = subtract_seconds(saved, self.settings.resume_overlap_seconds)
            logger.info(
                "[%s] resuming from checkpoint %s (query from %s)", alias, saved, start
            )
        else:
            start = self.settings.luminar_initial_fetch
            logger.info(
                "[%s] no checkpoint; starting from initial fetch date %s", alias, start
            )

        opts = TransformOptions(
            collection=alias,
            tlp_marking_ref=self.settings.tlp_marking_ref,
            default_validity_days=self.settings.default_validity_days,
            default_confidence=self.settings.default_confidence,
            enrich_from_reports=self.settings.enrich_from_reports,
            skip_expired=self.settings.skip_expired_indicators,
        )
        totals = {"received": 0, "sent": 0, "accepted": 0, "rejected": 0, "batches": 0}

        for batch in self.luminar.get_objects(alias, added_after=start):
            data = batch["results"]["data"]
            last_success: Optional[str] = batch["results"]["last_success"]
            error = batch.get("error")

            stix_objects, tstats = transform_batch(data, opts)
            logger.info(
                "[%s] batch %d transform: %s",
                alias,
                totals["batches"] + 1,
                tstats.as_dict(),
            )

            if stix_objects:
                ustats = self.sentinel.upload(stix_objects)
                logger.info(
                    "[%s] batch %d upload: %s",
                    alias,
                    totals["batches"] + 1,
                    ustats.as_dict(),
                )
                totals["accepted"] += ustats.objects_accepted
                totals["rejected"] += ustats.objects_rejected

            totals["received"] += tstats.received
            totals["sent"] += tstats.sent
            totals["batches"] += 1

            if last_success:
                checkpoints[alias] = last_success
                self.state.save(checkpoints)
                logger.info("[%s] checkpoint saved: %s", alias, last_success)

            if error:
                logger.error(
                    "[%s] Luminar reported an error after this batch: %s", alias, error
                )
                break
            if self.out_of_time():
                logger.warning(
                    "[%s] time budget reached; remaining data picked up next run", alias
                )
                break

        logger.info("[%s] done: %s", alias, totals)
        return totals


def build_runner(settings: Settings) -> Runner:
    luminar = LuminarManager(
        cognyte_client_id=settings.luminar_client_id,
        cognyte_client_secret=settings.luminar_client_secret,
        cognyte_account_id=settings.luminar_account_id,
        cognyte_base_url=settings.luminar_base_url,
        added_after=settings.luminar_initial_fetch,
        limit=settings.page_limit,
        pages_per_batch=settings.pages_per_batch,
        user_agent=LUMINAR_USER_AGENT,
    )
    sentinel = SentinelTIClient(
        tenant_id=settings.tenant_id,
        client_id=settings.application_id,
        client_secret=settings.client_secret,
        workspace_id=settings.workspace_id,
        source_system=settings.source_system,
    )
    state = StateManager(settings.storage_connection_string)
    return Runner(settings, luminar, sentinel, state)


def main(mytimer: func.TimerRequest) -> None:
    if mytimer.past_due:
        logger.info("The timer is past due; running anyway.")
    try:
        settings = Settings.from_env()
    except ConfigError as err:
        logger.error("Configuration error: %s", err)
        return
    logger.info(
        "Cognyte Luminar connector starting: collections=%s base_url=%s",
        settings.collections,
        settings.luminar_base_url,
    )
    try:
        build_runner(settings).run()
    except Exception as err:  # pylint: disable=broad-except
        logger.exception("Unhandled error in Cognyte Luminar connector: %s", err)
