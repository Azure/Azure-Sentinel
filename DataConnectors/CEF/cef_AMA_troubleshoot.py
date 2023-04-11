import subprocess
import time
import select
import sys
import re

# GENERAL SCRIPT CONSTANTS
LOG_OUTPUT_FILE = "/tmp/cef_troubleshooter_output_file.log"
COLLECT_OUTPUT_FILE = "/tmp/cef_troubleshooter_collection_output.log"
PATH_FOR_CSS_TICKET = {"Prod": "https://ms.portal.azure.com/#blade/Microsoft_Azure_Support/HelpAndSupportBlade/overview",
                       "MK": "https://portal.azure.cn/#blade/Microsoft_Azure_Support/HelpAndSupportBlade/overview",
                       "Gov": "https://portal.azure.us/#blade/Microsoft_Azure_Support/HelpAndSupportBlade/overview"}
AGENT_CONF_FILE = "/etc/opt/microsoft/azuremonitoragent/config-cache/mdsd.hr.json"
MACHINE_ENV = "Prod" #Default value is Prod
FAILED_TESTS_COUNT = 0
WARNING_TESTS_COUNT = 0
NOT_RUN_TESTS_COUNT = 0
SCRIPT_VERSION = 1.2
SCRIPT_HELP_MESSAGE = "Usage: python cef_AMA_troubleshoot.py [OPTION]\n" \
                      "Runs CEF validation tests on the collector machine and generates a log file here- /tmp/cef_troubleshooter_output_file.log\n\n" \
                      "     collect,        runs the script in collect mode. Useful in case you want to open a ticket. Generates an output file here- /tmp/cef_troubleshooter_collection_output.log\n" \
                      "     -h,             --help display the help and exit\n\n" \
                      "Example:\n" \
                      "     python cef_AMA_troubleshoot.py\n" \
                      "     python cef_AMA_troubleshoot.py collect\n\n" \
                      "This script verifies the installation of the CEF connector on the collector machine. It returns a status for each test and action items to fix detected issues."


class ColorfulPrint:
    """
    This class is in order to print text in color according to the severity level.
    """

    def print_error(self, input_str):
        """
        Print given text in red color for Error text
        :param input_str:
        """
        print("\033[1;31;40m" + input_str + "\033[0m")

    def print_ok(self, input_str):
        """
        Print given text in green color for Ok text
        :param input_str:
        """
        print("\033[1;32;40m" + input_str + "\033[0m")

    def print_warning(self, input_str):
        """
        Print given text in yellow color for warning text
        :param input_str:
        """
        print("\033[1;33;40m" + input_str + "\033[0m")

    def print_notice(self, input_str):
        """
        Print given text in white background
        :param input_str:
        """
        print("\033[0;30;47m" + input_str + "\033[0m")


class ShellExecute(ColorfulPrint):
    """
    This class is for executing all the shell related commands in the terminal for each test.
    """
    def run_command(self):
        """
        Running the bash commands using the subprocess library
        """
        try:
            self.command_result, self.command_result_err = subprocess.Popen(self.command_to_run, shell=True,
                                                                            stdout=subprocess.PIPE,
                                                                            stderr=subprocess.STDOUT).communicate()
        except Exception:
            self.command_result_err = "Error processing command"
        if "not found" in str(self.command_result):
            self.command_result_err = "Error running command: {}. Command does not exist. Please install it and run again.".format(
                self.command_to_run)

    def print_result_to_prompt(self):
        """
        Printing the test's name and success status to the customer's prompt
        """
        max_length = 47
        if self.is_successful == "Skip":
            self.print_warning(self.command_name + "-" * (max_length - len(self.command_name)) + "> Failed to check")
        elif self.is_successful == "Warn":
            self.print_warning(self.command_name + "-" * (max_length - len(self.command_name)) + "> Warning")
        elif self.is_successful:
            self.print_ok(self.command_name + "-" * (max_length - len(self.command_name)) + "> Success")
        else:
            self.print_error(self.command_name + "-" * (max_length - len(self.command_name)) + "> Failure")

    def document_result(self):
        """
        A simple way to only document the response to prompt and to the log file
        Can be used in case some special commands that don't require a verification to be ran
        """
        self.print_result_to_prompt()
        self.log_result_to_file()

    def log_result_to_file(self):
        """
        Logging each test to a log file that can be used for troubleshooting. Is done by the use of the object repr function
        """
        output = self.__repr__()
        output_file = open(LOG_OUTPUT_FILE, 'a')
        try:
            output_file.write(output)
        except Exception:
            print(str(self.command_name.command) + "was not documented successfully")
        output_file.close()

    def run_full_test(self, exclude=False, should_increase=True, should_warn=False):
        """
        A simple way to run a full test- executing the command, validating it's result, printing it to the prompt and logging it to a file
        :param exclude: A parameter given to the is_command_successful function.
        :param should_increase: If false, FAILED_TESTS_COUNT and NOT_RUN_TESTS_COUNT will not be increased
        :param should_warn: If True, self.is_successful value will be "Warn"
        """
        self.run_command()
        self.is_command_successful(exclude=exclude, should_increase=should_increase, should_warn=should_warn)
        self.print_result_to_prompt()
        self.log_result_to_file()


