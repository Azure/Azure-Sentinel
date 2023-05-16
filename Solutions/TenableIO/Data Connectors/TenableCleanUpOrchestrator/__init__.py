import os
from datetime import timedelta

import azure.functions as func
import azure.durable_functions as df

generate_stats_activity_name = 'TenableGenerateJobStats'
clean_tables_name = 'TenableCleanTables'
cleanup_schedule_minutes = int(os.getenv('TenableCleanupScheduleInMinutes', '10'))

def orchestrator_function(context: df.DurableOrchestrationContext):
    yield context.call_activity(generate_stats_activity_name, '')
    yield context.call_activity(clean_tables_name, '')


    next_check = context.current_utc_datetime + timedelta(minutes=cleanup_schedule_minutes)
    yield context.create_timer(next_check)
    context.continue_as_new(None)

main = df.Orchestrator.create(orchestrator_function)