import logging

from config.feeds import FEEDS
from models.feed import FeedConfig
from services.checkpoint import (
    get_checkpoint,
    save_checkpoint,
)
from services.lock import FeedLock, LockLostError
from services.normalizer import SUPPORTED_FEEDS, normalize_records
from services.sentinel import SentinelIngestionService
from services.whoisfreaks import WhoisFreaksClient


def resolve_enabled_feeds(
    enabled_feed_names: list[str],
) -> list[FeedConfig]:

    enabled_feeds = []

    for name in enabled_feed_names:

        name = name.strip().lower()

        if not name:
            continue

        feed = FEEDS.get(name)

        if not feed:
            logging.warning(
                "Unknown feed requested: %s",
                name,
            )
            continue

        if feed.name not in SUPPORTED_FEEDS:
            logging.warning(
                "Feed '%s' is enabled but has no normalizer "
                "implemented yet; skipping until it is implemented. "
                "See services/normalizer.py.",
                feed.name,
            )
            continue

        enabled_feeds.append(feed)

    return enabled_feeds


def process_feed(
    feed: FeedConfig,
    whoisfreaks: WhoisFreaksClient,
    sentinel: SentinelIngestionService,
    statuses: dict[str, dict],
    storage_account_name: str,
) -> None:

    # ---------------------------------------------------------
    # Distributed feed lock
    #
    # IMPORTANT:
    # The lock is acquired BEFORE reading the checkpoint.
    # This prevents two Function invocations from reading the
    # same checkpoint offset simultaneously.
    # ---------------------------------------------------------
    lock = FeedLock(storage_account_name, feed.name)

    if not lock.acquire():

        logging.info(
            "Another invocation is already processing feed=%s. "
            "Skipping this invocation.",
            feed.name,
        )

        return

    try:

        # -----------------------------------------------------
        # Read checkpoint
        # -----------------------------------------------------
        checkpoint = get_checkpoint(storage_account_name, feed)

        # -----------------------------------------------------
        # Get latest available feed date from WhoisFreaks. Each feed
        # is looked up in the status document for its own API version
        # (see FeedConfig.status_api_version) -- threat feeds and NRD
        # feeds are served from different WhoisFreaks API versions
        # and their status sections are not guaranteed to be present
        # in the other version's status document.
        # -----------------------------------------------------
        status = statuses[feed.status_api_version]
        feed_date = whoisfreaks.get_latest_feed_date(feed, status)

        logging.info(
            "Latest feed date: feed=%s date=%s",
            feed.name,
            feed_date,
        )

        # -----------------------------------------------------
        # Determine starting offset
        # -----------------------------------------------------
        offset = 0

        if checkpoint:

            checkpoint_date = checkpoint.get("feed_date")
            checkpoint_offset = checkpoint.get("offset", 0)
            checkpoint_status = checkpoint.get("status")

            # Resume an interrupted run for the same feed date.
            if checkpoint_date == feed_date and checkpoint_status == "running":

                offset = int(checkpoint_offset)

                logging.info(
                    "Resuming feed=%s from offset=%s date=%s",
                    feed.name,
                    offset,
                    feed_date,
                )

            # The current feed date was already completed.
            elif checkpoint_date == feed_date and checkpoint_status == "completed":

                logging.info(
                    "Feed already completed: feed=%s date=%s",
                    feed.name,
                    feed_date,
                )

                return

            # A new feed date is available.
            else:

                logging.info(
                    "Starting new feed date: feed=%s date=%s",
                    feed.name,
                    feed_date,
                )

                offset = 0

        else:

            logging.info(
                "No checkpoint found. Starting feed=%s from offset=0",
                feed.name,
            )

        # -----------------------------------------------------
        # Mark processing as running
        # -----------------------------------------------------
        save_checkpoint(
            storage_account_name=storage_account_name,
            feed=feed,
            feed_date=feed_date,
            offset=offset,
            status="running",
        )

        # -----------------------------------------------------
        # Process pages
        # -----------------------------------------------------
        while True:

            # -------------------------------------------------
            # Heartbeat the infinite Blob lease before processing
            # another page (see services/lock.py for why the lease
            # is infinite rather than fixed-duration). If the lease
            # was lost (e.g. explicitly broken by an operator), this
            # raises LockLostError and we stop rather than continuing
            # to write under a lock we may no longer hold.
            # -------------------------------------------------
            lock.renew()

            logging.info(
                "Fetching feed page: feed=%s date=%s offset=%s limit=%s",
                feed.name,
                feed_date,
                offset,
                feed.page_size,
            )

            records, raw_count = whoisfreaks.fetch_page(
                feed=feed,
                feed_date=feed_date,
                offset=offset,
            )

            # -------------------------------------------------
            # No more records (API returned an empty page)
            # -------------------------------------------------
            if raw_count == 0:

                logging.info(
                    "No more records returned: feed=%s date=%s offset=%s",
                    feed.name,
                    feed_date,
                    offset,
                )

                break

            # -------------------------------------------------
            # Normalize WhoisFreaks records
            # -------------------------------------------------
            normalized = normalize_records(
                feed,
                records,
            )

            # -------------------------------------------------
            # Upload normalized records to Sentinel (chunked)
            # -------------------------------------------------
            sentinel.upload(
                feed,
                normalized,
            )

            # Advance offset by the pre-filter raw count so that
            # domain-list header/invalid-line filtering cannot make
            # a full API page look short and stop pagination early.
            offset += raw_count
            records_count = raw_count

            # -------------------------------------------------
            # Save checkpoint ONLY after successful upload.
            #
            # This gives us at-least-once processing semantics.
            # -------------------------------------------------
            save_checkpoint(
                storage_account_name=storage_account_name,
                feed=feed,
                feed_date=feed_date,
                offset=offset,
                status="running",
            )

            logging.info(
                "Page processed successfully: " "feed=%s records=%s offset=%s",
                feed.name,
                records_count,
                offset,
            )

            # -------------------------------------------------
            # Short page means end of feed.
            #
            # Full pages continue requesting the next offset.
            # -------------------------------------------------
            if records_count < feed.page_size:

                logging.info(
                    "Last page detected: " "feed=%s records=%s page_size=%s",
                    feed.name,
                    records_count,
                    feed.page_size,
                )

                break

        # -----------------------------------------------------
        # Feed completely processed
        # -----------------------------------------------------
        save_checkpoint(
            storage_account_name=storage_account_name,
            feed=feed,
            feed_date=feed_date,
            offset=offset,
            status="completed",
        )

        logging.info(
            "Feed processing completed: " "feed=%s date=%s final_offset=%s",
            feed.name,
            feed_date,
            offset,
        )

    except LockLostError:

        logging.exception(
            "Lock lost while processing feed=%s. Another invocation "
            "may now be processing the same feed date/offset; "
            "stopping this invocation without releasing (lease is "
            "already invalid).",
            feed.name,
        )

        raise

    except Exception:

        logging.exception(
            "Error while processing feed=%s",
            feed.name,
        )

        # Leave the checkpoint as "running".
        #
        # The next invocation will resume from the last
        # successfully uploaded offset.
        raise

    finally:

        # -----------------------------------------------------
        # ALWAYS release the distributed lock (a no-op if we
        # already know the lease is gone, e.g. after LockLostError).
        # -----------------------------------------------------
        lock.release()


