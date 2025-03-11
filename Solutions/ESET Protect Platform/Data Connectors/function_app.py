import logging
import os

import azure.functions as func

app = func.FunctionApp()


@app.timer_trigger(
    schedule=f"0 */{os.getenv('INTERVAL', 5)} * * * *", arg_name="myTimer", run_on_startup=False, use_monitor=False
)
def timer_trigger(myTimer: func.TimerRequest) -> None:
    if myTimer.past_due:
        logging.info("The timer is past due!")

    logging.info("MAIN execution")
    try:
        from integration.main import main

        main()
    except Exception as e:
        logging.error(f"main error: {e}")

    logging.info("Python timer trigger function executed.")
