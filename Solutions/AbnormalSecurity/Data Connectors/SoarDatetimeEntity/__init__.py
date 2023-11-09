import azure.durable_functions as df
import datetime
import logging

min_time = "2023-10-01T00:00:00Z"

def entity_function(context: df.DurableEntityContext):

    state = context.get_state(lambda: {
        "threats_date": datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ"),
        "cases_date": datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
    })

    operation = context.operation_name
    input_data = context.get_input()
    
    logging.info(f"The operation is {operation} and current state is {state}")
    
    if operation == "set":
        date_type = input_data.get("type")  
        new_timestamp_str = input_data.get("date")
        if date_type in state:
            state[date_type] = new_timestamp_str
            logging.info(f"The Entity Function is being updated with this date for {date_type}: {new_timestamp_str}")
        else:
            logging.error(f"Invalid date type: {date_type}")

    elif operation == "reset":
       state = {"threats_date": min_time, "cases_date": min_time}
       
    elif operation == "get":
        logging.info(f"input data {input_data}")
        date_type = input_data.get("type")
        logging.info(f"this is the state {state}")
        if date_type in state:
            context.set_result(state[date_type])
        else:
            logging.error(f"Invalid date type: {date_type}")
            context.set_result(None)
            
    context.set_state(state)

main = df.Entity.create(entity_function)
