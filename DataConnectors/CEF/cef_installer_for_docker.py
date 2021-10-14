#! /usr/local/bin/python3
# ----------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ----------------------------------------------------------------------------
# This script is used to install the new CEF agent (AMA) on a linux machine an configure the
# syslog daemon on the linux machine.
# Supported OS:
#   64-bit
#       CentOS 7 and 8
#       Amazon Linux 2017.09
#       Oracle Linux 7
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
# Daemon versions:
#   Syslog-ng: 2.1 - 3.22.1
#   Rsyslog: v8
import subprocess
import time

rsyslog_daemon_name = "rsyslog"
daemon_default_incoming_port = "514"
omsagent_default_incoming_port = "25226"
rsyslog_conf_path = "/etc/rsyslog.conf"
rsyslog_daemon_forwarding_configuration_path = "/etc/rsyslog.d/security-config-omsagent.conf"
rsyslog_module_udp_content = "# provides UDP syslog reception\nmodule(load=\"imudp\")\ninput(type=\"imudp\" port=\"" + daemon_default_incoming_port + "\")\n"
rsyslog_module_tcp_content = "# provides TCP syslog reception\nmodule(load=\"imtcp\")\ninput(type=\"imtcp\" port=\"" + daemon_default_incoming_port + "\")\n"
rsyslog_old_config_udp_content = "# provides UDP syslog reception\n$ModLoad imudp\n$UDPServerRun " + daemon_default_incoming_port + "\n"
rsyslog_old_config_tcp_content = "# provides TCP syslog reception\n$ModLoad imtcp\n$InputTCPServerRun " + daemon_default_incoming_port + "\n"
rsyslog_documantation_path = "https://www.rsyslog.com/doc/master/configuration/actions.html"


def print_error(input_str):
    '''
    Print given text in red color for Error text
    :param input_str:
    '''
    print("\033[1;31;40m" + input_str + "\033[0m")


def print_ok(input_str):
    '''
    Print given text in green color for Ok text
    :param input_str:
    '''
    print("\033[1;32;40m" + input_str + "\033[0m")


def print_notice(input_str):
    '''
    Print given text in white background
    :param input_str:
    '''
    print("\033[0;30;47m" + input_str + "\033[0m")


def print_command_response(input_str):
    '''
    Print given text in green color for Ok text
    :param input_str:
    '''
    print("\033[1;34;40m" + input_str + "\033[0m")


def handle_error(e, error_response_str):
    """
    Gets an error response and prints out an error message using the print_error function
    """
    error_output = e.decode(encoding='UTF-8')
    print_error(error_response_str)
    print_error(error_output)


def process_check(process_name):
    '''
    function who check using the ps -ef command if the 'process_name' is running
    :param process_name:
    :return: True if the process is running else False
    '''
    p1 = subprocess.Popen(["ps", "-ef"], stdout=subprocess.PIPE)
    p2 = subprocess.Popen(["grep", "-i", process_name], stdin=p1.stdout, stdout=subprocess.PIPE)
    p3 = subprocess.Popen(["grep", "-v", "grep"], stdin=p2.stdout, stdout=subprocess.PIPE)
    o, e = p3.communicate()
    tokens = o.decode(encoding='UTF-8').split('\n')
    tokens.remove('')
    return len(tokens)


def set_file_read_permissions(file_path):
    """
    :param  file_path: the path to change the permissions for
    :return: True if successfully added read permissions to other in file otherwise false
    """
    command_tokens = ["sudo", "chmod", "o+r", file_path]
    change_permissions = subprocess.Popen(command_tokens, stdout=subprocess.PIPE)
    time.sleep(3)
    o, e = change_permissions.communicate()
    if e is not None:
        handle_error(e, error_response_str="Error: could not change the permissions for the file -" + file_path)
        return False
    return True


def append_content_to_file(line, file_path, override=False):
    """
    :param1: line- The line to add to the config file
    :param2: file_path- the config file path
    :param3: override- whether to override the file or not- Default equal to false.
    """
    command_tokens = ["sudo", "bash", "-c", "printf '" + "\n" + line + "' >> " + file_path] if not override else ["sudo",
                                                                                                                 "bash",
                                                                                                                 "-c",
                                                                                                                 "printf '" + "\n" + line + "' > " + file_path]
    write_new_content = subprocess.Popen(command_tokens, stdout=subprocess.PIPE)
    time.sleep(3)
    o, e = write_new_content.communicate()
    if e is not None:
        handle_error(e,
                     error_response_str="Error: could not change Rsyslog.conf configuration add line \"" + line + "\" to file -" + rsyslog_conf_path)
        return False
    set_file_read_permissions(file_path)
    return True

def get_rsyslog_daemon_configuration_content(omsagent_incoming_port):
    '''Rsyslog accept every message containing CEF or ASA(for Cisco ASA'''
    rsyslog_daemon_configuration_content = "if $rawmsg contains \"CEF:\" or $rawmsg contains \"ASA-\"" \
                                           " then @@127.0.0.1:" + omsagent_incoming_port
    print("Rsyslog daemon configuration content:")
    content = rsyslog_daemon_configuration_content
    print_command_response(content)
    return content


