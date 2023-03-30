# Schedule Library imported
import schedule
import time
from authomizeworker import searchIncident
#######################################
# USER TO CONFIGURE BEFORE STARTING   #
#######################################
# DO NOT SET BELOW 5 MINUTES
############################
NumberOfMinutes = 120
############################
#END OF CONFIGURATION      #
############################
# Functions setup
def heart_beat():
	print("Scheduler is alive and running - Will make contact with your Authomize tenant every", NumberOfMinutes, "minutes. A heart beat is issued every 2 minutes see you then...")

# Task scheduling
# After every 10mins geeks() is called.
schedule.every(2).minutes.do(heart_beat)
schedule.every(NumberOfMinutes).minutes.do(searchIncident)

# After every hour function_call() is called.
# schedule.every(5).seconds.do(function_call)

# Every day at 12am or 00:00 time function_call() is called.
# schedule.every().day.at("00:00").do(function_call)

# After every 5 to 10mins in between run function_call()
# schedule.every(5).to(10).minutes.do(function_call)

# Every monday function_call() is called
# schedule.every().monday.do(function_call)

# Every tuesday at 18:00 function_call() is called
# schedule.every().tuesday.at("18:00").do(function_call)

# Loop so that the scheduling task
# keeps on running all time.
print("The scheduler is set to pull data from your Authomize tenant every", NumberOfMinutes,"minutes." )
while True:

	# Checks whether a scheduled task
	# is pending to run or not
	schedule.run_pending()
	time.sleep(120)