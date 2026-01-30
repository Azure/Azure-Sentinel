# How to Run an Azure Function Locally with Python

This guide provides a step-by-step process for setting up your local environment and running an Azure Function written in Python.

### Step 1: Set up the Python Virtual Environment

It is a best practice to use a virtual environment to manage dependencies for your project. This prevents conflicts with other Python projects on your machine.

First, create a new virtual environment:

```
python -m venv .venv
```
<br/>

Next, activate the virtual environment. The command depends on your operating system:

**Windows:**
```
.venv\\Scripts\\activate  
```
<br/>


### Step 2: Install Project Dependencies

With the virtual environment active, install all the required Python packages listed in your requirements.txt file.
```
pip install -r requirements.txt  
```
<br/>

### Step 3: Install and Run Azurite (Local Storage Emulator)

Azurite is a local emulator for Azure Storage. This is necessary for functions that use bindings like queues, tables, or blobs.

Install Azurite globally using npm:
```
npm install -g azurite
```  
<br/>

Once installed, start the emulator. It will run in the background.
```
azurite  
```
<br/>

### Step 4: Install Azure Functions Core Tools

The Core Tools provide a local development experience for creating, running, and debugging Azure Functions.

Install version 4 of the Core Tools globally:
```
npm install -g azure-functions-core-tools@4 --unsafe-perm true  
```
<br/>

You can verify the installation by checking the version:
```
func --version  
```
<br/>

### Step 5: Configure Local Settings

Your local settings are stored in a local.settings.json file. This file contains environment variables and connection strings for local development.

Make sure your local.settings.json file is configured correctly to use the local storage emulator.
```
{  
"IsEncrypted": false,  
"Values": {  
"AzureWebJobsStorage": "UseDevelopmentStorage=true",  
"FUNCTIONS_WORKER_RUNTIME": "python"  
}  
}
```
<br/>

### Step 6: Test Functions Individually

If you have multiple functions in your project, it is highly recommended to test and debug them one at a time. This helps isolate issues and simplifies the logs. You can comment out the functions you are not currently testing.

