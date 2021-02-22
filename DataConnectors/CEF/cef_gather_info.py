# ----------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ----------------------------------------------------------------------------
# This script is used to install CEF agent on a linux machine an configure the
# syslog daemon on the linux machine.
# Supported OS:
#   64-bit
#       CentOS 7 and 8
#       Amazon Linux 2017.09
#       Oracle Linux 7
#       Red Hat Enterprise Linux Server 7 and 8
#       Debian GNU/Linux 8 and 9
#       Ubuntu Linux 14.04 LTS, 16.04 LTS and 18.04 LTS
#       SUSE Linux Enterprise Server 12, 15
#   32-bit
#       CentOS 7 and 8
#       Oracle Linux 7
#       Red Hat Enterprise Linux Server 7 and 8
#       Debian GNU/Linux 8 and 9
#       Ubuntu Linux 14.04 LTS and 16.04 LTS
# For more information please check the OMS-Agent-for-Linux documentation.
#

import time
import subprocess


class SystemInfo:
    def __init__(self, command, command_output="No output received"):
        self.command = command
        self.command_output = command_output

    def __repr__(self):
        delimiter = "\n-----------------------------------\n"
        return str(
            delimiter + "command: " + self.command + '\n' + "output: " + self.command_output + delimiter)


script_version = '1.0'
output_file_path = '/tmp/cef_get_info'

basic_command_dict = {
    "script_version": "echo {}".format(script_version),
    "date": "sudo date",
    "netstat": "sudo netstat -lnpvt",
    "df": "sudo df -h",
    "free": "sudo free -m",
    "iptables": "sudo iptables -vnL --line",
    "selinux": "sudo cat /etc/selinux/config",
    "os_version": "sudo cat /etc/issue",
    "python_version": "sudo python -V",
    "ram_stats": "sudo cat /proc/meminfo",
    "cron_jobs": "sudo crontab -l",
    "wd_list": "sudo ls -l .",
    "internet_connection": "sudo curl -D - http://google.com",
    "sudoers_list": "sudo cat /etc/sudoers",
    "rotation_configuration": "sudo cat /etc/logrotate.conf",
    "rsyslog_conf": "sudo cat /etc/rsyslog.conf",
    "rsyslog_dir": "sudo ls -l /etc/rsyslog.d/",
    "rsyslog_dir_content": "sudo find /etc/rsyslog.d/ -type f -exec cat {} \;",
    "syslog_ng_conf": "sudo cat /etc/syslog-ng/syslog-ng.conf",
    "syslog_ng_dir": "sudo ls -l /etc/syslog-ng/conf.d/",
    "syslog_ng_dir_content": "find /etc/syslog-ng/conf.d/ -type f -exec cat {} \;",
    "agent_log_snip": "sudo tail -15 /var/opt/microsoft/omsagent/log/omsagent.log",
    "agent_config_dir": "sudo ls -lR /etc/opt/microsoft/omsagent/",
    "agent_cef_config": "sudo cat /etc/opt/microsoft/omsagent/conf/omsagent.d/security_events.conf",
    "tcpdump": "sudo timeout 2 tcpdump -A -ni any port 25226 -vv"
}

# command with a pipe are considered special commands
advanced_command_dict = {
    "top_processes": ["sudo top -bcn1 -w512", "head -n 20"],
    "omsagent_process": ["sudo ps -aux", "grep omsagent"]
}


def print_notice(input_str):
    '''
    Print given text in white background
    :param input_str:
    '''
    print("\033[0;30;47m" + input_str + "\033[0m")


def append_content_to_file(command_object, file_path=output_file_path):
    """

    :param command_object: consists of the name and the output
    :param file_path: a file to share the commands outputs
    """
    output = repr(command_object).replace('%', '%%')
    command_tokens = ["sudo", "bash", "-c", "printf '" + "\n" + output + "' >> " + file_path]
    try:
        write_new_content = subprocess.Popen(command_tokens, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        write_new_content.communicate()
    except Exception:
        print(str(command_object.command) + "was not documented successfully")


def run_command(command):
    """

    :param command: the key value pair from the command dict
    :return: a command object consisting of a name and an output
    """
    command_to_run = subprocess.Popen(basic_command_dict[command].split(' '), stdout=subprocess.PIPE,
                                      stderr=subprocess.STDOUT)
    try:
        o, e = command_to_run.communicate()
    except Exception:
        print(basic_command_dict[command] + "failed to run")
    o = o.decode(encoding='UTF-8')
    command_object = SystemInfo(command, o)
    return command_object


def run_special_command(command):
    """

    :param command: the key value pair from the special command dict
    :return: a command object consisting of a name and an output
    """
    first_command = subprocess.Popen(advanced_command_dict[command][0].split(' '), stdout=subprocess.PIPE,
                                     stderr=subprocess.STDOUT)
    second_command = subprocess.Popen(advanced_command_dict[command][1].split(' '), stdin=first_command.stdout,
                                      stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    try:
        o, e = second_command.communicate()
    except Exception:
        print(command + "command failed to run")
    o = o.decode(encoding='UTF-8')
    command_object = SystemInfo(command, o)
    return command_object


def clean_up(path=output_file_path):
    """
    :param path: A path to delete
    """
    clean_up_command = subprocess.Popen(['rm', path, '2>', '/dev/null'],
                                        stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    try:
        o, e = clean_up_command.communicate()
    except Exception:
        print("Clean up command failed to run")


def main():
    print_notice("Note this script should be run in elevated privileges")
    print("Beginning to collect server data")
    clean_up()
    for command in basic_command_dict.keys():
        command_object = run_command(command)
        append_content_to_file(command_object)
        time.sleep(1)

    for command in advanced_command_dict.keys():
        command_object = run_special_command(command)
        append_content_to_file(command_object)
        time.sleep(1)
    print_notice(
        "Data collection complete. Please provide CSS with the content of the file {}".format(output_file_path))


if __name__ == '__main__':
    main()
