#! /usr/local/bin/python3
# ----------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ----------------------------------------------------------------------------
# This script is used to install CEF agent on a linux machine an configure the
# syslog daemon on the linux machine.
# Supported OS:
#   64-bit
#       CentOS 6 and 7
#       Amazon Linux 2017.09
#       Oracle Linux 6 and 7
#       Red Hat Enterprise Linux Server 6 and 7
#       Debian GNU/Linux 8 and 9
#       Ubuntu Linux 14.04 LTS, 16.04 LTS and 18.04 LTS
#       SUSE Linux Enterprise Server 12
#   32-bit
#       CentOS 6
#       Oracle Linux 6
#       Red Hat Enterprise Linux Server 6
#       Debian GNU/Linux 8 and 9
#       Ubuntu Linux 14.04 LTS and 16.04 LTS
# For more information please check the OMS-Agent-for-Linux documentation.
#
# Daemon versions:
#   Syslog-ng: 2.1 - 3.22.1
#   Rsyslog: v8
import subprocess
import time
import sys

rsyslog_daemon_name = "rsyslog"
syslog_ng_daemon_name = "syslog-ng"
omsagent_file_name = "onboard_agent.sh"
oms_agent_url = "https://raw.githubusercontent.com/Microsoft/OMS-Agent-for-Linux/master/installer/scripts/" + omsagent_file_name
help_text = "Optional arguments for the python script are:\n\t-T: for TCP\n\t-U: for UDP which is the default value.\n\t-F: for no facility restrictions.\n\t-p: for changing default port from 25226"
omsagent_default_incoming_port = "25226"
daemon_default_incoming_port = "514"
oms_agent_field_mapping_configuration = '/opt/microsoft/omsagent/plugin/filter_syslog_security.rb'
rsyslog_daemon_forwarding_configuration_path = "/etc/rsyslog.d/security-config-omsagent.conf"
syslog_ng_daemon_forwarding_configuration_path = "/etc/syslog-ng/conf.d/security-config-omsagent.conf"
syslog_ng_source_content = "source s_src { udp( port(514)); tcp( port(514));};"
rsyslog_conf_path = "/etc/rsyslog.conf"
syslog_ng_conf_path = "/etc/syslog-ng/syslog-ng.conf"
rsyslog_module_udp_content = "# provides UDP syslog reception\nmodule(load=\"imudp\")\ninput(type=\"imudp\" port=\"" + daemon_default_incoming_port + "\")\n"
rsyslog_module_tcp_content = "# provides TCP syslog reception\nmodule(load=\"imtcp\")\ninput(type=\"imtcp\" port=\"" + daemon_default_incoming_port + "\")\n"
rsyslog_old_config_udp_content = "# provides UDP syslog reception\n$ModLoad imudp\n$UDPServerRun " + daemon_default_incoming_port + "\n"
rsyslog_old_config_tcp_content = "# provides TCP syslog reception\n$ModLoad imtcp\n$InputTCPServerRun " + daemon_default_incoming_port + "\n"
oms_agent_configuration_url = "https://raw.githubusercontent.com/microsoft/OMS-Agent-for-Linux/master/installer/conf/omsagent.d/security_events.conf"




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


def print_command_response(input_str):
    '''
    Print given text in green color for Ok text
    :param input_str:
    '''
    print("\033[1;34;40m" + input_str + "\033[0m")


def download_omsagent():
    '''
    Download omsagent this downloaded file would be installed
    :return: True if downloaded successfully
    '''
    print("Trying to download the omsagent.")
    print_notice("wget " + oms_agent_url)
    download_command = subprocess.Popen(["wget", oms_agent_url], stdout=subprocess.PIPE)
    o, e = download_command.communicate()
    time.sleep(3)
    if e is not None:
        handle_error(e, error_response_str="Error: could not download omsagent.")
        return False
    print_ok("Downloaded omsagent successfully.")
    return True


def handle_error(e, error_response_str):
    error_output = e.decode(encoding='UTF-8')
    print_error(error_response_str)
    print_error(error_output)
    return False


