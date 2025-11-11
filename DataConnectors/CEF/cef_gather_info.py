#! /usr/local/bin/python3
# ----------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ----------------------------------------------------------------------------
# This script is used to gather info about the collector machine running the CEF collector
# in order to use it for investigating customer issues.
# Supported OS:
#   64-bit
#       CentOS 7 and 8
#       Amazon Linux 2017.09 and Amazon Linux 2
#       Oracle Linux 7, 8
#       Red Hat Enterprise Linux Server 7 and 8
#       Debian GNU/Linux 8 and 9
#       Ubuntu Linux 14.04 LTS, 16.04 LTS, 18.04 LTS and 20.04 LTS
#       SUSE Linux Enterprise Server 12, 15
#   32-bit
#       CentOS 7 and 8
#       Oracle Linux 7
#       Red Hat Enterprise Linux Server 7 and 8
#       Debian GNU/Linux 8 and 9
#       Ubuntu Linux 14.04 LTS and 16.04 LTS
# For more information please check the OMS-Agent-for-Linux documentation.
#

import subprocess


class SystemInfo:
    def __init__(self, command, command_output="No output received"):
        self.command = command
        self.command_output = command_output

    def __repr__(self):
        delimiter = "\n-----------------------------------\n"
        return str(
            delimiter + "command: " + self.command + '\n' + "output: " + self.command_output + delimiter).replace('%',
                                                                                                                  '%%')


script_version = '1.1'
output_file_path = '/tmp/cef_get_info'

command_dict = {
    "script_version": ["echo {}".format(script_version)],
    "date": ["sudo date"],
    "netstat": ["sudo netstat -lnpvt"],
    "df": ["sudo df -h"],
    "free": ["sudo free -m"],
    "iptables": ["sudo iptables -vnL --line"],
    "selinux": ["sudo cat /etc/selinux/config"],
    "os_version": ["sudo cat /etc/issue"],
    "python_version": ["sudo python -V"],
    "ram_stats": ["sudo cat /proc/meminfo"],
    "cron_jobs": ["sudo crontab -l"],
    "wd_list": ["sudo ls -l ."],
    "internet_connection": ["sudo curl -D - http://google.com"],
    "sudoers_list": ["sudo cat /etc/sudoers"],
    "rotation_configuration": ["sudo cat /etc/logrotate.conf"],
    "rsyslog_conf": ["sudo cat /etc/rsyslog.conf"],
    "rsyslog_dir": ["sudo ls -l /etc/rsyslog.d/"],
    "rsyslog_dir_content": ["sudo find /etc/rsyslog.d/ -type f -exec cat {} ;"],
    "syslog_ng_conf": ["sudo cat /etc/syslog-ng/syslog-ng.conf"],
    "syslog_ng_dir": ["sudo ls -l /etc/syslog-ng/conf.d/"],
    "syslog_ng_dir_content": ["find /etc/syslog-ng/conf.d/ -type f -exec cat {} ;"],
    "agent_log_snip": ["sudo tail -15 /var/opt/microsoft/omsagent/log/omsagent.log"],
    "agent_config_dir": ["sudo ls -lR /etc/opt/microsoft/omsagent/"],
    "agent_cef_config": ["sudo cat /etc/opt/microsoft/omsagent/conf/omsagent.d/security_events.conf"],
    "messages_log_snip": ["sudo tail -15 /var/log/messages"],
    "syslog_log_snip": ["sudo tail -15 /var/log/syslog"],
    "tcpdump": ["sudo timeout 2 tcpdump -A -ni any port 25226 -vv"],
    "top_processes": ["sudo top -bcn1 -w512", "head -n 20"],
    "omsagent_process": ["sudo ps -aux", "grep omsagent"]
}


def print_notice(input_str):
    '''
    Print given text in white background
    :param input_str: the string whose format will be changed.
    '''
    print("\033[0;30;47m" + input_str + "\033[0m")


def append_content_to_file(command_object, file_path=output_file_path):
    """

    :param command_object: consists of the name and the output
    :param file_path: a file to share the commands outputs
    """
    output = repr(command_object)
    cef_get_info_file = open(file_path, 'a')
    try:
        cef_get_info_file.write(output)
    except Exception:
        print(str(command_object.command) + "was not documented successfully")
    cef_get_info_file.close()


def run_command(command):
    """

    :param command: the key from the command dict
    :return: a command object consisting of a name and an output
    """
    if len(command_dict[command]) == 1:
        command_to_run = subprocess.Popen(command_dict[command][0].split(' '), stdout=subprocess.PIPE,
                                          stderr=subprocess.STDOUT)
    # for commands that consist of a single pipe
    else:
        first_command = subprocess.Popen(command_dict[command][0].split(' '), stdout=subprocess.PIPE,
                                         stderr=subprocess.STDOUT)
        command_to_run = subprocess.Popen(command_dict[command][1].split(' '), stdin=first_command.stdout,
                                          stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    try:
        o, e = command_to_run.communicate()
    except Exception:
        pass
    if not isinstance(o, str):
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


def handle_commands(commands=command_dict):
    """
    :param commands: A dictionary of commands to iterate over
    """
    for command in commands.keys():
        command_object = run_command(command)
        append_content_to_file(command_object)


def main():
    print_notice("Note this script should be run in elevated privileges")
    print("Beginning to collect server data- This may take a moment")
    clean_up()
    handle_commands()
    print_notice(
        "Data collection completed successfully. Please provide CSS with the content of the file {}".format(
            output_file_path))


if __name__ == '__main__':
    main()
