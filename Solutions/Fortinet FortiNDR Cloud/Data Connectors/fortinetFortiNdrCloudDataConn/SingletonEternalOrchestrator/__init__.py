import logging
from datetime import timedelta

import azure.durable_functions as df
from fnc.utils import str_to_utc_datetime


def orchestrator_function(context: df.DurableOrchestrationContext):
    args: dict = context.get_input()
    event_types: dict = args.get("event_types")
    interval: int = args.get("interval")

    logging.info(
        f"SingletonEternalOrchestrator: event_types: {list(event_types)} instance_id: {context.instance_id}"
    )

    if not event_types:
        return

    failing_history = args.get("failing_history", [])
    retrieved_history = args.get("retrieved_history", [])
    for event_type, event_type_args in event_types.items():
        if event_type in failing_history or event_type in retrieved_history:
            continue
        # Retrieving Detections history by checkpoint
        if event_type == "detections":
            history = event_type_args["history_detections"]
            end_date = str_to_utc_datetime(history.get("end_date_str"))
            checkpoint = str_to_utc_datetime(history.get("checkpoint"))

            if checkpoint < end_date:
                logging.info(f"Start fetching history for {event_type}")
                try:
                    next_checkpoint = yield context.call_activity(
                        "FetchAndSendDetectionsHistory",
                        {"event_type": event_type, "history": history},
                    )

                    history["checkpoint"] = next_checkpoint
                    event_types[event_type]["history_detections"] = history
                    retrieved_history.append(event_type)
                    args["retrieved_history"] = retrieved_history
                except Exception as ex:
                    logging.error(
                        f"Error when fetching Detections history. start_date: {checkpoint}, error: {ex}"
                    )
                    failing_history.append(event_type)
                    args["failing_history"] = failing_history

                args["event_types"] = event_types
                context.continue_as_new(args)
                return
        # Retrieving events history for each event_type hour by hour
        else:
            attempt = event_type_args.get("attempt", 0)
            history = event_type_args["history_events"]
            start_date = str_to_utc_datetime(history["start_date"])
            end_date = str_to_utc_datetime(history["end_date"])
            if start_date < end_date and attempt <= 3:
                logging.info(f"Start fetching history for {event_type}")
                try:
                    next_history = yield context.call_activity(
                        "FetchAndSendEventsHistory",
                        {"history": history, "event_type": event_type},
                    )

                    event_types[event_type]["history_events"] = next_history
                    event_type_args["attempt"] = 0
                    retrieved_history.append(event_type)
                    args["retrieved_history"] = retrieved_history
                except Exception as ex:
                    logging.error(
                        f"Error when fetching events history event_type: {event_type}, start_date: {start_date}, end_date: {end_date} error: {ex}"
                    )
                    attempt += 1
                    event_types[event_type]["attempt"] = attempt
                    if attempt <= 3:
                        logging.info(f"Retrying attempt {attempt}.")
                    else:
                        failing_history.append(event_type)
                        args["failing_history"] = failing_history

                # Run the orchastrator new for each day to help avoid timeouts.
                args["event_types"] = event_types
                context.continue_as_new(args)
                return

    failing = args.get("failing", [])
    retrieved = args.get("retrieved", [])
    for event_type, event_type_args in event_types.items():
        attempt = event_type_args.get("attempt", 0)
        if event_type in failing or event_type in retrieved or attempt > 3:
            continue

        checkpoint = event_type_args["checkpoint"]
        # Retriving piece of a day for detections
        if event_type == "detections":
            logging.info(f"Start fetching most recent data for {event_type}")
            try:
                next_checkpoint = yield context.call_activity(
                    "FetchAndSendDetections",
                    {"event_type": event_type, "checkpoint": checkpoint},
                )
                event_types[event_type]["checkpoint"] = next_checkpoint
                retrieved.append(event_type)
                args["retrieved"] = retrieved
            except Exception as ex:
                logging.error(
                    f"Error when fetching Detections by checkpoints, checkpoint: {checkpoint} error: {ex}"
                )
                failing.append(event_type)
                args["failing"] = failing

            args["event_types"] = event_types
            context.continue_as_new(args)
            return

        # Retrieving piece of a day for each event_type
        else:
            logging.info(f"Start fetching most recent data for {event_type}")
            try:
                next_checkpoint, is_done = yield context.call_activity(
                    "FetchAndSendEvents",
                    {"checkpoint": checkpoint, "event_type": event_type},
                )
                event_types[event_type]["checkpoint"] = next_checkpoint
                if is_done:
                    retrieved.append(event_type)
                    args["retrieved"] = retrieved
                event_type_args["attempt"] = 0
            except Exception as ex:
                logging.error(
                    f"Error when fetching events by checkpoints with event_type: {event_type}, checkpoint: {checkpoint} error: {ex}"
                )
                attempt += 1
                event_types[event_type]["attempt"] = attempt
                if attempt <= 3:
                    logging.info(f"Retrying attempt {attempt}.")
                else:
                    failing.append(event_type)
                    args["failing"] = failing

            args["event_types"] = event_types
            context.continue_as_new(args)
            return

    retrieved_events_history = args.get("retrieved_history", "none")
    retrieved_events = args.get("retrieved", "none")
    failed_events = args.get("failing", "none")
    failed_history = args.get("failing_history", "none")
    logging.info(
        f"Fetch events finished. Retrieved History: {retrieved_events_history}, Retrieved Events: {retrieved_events}, Failed History: {failed_history}, Failed Events: {failed_events}"
    )
    args.pop("retrieved_history", None)
    args.pop("retrieved", None)
    args.pop("failing_history", None)
    args.pop("failing", None)

    for event_type_args in event_types.values():
        event_type_args["attempt"] = 0
    args["event_types"] = event_types

    # sleep
    logging.info(f"SingletonEternalOrchestrator: Sleeping for {interval} minutes")
    yield context.create_timer(
        context.current_utc_datetime + timedelta(minutes=interval)
    )
    logging.info(f"SingletonEternalOrchestrator: Woke up and will continue as new.")
    context.continue_as_new(args)


main = df.Orchestrator.create(orchestrator_function)
