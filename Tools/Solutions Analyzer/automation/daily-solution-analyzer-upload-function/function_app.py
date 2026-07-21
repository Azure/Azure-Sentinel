import logging
import os
import subprocess
import sys
from pathlib import Path

import azure.functions as func


app = func.FunctionApp()


def _required_env(name: str) -> str:
    value = os.getenv(name)
    if not value:
        raise ValueError(f"Missing required app setting: {name}")
    return value


@app.timer_trigger(schedule="0 15 2 * * *", arg_name="mytimer", run_on_startup=False, use_monitor=True)
def daily_solution_analyzer_upload(mytimer: func.TimerRequest) -> None:
    """Daily upload of Solution Analyzer CSVs from output branch to ADX/Kusto."""
    if mytimer.past_due:
        logging.warning("Timer trigger was past due")

    cluster_url = _required_env("KUSTO_CLUSTER_URL")
    database = _required_env("KUSTO_DATABASE")
    raw_base_url = _required_env("SA_OUTPUT_RAW_BASE_URL")

    auth_mode = os.getenv("KUSTO_AUTH_MODE", "managed-identity")
    managed_identity_client_id = os.getenv("MANAGED_IDENTITY_CLIENT_ID", "").strip()

    # Function files live under: Tools/Solutions Analyzer/automation/daily-solution-analyzer-upload-function
    # upload_to_kusto.py is two levels up.
    function_dir = Path(__file__).resolve().parent
    uploader = function_dir.parent.parent / "upload_to_kusto.py"

    if not uploader.exists():
        raise FileNotFoundError(f"upload_to_kusto.py not found at {uploader}")

    cmd = [
        sys.executable,
        str(uploader),
        "--cluster",
        cluster_url,
        "--database",
        database,
        "--solution-analyzer",
        "--raw-base-url",
        raw_base_url,
        "--auth-mode",
        auth_mode,
    ]

    if auth_mode == "managed-identity" and managed_identity_client_id:
        cmd.extend(["--managed-identity-client-id", managed_identity_client_id])

    logging.info("Starting daily Solution Analyzer upload")
    logging.info("Uploader path: %s", uploader)
    logging.info("Raw base URL: %s", raw_base_url)

    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        timeout=1800,
    )

    if result.stdout:
        logging.info("Uploader stdout:\n%s", result.stdout)
    if result.stderr:
        logging.warning("Uploader stderr:\n%s", result.stderr)

    if result.returncode != 0:
        raise RuntimeError(f"Uploader exited with code {result.returncode}")

    logging.info("Daily Solution Analyzer upload completed successfully")
