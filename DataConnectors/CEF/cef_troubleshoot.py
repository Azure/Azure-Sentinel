#! /usr/local/bin/python3
# ----------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ----------------------------------------------------------------------------
# This script is used to troubleshoot the process of sending CEF messages to the
# workspace.
# In this script we check the configuration of the daemon and the OMS linux agent.
# We send mock data to validate correctness of the pipeline
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
import sys
import select
import subprocess
import time

daemon_port = "514"
agent_port = "25226"
rsyslog_security_config_omsagent_conf_content_tokens = ["*.", "*", "@127.0.0.1:25226", "CEF", "ASA"]
syslog_ng_security_config_omsagent_conf_content_tokens = ["f_oms_filter", "oms_destination", "port(25226)", "tcp",
                                                          "source", "s_src", "oms_destination"]
oms_agent_configuration_content_tokens = [daemon_port, "127.0.0.1"]
oms_agent_process_name = "opt/microsoft/omsagent"
syslog_log_dir = ["/var/log/syslog", "/var/log/messages"]
firewall_d_exception_configuration_file = "/etc/firewalld/zones/public.xml"
red_hat_rsyslog_security_enhanced_linux_documentation = "https://access.redhat.com/documentation/en-us/red_hat_enterprise_linux/6/html/deployment_guide/s1-configuring_rsyslog_on_a_logging_server"
rsyslog_daemon_forwarding_configuration_path = "/etc/rsyslog.d/security-config-omsagent.conf"
syslog_ng_daemon_forwarding_configuration_path = "/etc/syslog-ng/conf.d/security-config-omsagent.conf"
rsyslog_daemon_forwarding_configuration_dir_path = "/etc/rsyslog.d/"
syslog_ng_daemon_forwarding_configuration_dir_path = "/etc/syslog-ng/conf.d/"
rsyslog_daemon_name = "rsyslog.d"
syslog_ng_default_config_path = "/etc/syslog-ng/syslog-ng.conf"
tcpdump_time_restriction = 60


def print_error(input_str):
    print("\033[1;31;40m" + input_str + "\033[0m")


def print_ok(input_str):
    print("\033[1;32;40m" + input_str + "\033[0m")


def print_warning(input_str):
    print("\033[1;33;40m" + input_str + "\033[0m")


def print_notice(input_str):
    print("\033[0;30;47m" + input_str + "\033[0m")


def print_command_response(input_str):
    print("\033[1;34;40m" + input_str + "\033[0m")


def get_mock_message(index):
    fixed_message = "0|TestCommonEventFormat|MOCK|common=event-format-test|end|TRAFFIC|1|rt=$common=event-formatted-receive_time deviceExternalId=0002D01655 src=1.1.1.1 dst=2.2.2.2 sourceTranslatedAddress=1.1.1.1 destinationTranslatedAddress=3.3.3.3 cs1Label=Rule cs1=CEF_TEST_InternetDNS "
    return fixed_message + "|data" + str(index) + "=example"


def send_cef_message_local(port, amount):
    try:
        for index in range(0, amount):
            message_to_send = get_mock_message(index)
            command_tokens = ["logger", "-p", "local4.warn", "-t", "CEF:", message_to_send, "-P", str(port), "-n",
                              "127.0.0.1"]
            logger = subprocess.Popen(command_tokens, stdout=subprocess.PIPE)
            o, e = logger.communicate()
            if e is not None:
                print_error("Error could not send cef mock message")
        return
    except OSError:
        print_warning(
            "Warning: Could not execute \'logger\' command which is a part of the syslog daemon this means that no mock message was sent to your workspace.")