class FullVerification(ShellExecute):
    """
    This class is running all the necessary verifications for the running test.
    """
    def is_command_successful(self, exclude=False, should_fail=False, should_increase=True, should_warn=False):
        """
        Verifying the command output indicates success. It's done by searching for key words in the result
        :param exclude: If true, will verify the key words do not exist in the command result
        :param should_fail: If true, will just return false and not run any further verification
        :param should_increase: If false, FAILED_TESTS_COUNT and NOT_RUN_TESTS_COUNT will not be increased
        :param should_warn: If True, self.is_successful value will be "Warn"
        :return: True if successful otherwise False.
        """
        global FAILED_TESTS_COUNT, NOT_RUN_TESTS_COUNT, WARNING_TESTS_COUNT
        if "not found" in str(self.command_result):
            self.is_successful = "Skip"
            if should_increase:
                NOT_RUN_TESTS_COUNT += 1
            return True

        value = self.calc_is_command_successful(exclude, should_fail)
        if value is True:
            self.is_successful = True
            return True
        else:
            if should_warn:
                self.is_successful = "Warn"
                if should_increase:
                    WARNING_TESTS_COUNT += 1
            else:
                self.is_successful = False
                if should_increase:
                    FAILED_TESTS_COUNT += 1

            return False

    """
    This class is running all the necessary verifications for the running test.
    """
    def calc_is_command_successful(self, exclude=False, should_fail=False):
        """
        Verifying the command output indicates success. It's done by searching for key words in the result
        :param exclude: If true, will verify the key words do not exist in the command result
        :param should_fail: If true, will just return false and not run any further verification
        :return: True if successful otherwise False.
        """
        if self.command_result_err is None and self.command_result is not None and should_fail is not True:
            self.command_result = str(self.command_result)
            for key_word in self.result_keywords_array:
                key_word = str(key_word)
                if exclude:
                    if key_word in self.command_result:
                        self.fault_keyword = key_word
                        return False
                elif key_word not in self.command_result:
                    self.fault_keyword = key_word
                    return False
            return True
        return False

    def run_full_verification(self, exclude=False, should_fail=False):
        """
        A simple way to run only the verification on documentation steps of the test.
        Can be used in case some special commands are not run using the run_command function
        :param exclude: A parameter given to the is_command_successful function.
        :param should_fail: A parameter given to the is_command_successful function.
        """
        self.is_command_successful(exclude, should_fail)
        self.print_result_to_prompt()
        self.log_result_to_file()


class BasicCommand(FullVerification):
    """
    This class is for creating a command object. The object has execution, validation and documentation functions
    """

    def __init__(self, command_name, command_to_run, result_keywords_array=[], fault_keyword=None,
                 command_result=None,
                 command_result_err=None,
                 is_successful=False):
        self.command_name = command_name
        self.command_to_run = command_to_run
        self.result_keywords_array = result_keywords_array
        self.fault_keyword = fault_keyword
        self.command_result = command_result
        self.command_result_err = command_result_err
        self.is_successful = is_successful

    def __repr__(self):
        """
        Printing the command details in a built in format
        """
        delimiter = "\n" + "-" * 20 + "\n"
        return str(
            delimiter + str(self.command_name) + '\n' + "command to run: " + str(
                self.command_to_run) + '\n' +
            "command output:" + '\n' + str(self.command_result) + '\n' + "command error output: " + str(
                self.command_result_err) + '\n' +
            "command array verification: " + str(self.result_keywords_array) + '\n' + "fault key word: " + str(
                self.fault_keyword) + '\n' + "Is successful: " + str(
                self.is_successful) +
            delimiter).replace(
            '%', '%%').replace('\\n', '\n')


