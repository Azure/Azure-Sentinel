import logging
import azure.functions as func
from azure.core.exceptions import ResourceNotFoundError
from ..SharedCode.azure_functions.tier_zero_assets_collector import run_tier_zero_assets_collection_process

def main(myTimer: func.TimerRequest) -> None:
    """Main function for the tier zero assets collector Azure Function."""
    logging.info("Timer triggered: tier zero assets collector executed.")

    try:
        if myTimer.past_due:
            logging.info('The timer is past due!')

        logging.info("Starting tier zero assets collector function")
        success = run_tier_zero_assets_collection_process()
        
        if not success:
            logging.error("Tier zero assets collection process failed. Check the logs for details.")
        else:
            logging.info("Tier zero assets collection process completed successfully.")

    except KeyError as e:
        logging.error(f"Missing one or more required environment variables: {e}")
    except ValueError as e:
        logging.error(f"Configuration error: {e}")
    except ResourceNotFoundError as e:
        logging.error(f"Azure Key Vault resource not found: {e}")
    except Exception as e:
        logging.error(f"Unexpected error: {str(e)}", exc_info=True)
    finally:
        logging.info("Tier zero assets collector execution finished.")