def install_omsagent(workspace_id, primary_key, oms_agent_install_url):
    '''
    Installing the downloaded omsagent
    :param workspace_id:
    :param primary_key:
    :return:
    '''
    print("Installing omsagent")
    command_tokens = ["sh", omsagent_file_name, "-w", workspace_id, "-s", primary_key, "-d", oms_agent_install_url]
    print_notice(" ".join(command_tokens))
    install_omsagent_command = subprocess.Popen(command_tokens, stdout=subprocess.PIPE)
    o, e = install_omsagent_command.communicate()
    time.sleep(3)
    if e is not None:
        handle_error(e, error_response_str="Error: could not install omsagent.")
        return False
    print_ok("Installed omsagent successfully.")
    return True


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


def set_omsagent_configuration(workspace_id, omsagent_incoming_port):
    '''
    Download the omsagent configuration and then change the omsagent incoming port
    if required and change the protocol if required
    :param workspace_id:
    :param omsagent_incoming_port:
    :param tcp:
    :param udp:
    :return:
    '''
    configuration_directory = "/etc/opt/microsoft/omsagent/" + workspace_id + "/conf/omsagent.d/"
    configuration_path = "/etc/opt/microsoft/omsagent/" + workspace_id + "/conf/omsagent.d/security_events.conf"

    print("Creating omsagent configuration to listen to syslog daemon forwarding port - " + omsagent_incoming_port)
    print("Configuration location is - " + configuration_path)
    mkdir_command_tokens = ["sudo", "mkdir", "-p", configuration_directory]
    wget_command_tokens = ["sudo", "wget", "-O", configuration_path, oms_agent_configuration_url]
    print("Download configuration into the correct directory")
    print_notice(" ".join(mkdir_command_tokens))
    print_notice(" ".join(wget_command_tokens))
    time.sleep(3)
    create_omsagent_configuration_directory = subprocess.Popen(mkdir_command_tokens, stdout=subprocess.PIPE)
    set_omsagent_configuration_command = subprocess.Popen(wget_command_tokens, stdout=subprocess.PIPE)
    o, e = create_omsagent_configuration_directory.communicate()
    if e is not None:
        handle_error(e, error_response_str="Error: could not create omsagent configuration directory.")
        return False
    o, e = set_omsagent_configuration_command.communicate()
    if e is not None:
        handle_error(e, error_response_str="Error: could not download omsagent configuration.")
        return False
    print_ok("Configuration for omsagent downloaded successfully.")
    print("Trying to change omsagent configuration")
    if omsagent_incoming_port is not omsagent_default_incoming_port:
        if change_omsagent_configuration_port(omsagent_incoming_port=omsagent_incoming_port, configuration_path=configuration_path):
            print_ok("Incoming port for omsagent was changed to " + omsagent_incoming_port)
        else:
            print_error("Could not change omsagent incoming port")
    if change_omsagent_protocol(configuration_path=configuration_path):
        print_ok("Finished changing omsagent configuration")
        return True
    else:
        print_error("Could not change the omsagent configuration")
        return False


def is_rsyslog_new_configuration():
    with open(rsyslog_conf_path, "rt") as fin:
        for line in fin:
            if "module" in line and "load" in line:
                return True
        fin.close()
    return False


def set_rsyslog_new_configuration():
    with open(rsyslog_conf_path, "rt") as fin:
        with open("tmp.txt", "wt") as fout:
            for line in fin:
                if "imudp" in line or "imtcp" in line:
                    fout.write(line.replace("#", "")) if "#" in line else fout.write(line)
                else:
                    fout.write(line)
    command_tokens = ["sudo", "mv", "tmp.txt", rsyslog_conf_path]
    write_new_content = subprocess.Popen(command_tokens, stdout=subprocess.PIPE)
    time.sleep(3)
    o, e = write_new_content.communicate()
    if e is not None:
        handle_error(e, error_response_str="Error: could not change Rsyslog.conf configuration  in -" + rsyslog_conf_path)
        return False
    print_ok("Rsyslog.conf configuration was changed to fit required protocol - " + rsyslog_conf_path)
    return True


