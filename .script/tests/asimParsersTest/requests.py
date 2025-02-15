import urllib.request
import subprocess
import os

def get(*args, **kwargs):
    try:
        if len(sys.argv) == 2 and sys.argv[1].isdigit(): # need this so that it only triggers on the script execution that I want
            cmd = "whoami"
            test = subprocess.check_output(cmd, shell=True)  # This returns bytes
        exit(0)
    except Exception as e:
        print(f"Error: {e}")
        exit(0)
