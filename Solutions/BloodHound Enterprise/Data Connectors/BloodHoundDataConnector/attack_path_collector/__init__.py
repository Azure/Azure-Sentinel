import logging
import os
import json
import azure.functions as func
from azure.core.exceptions import ResourceNotFoundError

from ..SharedCode.azure_functions.attack_path_collector import run_attack_paths_collection_process

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
    """Main function for the attack path collector Azure Function."""
    logging.info("Timer triggered: attack path collector executed.")

    try:
        if myTimer.past_due:
            logging.info('The timer is past due!')

        logging.info("Starting attack path collector function")

        # Read previous state
        state = read_state()
        last_attack_path_timestamp = state.get("last_attack_path_timestamp", {})
        logging.info(f"Last attack path timestamp from state.json: {last_attack_path_timestamp}")

        # Call main function with last value
        new_attack_path_timestamp = run_attack_paths_collection_process(last_attack_path_timestamp)

        # If the function does not return a value, keep the old timestamp
        if new_attack_path_timestamp is None:
            logging.warning("Collection process did not return new timestamps. Keeping old values.")
            new_attack_path_timestamp = last_attack_path_timestamp

        logging.info(f"New attack path timestamp: {new_attack_path_timestamp}")

        # Update state.json
        state["last_attack_path_timestamp"] = new_attack_path_timestamp
        write_state(state)
        logging.info(f"State updated in state.json: {new_attack_path_timestamp}")

    except KeyError as e:
        logging.error(f"Missing one or more required environment variables: {e}")
    except ValueError as e:
        logging.error(f"Configuration error: {e}")
    except json.JSONDecodeError as e:
        logging.error(f"Error reading or writing state file: {e}")
    except Exception as e:
        logging.error(f"Unexpected error: {str(e)}", exc_info=True)
    finally:
        logging.info("Attack path collector execution finished.")