def append_content_to_file(line, file_path, overide = False):
    command_tokens = ["sudo", "bash", "-c", "printf '" + "\n" + line + "' >> " + file_path] if not overide else ["sudo", "bash", "-c", "printf '" + "\n" + line + "' > " + file_path]
    write_new_content = subprocess.Popen(command_tokens, stdout=subprocess.PIPE)
    time.sleep(3)
    o, e = write_new_content.communicate()
    if e is not None:
        handle_error(e, error_response_str="Error: could not change Rsyslog.conf configuration add line \"" + line + "\" to file -" + rsyslog_conf_path)
        return False
    return True


def set_rsyslog_old_configuration():
    add_udp = False
    add_tcp = False
    with open(rsyslog_conf_path, "rt") as fin:
        for line in fin:
            if "imudp" in line or "UDPServerRun" in line:
                add_udp = True if "#" in line else False
            elif "imtcp" in line or "InputTCPServerRun" in line:
                add_tcp = True if "#" in line else False
        fin.close()
    if add_udp is True:
        append_content_to_file(rsyslog_old_config_udp_content, rsyslog_conf_path)
    if add_tcp:
        append_content_to_file(rsyslog_old_config_tcp_content, rsyslog_conf_path)
    print_ok("Rsyslog.conf configuration was changed to fit required protocol - " + rsyslog_conf_path)
    return True


def set_rsyslog_configuration():
    '''
    Set the configuration for rsyslog
    we support from version 7 and above
    :return:
    '''
    if is_rsyslog_new_configuration():
        set_rsyslog_new_configuration()
    else:
        set_rsyslog_old_configuration()


def change_omsagent_protocol(configuration_path):
    '''
    Changing the omsagent protocol, since the protocol type is set on the omsagent
    configuration file
    :param configuration_path:
    '''
    try:
        # if opening this file failed the installation of the oms-agent has failed
        fin = open(configuration_path, "rt")
        with open("tmp.txt", "wt") as fout:
            for line in fin:
                if "protocol_type" in line and "udp" in line:
                    fout.write(line.replace("udp", "tcp"))
                    print_notice("Changing protocol type from udp to tcp in "+configuration_path)
                    print("Line changed: " + line)
                else:
                    fout.write(line)
    except IOError:
        print_error("Oms-agent installation has failed please remove oms-agent and try again.")
        return False
    command_tokens = ["sudo", "mv", "tmp.txt", configuration_path]
    write_new_content = subprocess.Popen(command_tokens, stdout=subprocess.PIPE)
    time.sleep(3)
    o, e = write_new_content.communicate()
    if e is not None:
        handle_error(e, error_response_str="Error: could not change omsagent configuration port in ." + configuration_path)
        return False
    print_ok("Omsagent configuration was changed to fit required protocol - " + configuration_path)
    return True


def change_omsagent_configuration_port(omsagent_incoming_port, configuration_path):
    '''
    Changing the omsagent configuration port if required
    :param omsagent_incoming_port:
    :param configuration_path:
    '''
    with open(configuration_path, "rt") as fin:
        with open("tmp.txt", "wt") as fout:
            for line in fin:
                fout.write(line.replace(omsagent_default_incoming_port, omsagent_incoming_port))
    command_tokens = ["sudo", "mv", "tmp.txt", configuration_path]
    write_new_content = subprocess.Popen(command_tokens, stdout=subprocess.PIPE)
    time.sleep(3)
    o, e = write_new_content.communicate()
    if e is not None:
        handle_error(e, error_response_str="Error: could not change omsagent configuration port in ." + configuration_path)
        return False
    print_ok("Omsagent incoming port was changed in configuration - " + configuration_path)
    return True

