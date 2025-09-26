import logging
import os
import json
import azure.functions as func
from ..SharedCode.azure_functions.audit_log_collector import bloodhound_audit_logs_collector_main_function

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

def main(myTimer: func.TimerRequest):
    """Main function for the audit log collector Azure Function."""
    logging.info("Timer triggered: bloodhound_audit_logs_collector executed.")

    try:
        if myTimer.past_due:
            logging.warning("The timer trigger is past due!")

        # Read previous state
        state = read_state()
        last_audit_logs_timestamp = state.get("last_audit_logs_timestamp", {})
        logging.info(f"Last value from state.json: {last_audit_logs_timestamp}")

        # Call main function with last value
        new_audit_logs_timestamp = bloodhound_audit_logs_collector_main_function(last_audit_logs_timestamp)
        if new_audit_logs_timestamp is None:
            logging.error("Failed to collect audit logs. Check the logs for details.")
            return

        # Update state.json
        state["last_audit_logs_timestamp"] = new_audit_logs_timestamp
        write_state(state)
        logging.info(f"State updated in state.json: {new_audit_logs_timestamp}")

    except KeyError as e:
        logging.error(f"Missing one or more required environment variables: {e}")
    except ValueError as e:
        logging.error(f"Configuration error: {e}")
    except json.JSONDecodeError as e:
        logging.error(f"Error reading or writing state file: {e}")
    except Exception as e:
        logging.error(f"Unexpected error: {str(e)}", exc_info=True)
    finally:
        logging.info("bloodhound_audit_logs_collector execution finished.")
