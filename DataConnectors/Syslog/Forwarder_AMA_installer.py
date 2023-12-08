#! /usr/local/bin/python3
# ----------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ----------------------------------------------------------------------------
# This script is used to install the AMA on a linux machine and configure the
# Syslog daemon on the linux machine for a data forwarding connector scenario.
# For more information please check the Azure Monitoring Agent documentation.
import subprocess
import time

rsyslog_daemon_name = "rsyslog"
syslog_ng_daemon_name = "syslog-ng"
daemon_default_incoming_port = "514"
syslog_ng_source_content = "source s_src { udp( port(%(port)s)); tcp( port(%(port)s));};" % {'port': daemon_default_incoming_port}
rsyslog_conf_path = "/etc/rsyslog.conf"
syslog_ng_conf_path = "/etc/syslog-ng/syslog-ng.conf"
rsyslog_module_udp_content = "# provides UDP syslog reception\nmodule(load=\"imudp\")\ninput(type=\"imudp\" port=\"" + daemon_default_incoming_port + "\")\n"
rsyslog_module_tcp_content = "# provides TCP syslog reception\nmodule(load=\"imtcp\")\ninput(type=\"imtcp\" port=\"" + daemon_default_incoming_port + "\")\n"
rsyslog_old_config_udp_content = "# provides UDP syslog reception\n$ModLoad imudp\n$UDPServerRun " + daemon_default_incoming_port + "\n"
rsyslog_old_config_tcp_content = "# provides TCP syslog reception\n$ModLoad imtcp\n$InputTCPServerRun " + daemon_default_incoming_port + "\n"
syslog_ng_documantation_path = "https://www.syslog-ng.com/technical-documents/doc/syslog-ng-open-source-edition/3.26/administration-guide/34#TOPIC-1431029"
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


def print_warning(input_str):
    '''
    Print given text in yellow color for warning text
    :param input_str:
    '''
    print("\033[1;33;40m" + input_str + "\033[0m")


def print_notice(input_str):
    '''
    Print given text in white background
    :param input_str:
    '''
    print("\033[0;30;47m" + input_str + "\033[0m")


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


def append_content_to_file(line, file_path, overide=False):
    command_tokens = ["sudo", "bash", "-c", "printf '" + "\n" + line + "' >> " + file_path] if not overide else ["sudo",
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


def restart_syslog_ng():
    '''
    Restart the syslog-ng daemon for configuration changes to apply
    '''
    print("Restarting syslog-ng daemon.")
    command_tokens = ["sudo", "service", "syslog-ng", "restart"]
    print_notice(" ".join(command_tokens))
    restart_syslog_ng_command = subprocess.Popen(command_tokens, stdout=subprocess.PIPE)
    time.sleep(3)
    o, e = restart_syslog_ng_command.communicate()
    if e is not None:
        handle_error(e, error_response_str="Could not restart syslog-ng daemon")
        return False
    print_ok("Syslog-ng daemon restarted successfully")
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


def is_syslog_ng():
    '''
    Returns True if the daemon is 'Syslog-ng'
    '''
    # Meaning ps -ef | grep "daemon name" has returned more then the grep result
    return process_check(syslog_ng_daemon_name) > 0


def set_syslog_ng_configuration():
    '''
    syslog-ng has a default configuration, which enables the incoming ports and defines that
    the source pipe to the daemon will verify it is configured correctly.
    '''
    comment_line = False
    snet_found = False
    with open(syslog_ng_conf_path, "rt") as fin:
        with open("tmp.txt", "wt") as fout:
            for line in fin:
                # fount snet
                if "s_net" in line and not "#":
                    snet_found = True
                # found source that is not s_net - should remove it
                elif "source" in line and "#" not in line and "s_net" not in line and "log" not in line:
                    comment_line = True
                # if starting a new definition stop commenting
                elif comment_line is True and "#" not in line and (
                        "source" in line or "destination" in line or "filter" in line or "log" in line):
                    # stop commenting out
                    comment_line = False
                # write line correctly
                fout.write(line if not comment_line else ("#" + line))
    command_tokens = ["sudo", "mv", "tmp.txt", syslog_ng_conf_path]
    write_new_content = subprocess.Popen(command_tokens, stdout=subprocess.PIPE)
    time.sleep(3)
    o, e = write_new_content.communicate()
    if e is not None:
        handle_error(e,
                     error_response_str="Error: could not change syslog-ng.conf configuration  in -" + syslog_ng_conf_path)
        return False
    if not snet_found:
        append_content_to_file(line=syslog_ng_source_content, file_path=syslog_ng_conf_path)
    print_ok("syslog-ng.conf configuration was changed to fit required protocol - " + syslog_ng_conf_path)
    return True


def print_full_disk_warning():
    '''
    Warn from potential full disk issues that can be caused by the daemon running on the machine.
    The function points the user to the relevant documentation according to his daemon type.
    '''
    warn_message = "\nWarning: please make sure your Syslog daemon configuration does not store unnecessary logs. " \
                   "This may cause a full disk on your machine, which will disrupt the function of the oms agent installed." \
                   " For more information:"

    if process_check(rsyslog_daemon_name):
        if process_check(syslog_ng_daemon_name):
            print_warning(warn_message + '\n' + rsyslog_documantation_path + '\n' + syslog_ng_documantation_path)
        else:
            print_warning(warn_message + '\n' + rsyslog_documantation_path)
    elif process_check(syslog_ng_daemon_name):
        print_warning(warn_message + '\n' + syslog_ng_documantation_path)
    else:
        print_warning("No daemon was found on the machine")


def main():
    if is_rsyslog():
        print("Located rsyslog daemon running on the machine")
        set_rsyslog_configuration()
        restart_rsyslog()
        print_warning("Please note that the installation script opens port 514 to listen to incoming messages in both"
                      " UDP and TCP protocols. To change this setting, refer to the Rsyslog configuration file located at "
                      "'/etc/rsyslog.conf'.")
    elif is_syslog_ng():
        print("Located syslog-ng daemon running on the machine")
        set_syslog_ng_configuration()
        restart_syslog_ng()
        print_warning("Please note that the installation script opens port 514 to listen to incoming messages in both"
                      " UDP and TCP protocols. To change this setting, refer to the Syslog-ng configuration file located at"
                      " '/etc/syslog-ng/syslog-ng.conf'.")
    else:
        print_error(
            "Could not detect a running Syslog daemon on the machine, aborting installation. Please make sure you have "
            "a running Syslog daemon and rerun this script.")
        exit()
    print_full_disk_warning()
    print_ok("Installation completed successfully")



main()