def check_red_hat_firewall_issue():
    '''
    Checking if a firewall is found on the device if firewall was found,
        trying to see if the agent port was added as exception
            if so restart the firewall
    :return:
    '''
    print_notice("Checking if firewalld is installed.")
    print_notice("systemctl status firewalld")
    firewall_status = subprocess.Popen(["systemctl", "status", "firewalld"], stdout=subprocess.PIPE)
    o, e = firewall_status.communicate()
    if e is not None:
        print_error("Error: could not check CentOS / RHEL 7 firewalld status.")
    else:
        if "running" in str(o):
            print_warning(
                "Warning: you have a firewall running on your linux machine this can prevent communication between the syslog daemon and the omsagent.")
            print("Checking if firewall has exception for omsagent port.[" + agent_port + "]")
            if red_hat_firewall_d_exception_for_omsagent():
                print_ok("Found exception in the firewalld for the omsagent port.[" + agent_port + "]")
                restart_red_hat_firewall_d()
            else:
                print_warning("Warning: no exception found for omsagent in the firewall")
                print_warning(
                    "You can add exception for the agent port[" + agent_port + "] by using the following commands:")
                print_warning("Add exception:")
                print_notice(
                    "sudo firewall-cmd --direct --add-rule ipv4 filter INPUT 0 -p tcp --dport " + agent_port + "  -j ACCEPT")
                print_warning("Validate the exception was added in the configuration:")
                print_notice("sudo firewall-cmd --direct --get-rules ipv4 filter INPUT")
                print_warning("Reload the firewall:")
                print_notice("sudo firewall-cmd --reload")
                print_warning("You can disable your firewall by using this command - not recommended:")
                print_notice("sudo systemctl stop firewalld")


def red_hat_firewall_d_exception_for_omsagent():
    '''
    Check that the firewall_d has an exception for the omsagent
    :return:
    '''
    print("Checking for exception for omsagent")
    print_notice(firewall_d_exception_configuration_file)
    firewall_status = subprocess.Popen(["sudo", "cat", firewall_d_exception_configuration_file], stdout=subprocess.PIPE)
    o, e = firewall_status.communicate()
    if e is not None:
        print_error("Error: could not get /etc/firewalld/zones/public.xml file holding firewall exceptions")
    print_command_response(str(o))
    return agent_port in str(o)


def restart_red_hat_firewall_d():
    '''
    Method for restarting the firewall_d
    :return:
    '''
    print("Trying to restart firewall_d")
    print_notice("sudo firewall-cmd --reload")
    restart = subprocess.Popen(["sudo", "firewall-cmd", "--reload"], stdout=subprocess.PIPE)
    o, e = restart.communicate()
    time.sleep(2)
    if e is not None:
        print_error("Error: could not get /etc/firewalld/zones/public.xml file holding firewall exceptions.")
    else:
        print_ok("Restarted firewalld.")


def security_enhanced_linux_enabled():
    print("Checking if security enhanced linux is enabled")
    print_notice("sestatus")
    command_tokens = ["sudo", "sestatus"]
    sestatus_command = subprocess.Popen(command_tokens, stdout=subprocess.PIPE)
    o, e = sestatus_command.communicate()
    if e is not None:
        print_error("Could not execute \'sestatus\' to check if security enhanced linux is enabled")
    else:
        for line in o.decode('ascii').split('\n'):
            if "SELinux status" in line and "enabled" in line:
                return True
        return False


def security_enhanced_linux():
    if security_enhanced_linux_enabled() is True:
        print_warning(
            "Security enhanced linux is enabled.\nTo use TCP with syslog daemon the omsagent incoming port should be inserted")
        print("Use elevated privileges to perform the following:")
        print("\tTo enable the port")
        print_notice("\tsemanage port -a -t syslogd_port_t -p tcp " + agent_port)
        print("\tTo validate enabled port")
        print_notice("\tsemanage port -l | grep " + agent_port)
        print("\tTo install the policy editor")
        print_notice("\tyum install policycoreutils-python")
        print("For more information: " + red_hat_rsyslog_security_enhanced_linux_documentation)