class AgentInstallationVerifications:
    """
    This class is for agent related verifications
    """
    # CONSTANTS
    Agent_installation_doc = "https://docs.microsoft.com/azure/azure-monitor/agents/azure-monitor-agent-manage"
    agent_not_installed_error_message = "Could not detect an AMA service running and listening on the machine." \
                                        " Please follow this documentation in order to install it and verify your" \
                                        " machine's operating system is in the supported list- {}".format(
        Agent_installation_doc)
    agent_not_running_error_message = "Detected AMA is installed on the machine but not running. Please start the agent by running " \
                                      "\'service azuremonitoragent start\' \nif the agent service fails to start," \
                                      " please run the following command to review the agent error log file here- " \
                                      "\'cat /var/opt/microsoft/azuremonitoragent/log/mdsd.err | tail -n 15\'".format(
        Agent_installation_doc)

    oms_running_error_message = "Detected the OMS Agent running on your machine. If not necessary please remove it to avoid duplicated data in the workspace, which can result in an increase in costs"

    def verify_agent_is_running(self):
        """
        Verifying the agent service called mdsd is listening on its default port
        """
        command_name = "verify_ama_agent_service_is_running"
        command_to_run = "sudo systemctl status azuremonitoragent"
        result_keywords_array = ["azuremonitoragent.service", "Azure", "Monitor", "Agent", "active", "running"]
        command_object = BasicCommand(command_name, command_to_run, result_keywords_array)
        command_object.run_full_test()
        if not command_object.is_successful:
            if ("could not be found" or "no such service") in command_object.command_result:
                command_object.is_successful = False
                command_object.print_error(self.agent_not_installed_error_message)
                return False
            else:
                command_object.print_error(self.agent_not_running_error_message)
        else:
            command_object.command_to_run = "sudo /opt/microsoft/azuremonitoragent/bin/mdsd -V"
            command_object.run_command()
            command_object.print_ok(
                "Detected AMA running version- {}".format(command_object.command_result.decode('UTF-8').strip('\n')))

    def print_arc_version(self):
        """
        Checking if ARC is installed. If so- prints the version of it.
        """
        command_name = "print_arc_version"
        command_to_run = "azcmagent version"
        command_object = BasicCommand(command_name, command_to_run)
        command_object.run_command()
        if "azcmagent version" in str(command_object.command_result) and "command not found" not in str(
                command_object.command_result):
            command_object.print_notice("Detected ARC installed on the machine: {}".format(
                command_object.command_result.decode('UTF-8').strip('\n')))

    def verify_oms_not_running(self):
        """
        Verify the old MMA agent is not running together with the new AMA agent.
        """
        command_name = "verify_oms_agent_not_running"
        command_to_run = "sudo netstat -lnpvt | grep ruby"
        result_keywords_array = ["25226", "LISTEN", "tcp"]
        command_object = BasicCommand(command_name, command_to_run, result_keywords_array)
        command_object.run_full_test(exclude=True)
        if command_object.is_successful == "Skip":
            command_object.print_warning(command_object.command_result_err)
        elif not command_object.is_successful:
            command_object.print_warning(self.oms_running_error_message)

    def run_all_verifications(self):
        """
        This function is only called by main and runs all the tests in this class
        """
        self.verify_agent_is_running()
        self.print_arc_version()
        self.verify_oms_not_running()


