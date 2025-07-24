import azure.durable_functions as df
import logging


def entity_function(context: df.DurableEntityContext):
    state = context.get_state(lambda: {
        "last_connection_time": 0,
        "last_incident_time": 0
    })
    operation = context.operation_name
    input_data = context.get_input()
    if operation == "set":
        date_type = input_data.get("type")
        new_timestamp_str = input_data.get("time")
        if date_type in state:
            state[date_type] = new_timestamp_str
            logging.info(f"The Entity Function is being updated with {date_type}: {new_timestamp_str}")
        else:
            logging.error(f"Invalid date type: {date_type}")

    elif operation == "reset":
        state = {"threats_date": 0, "cases_date": 0}

    elif operation == "get":
        date_type = input_data.get("type")
        if date_type in state:
            context.set_result(state[date_type])
        else:
            logging.error(f"Invalid date type: {date_type}")
            context.set_result(None)

    context.set_state(state)


main = df.Entity.create(entity_function)
