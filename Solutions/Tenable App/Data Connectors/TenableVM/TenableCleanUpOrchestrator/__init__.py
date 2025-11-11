import os
from datetime import timedelta

import azure.durable_functions as df
import logging

generate_stats_activity_name = "TenableGenerateJobStats"
clean_tables_name = "TenableCleanTables"
cleanup_schedule_minutes = int(os.getenv("TenableCleanupScheduleInMinutes", "10"))
logs_starts_with = "TenableVM"
function_name = "TenableCleanUpOrchestrator"


def orchestrator_function(context: df.DurableOrchestrationContext):
    """
    Orchestrator function to handle Tenable.io cleanup operations.

    This function is responsible for generating statistics and cleaning up any temporary tables
    created during the export process.

    Args:
        context (df.DurableOrchestrationContext): The durable orchestration context.

    Returns:
        None
    """
    logging.info(f"{logs_starts_with} {function_name} function started.")
    yield context.call_activity(generate_stats_activity_name, "")
    yield context.call_activity(clean_tables_name, "")

    next_check = context.current_utc_datetime + timedelta(minutes=cleanup_schedule_minutes)
    yield context.create_timer(next_check)
    yield context.continue_as_new(None)


main = df.Orchestrator.create(orchestrator_function)