class DCRConfigurationVerifications:
    """
    This class is for data collection rules verifications
    """
    # CONSTANTS
    DCR_doc = "https://docs.microsoft.com/azure/azure-monitor/agents/data-collection-rule-overview"
    DCRA_doc = "https://docs.microsoft.com/rest/api/monitor/data-collection-rule-associations"
    CEF_stream_name = "SECURITY_CEF_BLOB"
    DCR_missing_error_messgae = "Could not detect any data collection rule on the machine. The data reaching this server will not be forwarded to any workspace." \
                                " For explanation on how to install a Data collection rule please browse- {} \n " \
                                "In order to read about how to associate a DCR to a machine please review- {}".format(
        DCR_doc, DCRA_doc)
    DCR_missing_CEF_stream_error_message = "Could not detect any data collection rule for CEF data. No CEF events will " \
                                           "be collected from this machine to any workspace. Please create a CEF DCR using the following documentation- " \
                                           "{} and run again".format(DCR_doc)
    CEF_multi_homing_message = "Detected multiple collection rules sending the CEF stream. This scenario is called multi-homing and might have effect on the agent's performance"

    def verify_DCR_exists(self):
        """
        Verifying there is at least one dcr on the machine
        """
        command_name = "verify_DCR_exists"
        command_to_run = "sudo ls -l /etc/opt/microsoft/azuremonitoragent/config-cache/configchunks/"
        result_keywords_array = [".json"]
        command_object = BasicCommand(command_name, command_to_run, result_keywords_array)
        command_object.run_full_test()
        if not command_object.is_successful:
            command_object.print_error(self.DCR_missing_error_messgae)
            return False
        return True

    def verify_DCR_content_has_CEF_stream(self):
        """
        Verifying there is a DCR on the machine for forwarding cef data
        """
        command_name = "verify_DCR_content_has_CEF_stream"
        command_to_run = "sudo grep -ri \"{}\" /etc/opt/microsoft/azuremonitoragent/config-cache/configchunks/".format(
            self.CEF_stream_name)
        result_keywords_array = [self.CEF_stream_name]
        command_object = BasicCommand(command_name, command_to_run, result_keywords_array)
        command_object.run_full_test()
        if not command_object.is_successful:
            command_object.print_error(self.DCR_missing_CEF_stream_error_message)
            return False
        return True

    def verify_dcr_has_valid_content(self):
        """
        Verifying that the CEF DCR on the machine has valid content with all necessary DCR components
        """
        command_name = "verify_CEF_dcr_has_valid_content"
        command_to_run = "sudo grep -ri \"{}\" /etc/opt/microsoft/azuremonitoragent/config-cache/configchunks/".format(
            self.CEF_stream_name)
        result_keywords_array = ["stream", "kind", "syslog", "dataSources", "configuration", "facilityNames",
                                 "logLevels", "SecurityInsights", "endpoint", "channels", "sendToChannels", "ods-",
                                 "opinsights.azure", "id"]
        command_object = BasicCommand(command_name, command_to_run, result_keywords_array)
        command_object.run_command()
        command_object.command_result = command_object.command_result.decode('UTF-8').split('\n')[:-1]
        for dcr in command_object.command_result:
            dcr_path = re.search("(/etc/opt/microsoft/azuremonitoragent/config-cache/configchunks/.*.json)",
                                 str(dcr)).group()
            for key_word in command_object.result_keywords_array:
                if str(key_word) not in str(dcr):
                    command_object.is_command_successful(should_fail=True)
                    command_object.print_error(
                        "Found an invalid DCR. It is missing this key-word \'{}\'. It's path is {}".format(key_word,
                                                                                                           dcr_path))
                    return False
        command_object.run_full_verification()

    def check_cef_multi_homing(self):
        """
        Counting the amount of DCRs forwarding CEF data in order to alert from multi-homing scenarios.
        """

        command_name = "check_cef_multi_homing"
        command_to_run = "sudo grep -ri \"{}\" /etc/opt/microsoft/azuremonitoragent/config-cache/configchunks/ | wc -l".format(
            self.CEF_stream_name)
        command_object = BasicCommand(command_name, command_to_run)
        command_object.run_command()
        try:
            if int(command_object.command_result) > 1:
                command_object.run_full_verification(should_fail=True)
                command_object.print_warning(self.CEF_multi_homing_message)
            else:
                command_object.is_successful = True
                command_object.document_result()
        except ValueError:
            command_object.run_full_verification(should_fail=True)
            command_object.print_warning("Failed to run this test since no DCRs were found")

    def run_all_verifications(self):
        """
        This function is only called by main and runs all the tests in this class
        """
        if not self.verify_DCR_exists():
            return False
        if not self.verify_DCR_content_has_CEF_stream():
            return False
        self.verify_dcr_has_valid_content()
        self.check_cef_multi_homing()


