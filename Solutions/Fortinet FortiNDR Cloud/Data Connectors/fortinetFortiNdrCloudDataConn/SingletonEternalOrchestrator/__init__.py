import logging
from datetime import timedelta

import azure.durable_functions as df

def orchestrator_function(context: df.DurableOrchestrationContext):
    args: dict = context.get_input()
    event_types: dict = args.get('event_types')
    interval: int = args.get('interval')
    
    logging.info(
        f'SingletonEternalOrchestrator: event_types: {list(event_types)} instance_id: {context.instance_id}')

    if not event_types:
        return

    # Retrieving full days for each event_type one by one
    failing = args.get('failing', [])
    for event_type, event_type_args in event_types.items():    
        if event_type in failing:
            continue
        attempt = event_type_args.get('attempt', 0)
        remaining_days = event_type_args['days_to_collect']
        if remaining_days > 0 and attempt <= 3:
            try:
                yield context.call_activity('FetchAndSendByDayActivity', {'day': remaining_days, 'event_type': event_type})
                event_types[event_type]['days_to_collect'] = remaining_days-1
                event_type_args['attempt'] = 0
            except Exception as ex:
                logging.error(f'Error when fetching events by day with event_type => {event_type} error => {ex}')
                attempt += 1
                event_types[event_type]['attempt'] = attempt
                if attempt <= 3:
                    logging.info(f"Retrying attempt {attempt}.")
                else:
                    failing.append(event_type)
                    args['failing'] = failing

            # Run the orchastrator new for each day to help avoid timeouts.
            args['event_types'] = event_types
            context.continue_as_new(args)
            return

    # Retrieving piece of a day for each event_type one by one
    retrieved = args.get('retrieved', [])
    for event_type, event_type_args in event_types.items():
        attempt = event_type_args.get('attempt', 0)
        if event_type in failing or event_type in retrieved or attempt > 3:
            continue

        try:
            checkpoint = event_type_args['checkpoint']
            next_checkpoint = yield context.call_activity('FetchAndSendActivity',  {'checkpoint': checkpoint, 'event_type': event_type})
            event_types[event_type]['checkpoint'] = next_checkpoint
            retrieved.append(event_type)
            args['retrieved'] = retrieved
            event_type_args['attempt'] = 0
        except Exception as ex:
            logging.error(f'Error when fetching events by checkpoints with event_type => {event_type} error => {ex}')
            attempt += 1
            event_types[event_type]['attempt'] = attempt
            if attempt <= 3:
                logging.info(f"Retrying attempt {attempt}.")
            else:
                failing.append(event_type)
                args['failing'] = failing

        args['event_types'] = event_types
        context.continue_as_new(args)
        return

    retrieved_events = args.get('retrieved', 'none')
    failed_events = args.get('failing', 'none')
    logging.info(f'Fech events finished. Retrieved Events: {retrieved_events}, Failed Events: {failed_events}')
    args.pop('retrieved', None)
    args.pop('failing', None)
    for event_type_args in event_types.values():
        event_type_args['attempt'] = 0
    args['event_types'] = event_types

    # sleep
    logging.info(
        f'SingletonEternalOrchestrator: Sleeping for {interval} minutes')
    yield context.create_timer(context.current_utc_datetime + timedelta(minutes=interval))
    logging.info(
        f'SingletonEternalOrchestrator: Woke up and will continue as new.')
    context.continue_as_new(args)

main = df.Orchestrator.create(orchestrator_function)
