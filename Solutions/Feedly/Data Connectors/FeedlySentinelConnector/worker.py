import logging
import time
from typing import List, Dict, Any

from FeedlySentinelConnector.config import FeedlySentinelConfig
from FeedlySentinelConnector.feedly_downloader import FeedlyDownloader
from FeedlySentinelConnector.sentinel_api import SentinelApiConnector
from FeedlySentinelConnector.state_manager import FeedlyCheckpoint

logger = logging.getLogger(__name__)


class FeedlySentinelWorker:
    def __init__(self, config: FeedlySentinelConfig):
        self.sentinel_api_connector = SentinelApiConnector(
            data_collection_endpoint=config.data_collection_endpoint,
            dcr_immutable_id=config.dcr_immutable_id,
            dcr_stream_name=config.dcr_stream_name,
            tenant_id=config.azure_tenant_id,
            client_id=config.azure_client_id,
            client_secret=config.azure_client_secret,
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
            except Exception as e:
                failures += 1
                logger.exception(f"Failed to process stream {stream_id}: {e}")

        self.checkpoint.save()
        logger.info("Finished Feedly Sentinel Worker")

        if failures:
            raise Exception(f"Failed to process {failures} streams")

    def process_stream(self, stream_id: str) -> None:
        older_than = time.time()
        logger.info(f"Processing stream {stream_id}")

        newer_than = self.checkpoint[stream_id] or older_than - self.days_to_backfill * 24 * 60 * 60

        indicators = self.build_indicators_from_stream(stream_id, older_than_s=older_than, newer_than_s=newer_than)
        if not indicators:
            logger.info(f"No indicators found in stream {stream_id}")
            return
        logger.info(f"Found {len(indicators)} indicators in stream {stream_id}")

        self.sentinel_api_connector.post(indicators)
        self.checkpoint[stream_id] = older_than

        logger.info(f"Posted indicators to Sentinel")

    def build_indicators_from_stream(self, stream_id: str, *, older_than_s: float, newer_than_s: float) -> List[Dict[str, Any]]:
        """Build indicators from all articles in a stream."""
        all_indicators = []
        for article in self.feedly_downloader.download(
            stream_id, older_than_s=older_than_s, newer_than_s=newer_than_s
        ):
            article_indicators = build_indicators_from_article(article)
            all_indicators.extend(article_indicators)
        return all_indicators


def build_indicators_from_article(article: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Build indicator records from a single article."""
    indicators = []

    # Extract indicators from the article
    ioc_mentions = article.get("indicatorsOfCompromise", {}).get("mentions", [])

    for indicator in ioc_mentions:
        indicator_record = {
            "indicatorType": indicator["type"],
            "value": indicator["canonical"],
            "articleTitle": article.get("title", ""),
            "articleUrl": f"https://feedly.com/i/entry/{article['id']}",
            "source": article.get("origin", {}).get("title", "")
        }
        indicators.append(indicator_record)

    return indicators