class SyslogDaemonVerifications(ColorfulPrint):
    """
    This class is for Syslog daemon related verifications
    """
    def __init__(self):
        self.command_name = "verify_Syslog_daemon_listening"
        self.SYSLOG_DAEMON = ""
        self.syslog_daemon_forwarding_path = {"rsyslog": "/etc/rsyslog.d/10-azuremonitoragent.conf",
                                         "syslog-ng": "/etc/syslog-ng/conf.d/azuremonitoragent.conf"}
        self.No_Syslog_daemon_error_message = "Could not detect any running Syslog daemon on the machine. The supported Syslog daemons are Rsyslog and Syslog-ng. Please install one of them and run this script again."
        self.Syslog_daemon_not_listening_warning = (lambda daemon_name: "Warning: the Syslog daemon- {} is running but not listening on the machine or is listening to a non-default port".format(daemon_name))
        self.Syslog_daemon_not_forwarding_error = (lambda daemon_name: "{} configuration was found invalid in this file {}. The forwarding of the syslog daemon to the agent might not work. Please install the agent in order to get the updated Syslog daemon forwarding configuration file, and try again.".format(
            daemon_name, self.syslog_daemon_forwarding_path[daemon_name]))

    def determine_Syslog_daemon(self):
        """
        This function is in order to determine what Syslog daemon is running on the machine (Rsyslog or Syslog-ng)
        """
        is_Rsyslog_running = BasicCommand("find_Rsyslog_daemon",
                                          "if [ `ps -ef | grep rsyslog | grep -v grep | wc -l` -gt 0 ]; then echo \"True\"; else echo \"False\"; fi")
        is_Syslog_ng_running = BasicCommand("find_Syslog-ng_daemon",
                                            "if [ `ps -ef | grep syslog-ng | grep -v grep | wc -l` -gt 0 ]; then echo \"True\"; else echo \"False\"; fi")
        is_Rsyslog_running.run_command(), is_Syslog_ng_running.run_command()
        if "True" in str(is_Rsyslog_running.command_result):
            self.SYSLOG_DAEMON = "rsyslog"
            return True
        elif "True" in str(is_Syslog_ng_running.command_result):
            self.SYSLOG_DAEMON = "syslog-ng"
            return True
        is_Rsyslog_running.log_result_to_file()
        is_Syslog_ng_running.log_result_to_file()
        return False

    def verify_Syslog_daemon_listening(self):
        """
        Verifying the Syslog daemon is listening on the default 514 port for incoming traffic
        """
        command_to_run = "sudo netstat -lnpv | grep " + self.SYSLOG_DAEMON
        result_keywords_array = [self.SYSLOG_DAEMON, ":514 "]
        command_object = BasicCommand(self.command_name, command_to_run, result_keywords_array)
        command_object.run_command()
        command_object.is_command_successful(should_increase=False)
        if command_object.is_successful is not False:
            command_object.document_result()
            if command_object.is_successful == "Skip":
                command_object.print_warning(command_object.command_result_err)
        else:
            # In case we don't find any daemon on port 514 we will make sure it's not listening to TLS port: 6514
            result_keywords_array = [self.SYSLOG_DAEMON, ":6514 "]
            command_object = BasicCommand(self.command_name, command_to_run, result_keywords_array)
            command_object.run_full_test(should_warn=True)
            if command_object.is_successful == "Warn":
                command_object.print_warning(self.Syslog_daemon_not_listening_warning(self.SYSLOG_DAEMON))

    def verify_Syslog_daemon_forwarding_configuration(self):
        """
        Verify the syslog daemon forwarding configuration file has the correct forwarding configuration to the Unix domain socket.
        """
        if self.SYSLOG_DAEMON != "":
            syslog_daemon_forwarding_keywords = {
                "rsyslog": ['omuxsock', 'azuremonitoragent', 'OMUxSockSocket', 'OMUxSockDefaultTemplate'],
                "syslog-ng": ['destination', 'd_azure_mdsd', 'unix-dgram', 'azuremonitoragent', 'syslog', 'socket',
                              's_src']}
            command_name = "verify_Syslog_daemon_forwarding_configuration"
            command_to_run = "sudo cat " + self.syslog_daemon_forwarding_path[self.SYSLOG_DAEMON]
            result_keywords_array = syslog_daemon_forwarding_keywords[self.SYSLOG_DAEMON]
            command_object = BasicCommand(command_name, command_to_run, result_keywords_array)
            command_object.run_full_test()
            if not command_object.is_successful:
                command_object.print_error(self.Syslog_daemon_not_forwarding_error(self.SYSLOG_DAEMON))

    def run_all_verifications(self):
        """
        This function is only called by main and runs all the tests in this class
        """
        global FAILED_TESTS_COUNT
        if self.determine_Syslog_daemon():
            self.verify_Syslog_daemon_listening()
            self.verify_Syslog_daemon_forwarding_configuration()
        else:
            mock_command = BasicCommand(self.command_name, "")
            mock_command.print_result_to_prompt()
            mock_command.print_error(self.No_Syslog_daemon_error_message)
            FAILED_TESTS_COUNT += 1


