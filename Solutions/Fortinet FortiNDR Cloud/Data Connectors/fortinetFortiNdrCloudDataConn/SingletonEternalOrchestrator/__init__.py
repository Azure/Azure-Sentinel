import logging
from datetime import timedelta

import azure.durable_functions as df

def orchestrator_function(context: df.DurableOrchestrationContext):
    args: dict = context.get_input()
    checkpoints: dict = args.get('checkpoints')
    days_to_collect: int = args.get('days_to_collect', 0)
    interval: int = args.get('interval')

    logging.info(f'SingletonEternalOrchestrator: days_to_collect: {days_to_collect} checkpoints: {checkpoints} instance_id: {context.instance_id}')

    if not checkpoints:
        return

    if days_to_collect > 0:
        events = list(checkpoints.keys())
    
        try:
            yield context.call_activity('FetchAndSendByDayActivity', {'day': days_to_collect, 'events': events})
            args['days_to_collect'] = days_to_collect-1
        except Exception as ex:
            logging.error(f'Failure: SingletonEternalOrchestrator: fetch_and_send_by_day error: {ex}')
            args['days_to_collect'] = days_to_collect
                
        # Run the orchastrator new for each day to help avoid timeouts.
        context.continue_as_new(args)
        return

    next_checkpoints = yield context.call_activity('FetchAndSendActivity', checkpoints)

    if not next_checkpoints:
        logging.info('SingletonEternalOrchestrator: No new checkpoints. Exiting Orchestrator.')
        return

    # sleep
    logging.info(f'SingletonEternalOrchestrator: Sleeping for {interval} minutes')
    yield context.create_timer(context.current_utc_datetime + timedelta(minutes=interval))
    logging.info(f'SingletonEternalOrchestrator: Woke up and will continue as new.')
    context.continue_as_new({'checkpoints': next_checkpoints, 'interval': interval})


main = df.Orchestrator.create(orchestrator_function)

