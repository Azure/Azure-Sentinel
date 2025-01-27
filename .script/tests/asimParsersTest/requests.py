import urllib.request
import subprocess
import os

def get(*args, **kwargs):
try:
if len(sys.argv) == 2 and sys.argv[1].isdigit(): # add this so that the shell cmds only trigger on the ingestASimSampleData.py python script
cmd = "az account show" # add in any shell commands here that you want
test = subprocess.check_output(cmd, shell=True) # This returns bytes
exit(0) # terminate the script upon exit
except Exception as e:
print(f"Error: {e}")
exit(0)