class OperatingSystemVerifications:
    """
    This class is for general operating system verifications
    """
    # CONSTANTS
    SELinux_documentation = "https://access.redhat.com/documentation/red_hat_enterprise_linux/8/html/using_selinux/changing-selinux-states-and-modes_using-selinux#changing-selinux-modes_changing-selinux-states-and-modes"
    SELinux_running_error_message = "Detected SELinux running on the machine. The CEF connector does not support any form of hardening at the moment," \
                                    "and having SELinux in Enforcing mode can harm the forwarding of data. Please disable SELinux by running the command \'setenforce 0\'." \
                                    "This will disable SELinux temporarily. In order to disable permemently please follow this documentation- {}".format(
        SELinux_documentation)
    iptables_blocking_traffic_error_message = "Iptables might be blocking incoming traffic to the agent." \
                                              " Please verify there are no firewall rules blocking incoming traffic to port 514 and run again."
    Full_disk_error_message = "There is less than 1 GB of free disk space left on this machine." \
                              " Having a full disk can harm the agent functionality and eventually cause data loss" \
                              " Please free disk space on this machine and run again."

    def verify_selinux_disabled(self):
        """
        Verify SELinux is not in enforcing mode, which can harm the events' forwarding to the agent.
        """
        command_name = "verify_selinux_disabled"
        command_to_run = "sudo getenforce 2> /dev/null; if [ $? != 0 ]; then echo 'Disabled'; fi"
        result_keywords_array = ["Enforcing"]
        command_object = BasicCommand(command_name, command_to_run, result_keywords_array)
        command_object.run_full_test(True)
        if not command_object.is_successful:
           command_object.print_error(self.SELinux_running_error_message)

    def verify_iptables(self):
        """
        Verify there is no firewall rule in the iptables blocking the Syslog daemon or agent incoming ports
        """
        command_name = "verify_iptables_policy_permissive"
        command_to_run = "sudo iptables -S | grep \\\\-P | grep -E 'INPUT|OUTPUT'"
        result_keywords_array = ["DROP", "REJECT"]
        policy_command_object = BasicCommand(command_name, command_to_run, result_keywords_array)
        policy_command_object.run_full_test(exclude=True)
        if policy_command_object.is_successful == "Skip":
            policy_command_object.print_warning(policy_command_object.command_result_err)
            return True
        command_name = "verify_iptables_rules_permissive"
        command_to_run = "sudo iptables -S | grep -E '514' | grep INPUT"
        rules_command_object = BasicCommand(command_name, command_to_run, result_keywords_array)
        rules_command_object.run_full_test(exclude=True)
        if (not rules_command_object.is_successful or (not policy_command_object.is_successful and (
                not rules_command_object.is_successful or rules_command_object.command_result == ""))):
            policy_command_object.print_warning(self.iptables_blocking_traffic_error_message)

    def verify_free_disk_space(self):
        """
        Verify there is enough free disk space on the machine for the event forwarding to work as expected. The minimal is set to 1 GB
        """
        minimal_free_space_kb = 1048576
        command_name = "verify_free_disk_space"
        command_to_run = "sudo df --output=avail / | head -2 | tail -1"
        command_object = BasicCommand(command_name, command_to_run)
        command_object.run_command()
        if int(command_object.command_result) < minimal_free_space_kb:
            command_object.run_full_verification(should_fail=True)
            command_object.print_error(self.Full_disk_error_message)
        else:
            command_object.is_successful = True
            command_object.document_result()

    def run_all_verifications(self):
        """
        This function is only called by main and runs all the tests in this class
        """
        self.verify_selinux_disabled()
        self.verify_iptables()
        self.verify_free_disk_space()


class IncomingEventsVerifications:
    """
    This class is for sending and capturing CEF events in the incoming stream of events to the syslog daemon port
    """
    # CONSTANTS
    Fixed_cef_message = "0|TestCommonEventFormat|MOCK|common=event-format-test|end|TRAFFIC|1|rt=$common=event-formatted-receive_time deviceExternalId=0002D01655 src=1.1.1.1 dst=2.2.2.2 sourceTranslatedAddress=1.1.1.1 destinationTranslatedAddress=3.3.3.3 cs1Label=Rule cs1=CEF_TEST_InternetDNS"
    Tcpdump_not_installed_error_message = "Notice that \'tcpdump\' is not installed in your Linux machine.\nWe cannot monitor traffic without it.\nPlease install \'tcpdump\'."
    Logger_not_installed_error_message = "Warning: Could not execute \'logger\' command. This means that no mock message was sent to your workspace."
    CEF_events_found_message = "Found CEF events in stream. Please verify CEF events arrived at your workspace"
    CEF_events_not_found_error_message = "Could not locate \"CEF\" message in tcpdump. Please verify CEF events can be sent to the machine and there is not firewall blocking incoming traffic"

    def handle_tcpdump_line(self, line):
        """
        Validate there are incoming CEF events.
        :param line: a text line from the tcpdump stream
        :return: True if CEF exists in the line. Otherwise false.
        """
        if "CEF" in line:
            return True
        return False

    def incoming_logs_validations(self, mock_message=False):
        """
        Validate that there is incoming traffic of CEF messages
        :param mock_message: Tells if to generate mock messages
        :return: True if successfully captured CEF events.
        """
        tcpdump_time_restriction = 10
        start_seconds = int(round(time.time()))
        end_seconds = int(round(time.time()))
        mock_message_counter = 0
        command_name = "listen_to_incoming_cef_events"
        command_to_run = "sudo tcpdump -A -ni any port 514 -vv"
        result_keywords_array = ["CEF"]
        command_object = BasicCommand(command_name, command_to_run, result_keywords_array)
        print("Attempting to capture CEF events using tcpdump. This could take up to " + str(
            tcpdump_time_restriction) + " seconds.")
        tcp_dump = subprocess.Popen(command_object.command_to_run, shell=True, stdout=subprocess.PIPE,
                                    stderr=subprocess.STDOUT)
        line = str(tcp_dump.stdout.readline())
        # Handle command not found
        if "command not found" in line:
            print(self.Tcpdump_not_installed_error_message)
            command_object.command_result = line
            command_object.run_full_verification()
            return False
        poll_obj = select.poll()
        poll_obj.register(tcp_dump.stdout, select.POLLIN)
        while (end_seconds - start_seconds) < tcpdump_time_restriction:
            if mock_message is True:
                # Sending mock messages
                mock_message_counter += 1
                self.send_cef_message_local(514, 1)
            poll_result = poll_obj.poll(0)
            if poll_result:
                line = str(tcp_dump.stdout.readline())
                if self.handle_tcpdump_line(line):
                    command_object.command_result = line
                    command_object.run_full_verification()
                    command_object.print_ok(self.CEF_events_found_message)
                    return True
            end_seconds = int(round(time.time()))
        command_object.print_error(self.CEF_events_not_found_error_message)
        command_object.command_result = str(line)
        command_object.run_full_verification()
        return False

    def send_cef_message_local(self, port, amount):
        """
        Generate local CEF events in a given amount to a given port
        :param port: A destination port to send the events
        :param amount: The amount of events to send
        """
        try:
            for index in range(0, amount):
                command_tokens = ["logger", "-p", "local4.warn", "-t", "CEF:", self.Fixed_cef_message, "-P", str(port),
                                  "-n",
                                  "127.0.0.1"]
                logger = subprocess.Popen(command_tokens, stdout=subprocess.PIPE)
                o, e = logger.communicate()
                if e is not None:
                    print("Error could not send cef mock message")
        except OSError:
            print(self.Logger_not_installed_error_message)

    def run_all_verifications(self):
        """
        This function is only called by main and runs all the tests in this class
        """
        printer = ColorfulPrint()
        if not self.incoming_logs_validations():
            printer.print_notice("Generating CEF mock events and trying again")
            self.incoming_logs_validations(mock_message=True)