def rsyslog_get_cef_log_counter():
    '''
    Count using tac and wc -l the amount of CEF messages arrived and see it is in increasing
    count
    :return:
    '''
    print("Validating the CEF\\ASA logs are received and are in the correct format when received by syslog daemon")
    print_notice("sudo tac /var/log/syslog")
    tac = subprocess.Popen(["sudo", "tac", syslog_log_dir[0]], stdout=subprocess.PIPE)
    grep = subprocess.Popen(["grep", "-E", "CEF\|ASA"], stdin=tac.stdout, stdout=subprocess.PIPE)
    count_lines = subprocess.Popen(["wc", "-l"], stdin=grep.stdout, stdout=subprocess.PIPE)
    o, e = count_lines.communicate()
    output = o.decode(encoding='UTF-8')
    if e is None:
        print("Located " + str(output) + " CEF\\ASA messages")
        return int(output)
    elif "No such file or directory" in output:
        print("Validating the CEF\\ASA logs are received and are in the correct format when received by syslog daemon")
        print_notice("sudo tac /var/log/messages")
        tac = subprocess.Popen(["sudo", "tac", syslog_log_dir[1]], stdout=subprocess.PIPE)
        grep = subprocess.Popen(["grep", "-E", "CEF\|ASA"], stdin=tac.stdout, stdout=subprocess.PIPE)
        count_lines = subprocess.Popen(["wc", "-l"], stdin=grep.stdout, stdout=subprocess.PIPE)
        o, e = count_lines.communicate()
        output = o.decode(encoding='UTF-8')
        if e is None:
            print("Located " + str(output) + " CEF messages")
            return int(output)
    print_error("Error: could not find CEF\\ASA logs.")
    print_notice("Notice: execute \"sudo tac /var/log/syslog or /var/log/messages | grep -E \"CEF|ASA\" -m 10\" manually.")
    return 0


def rsyslog_cef_logs_received_in_correct_format():
    print("Fetching CEF messages from daemon files.")
    print("Taking 2 snapshots in 5 seconds diff and compering the amount of CEF messages.")
    print("If found increasing CEF messages daemon is receiving CEF messages.")
    start_amount = rsyslog_get_cef_log_counter()
    time.sleep(5)
    end_amount = rsyslog_get_cef_log_counter()
    if end_amount > start_amount:
        print_ok("Received CEF messages by the daemon")
    else:
        print_warning(
            "Error: no CEF messages received by the daemon.\nPlease validate that you do send CEF messages to agent.")


def handle_tcpdump_line(line, incoming_port, ok_message):
    if "CEF" in line or "ASA" in line:
        print_ok(ok_message)
        print_notice(
            "Notice: To tcp dump manually execute the following command - \'tcpdump -A -ni any port " + incoming_port + " -vv\'")
        time.sleep(1)
        return True
    # Handle command not found
    elif "command not found" in line:
        print_error(
            "Notice that \'tcpdump\' is not installed in your linux machine.\nWe cannot monitor traffic without it.\nPlease install \'tcpdump\'.")
        return False
    else:
        # print the output
        print_command_response(line.rstrip())
        return False


