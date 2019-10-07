import subprocess
import datetime


def executeProcess(cmdLine):
    try:
        rawoutput = subprocess.check_output(
            cmdLine, stderr=subprocess.STDOUT).decode().strip()
    except subprocess.CalledProcessError as exc:
        raise Exception("Failed Executing cmd : {0}\nReturn Code : {1}\nOutput :{2}".format(
            " ".join(exc.cmd), exc.returncode, exc.output))
    return rawoutput


def validatedate(timestr):
    try:
        datetime.datetime.strptime(timestr, '%Y-%m-%d')
    except ValueError:
        raise ValueError("Incorrect date format, should be yyyy-MM-dd")