def get_daemon_configuration_content(daemon_name, omsagent_incoming_port):
    '''
    Return the correct configuration according to the daemon name
    :param daemon_name:
    :param omsagent_incoming_port:
    :return:
    '''
    if daemon_name is rsyslog_daemon_name:
        return get_rsyslog_daemon_configuration_content(omsagent_incoming_port)
    else:
        print_error("Could not create daemon configuration.")
        return False


def create_daemon_forwarding_configuration(omsagent_incoming_port, daemon_configuration_path, daemon_name):
    '''
    Create the daemon configuration to forward messages over TCP to the
    oms agent
    :param omsagent_incoming_port: port for communication between the omsagent the the daemon
    :param daemon_configuration_path: path of the configuration file
    :param daemon_name: name of the daemon
    :return:
    '''
    print("Creating " + daemon_name + " daemon configuration.")
    print("Configuration is changed to forward daemon incoming syslog messages into the omsagent.")
    print("Every command containing \'CEF\' string will be forwarded.")
    print("Path:")
    print_notice(daemon_configuration_path)
    file_content = get_daemon_configuration_content(daemon_name, omsagent_incoming_port)
    append_content_to_file(file_content, daemon_configuration_path, overide=True)
    print_ok("Configuration for " + daemon_name + " daemon was changed successfully.")
    return True


def is_rsyslog_new_configuration():
    """
    Checks if Rsyslog is running the new or old config format
    """
    with open(rsyslog_conf_path, "rt") as fin:
        for line in fin:
            if "module(load=" in line:
                return True
        fin.close()
    return False


def set_rsyslog_new_configuration():
    """
    Sets the Rsyslog configuration to listen on port 514 for incoming requests- For new config format
    """
    with open(rsyslog_conf_path, "rt") as fin:
        with open("tmp.txt", "wt") as fout:
            for line in fin:
                if "imudp" in line or "imtcp" in line:
                    # Load configuration line requires 1 replacement
                    if "load" in line:
                        fout.write(line.replace("#", "", 1))
                    # Port configuration line requires 2 replacements
                    elif "port" in line:
                        fout.write(line.replace("#", "", 2))
                    else:
                        fout.write(line)
                else:
                    fout.write(line)
    command_tokens = ["sudo", "mv", "tmp.txt", rsyslog_conf_path]
    write_new_content = subprocess.Popen(command_tokens, stdout=subprocess.PIPE)
    time.sleep(3)
    o, e = write_new_content.communicate()
    if e is not None:
        handle_error(e,
                     error_response_str="Error: could not change Rsyslog.conf configuration  in -" + rsyslog_conf_path)
        return False
    print_ok("Rsyslog.conf configuration was changed to fit required protocol - " + rsyslog_conf_path)
    return True


def set_rsyslog_old_configuration():
    """
    Sets the Rsyslog configuration to listen on port 514 for incoming requests- For old config format
    """
    add_udp = False
    add_tcp = False
    # Do the configuration lines exist
    is_exist_udp_conf = False
    is_exist_tcp_conf = False
    with open(rsyslog_conf_path, "rt") as fin:
        for line in fin:
            if "imudp" in line or "UDPServerRun" in line:
                is_exist_udp_conf = True
                add_udp = True if "#" in line else False
            elif "imtcp" in line or "InputTCPServerRun" in line:
                is_exist_tcp_conf = True
                add_tcp = True if "#" in line else False
        fin.close()
    if add_udp or not is_exist_udp_conf:
        append_content_to_file(rsyslog_old_config_udp_content, rsyslog_conf_path)
    if add_tcp or not is_exist_tcp_conf:
        append_content_to_file(rsyslog_old_config_tcp_content, rsyslog_conf_path)
    print_ok("Rsyslog.conf configuration was changed to fit required protocol - " + rsyslog_conf_path)
    return True


def restart_rsyslog():
    '''
    Restart the Rsyslog daemon for configuration changes to apply
    '''
    print("Restarting rsyslog daemon.")
    command_tokens = ["sudo", "service", "rsyslog", "restart"]
    print_notice(" ".join(command_tokens))
    restart_rsyslog_command = subprocess.Popen(command_tokens, stdout=subprocess.PIPE)
    time.sleep(3)
    o, e = restart_rsyslog_command.communicate()
    if e is not None:
        handle_error(e, error_response_str="Could not restart rsyslog daemon")
        return False
    print_ok("Rsyslog daemon restarted successfully")
    return True


def set_rsyslog_configuration():
    '''
    Set the configuration for rsyslog
    we support from version 7 and above
    '''
    if is_rsyslog_new_configuration():
        set_rsyslog_new_configuration()
    else:
        set_rsyslog_old_configuration()


def is_rsyslog():
    '''
    Returns True if the daemon is 'Rsyslog'
    '''
    # Meaning ps -ef | grep "daemon name" has returned more then the grep result
    return process_check(rsyslog_daemon_name) > 0


def main():
    omsagent_incoming_port = omsagent_default_incoming_port
    if is_rsyslog():
        print("Located rsyslog daemon running on the machine")
        create_daemon_forwarding_configuration(omsagent_incoming_port=omsagent_incoming_port,
                                               daemon_configuration_path=rsyslog_daemon_forwarding_configuration_path,
                                               daemon_name=rsyslog_daemon_name)
        set_rsyslog_configuration()
        restart_rsyslog()
    else:
        print_error("No Rsyslog daemon found")
    print_ok("Installation completed")


main()