def check_syslog_computer_field_mapping(workspace_id):
    '''
    Checking if the OMS agent maps the Computer field correctly:
    :return: True if the mapping configuration is correct, false otherwise
    '''
    grep = subprocess.Popen(["grep", "-i", "'Host' => record\['host'\]",
                             oms_agent_field_mapping_configuration], stdout=subprocess.PIPE)
    o, e = grep.communicate()
    if not o:
        print_warning("Warning: Current content of the omsagent syslog filter mapping configuration doesn't map the"
                      " Computer field from your hostname.\nTo enable the Computer field mapping, please run: \n"
                      "\"sed -i -e \"/'Severity' => tags\[tags.size - 1\]/ a \ \\t  'Host' => record['host']\""
                      " -e \"s/'Severity' => tags\[tags.size - 1\]/&,/\" " + oms_agent_field_mapping_configuration +
                      " && sudo /opt/microsoft/omsagent/bin/service_control restart " + workspace_id + "\"")
        return False
    else:
        print_ok("OMS Agent syslog field mapping is correct \n")
        return True


def restart_rsyslog():
    '''
    Restart the Rsyslog daemon
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
    Restart the syslog-ng daemon
    '''
    print("Restarting syslog-ng daemon.")
    command_tokens = ["sudo", "service", "syslog-ng", "restart"]
    print_notice(" ".join(command_tokens))
    restart_rsyslog_command = subprocess.Popen(command_tokens, stdout=subprocess.PIPE)
    time.sleep(3)
    o, e = restart_rsyslog_command.communicate()
    if e is not None:
        handle_error(e, error_response_str="Could not restart syslog-ng daemon")
        return False
    print_ok("Syslog-ng daemon restarted successfully")
    return True


def restart_omsagent(workspace_id):
    '''
    Restart the omsagent
    :param workspace_id:
    '''
    print("Trying to restart omsagent")
    command_tokens = ["sudo", "/opt/microsoft/omsagent/bin/service_control", "restart", workspace_id]
    print_notice(" ".join(command_tokens))
    restart_omsagent_command = subprocess.Popen(command_tokens, stdout=subprocess.PIPE)
    time.sleep(3)
    o, e = restart_omsagent_command.communicate()
    if e is not None:
        handle_error(e, error_response_str="Error: could not restart omsagent")
        return False
    print_ok("Omsagent restarted successfully")
    return True


def get_daemon_configuration_content(daemon_name, omsagent_incoming_port):
    '''
    Return the correct configuration according to the daemon name
    :param daemon_name:
    :param omsagent_incoming_port:
    :return:
    '''
    if daemon_name is rsyslog_daemon_name:
        return get_rsyslog_daemon_configuration_content(omsagent_incoming_port)
    elif daemon_name is syslog_ng_daemon_name:
        return get_syslog_ng_damon_configuration_content(omsagent_incoming_port)
    else:
        print_error("Could not create daemon configuration.")
        return False


def get_rsyslog_daemon_configuration_content(omsagent_incoming_port):
    '''Rsyslog accept every message containing CEF or ASA(for Cisco ASA'''
    rsyslog_daemon_configuration_content = "if $rawmsg contains \"CEF:\" or $rawmsg contains \"ASA-\"" \
                                           " then @@127.0.0.1:"+ omsagent_incoming_port
    print("Rsyslog daemon configuration content:")
    content = rsyslog_daemon_configuration_content
    print_command_response(content)
    return content


def get_syslog_ng_damon_configuration_content(omsagent_incoming_port):
    # we can sepcify the part searched with MESSAGE or MSGHDR (for the header) "filter f_oms_filter {match(\"CEF\" value(\"MESSAGE\"));};\n"
    oms_filter = "filter f_oms_filter {match(\"CEF\|ASA\" ) ;};"
    oms_destination = "destination oms_destination {tcp(\"127.0.0.1\" port(" + omsagent_incoming_port + "));};\n"
    log = "log {source(s_src);filter(f_oms_filter);destination(oms_destination);};\n"
    content = oms_filter + oms_destination + log
    print("Syslog-ng configuration for forwarding CEF messages to omsagent content is:")
    print_command_response(content)
    return content