def incoming_logs_validations(incoming_port, ok_message, mock_message=False):
    '''
    Validate that there is incoming traffic of CEF messages to the given port
    :param mock_message: Tells if to mock messages into the tcpdump
    :param mock_messages: Tels if to send mock messages to the pipe to validate it
    :param incoming_port: port to validate
    :param ok_message: message printed if found CEF messages
    :return:
    '''
    start_seconds = int(round(time.time()))
    end_seconds = int(round(time.time()))
    print("This will take " + str(tcpdump_time_restriction) + " seconds.")
    command_tokens = ["sudo", "tcpdump", "-A", "-ni", "any", "port", incoming_port, "-vv"]
    print_notice(" ".join(command_tokens))
    tcp_dump = subprocess.Popen(command_tokens, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    poll_obj = select.poll()
    poll_obj.register(tcp_dump.stdout, select.POLLIN)
    while (end_seconds - start_seconds) < tcpdump_time_restriction:
        if mock_message is True:
            # Sending mock messages
            send_cef_message_local(daemon_port, 1)
        poll_result = poll_obj.poll(0)
        if poll_result:
            line = str(tcp_dump.stdout.readline())
            if handle_tcpdump_line(line, incoming_port, ok_message):
                return True
        end_seconds = int(round(time.time()))
    print_error("Could not locate \"CEF\" message in tcpdump")
    return False


def netstat_open_port(in_port, ok_message, error_message):
    netstat = subprocess.Popen(["sudo", "netstat", "-an"], stdout=subprocess.PIPE)
    print("Incoming port grep: " + in_port)
    grep = subprocess.Popen(["grep", in_port], stdin=netstat.stdout, stdout=subprocess.PIPE)
    o, e = grep.communicate()
    output = o.decode(encoding='UTF-8')
    print(output)
    if e is None and in_port in output:
        print_ok(ok_message)
        return True
    print_error(error_message)
    return False


def check_file_in_directory(file_name, path):
    '''
    Check if the given file is found in the current directory.
    :param path:
    :param file_name:
    :return: return True if it is found elsewhere False
    '''
    current_dir = subprocess.Popen(["ls", "-ltrh", path], stdout=subprocess.PIPE)
    grep = subprocess.Popen(["grep", "-i", file_name], stdin=current_dir.stdout, stdout=subprocess.PIPE)
    o, e = grep.communicate()
    output = o.decode(encoding='UTF-8')
    if e is None and file_name in output:
        return True
    return False


def locate_check(process_name):
    '''
    Check if the process_name is installed using the locate command
    :param process_name:onfiguration under the nam
    :return: True if locate has returned a valid value else False
    '''
    try:
        print("Trying to use the \'locate\' command to locate " + process_name)
        locate = subprocess.Popen(["locate", process_name], stdout=subprocess.PIPE)
        o, e = locate.communicate()
        response = o.decode(encoding='UTF-8')
        if e is not None:
            print_warning("Warning: Could not execute \'locate\' command.")
            print_notice(
                "Notice: To install locate command - \"sudo yum install mlocate[On CentOS/RHEL]\" or \"sudo apt"
                " install mlocate[On Debian/Ubuntu] \"")
        elif response == "":
            print_error("Error: Could not locate \'omsagent\' trying to validate by checking the process.\n")
            return False
        else:
            print_ok("Located \'omsagent\'")
            return True
    except OSError:
        print_warning("Warning: Could not execute \'locate\' command.")
        print_notice("Notice: To install locate command - \"sudo yum install mlocate[On CentOS/RHEL]\" or \"sudo apt"
                     " install mlocate[On Debian/Ubuntu] \"")


def omsagent_process_check(oms_process_name):
    tokens = process_check(oms_process_name)
    if len(tokens) > 1:
        for single_token in tokens:
            if oms_agent_process_name in single_token:
                print_ok("Found omsagent process running on this machine.")
                return True
    print_error("Error: Could not find omsagent process running on this machine.")
    return False


def process_check(process_name):
    '''
    function who check using the ps -ef command if the 'process_name' is running
    :param process_name:
    :return: True if the process is running else False
    '''
    p1 = subprocess.Popen(["ps", "-ef"], stdout=subprocess.PIPE)
    p2 = subprocess.Popen(["grep", "-i", process_name], stdin=p1.stdout, stdout=subprocess.PIPE)
    o, e = p2.communicate()
    tokens = o.decode(encoding='UTF-8').split('\n')
    tokens.remove('')
    return tokens


def check_oms_agent_status():
    '''
        Checking if the OMS agent is installed and running this is done by:
        1. using the locate command if one is installed
        2. using pe -ef - will check if the agent is running

        :return: True if the process is installed and/or running false elsewhere
    '''
    agent_name = "omsagent"
    is_located = locate_check(agent_name)
    is_process_running = process_check(agent_name)

    if not is_located and not is_process_running:
        print_error("Error: Oms agent is not installed or running on this machine")
        return False
    else:
        return True


def file_contains_string(file_tokens, file_path):
    print_notice(file_path)
    content = open(file_path).read()
    print_command_response("Current content of the daemon configuration is:\n" + content)
    return all(check_token(token, content) for token in file_tokens)


def sudo_read_file_contains_string(file_tokens, file_path):
    restart = subprocess.Popen(["sudo", "cat", file_path], stdout=subprocess.PIPE)
    o, e = restart.communicate()
    if e is not None:
        print_error("Error: could not load " + file_path)
        return False
    else:
        content = o.decode(encoding='UTF-8')
        print_command_response("Current content of the daemon configuration is:\n" + content)
        return all(token in file_tokens for token in file_tokens)


def check_token(tokens, file_content):
    splited_tokens = tokens.split("|")
    return any(token in file_content for token in splited_tokens)


def test_daemon_configuration(daemon_name):
    '''
    Checking if the daemon configuration file and folder exists
    :param daemon_name:
    :return: True if exists
    '''
    print("Testing if the daemon configuration folder exists")
    is_daemon_dir_exists = check_file_in_directory(daemon_name, "/etc/")
    if not is_daemon_dir_exists:
        print_error("Could not locate " + daemon_name + " directory.[under \'/etc/\']")
        return False
    print_ok("Located /etc/" + daemon_name + " directory.")
    print("Checking omsagent configuration under the name of: \'security-config-omsagent.conf\'")
    config_exists = check_file_in_directory("security-config-omsagent.conf",
                                            rsyslog_daemon_forwarding_configuration_dir_path if daemon_name == rsyslog_daemon_name else syslog_ng_daemon_forwarding_configuration_dir_path)
    if not config_exists:
        print_error("security-config-omsagent.conf does not exists in " + daemon_name + " directory")
        return False
    else:
        print_ok("Located security-config-omsagent.conf")
        return True


def validate_daemon_configuration_content(daemon_name, valid_content_tokens_arr):
    print("Trying to validate the content of daemon configuration.")
    print_notice(
        "For extra verification please make sure the configuration content is as defined in the documentation.")
    # set path according to the daemon
    path = rsyslog_daemon_forwarding_configuration_path if daemon_name == rsyslog_daemon_name else syslog_ng_daemon_forwarding_configuration_path
    if not file_contains_string(valid_content_tokens_arr, path):
        print_error(
            "Error - security-config-omsagent.conf does not contain " + daemon_name + " daemon routing to oms-agent")
        return False
    else:
        print_ok("Security-config-omsagent.conf contains " + daemon_name + " routing configuration")
        return True


def security_config_omsagent_test(workspace_id):
    path = "/etc/opt/microsoft/omsagent/" + workspace_id + "/conf/omsagent.d/"
    is_security_config_omsagent_dir_exists = check_file_in_directory("security_events.conf", path)
    if not is_security_config_omsagent_dir_exists:
        print_error(
            "Error: Could not locate security_events.conf which configures the OMS agent to listen on port " + agent_port)
        return False
    else:
        print_ok("Located security_events.conf")
        return True


def omsagent_security_event_conf_validation(workspace_id):
    path = "/etc/opt/microsoft/omsagent/" + workspace_id + "/conf/omsagent.d/security_events.conf"
    print_notice("Validating " + path + " content.")
    if not sudo_read_file_contains_string(file_tokens=oms_agent_configuration_content_tokens, file_path=path):
        print_error("Could not locate necessary port and ip in the agent's configuration.\npath:" + path)
    else:
        print_ok("Omsagent event configuration content is valid")


def check_daemon(daemon_name):
    tokens = process_check(daemon_name)
    print(tokens)
    if len(tokens) > 1:
        for single_token in tokens:
            if "/usr/sbin/" + daemon_name in single_token:
                print_ok("Found " + daemon_name + " process running on this machine.")
                return True
    elif check_file_in_directory(daemon_name, "/etc/"):
        print_notice("Notice: " + daemon_name + " is not running but found configuration directory for it.")
        return False
    return False


def restart_daemon(daemon_name):
    print("Restarting " + daemon_name + " daemon - \'sudo service rsyslog restart\'")
    restart = subprocess.Popen(["sudo", "service", daemon_name, "restart"], stdout=subprocess.PIPE)
    o, e = restart.communicate()
    if e is not None:
        print_error("Error: could not restart " + daemon_name + "syslog daemon")
        return
    else:
        print_ok("" + daemon_name + " daemon restarted.")
        print("This will take a few seconds.")
        time.sleep(8)


def restart_omsagent(workspace_id):
    restart = subprocess.Popen(["sudo", "/opt/microsoft/omsagent/bin/service_control", "restart", workspace_id],
                               stdout=subprocess.PIPE)
    o, e = restart.communicate()
    if e is not None:
        print_error("Error: could not restart omsagent")
        return
    else:
        print_ok("Omsagent restarted.")
        print("This will take a few seconds.")
        time.sleep(8)


def check_rsyslog_configuration():
    udp = False
    tcp = False
    if check_file_in_directory("rsyslog.conf", "/etc/"):
        content = open("/etc/rsyslog.conf").read()
        lines = content.split("\n")
        print("Checking daemon incoming connection for tcp and udp")
        for line in lines:
            # second part is for red hat [DPServerRun]
            if "imudp" in line or "DPServerRun" in line:
                if "#" in line:
                    udp = False
                else:
                    udp = True
            # second part is for red hat [InputTCPServerRun]
            if "imtcp" in line or "InputTCPServerRun" in line:
                if "#" in line:
                    tcp = False
                else:
                    tcp = True
        if not udp:
            print_warning("Warning: udp communication is not enabled to the daemon.")
        if not tcp:
            print_warning("Warning: tcp communication is not enabled to the daemon.")
        return udp or tcp


def handle_syslog_ng(workspace_id):
    print("Checking syslog-ng:")
    if test_daemon_configuration("syslog-ng"):
        daemon_config_valid = validate_daemon_configuration_content("syslog-ng",
                                                                    syslog_ng_security_config_omsagent_conf_content_tokens)
        if daemon_config_valid:
            print_ok("Syslog-ng daemon configuration was found valid.")
            print("Trying to restart syslog daemon")
            restart_daemon("syslog-ng")
            restart_omsagent(workspace_id)
            netstat_open_port("0.0.0.0:" + daemon_port, "Daemon incoming port " + daemon_port + " is open",
                              "Error: daemon incoming port is not open, please check that the process is up and running and the port is configured correctly.")
            netstat_open_port(agent_port, "Omsagent is listening to incoming port " + agent_port,
                              "Error: agent is not listening to incoming port " + agent_port + " please check that the process is up and running and the port is configured correctly.[Use netstat -an | grep [daemon port] to validate the connection or re-run ths script]")
            print("Validating CEF into syslog-ng daemon")
            time.sleep(1)
            incoming_logs_validations(daemon_port,
                                      "Received CEF message in daemon incoming port.[" + daemon_port + "]", mock_message=False)
            time.sleep(1)
            incoming_logs_validations(agent_port,
                                      "Received CEF message in agent incoming port.[" + agent_port + "]", mock_message=False)
        else:
            print_error("Error: syslog-ng daemon configuration was found invalid.")
            print_notice("Notice: please make sure:")
            print_notice("\t/etc/syslog-ng/conf.d/security-config-omsagent.conf file exists")


def handle_rsyslog(workspace_id):
    print("Checking rsyslog daemon:")
    if test_daemon_configuration("rsyslog.d"):
        print_ok(
            "rsyslog daemon found, checking daemon configuration content - forwarding all data to port " + daemon_port)
        daemon_config_valid = validate_daemon_configuration_content("rsyslog.d",
                                                                    rsyslog_security_config_omsagent_conf_content_tokens)
        if not daemon_config_valid:
            print_error("Error: rsyslog daemon configuration was found invalid. ")
            print_notice("Notice: please make sure:")
            print_notice("\t1. /etc/rsyslog.d/security-config-omsagent.conf file exists")
            print_notice("\t2. File contains the following content:" + "\":rawmsg, regex, \"CEF\"|\"ASA\" \n*.* @@127.0.0.1:" + agent_port + "\"")
        else:
            print_ok("rsyslog daemon configuration was found valid.")
        print("Trying to restart syslog daemon")
        restart_daemon("rsyslog")
        restart_omsagent(workspace_id)
        netstat_open_port("0.0.0.0:" + daemon_port, "Daemon incoming port " + daemon_port + " is open",
                          "Error: daemon incoming port is not open, please check that the process is up and running and the port is configured correctly.\nAction: enable ports in \'/etc/rsyslog.conf\' file which contains daemon incoming ports.")
        netstat_open_port(agent_port, "Omsagent is listening to incoming port " + agent_port,
                          "Error: agent is not listening to incoming port " + agent_port + " please check that the process is up and running and the port is configured correctly.[Use netstat -an | grep [daemon port] to validate the connection or re-run ths script]")
        print("Validating CEF\\ASA into rsyslog daemon - port " + daemon_port)
        time.sleep(1)
        incoming_logs_validations(daemon_port,
                                  "Received CEF\\ASA message in daemon incoming port.[" + daemon_port + "]", mock_message=False)
        time.sleep(1)
        rsyslog_cef_logs_received_in_correct_format()
        # after validating logs are arriving validation that the daemon will accept them
        if check_rsyslog_configuration():
            incoming_logs_validations(agent_port,
                                      "Received CEF message in agent incoming port.[" + agent_port + "]", mock_message=False)
            time.sleep(1)


def main():
    print_notice("Note this script should be run in elevated privileges")
    print_notice("Please validate you are sending CEF messages to agent machine.")
    if len(sys.argv) != 2:
        print_error("The installation script is expecting 1 arguments:")
        print_error("\t1) workspace id")
        return
    else:
        workspace_id = sys.argv[1]
    # test the oms agent is installed
    check_oms_agent_status()
    # test oms agent configuration
    security_config_omsagent_test(workspace_id=workspace_id)
    omsagent_security_event_conf_validation(workspace_id=workspace_id)
    # validate firewalld
    check_red_hat_firewall_issue()
    # Check issue regarding security enhanced linux blocking tcp ports
    security_enhanced_linux()
    # testing that the daemon is running
    if check_daemon("rsyslog"):
        handle_rsyslog(workspace_id)
    elif check_daemon("syslog-ng"):
        handle_syslog_ng(workspace_id)
    print("Simulating mock data which you can find in your workspace")
    # we always simulate to the daemon port
    incoming_logs_validations(agent_port, "Mock messages sent and received in daemon incoming port [" + daemon_port + "] and to the omsagent port [" + agent_port + "].", mock_message=True)
    print_ok("Completed troubleshooting.")
    print(
        "Please check Log Analytics to see if your logs are arriving. All events streamed from these appliances appear in raw form in Log Analytics under CommonSecurityLog type")
    print("Notice: If no logs appear in workspace try looking at omsagent logs:")
    print_notice("tail -f /var/opt/microsoft/omsagent/" + workspace_id + "/log/omsagent.log")
    print_warning("Warning: Make sure that the logs you send comply with RFC 5424.")


main()
