import azure.durable_functions as df
import datetime

min_time = "2021-01-01T00:00:00Z"

def entity_function(context: df.DurableEntityContext):
    current_datetime_str = context.get_state(lambda: datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ"))
    operation = context.operation_name
    if operation == "set":
        new_timestamp_str = context.get_input()
        current_datetime_str = new_timestamp_str
    elif operation == "reset":
        current_datetime_str = min_time
    elif operation == "get":
        
        context.set_result(current_datetime_str)
    context.set_state(current_datetime_str)


main = df.Entity.create(entity_function)