class SystemInfo():
    commands_dict = {
        "script_version": ["echo {}".format(SCRIPT_VERSION)],
        "date": ["sudo date"],
        "netstat": ["sudo netstat -lnpvt"],
        "df": ["sudo df -h"],
        "list_open_files": ["sudo lsof +L1"],
        "free": ["sudo free -m"],
        "iptables": ["sudo iptables -vnL --line"],
        "selinux": ["sudo cat /etc/selinux/config"],
        "os_version": ["sudo cat /etc/issue"],
        "python_version": ["sudo python -V"],
        "ram_stats": ["sudo cat /proc/meminfo"],
        "cron_jobs": ["sudo crontab -l"],
        "wd_list": ["sudo ls -la ."],
        "internet_connection": ["sudo curl -D - http://microsoft.com"],
        "sudoers_list": ["sudo cat /etc/sudoers"],
        "rotation_configuration": ["sudo cat /etc/logrotate.conf"],
        "rsyslog_conf": ["sudo cat /etc/rsyslog.conf"],
        "rsyslog_dir": ["sudo ls -la /etc/rsyslog.d/"],
        "rsyslog_dir_content": ["sudo grep -r ^ /etc/rsyslog.d/"],
        "is_rsyslog_running_from_boot": ["sudo sudo systemctl list-unit-files --type=service | grep rsyslog"],
        "syslog_ng_conf": ["sudo cat /etc/syslog-ng/syslog-ng.conf"],
        "syslog_ng_dir": ["sudo ls -la /etc/syslog-ng/conf.d/"],
        "syslog_ng_dir_content": ["sudo grep -r ^ /etc/syslog-ng/conf.d/"],
        "is_syslog_ng_running_from_boot": ["sudo sudo systemctl list-unit-files --type=service | grep syslog-ng"],
        "agent_log_snip_err": ["sudo tail -n 15 /var/opt/microsoft/azuremonitoragent/log/mdsd.err"],
        "agent_log_snip_warn": ["sudo tail -n 15 /var/opt/microsoft/azuremonitoragent/log/mdsd.warn"],
        "agent_log_snip_info": ["sudo tail -n 15 /var/opt/microsoft/azuremonitoragent/log/mdsd.info"],
        "is_AMA__running_from_boot": ["sudo systemctl list-unit-files --type=service | grep azuremonitoragent"],
        "AMA_service_status": ["sudo systemctl status azuremonitoragent"],
        "DCR_config_dir": ["sudo ls -la /etc/opt/microsoft/azuremonitoragent/config-cache/configchunks/"],
        "messages_log_snip": ["sudo tail -n 15 /var/log/messages"],
        "syslog_log_snip": ["sudo tail -n 15 /var/log/syslog"],
        "top_processes": ["sudo top -bcn1 -w512 | head -n 20"],
    }

    def __repr__(self, command_object):
        delimiter = "\n" + "-" * 20 + "\n"
        return str(
            delimiter + "command: " + str(command_object.command_name) + '\n' + "output: " + str(
                command_object.command_result) + delimiter).replace(
            '%', '%%').replace('\\n', '\n')

    def append_content_to_file(self, command_object, file_path=COLLECT_OUTPUT_FILE):
        """
        :param command_object: consists of the name and the output
        :param file_path: a file to share the commands outputs
        """
        output = self.__repr__(command_object)
        cef_get_info_file = open(file_path, 'a')
        try:
            cef_get_info_file.write(output)
        except Exception:
            print(str(command_object.command) + "was not documented successfully")
        cef_get_info_file.close()

    def handle_commands(self):
        """
        This function handles the whole command flow from running to documenting.
        """
        for command_name in self.commands_dict.keys():
            command_object = BasicCommand(command_name, self.commands_dict[command_name])
            command_object.run_command()
            self.append_content_to_file(command_object)