Here is an example of how to comment out all but one of your functions in a file named function_app.py:
```
import logging
import azure.functions as func

from audit_logs_collector import bloodhound_audit_logs_collector_main_function
from finding_trends_collector import run_finding_trends_collection_process
from posture_history_collector import run_posture_history_collection_process
from attack_path_collector import run_attack_paths_collection_process
from attack_path_timeline_collector import run_attack_paths_timeline_collection_process
from tier_zero_assets_collector import run_tier_zero_assets_collection_process

import azure.durable_functions as df

# Initialize the Azure Functions App
app = func.FunctionApp()

@app.entity_trigger(context_name="context")
def simple_entity(context: df.DurableEntityContext):
    state = context.get_state(lambda: None)
    op = context.operation_name
    if op == "set":
        new_value = context.get_input()
        if new_value is None:
            # instead of crashing, just ignore or keep old state
            new_value = state if state is not None else 0
        context.set_state(new_value)
        context.set_result(new_value)

    elif op == "reset":
        context.set_state({})
    elif op == "get":
        context.set_result(state)

# To run this function, uncomment it and comment out the others.
# @app.timer_trigger(
#     schedule="0 */10 * * * *", 
#     arg_name="myTimer",
#     run_on_startup=True,
#     use_monitor=False,
# )
# @app.durable_client_input(client_name="client")
# async def bloodhound_audit_logs_collector(
#     myTimer: func.TimerRequest, client: df.DurableOrchestrationClient
# ) -> None:
#     logging.info("Timer triggered: bloodhound_audit_logs_collector executed.")
# 
#     if myTimer.past_due:
#         logging.warning("The timer trigger is past due!")
# 
#     entity_name = "audit_logs_last_timestamp_durable_audit_2_days_logic_1"
#     entity_id = df.EntityId("simple_entity", entity_name)
# 
#     # Fetch previous value from entity
#     entity_state = await client.read_entity_state(entity_id)
#     last_audit_logs_timestamp = entity_state.entity_state if entity_state.entity_exists else {}
# 
#     logging.info(f"************************************************************************** last_value: {last_audit_logs_timestamp}")
#     # Call main function with last value
#     new_audit_logs_timestamp = bloodhound_audit_logs_collector_main_function(last_audit_logs_timestamp)
#     logging.info(f"************************************************************************** new_value: {new_audit_logs_timestamp}")
# 
#     # Update entity with new value
#     await client.signal_entity(entity_id, "set", new_audit_logs_timestamp)
#     logging.info(f"Entity '{entity_name}' updated with new value: {new_audit_logs_timestamp}")

# To run this function, uncomment it and comment out the others.
@app.timer_trigger(
    schedule="0 */10 * * * *", 
    arg_name="myTimer",
    run_on_startup=True,
    use_monitor=False,
)
@app.durable_client_input(client_name="client")
async def bloodhound_attack_paths_collector(
    myTimer: func.TimerRequest, client: df.DurableOrchestrationClient
) -> None:
    logging.info("Timer triggered: bloodhound_attack_paths_collector executed.")

    if myTimer.past_due:
        logging.warning("The timer trigger is past due!")

    entity_name = "attack_path_last_timestamps_array_durable_2_days_logic_2"
    entity_id = df.EntityId("simple_entity", entity_name)

    # Fetch previous value from entity
    entity_state = await client.read_entity_state(entity_id)
    last_attack_path_timestamps = entity_state.entity_state if entity_state.entity_exists else {}

    logging.info(f"************************************************************************** last_value: {last_attack_path_timestamps}")
    # Call main function with last value
    new_attack_path_timestamps = run_attack_paths_collection_process(last_attack_path_timestamps)
    logging.info(f"************************************************************************** new_value: {new_attack_path_timestamps}")

    # Update entity with new value
    await client.signal_entity(entity_id, "set", new_attack_path_timestamps)
    logging.info(f"Entity '{entity_name}' updated with new value: {new_attack_path_timestamps}")

# To run this function, uncomment it and comment out the others.
# @app.timer_trigger(
#     schedule="0 */10 * * * *", 
#     arg_name="myTimer",
#     run_on_startup=True,
#     use_monitor=False,
# )
# @app.durable_client_input(client_name="client")
# async def bloodhound_posture_history_collector(
#     myTimer: func.TimerRequest, client: df.DurableOrchestrationClient
# ) -> None:
#     logging.info("Timer triggered: bloodhound_posture_history_collector executed.")
# 
#     if myTimer.past_due:
#         logging.warning("The timer trigger is past due!")
# 
#     entity_name = "posture_history_last_timestamps_array_durable_logic_1"
#     entity_id = df.EntityId("simple_entity", entity_name)
# 
#     # Fetch previous value from entity
#     entity_state = await client.read_entity_state(entity_id)
#     last_posture_history_timestamps = entity_state.entity_state if entity_state.entity_exists else {}
# 
#     logging.info(f"************************************************************************** last_value: {last_posture_history_timestamps}")
#     # Call main function with last value
#     new_posture_history_timestamps = run_posture_history_collection_process(last_posture_history_timestamps)
#     logging.info(f"************************************************************************ new_vallue", new_posture_history_timestamps)
# 
#     # Update entity with new value
#     await client.signal_entity(entity_id, "set", new_posture_history_timestamps)
#     logging.info(f"Entity '{entity_name}' updated with new value: {new_posture_history_timestamps}")
# 
# # To run this function, uncomment it and comment out the others.
# @app.timer_trigger(
#     schedule="0 */10 * * * *", 
#     arg_name="myTimer",
#     run_on_startup=True,
#     use_monitor=False,
# )
# @app.durable_client_input(client_name="client")
# async def bloodhound_attack_path_timeline_collector(
#     myTimer: func.TimerRequest, client: df.DurableOrchestrationClient
# ) -> None:
#     logging.info("Timer triggered: bloodhound_attack_path_timeline_collector executed.")
# 
#     if myTimer.past_due:
#         logging.warning("The timer trigger is past due!")
# 
#     entity_name = "attack_path_timeline_timestamps_object_durable_days_logic_1"
#     entity_id = df.EntityId("simple_entity", entity_name)
# 
#     # Fetch previous value from entity
#     entity_state = await client.read_entity_state(entity_id)
#     last_attack_path_timeline_timestamps = entity_state.entity_state if entity_state.entity_exists else {}
# 
#     logging.info(f"************************************************************************** last_value: {last_attack_path_timeline_timestamps}")
#     # Call main function with last value
#     new_attack_path_timeline_timestamps = run_attack_paths_timeline_collection_process(last_attack_path_timeline_timestamps)
#     logging.info(f"************************************************************************** new_value: {new_attack_path_timeline_timestamps}")
# 
#     # Update entity with new value
#     await client.signal_entity(entity_id, "set", new_attack_path_timeline_timestamps)
#     logging.info(f"Entity '{entity_name}' updated with new value: {new_attack_path_timeline_timestamps}")
# 
# # To run this function, uncomment it and comment out the others.
# @app.timer_trigger(
#     schedule="0 */50 * * * *",
#     arg_name="myTimer",
#     run_on_startup=True,
#     use_monitor=False,
# )
# def bloodhound_finding_trends(myTimer: func.TimerRequest) -> None:
# 
#     if myTimer.past_due:
#         logging.info("The timer is past due!")
# 
#     run_finding_trends_collection_process()
# 
#     logging.info("Python timer trigger function executed.")
# 
# 
# # To run this function, uncomment it and comment out the others.
# @app.timer_trigger(
#     schedule="0 */50 * * * *",
#     arg_name="myTimer",
#     run_on_startup=True,
#     use_monitor=False,
# )
# def bloodhound_tier_zero_assets(myTimer: func.TimerRequest) -> None:
# 
#     if myTimer.past_due:
#         logging.info("The timer is past due!")
# 
#     run_tier_zero_assets_collection_process()
# 
#     logging.info("Python timer trigger function executed.")
``` 
<br/>\### Step 7: Run Your Function  
<br/>With all the prerequisites in place, you can now start your Azure Function locally.  
<br/>\`\`\`bash 
``` 
func start  
```
<br/>

### Step 8: Verify Function Execution

After running func start, the terminal will display logs from the Azure Functions host. These logs provide valuable information about which functions are being loaded and executed.

Look for lines similar to the following to confirm that your function is running and being triggered successfully:
```
\[2024-05-15T12:00:00.000Z\] Executing 'bloodhound_attack_paths_collector' (Reason='TimerFired', Id=...)  
\[2024-05-15T12:00:00.000Z\] Timer triggered: bloodhound_attack_paths_collector executed.  
```
The first line indicates the function execution, and the second line is a custom log message you added to your function. You can also monitor your custom logging.info() messages to trace the function's progress and debug issues.