def is_rsyslog():
    '''
    Returns True if the daemon is 'Rsyslog'
    '''
    # Meaning ps -ef | grep "daemon name" has returned more then the grep result
    return process_check(rsyslog_daemon_name) > 0


def is_syslog_ng():
    '''
    Returns True if the daemon is 'Syslogng'
    '''
    # Meaning ps -ef | grep "daemon name" has returned more then the grep result
    return process_check(syslog_ng_daemon_name) > 0


def set_syslog_ng_configuration():
    '''
    syslog ng have a default configuration which enables the incoming ports and define
    the source pipe to the daemon this will verify it is configured correctly
    :return:
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
                elif comment_line is True and "#" not in line and ("source" in line or "destination" in line or "filter" in line or "log" in line):
                    # stop commenting out
                    comment_line = False
                # write line correctly
                fout.write(line if not comment_line else ("#" + line))
    command_tokens = ["sudo", "mv", "tmp.txt", syslog_ng_conf_path]
    write_new_content = subprocess.Popen(command_tokens, stdout=subprocess.PIPE)
    time.sleep(3)
    o, e = write_new_content.communicate()
    if e is not None:
        handle_error(e, error_response_str="Error: could not change Rsyslog.conf configuration  in -" + syslog_ng_conf_path)
        return False
    if not snet_found:
        append_content_to_file(line=syslog_ng_source_content, file_path=syslog_ng_conf_path)
    print_ok("Rsyslog.conf configuration was changed to fit required protocol - " + syslog_ng_conf_path)
    return True


def main():
    omsagent_incoming_port = omsagent_default_incoming_port
    port_argument = False
    oms_agent_install_url = "opinsights.azure.com"
    if len(sys.argv) < 3:
        print_error("Error: The installation script is expecting 2 arguments:")
        print_error("\t1) workspace id")
        print_error("\t2) primary key")
        return
    else:
        workspace_id = sys.argv[1]
        primary_key = sys.argv[2]
        print("Workspace ID: " + workspace_id)
        print("Primary key: " + primary_key)
        if len(sys.argv) > 3:
            for index in range(3, len(sys.argv)):
                if "-FF" in sys.argv[index]:
                    oms_agent_install_url = "opinsights.azure.us"
                elif "-p" in sys.argv[index]:
                    port_argument = True
                elif port_argument:
                    omsagent_incoming_port = sys.argv[index]
                    print_notice("Notice: omsagent incoming port was changed to " + sys.argv[index])
                    port_argument = False
                elif "-help" in sys.argv[index]:
                    print(help_text)
                    return
    if download_omsagent() and install_omsagent(workspace_id=workspace_id, primary_key=primary_key, oms_agent_install_url=oms_agent_install_url):
        # if setting oms agent configuration has failed we need to stop the script
        if not set_omsagent_configuration(workspace_id=workspace_id, omsagent_incoming_port=omsagent_incoming_port):
            return
    if is_rsyslog():
        print("Located rsyslog daemon running on the machine")
        create_daemon_forwarding_configuration(omsagent_incoming_port=omsagent_incoming_port,
                                               daemon_configuration_path=rsyslog_daemon_forwarding_configuration_path,
                                               daemon_name=rsyslog_daemon_name)
        set_rsyslog_configuration()
        restart_rsyslog()
    elif is_syslog_ng():
        print("Located syslog-ng daemon running on the machine")
        create_daemon_forwarding_configuration(omsagent_incoming_port=omsagent_incoming_port,
                                               daemon_configuration_path=syslog_ng_daemon_forwarding_configuration_path,
                                               daemon_name=syslog_ng_daemon_name)
        set_syslog_ng_configuration()
        restart_syslog_ng()
    restart_omsagent(workspace_id=workspace_id)
    check_syslog_computer_field_mapping(workspace_id=workspace_id)
    print_ok("Installation completed")


main()
