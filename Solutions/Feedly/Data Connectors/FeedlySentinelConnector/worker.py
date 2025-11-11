import logging
import time
from collections.abc import Iterable

from FeedlySentinelConnector.config import FeedlySentinelConfig
from FeedlySentinelConnector.feedly_downloader import FeedlyDownloader
from FeedlySentinelConnector.sentinel_api import SentinelApiConnector
from FeedlySentinelConnector.state_manager import FeedlyCheckpoint
from pandas import DataFrame, concat

logger = logging.getLogger(__name__)


class FeedlySentinelWorker:
    def __init__(self, config: FeedlySentinelConfig):
        self.sentinel_api_connector = SentinelApiConnector(
            workspace_id=config.sentinel_workspace_id,
            log_analytics_uri=config.sentinel_log_analytics_uri,
            shared_key=config.sentinel_workspace_key,
            log_type="feedly_indicators",
        )
        self.feedly_downloader = FeedlyDownloader(config.feedly_api_key)
        self.feedly_stream_ids = config.feedly_stream_ids.split(",")
        self.checkpoint = FeedlyCheckpoint(config.azure_web_jobs_storage)
        self.days_to_backfill = config.days_to_backfill

    @staticmethod
    def from_env() -> "FeedlySentinelWorker":
        return FeedlySentinelWorker(FeedlySentinelConfig.from_env())

    def run(self) -> None:
        logger.info("Starting Feedly Sentinel Worker")

        failures = 0
        for stream_id in self.feedly_stream_ids:
            try:
                self.process_stream(stream_id)
            except:
                failures += 1
                logger.exception(f"Failed to process stream {stream_id}")

        self.checkpoint.save()
        logger.info("Finished Feedly Sentinel Worker")

        if failures:
            raise Exception(f"Failed to process {failures} streams")

    def process_stream(self, stream_id: str) -> None:
        older_than = time.time()
        logger.info(f"Processing stream {stream_id}")

        newer_than = self.checkpoint[stream_id] or older_than - self.days_to_backfill * 24 * 60 * 60

        indicators = self.build_indicators_from_stream(stream_id, older_than_s=older_than, newer_than_s=newer_than)
        if indicators.empty:
            logger.info(f"No indicators found in stream {stream_id}")
            return
        logger.info(f"Found {len(indicators)} indicators in stream {stream_id}")

        self.sentinel_api_connector.post(indicators.to_dict("records"))
        self.checkpoint[stream_id] = older_than

        logger.info(f"Posted indicators to Sentinel")

    def build_indicators_from_stream(self, stream_id: str, *, older_than_s: float, newer_than_s: float) -> DataFrame:
        return safe_concat(
            [
                build_indicators_from_article(article)
                for article in self.feedly_downloader.download(
                    stream_id, older_than_s=older_than_s, newer_than_s=newer_than_s
                )
            ]
        )


def build_indicators_from_article(article: dict) -> DataFrame:
    df = DataFrame(
        [
            {"type": indicator["type"], "value": indicator["canonical"]}
            for indicator in article.get("indicatorsOfCompromise", {}).get("mentions", [])
        ]
    )
    df["articleTitle"] = article.get("title", "")
    df["articleUrl"] = f"https://feedly.com/i/entry/{article['id']}"
    df["source"] = article.get("origin", {}).get("title", "")
    return df


def safe_concat(dataframes: Iterable[DataFrame]) -> DataFrame:
    dataframes = list(dataframes)
    if not dataframes:
        return DataFrame()
    return concat(dataframes)