def process_enabled_feeds(
    api_key: str,
    enabled_feed_names: list[str],
    storage_account_name: str,
    dcr_ingestion_endpoint: str,
    dcr_immutable_id: str,
) -> None:

    feeds = resolve_enabled_feeds(enabled_feed_names)

    if not feeds:

        logging.warning("No enabled and supported WhoisFreaks feeds to process.")

        return

    whoisfreaks = WhoisFreaksClient(api_key)

    sentinel = SentinelIngestionService(
        endpoint=dcr_ingestion_endpoint,
        dcr_immutable_id=dcr_immutable_id,
    )

    # Fetch each distinct WhoisFreaks status document once per
    # invocation (not once per feed) and cache by API version.
    statuses = {
        version: whoisfreaks.get_status(api_version=version)
        for version in {feed.status_api_version for feed in feeds}
    }

    failed_feeds = []

    for feed in feeds:

        try:

            process_feed(
                feed=feed,
                whoisfreaks=whoisfreaks,
                sentinel=sentinel,
                statuses=statuses,
                storage_account_name=storage_account_name,
            )

        except Exception as e:

            logging.exception("Feed processing failed: %s %s", feed.name, str(e))

            failed_feeds.append(feed.name)

    if failed_feeds:
        raise RuntimeError("Feed processing failed for: " + ", ".join(failed_feeds))
