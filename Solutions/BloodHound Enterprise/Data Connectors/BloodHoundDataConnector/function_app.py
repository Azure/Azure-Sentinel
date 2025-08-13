import logging
import azure.functions as func

from audit_logs_collector import bloodhound_audit_logs_collector_main_function
from finding_trends_collector import run_finding_trends_collection_process
from posture_history_collector import run_posture_history_collection_process
from posture_stats_collector import run_posture_stats_collection_process
from attack_path_collector import run_attack_paths_collection_process
from attack_path_timeline_collector import run_attack_paths_timeline_collection_process
from tier_zero_assets_collector import run_tier_zero_assets_collection_process

# Initialize the Azure Functions App
app = func.FunctionApp()


@app.timer_trigger(
    schedule="0 */12 * * *",  # Runs every 12 hours
    arg_name="myTimer",
    run_on_startup=False,
    use_monitor=False,
)
def bloodhound_audit_logs_collector(myTimer: func.TimerRequest) -> None:
    """
    Azure Function Timer Trigger to collect BloodHound audit logs and send them to Azure Monitor.
    """
    logging.info(
        "Python timer trigger function 'bloodhound_audit_logs_collector' executed."
    )

    if myTimer.past_due:
        logging.warning("The timer trigger is past due!")

    bloodhound_audit_logs_collector_main_function()

    logging.info(
        "Python timer trigger function 'bloodhound_audit_logs_collector' finished execution."
    )


@app.timer_trigger(
    schedule="0 */12 * * *",
    arg_name="myTimer",
    run_on_startup=False,
    use_monitor=False,
)
def bloodhound_finding_trends(myTimer: func.TimerRequest) -> None:

    if myTimer.past_due:
        logging.info("The timer is past due!")

    run_finding_trends_collection_process()

    logging.info("Python timer trigger function executed.")


@app.timer_trigger(
    schedule="0 */12 * * *",
    arg_name="myTimer",
    run_on_startup=False,
    use_monitor=False,
)
def bloodhound_posture_history(myTimer: func.TimerRequest) -> None:

    if myTimer.past_due:
        logging.info("The timer is past due!")

    run_posture_history_collection_process()

    logging.info("Python timer trigger function executed.")


@app.timer_trigger(
    schedule="0 */12 * * *",
    arg_name="myTimer",
    run_on_startup=False,
    use_monitor=False,
)
def bloodhound_posture_stats(myTimer: func.TimerRequest) -> None:

    if myTimer.past_due:
        logging.info("The timer is past due!")

    run_posture_stats_collection_process()

    logging.info("Python timer trigger function executed.")


@app.timer_trigger(
    schedule="0 */24 * * *",
    arg_name="myTimer",
    run_on_startup=False,
    use_monitor=False,
)
def bloodhound_attack_paths(myTimer: func.TimerRequest) -> None:

    if myTimer.past_due:
        logging.info("The timer is past due!")

    run_attack_paths_collection_process()

    logging.info("Python timer trigger function executed.")


@app.timer_trigger(
    schedule="0 */24 * * *",
    arg_name="myTimer",
    run_on_startup=False,
    use_monitor=False,
)
def bloodhound_attack_paths_timeline(myTimer: func.TimerRequest) -> None:

    if myTimer.past_due:
        logging.info("The timer is past due!")

    run_attack_paths_timeline_collection_process()

    logging.info("Python timer trigger function executed.")


@app.timer_trigger(
    schedule="0 */12 * * *",
    arg_name="myTimer",
    run_on_startup=False,
    use_monitor=False,
)
def bloodhound_tier_zero_assets(myTimer: func.TimerRequest) -> None:

    if myTimer.past_due:
        logging.info("The timer is past due!")

    run_tier_zero_assets_collection_process()

    logging.info("Python timer trigger function executed.")
