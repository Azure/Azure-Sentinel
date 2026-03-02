import logging
import azure.functions as func
from azure.core.exceptions import ResourceNotFoundError

import time

from ..SharedCode.azure_functions.finding_trends_collector import run_finding_trends_collection_process

def main(myTimer: func.TimerRequest) -> None:
    """Main function for the finding trends collector Azure Function."""
    logging.info("Timer triggered: finding trends collector executed.")

    try:
        if myTimer.past_due:
            logging.info('The timer is past due!')

        logging.info("Starting finding trends collector function")
        success = run_finding_trends_collection_process()
        
        if not success:
            logging.error("Finding trends collection process failed. Check the logs for details.")
        else:
            logging.info("Finding trends collection process completed successfully.")

    except KeyError as e:
        logging.error(f"Missing one or more required environment variables: {e}")
    except ValueError as e:
        logging.error(f"Configuration error: {e}")
    except ResourceNotFoundError as e:
        logging.error(f"Azure Key Vault resource not found: {e}")
    except Exception as e:
        logging.error(f"Unexpected error: {str(e)}", exc_info=True)
    finally:
        logging.info("Finding trends collector execution finished.")
