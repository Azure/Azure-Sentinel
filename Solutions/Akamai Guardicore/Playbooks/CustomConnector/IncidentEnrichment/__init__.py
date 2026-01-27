import datetime
import json
import logging
import azure.durable_functions as df


def orchestrator_function(context: df.DurableOrchestrationContext):
    logging.info('Starting eternal task processor orchestration')

    while True:
        try:
            task_result = yield context.call_activity("GetPendingTask", None)
            if task_result:
                logging.info(f"Found task: {task_result['partition_key']}/{task_result['row_key']}")

                try:
                    yield context.call_activity("ProcessTask", json.dumps(task_result))

                    logging.info(
                        f"Successfully processed task: {task_result['partition_key']}/{task_result['row_key']}")
                    continue

                except Exception as e:
                    logging.error(
                        f"Error processing task {task_result['partition_key']}/{task_result['row_key']}: {str(e)}")
                    yield context.call_activity("MarkTaskFailed", json.dumps(task_result))

                    continue
            else:
                logging.debug("No pending tasks found, waiting 2 minutes")

                next_check = context.current_utc_datetime + datetime.timedelta(minutes=2)
                yield context.create_timer(next_check)

        except Exception as e:
            logging.error(f"Error in task processor orchestration: {str(e)}")

            # Wait 2 minutes before retrying on error
            next_check = context.current_utc_datetime + datetime.timedelta(minutes=2)
            yield context.create_timer(next_check)


main = df.Orchestrator.create(orchestrator_function)
