import azure.durable_functions as df
import datetime
import logging

current_time = datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")

def entity_function(context: df.DurableEntityContext):

    state = context.get_state(lambda: {
        "threats_date": current_time,
        "cases_date": current_time  
    })

    operation = context.operation_name
    input_data = context.get_input()
    
    if operation == "set":
        date_type = input_data.get("type")  
        new_timestamp_str = input_data.get("date")
        if date_type in state:
            state[date_type] = new_timestamp_str
            logging.info(f"The Entity Function is being updated with {date_type}: {new_timestamp_str}")
        else:
            logging.error(f"Invalid date type: {date_type}")

    elif operation == "reset":
       state = {"threats_date": current_time, "cases_date": current_time}
       
    elif operation == "get":
        date_type = input_data.get("type")
        if date_type in state:
            context.set_result(state[date_type])
        else:
            logging.error(f"Invalid date type: {date_type}")
            context.set_result(None)
            
    context.set_state(state)

main = df.Entity.create(entity_function)