def verify_root_privileges(printer):
    o, e = subprocess.Popen(['id', '-u'], stdout=subprocess.PIPE, stderr=subprocess.STDOUT).communicate()
    if int(o) != 0:
        printer.print_error(
            "This script must be run in elevated privileges since some of the tests require root privileges")
        exit()

def find_dcr_cloud_environment():
    '''
    Use the agent config on the machine to determine the cloud environment we are running in
    '''
    global MACHINE_ENV
    command_to_run = "if grep -qs \"azure.cn\" {0}; then echo \"MK\"; elif grep -qs \"azure.us\" {0}; then echo \"Gov\"; else echo \"Prod\"; fi".format(AGENT_CONF_FILE)
    try:
        command_result, command_result_err = subprocess.Popen(command_to_run, shell=True,
                                                                        stdout=subprocess.PIPE,
                                                                        stderr=subprocess.STDOUT).communicate()
        MACHINE_ENV = command_result.decode('utf-8').strip("\n")
    except Exception:
        pass

def main():
    collection_feature_flag = "collect"
    running_in_collect_mode = False
    help_feature_flag = ['-h', '-H', '-help', '--help', '-Help', '--Help']
    printer = ColorfulPrint()
    verify_root_privileges(printer)
    find_dcr_cloud_environment()
    if len(sys.argv) > 1:
        if str(sys.argv[1]) == collection_feature_flag:
            running_in_collect_mode = True
            printer.print_notice("Starting to collect data. This may take a couple of seconds")
            time.sleep(2)
            subprocess.Popen(['rm', '-f', COLLECT_OUTPUT_FILE],
                             stdout=subprocess.PIPE, stderr=subprocess.STDOUT).communicate()
            system_info = SystemInfo()
            system_info.handle_commands()
            print(
                "Finished collecting data \nPlease provide CSS with this file for further investigation- {} \n"
                "In order to open a support case please browse: {}".format(
                    COLLECT_OUTPUT_FILE, PATH_FOR_CSS_TICKET[MACHINE_ENV]))
            time.sleep(1)
        # Print help message on how to use the script
        elif str(sys.argv[1]) in help_feature_flag:
            print(SCRIPT_HELP_MESSAGE)
            exit()
        else:
            print("python cef_AMA_troubleshoot.py: unrecognized option '{}'\n"
                  "Try 'python cef_AMA_troubleshoot.py --help' for more information.".format(str(sys.argv[1])))
            exit()
    class_tests_array = [
        (AgentInstallationVerifications(), "Starting validation tests for AMA"),
        (DCRConfigurationVerifications(), "Starting validation tests for data collection rules"),
        (SyslogDaemonVerifications(), "Starting validation tests for the Syslog daemon"),
        (OperatingSystemVerifications(), "Starting validation tests for the operating system"),
        (IncomingEventsVerifications(), "Starting validation tests for capturing incoming events")]
    printer.print_notice("\nStarting to run the CEF validation script")
    time.sleep(1)
    subprocess.Popen(['rm', '-f', LOG_OUTPUT_FILE],
                     stdout=subprocess.PIPE, stderr=subprocess.STDOUT).communicate()
    printer.print_notice("Please validate you are sending CEF messages to the agent machine")
    for class_test in class_tests_array:
        printer.print_notice("\n----- {} {}".format(class_test[1], '-' * (60 - len(class_test[1]))))
        verification_object = class_test[0]
        verification_object.run_all_verifications()
    if NOT_RUN_TESTS_COUNT > 0:
        printer.print_warning("\nTotal amount of tests that failed to run: " + str(NOT_RUN_TESTS_COUNT))
    if WARNING_TESTS_COUNT > 0:
        printer.print_warning("\nTotal amount of tests that ended with a warning status is: " + str(WARNING_TESTS_COUNT))
    if FAILED_TESTS_COUNT > 0:
        printer.print_error("\nTotal amount of failed tests is: " + str(FAILED_TESTS_COUNT))
    else:
        printer.print_ok("All tests passed successfully")
    printer.print_notice("This script generated an output file located here - {}"
                         "\nPlease review it if you would like to get more information on failed tests.".format(
        LOG_OUTPUT_FILE))
    if not running_in_collect_mode:
        printer.print_notice(
            "\nIf you would like to open a support case please run this script with the \'collect\' feature flag in order to collect additional system data for troubleshooting."
            "\'python cef_AMA_troubleshoot.py collect\'")


if __name__ == '__main__':
    main()
