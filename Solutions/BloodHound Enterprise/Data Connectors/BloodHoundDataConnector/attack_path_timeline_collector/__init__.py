import logging
import os
import json
import azure.functions as func

from ..SharedCode.azure_functions.attack_path_timeline_collector import run_attack_paths_timeline_collection_process

# Path to state.json inside the same directory as __init__.py
STATE_FILE = os.path.join(os.path.dirname(__file__), "state.json")

def read_state():
    """
    Read the state from state.json. Return {} if file does not exist or is empty.
    
    Note: This function does not handle exceptions. The caller is responsible for
    catching and logging any errors that occur during file I/O or JSON decoding.
    """
    if not os.path.exists(STATE_FILE):
        with open(STATE_FILE, "w") as f:
            json.dump({}, f)
        return {}

    with open(STATE_FILE, "r") as f:
        content = f.read().strip()
        if not content:
            logging.warning("state.json is empty. Initializing with {}.")
            return {}
        return json.loads(content)

def write_state(state):
    """Write updated state to state.json"""
    with open(STATE_FILE, "w") as f:
        json.dump(state, f)

def main(myTimer: func.TimerRequest) -> None:
    try:
        logging.info("Timer triggered: attack_path_timeline_collector executed.")

        if myTimer.past_due:
            logging.warning("The timer trigger is past due!")

        # Read previous state
        state = read_state()
        last_attack_path_timeline_timestamp = state.get("last_attack_path_timeline_timestamp", {})

        logging.info(f"Last attack path timeline timestamp from state.json: {last_attack_path_timeline_timestamp}")

        # Call main function with last value and capture new timestamp
        new_attack_path_timeline_timestamp = run_attack_paths_timeline_collection_process(last_attack_path_timeline_timestamp)
        
        if new_attack_path_timeline_timestamp:
            # Update state.json only if we got valid results
            state["last_attack_path_timeline_timestamp"] = new_attack_path_timeline_timestamp
            write_state(state)
            logging.info(f"State updated in state.json: {new_attack_path_timeline_timestamp}")
        else:
            logging.warning("No new timestamps were collected. State remains unchanged.")

        logging.info("attack_path_timeline_collector execution finished.")
        
    except KeyError as e:
        logging.error(f"Missing required environment variable: {e}")
        raise
    except Exception as e:
        logging.error(f"Unexpected error in attack_path_timeline_collector: {str(e)}")
        raise
