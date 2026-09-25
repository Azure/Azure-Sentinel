import json
import logging
import os
import sys
from pathlib import Path

import azure.functions as func


APP_ROOT = Path(__file__).resolve().parent
APP_ROOT_STRING = str(APP_ROOT)
if APP_ROOT_STRING in sys.path:
    sys.path.remove(APP_ROOT_STRING)
sys.path.insert(0, APP_ROOT_STRING)

from config.settings import ConfigError, load_settings
from services.processor import process_enabled_feeds


app = func.FunctionApp()

# Every feed WhoisFreaks offers that this connector knows how to
# toggle. Add a name here (and a matching entry in config/feeds.py
# plus a normalizer in services/normalizer.py) when you extend to a
# new feed. Each one gets its own on/off App Setting so a customer
# can independently enable only the feeds included in their
# WhoisFreaks subscription.
STREAM_NAMES = (
    "malware",
    "phishing",
    "spam",
    "nrd_gtld_with_whois",
    "nrd_cctld_with_whois",
    "nrd_gtld_without_whois",
    "nrd_cctld_without_whois",
)


def get_enabled_feed_names() -> list[str]:
    enabled_feeds = []

    for stream_name in STREAM_NAMES:
        setting_name = f"WHOISFREAKS_FEED_{stream_name.upper()}_ENABLED"
        enabled = os.getenv(setting_name, "false").lower() == "true"

        if enabled:
            enabled_feeds.append(stream_name)

    return enabled_feeds


def _run_ingestion() -> dict:
    try:
        settings = load_settings()
    except ConfigError as exc:
        msg = f"WhoisFreaks connector missing configuration: {exc}"
        logging.exception(msg)
        return {"status": "error", "message": msg}

    # API key is collected from the end-user at Content Hub installation
    # time (createUiDefinition). Allow empty key only so a developer can
    # deploy / start the Function App for infrastructure testing without
    # a real WhoisFreaks subscription key.
    if not settings.api_key:
        msg = (
            "WHOISFREAKS_API_KEY is not set. "
            "Supply the key during Content Hub installation (or set the "
            "Function App application setting) before enabling feeds."
        )
        logging.warning(msg)
        return {"status": "warning", "message": msg}

    enabled_feeds = get_enabled_feed_names()
    logging.info("Enabled WhoisFreaks feeds: %s", enabled_feeds)

    if not enabled_feeds:
        msg = "No WhoisFreaks feeds are enabled. Nothing to process."
        logging.warning(msg)
        return {"status": "warning", "message": msg}

    process_enabled_feeds(
        api_key=settings.api_key,
        enabled_feed_names=enabled_feeds,
        storage_account_name=settings.checkpoint_storage_account,
        dcr_ingestion_endpoint=settings.dcr_ingestion_endpoint,
        dcr_immutable_id=settings.dcr_immutable_id,
    )
    return {"status": "success", "enabled_feeds": enabled_feeds}


@app.timer_trigger(
    schedule="0 0 0 * * *",
    arg_name="myTimer",
    run_on_startup=False,
    use_monitor=True,
)
def WhoisFreaksTimer(myTimer: func.TimerRequest) -> None:
    if myTimer.past_due:
        logging.warning("WhoisFreaks timer is past due!")

    result = _run_ingestion()
    # Surface config / no-feeds / missing-key as failures so App Insights
    # and Azure Monitor alerts treat the run as failed instead of green.
    if result.get("status") != "success":
        raise RuntimeError(
            f"WhoisFreaks timer ingestion did not succeed: {result}"
        )


@app.route(route="run", methods=["GET", "POST"], auth_level=func.AuthLevel.FUNCTION)
def WhoisFreaksManualTrigger(req: func.HttpRequest) -> func.HttpResponse:
    logging.info("WhoisFreaksManualTrigger invoked.")
    try:
        result = _run_ingestion()
        status_code = 200 if result.get("status") == "success" else 400
        return func.HttpResponse(
            body=json.dumps(result),
            status_code=status_code,
            mimetype="application/json",
        )
    except Exception as exc:
        logging.exception("WhoisFreaksManualTrigger failed.")
        return func.HttpResponse(
            body=json.dumps({"status": "error", "message": str(exc)}),
            status_code=500,
            mimetype="application/json",
        )
