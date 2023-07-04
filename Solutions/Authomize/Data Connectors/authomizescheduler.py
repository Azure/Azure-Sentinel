import schedule
import time
import logging
from authomizeworker import searchIncident

# Configuring logging
logging.basicConfig(filename='scheduler.log', level=logging.INFO, format='%(asctime)s:%(levelname)s:%(message)s')

# Configuration
NumberOfMinutes = 120

if NumberOfMinutes < 5:
    logging.error("NumberOfMinutes should be at least 5")
    exit()

def heart_beat():
    logging.info("Scheduler is alive and running - Will make contact with your Authomize tenant every %d minutes. A heart beat is issued every 2 minutes see you then...", NumberOfMinutes)

# Task scheduling
schedule.every(2).minutes.do(heart_beat)
schedule.every(NumberOfMinutes).minutes.do(searchIncident)

# Informing about the scheduler
logging.info("The scheduler is set to pull data from your Authomize tenant every %d minutes.", NumberOfMinutes)

try:
    # Call the searchIncident function once before entering the scheduling loop
    # This forces the immediate processing of Authomize incidents
    logging.info("The scheduler is starting to try and pull data from Authomize NOW.")
    searchIncident()
    while True:
        # Running scheduled tasks
        schedule.run_pending()
        time.sleep(120)

# Handling Keyboard Interrupt
except KeyboardInterrupt:
    logging.info("Scheduler stopped by user")
except Exception as e:
    logging.error("An error occurred: %s", str(e))