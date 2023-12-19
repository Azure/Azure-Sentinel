import subprocess
import time
import select
import re
import argparse
import sys
from distutils.version import StrictVersion

SCRIPT_VERSION = 2.5
PY3 = sys.version_info.major == 3

# GENERAL SCRIPT CONSTANTS
DEFAULT_MACHINE_ENV = "Prod"
LOG_OUTPUT_FILE = "/tmp/troubleshooter_output_file.log"
PATH_FOR_CSS_TICKET = {
    "Prod": "https://ms.portal.azure.com/#blade/Microsoft_Azure_Support/HelpAndSupportBlade/overview",
    "MK": "https://portal.azure.cn/#blade/Microsoft_Azure_Support/HelpAndSupportBlade/overview",
    "Gov": "https://portal.azure.us/#blade/Microsoft_Azure_Support/HelpAndSupportBlade/overview"}
AGENT_CONF_FILE = "/etc/opt/microsoft/azuremonitoragent/config-cache/mdsd.hr.json"
AGENT_VERSION = "0.0"
UPDATED_AGENT_VERSION = "1.28.11"
IS_AGENT_VERSION_UPDATED = False
AGENT_MIN_HARDENING_VERSION = "1.26.0"
FAILED_TESTS_COUNT = 0
STREAM_SCENARIO = "cef"  # default value
WARNING_TESTS_COUNT = 0
NOT_RUN_TESTS_COUNT = 0
DELIMITER = "\n" + "-" * 20 + "\n"


def print_error(input_str):
    """
    Print given text in red color for Error text
    :param input_str:
    """
    print("\033[1;31;40m" + input_str + "\033[0m")


def print_ok(input_str):
    """
    Print given text in green color for Ok text
    :param input_str:
    """
    print("\033[1;32;40m" + input_str + "\033[0m")


def print_warning(input_str):
    """
    Print given text in yellow color for warning text
    :param input_str:
    """
    print("\033[1;33;40m" + input_str + "\033[0m")


def print_notice(input_str):
    """
    Print given text in white background
    :param input_str:
    """
    print("\033[0;30;47m" + input_str + "\033[0m")


class CommandShellExecution(object):
    """
    This class is for executing all the shell related commands in the terminal for each test.
    """

    def __init__(self, command_name, command_to_run, result_keywords_array=None, fault_keyword=None,
                 command_result=None,
                 command_result_err=None):
        self.command_name = command_name
        self.command_to_run = command_to_run
        self.result_keywords_array = result_keywords_array if result_keywords_array is not None else []
        self.fault_keyword = fault_keyword
        self.command_result = command_result
        self.command_result_err = command_result_err

    def __repr__(self):
        """
        Printing the command details in a built-in format
        """
        return str(
            DELIMITER + str(self.command_name) + '\n' + "command to run: " + str(
                self.command_to_run) + '\n' +
            "command output:" + '\n' + str(self.command_result) + '\n' + "command error output: " + str(
                self.command_result_err) + '\n' +
            "command array verification: " + str(self.result_keywords_array) + '\n' + "fault key word: " + str(
                self.fault_keyword) +
            DELIMITER).replace(
            '%', '%%').replace('\\n', '\n')

    def run_command(self, should_decode=True):
        """
        Running the bash commands using the subprocess library
        """
        try:
            self.command_result, self.command_result_err = subprocess.Popen(self.command_to_run, shell=True,
                                                                            stdout=subprocess.PIPE,
                                                                            stderr=subprocess.STDOUT).communicate()
            if should_decode and PY3:
                self.command_result = self.command_result.decode('UTF-8').strip('\n')
        except Exception:
            self.command_result_err = "Error processing command"
        if "not found" in str(self.command_result):
            self.command_result_err = "Error running command: {}. Command does not exist. Please install it and run again.".format(
                self.command_to_run)


class CommandVerification(CommandShellExecution):
    """
    This class is running all the necessary verifications for the running test.
    """

    def __init__(self, command_name, command_to_run, result_keywords_array=None, fault_keyword=None,
                 command_result=None,
                 command_result_err=None,
                 is_successful=False):
        super(CommandVerification, self).__init__(command_name, command_to_run, result_keywords_array, fault_keyword,
                                                  command_result, command_result_err)
        self.is_successful = is_successful

    def __repr__(self):
        """
        Printing the command details in a built-in format
        """
        command_repr = super(CommandVerification, self).__repr__()
        return str(command_repr + "Is successful: " + str(self.is_successful) + DELIMITER + '\n').replace(
            '%', '%%').replace('\\n', '\n')

    def is_command_successful(self, exclude=False, should_fail=False, should_increase=True, should_warn=False):
        """
        Verifying the command output indicates success. It's done by searching for keywords in the result
        :param exclude: If true, will verify the keywords do not exist in the command result
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

    def calc_is_command_successful(self, exclude=False, should_fail=False):
        """
        Verifying the command output indicates success. It's done by searching for keywords in the result
        :param exclude: If true, will verify the keywords do not exist in the command result
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

    def print_result_to_prompt(self):
        """
        Printing the test's name and success status to the customer's prompt
        """
        max_length = 47
        if self.is_successful == "Skip":
            print_warning(self.command_name + "-" * (max_length - len(self.command_name)) + "> Failed to check")
        elif self.is_successful == "Warn":
            print_warning(self.command_name + "-" * (max_length - len(self.command_name)) + "> Warning")
        elif self.is_successful:
            print_ok(self.command_name + "-" * (max_length - len(self.command_name)) + "> Success")
        else:
            print_error(self.command_name + "-" * (max_length - len(self.command_name)) + "> Failure")

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
            print(str(self.command_name) + "was not documented successfully")
        output_file.close()

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

    def run_full_test(self, exclude=False, should_increase=True, should_warn=False):
        """
        A simple way to run a full test-executing the command, validating its result, printing it to the prompt and logging it to a file
        :param exclude: A parameter given to the is_command_successful function.
        :param should_increase: If false, FAILED_TESTS_COUNT and NOT_RUN_TESTS_COUNT will not be increased
        :param should_warn: If True, self.is_successful value will be "Warn"
        """
        self.run_command()
        self.is_command_successful(exclude=exclude, should_increase=should_increase, should_warn=should_warn)
        self.print_result_to_prompt()
        self.log_result_to_file()


class AgentInstallationVerifications:
    """
    This class is for agent related verifications
    """
    # CONSTANTS
    AGENT_INSTALLATION_DOC = "https://docs.microsoft.com/azure/azure-monitor/agents/azure-monitor-agent-manage"
    AGENT_NOT_INSTALLED_ERROR_MESSAGE = "Could not detect an AMA service running and listening on the machine." \
                                        " Please follow this documentation in order to install it and verify your" \
                                        " machine's operating system is in the supported list- {}".format(
        AGENT_INSTALLATION_DOC)
    AGENT_NOT_RUNNING_ERROR_MESSAGE = "Detected AMA is installed on the machine but not running. Please start the agent by running " \
                                      "\'service azuremonitoragent start\' \nif the agent service fails to start," \
                                      " please run the following command to review the agent error log file here- " \
                                      "\'cat /var/opt/microsoft/azuremonitoragent/log/mdsd.err | tail -n 15\'".format(
        AGENT_INSTALLATION_DOC)

    OMS_RUNNING_ERROR_MESSAGE = "Detected the OMS Agent running on your machine. If not necessary please remove it to avoid duplicated data in the workspace, which can result in an increase in costs"

    def verify_agent_is_running(self):
        global AGENT_VERSION
        """
        Verifying the agent service called mdsd is listening on its default port
        """
        command_name = "verify_ama_agent_service_is_running"
        command_to_run = "sudo systemctl status azuremonitoragent"
        result_keywords_array = ["azuremonitoragent.service", "Azure", "Monitor", "Agent", "active", "running"]
        command_object = CommandVerification(command_name, command_to_run, result_keywords_array)
        command_object.run_full_test()
        if not command_object.is_successful:
            if ("could not be found" or "no such service") in command_object.command_result:
                command_object.is_successful = False
                print_error(self.AGENT_NOT_INSTALLED_ERROR_MESSAGE)
                return False
            else:
                print_error(self.AGENT_NOT_RUNNING_ERROR_MESSAGE)
        else:
            command_object.command_to_run = "sudo /opt/microsoft/azuremonitoragent/bin/mdsd -V"
            command_object.run_command()
            AGENT_VERSION = str(command_object.command_result)
            print_ok(
                "Detected AMA running version- {}".format(AGENT_VERSION))

    @staticmethod
    def is_agent_version_updated():
        """
        Starting from agent version of 1.28.11 the forwarding mechanism of the agent changed.
        This function tess whether the agent on the machine is running with this updated agent version.
        """
        global IS_AGENT_VERSION_UPDATED
        IS_AGENT_VERSION_UPDATED = StrictVersion(UPDATED_AGENT_VERSION) <= StrictVersion(AGENT_VERSION)

    @staticmethod
    def print_arc_version():
        """
        Checking if ARC is installed. If so- prints the version of it.
        """
        command_name = "print_arc_version"
        command_to_run = "azcmagent version"
        command_object = CommandVerification(command_name, command_to_run)
        command_object.run_command()
        if "azcmagent version" in str(command_object.command_result) and "command not found" not in str(
                command_object.command_result):
            print_notice("Detected ARC installed on the machine: {}".format(
                command_object.command_result))

    def verify_oms_not_running(self):
        """
        Verify the old MMA agent is not running together with the new AMA agent.
        """
        command_name = "verify_oms_agent_not_running"
        command_to_run = "sudo netstat -lnpvt | grep ruby"
        result_keywords_array = ["25226", "LISTEN", "tcp"]
        command_object = CommandVerification(command_name, command_to_run, result_keywords_array)
        command_object.run_full_test(exclude=True)
        if command_object.is_successful == "Skip":
            print_warning(command_object.command_result_err)
        elif not command_object.is_successful:
            print_warning(self.OMS_RUNNING_ERROR_MESSAGE)

    def run_all_verifications(self):
        """
        This function is only called by main and runs all the tests in this class
        """
        self.verify_agent_is_running()
        self.print_arc_version()
        self.verify_oms_not_running()
        self.is_agent_version_updated()



class DCRConfigurationVerifications:
    """
    This class is for data collection rules verifications
    """
    # CONSTANTS
    DCR_DOC = "https://docs.microsoft.com/azure/azure-monitor/agents/data-collection-rule-overview"
    DCRA_DOC = "https://docs.microsoft.com/rest/api/monitor/data-collection-rule-associations"
    CEF_STREAM_NAME = "SECURITY_CEF_BLOB"
    CISCO_STREAM_NAME = "SECURITY_CISCO_ASA_BLOB"
    SYSLOG_STREAM_NAME = "LINUX_SYSLOGS_BLOB"
    STREAM_NAME = {"cef": CEF_STREAM_NAME, "asa": CISCO_STREAM_NAME, "syslog": SYSLOG_STREAM_NAME}
    DCR_MISSING_ERR = "Could not detect any data collection rule on the machine. The data reaching this server will not be forwarded to any workspace." \
                      " For explanation on how to install a Data collection rule please browse- {} \n " \
                      "In order to read about how to associate a DCR to a machine please review- {}".format(DCR_DOC,
                                                                                                            DCRA_DOC)
    DCR_MISSING_CEF_STREAM_ERR = "Could not detect any data collection rule for the provided datatype. No such events will " \
                                 "be collected from this machine to any workspace. Please create a DCR using the following documentation- " \
                                 "{} and run again".format(DCR_DOC)
    MULTI_HOMING_MESSAGE = "Detected multiple collection rules sending the same stream. This scenario is called multi-homing and might have effect on the agent's performance"

    def verify_dcr_exists(self):
        """
        Verifying there is at least one dcr on the machine
        """
        command_name = "verify_DCR_exists"
        command_to_run = "sudo ls -l /etc/opt/microsoft/azuremonitoragent/config-cache/configchunks/"
        result_keywords_array = [".json"]
        command_object = CommandVerification(command_name, command_to_run, result_keywords_array)
        command_object.run_full_test()
        if not command_object.is_successful:
            print_error(self.DCR_MISSING_ERR)
            return False
        return True

    def verify_dcr_content_has_stream(self, dcr_stream):
        """
        Verifying there is a DCR on the machine for forwarding cef data
        """
        global STREAM_SCENARIO
        command_name = "verify_DCR_content_has_stream"
        command_to_run = "sudo grep -ri \"{}\" /etc/opt/microsoft/azuremonitoragent/config-cache/configchunks/".format(
            self.STREAM_NAME[dcr_stream])
        result_keywords_array = [self.STREAM_NAME[dcr_stream]]
        command_object = CommandVerification(command_name, command_to_run, result_keywords_array)
        command_object.run_full_test()
        if not command_object.is_successful:
            print_error(self.DCR_MISSING_CEF_STREAM_ERR)
            return False
        return True

    def verify_dcr_has_valid_content(self, dcr_stream):
        """
        Verifying that the CEF DCR on the machine has valid content with all necessary DCR components
        """
        global STREAM_SCENARIO
        command_name = "verify_dcr_has_valid_content"
        command_to_run = "sudo grep -ri \"{}\" /etc/opt/microsoft/azuremonitoragent/config-cache/configchunks/".format(
            self.STREAM_NAME[dcr_stream])
        result_keywords_array = ["stream", "kind", "syslog", "dataSources", "configuration", "facilityNames",
                                 "logLevels", "SecurityInsights", "endpoint", "channels", "sendToChannels", "ods-",
                                 "opinsights.azure", "id"]
        command_object = CommandVerification(command_name, command_to_run, result_keywords_array)
        command_object.run_command(should_decode=False)
        command_object.command_result = command_object.command_result.decode('UTF-8').split('\n')[:-1]
        for dcr in command_object.command_result:
            dcr_path = re.search("(/etc/opt/microsoft/azuremonitoragent/config-cache/configchunks/.*.json)",
                                 str(dcr)).group()
            for key_word in command_object.result_keywords_array:
                if str(key_word) not in str(dcr):
                    command_object.is_command_successful(should_fail=True)
                    print_error(
                        "Found an invalid DCR. It is missing this key-word \'{}\'. It's path is {}".format(key_word,
                                                                                                           dcr_path))
                    return False
        command_object.run_full_verification()

    def check_multi_homing(self, dcr_stream):
        """
        Counting the amount of DCRs forwarding CEF data in order to alert from multi-homing scenarios.
        """
        global STREAM_SCENARIO
        command_name = "check_multi_homing"
        command_to_run = "sudo grep -ri \"{}\" /etc/opt/microsoft/azuremonitoragent/config-cache/configchunks/ | wc -l".format(
            self.STREAM_NAME[dcr_stream])
        command_object = CommandVerification(command_name, command_to_run)
        command_object.run_command()
        try:
            if int(command_object.command_result) > 1:
                command_object.run_full_verification(should_fail=True)
                print_warning(self.MULTI_HOMING_MESSAGE)
            else:
                command_object.is_successful = True
                command_object.document_result()
        except ValueError:
            command_object.run_full_verification(should_fail=True)
            print_warning("Failed to run this test since no DCRs were found")

    def run_all_verifications(self):
        """
        This function is only called by main and runs all the tests in this class
        """
        dcr_stream = 'asa' if STREAM_SCENARIO == 'ftd' else STREAM_SCENARIO
        if not self.verify_dcr_exists():
            return False
        if not self.verify_dcr_content_has_stream(dcr_stream):
            return False
        self.verify_dcr_has_valid_content(dcr_stream)
        self.check_multi_homing(dcr_stream)


class SyslogDaemonVerifications:
    """
    This class is for Syslog daemon related verifications
    """

    def __init__(self):
        self.command_name = "verify_Syslog_daemon_listening"
        self.SYSLOG_DAEMON = ""
        self.syslog_daemon_forwarding_path_old = {"rsyslog": "/etc/rsyslog.d/10-azuremonitoragent.conf",
                                              "syslog-ng": "/etc/syslog-ng/conf.d/azuremonitoragent.conf"}
        self.syslog_daemon_forwarding_path_new = {"rsyslog": "/etc/rsyslog.d/10-azuremonitoragent-omfwd.conf",
                                                  "syslog-ng": "/etc/syslog-ng/conf.d/azuremonitoragent-tcp.conf"}
        self.No_Syslog_daemon_error_message = "Could not detect any running Syslog daemon on the machine. The supported Syslog daemons are Rsyslog and Syslog-ng. Please install one of them and run this script again."
        self.Syslog_daemon_not_listening_warning = "Warning: the Syslog daemon- {} is running but not listening on the machine or is listening to a non-default port"
        self.Syslog_daemon_not_forwarding_error = "{} configuration was found invalid in this file {}. The forwarding of the syslog daemon to the agent might not work. Please install the agent in order to get the updated Syslog daemon forwarding configuration file, and try again."

    def determine_syslog_daemon(self):
        """
        This function is in order to determine what Syslog daemon is running on the machine (Rsyslog or Syslog-ng)
        """
        is_rsyslog_running = CommandVerification("find_Rsyslog_daemon",
                                                 "if [ `ps -ef | grep rsyslog | grep -v grep | wc -l` -gt 0 ]; then echo \"True\"; else echo \"False\"; fi")
        is_syslog_ng_running = CommandVerification("find_Syslog-ng_daemon",
                                                   "if [ `ps -ef | grep syslog-ng | grep -v grep | wc -l` -gt 0 ]; then echo \"True\"; else echo \"False\"; fi")
        is_rsyslog_running.run_command(), is_syslog_ng_running.run_command()
        if "True" in str(is_rsyslog_running.command_result):
            self.SYSLOG_DAEMON = "rsyslog"
            return True
        elif "True" in str(is_syslog_ng_running.command_result):
            self.SYSLOG_DAEMON = "syslog-ng"
            return True
        is_rsyslog_running.log_result_to_file()
        is_syslog_ng_running.log_result_to_file()
        return False

    def verify_syslog_daemon_listening(self):
        """
        Verifying the Syslog daemon is listening on the default 514 port for incoming traffic
        """
        command_to_run = "sudo netstat -lnpv | grep " + self.SYSLOG_DAEMON
        result_keywords_array = [self.SYSLOG_DAEMON, ":514 "]
        command_object = CommandVerification(self.command_name, command_to_run, result_keywords_array)
        command_object.run_command()
        command_object.is_command_successful(should_increase=False)
        if command_object.is_successful is not False:
            command_object.document_result()
            if command_object.is_successful == "Skip":
                print_warning(command_object.command_result_err)
        else:
            # In case we don't find any daemon on port 514 we will make sure it's not listening to TLS port: 6514
            result_keywords_array = [self.SYSLOG_DAEMON, ":6514 "]
            command_object = CommandVerification(self.command_name, command_to_run, result_keywords_array)
            command_object.run_full_test(should_warn=True)
            if command_object.is_successful == "Warn":
                print_warning(self.Syslog_daemon_not_listening_warning.format(self.SYSLOG_DAEMON))

    def verify_syslog_daemon_forwarding_configuration_pre_1_28(self):
        """
        Verify the syslog daemon forwarding configuration file has the correct forwarding configuration to the Unix domain socket.
        This function will be used in case the script detects the agent running is of a version older than 1.28.11.
        """
        if self.SYSLOG_DAEMON != "":
            syslog_daemon_forwarding_keywords = {
                "rsyslog": ['omuxsock', 'azuremonitoragent', 'OMUxSockSocket', 'OMUxSockDefaultTemplate'],
                "syslog-ng": ['destination', 'd_azure_mdsd', 'unix-dgram', 'azuremonitoragent', 'syslog', 'socket',
                              's_src']}
            command_name = "verify_Syslog_daemon_forwarding_configuration"
            command_to_run = "sudo cat " + self.syslog_daemon_forwarding_path_old[self.SYSLOG_DAEMON]
            result_keywords_array = syslog_daemon_forwarding_keywords[self.SYSLOG_DAEMON]
            command_object = CommandVerification(command_name, command_to_run, result_keywords_array)
            command_object.run_full_test()
            if not command_object.is_successful:
                print_error(self.Syslog_daemon_not_forwarding_error.format(self.SYSLOG_DAEMON,
                                                                           self.syslog_daemon_forwarding_path_old[
                                                                               self.SYSLOG_DAEMON]))

    def verify_syslog_daemon_forwarding_configuration_post_1_28(self):
        """
        Verify the syslog daemon forwarding configuration file has the correct forwarding configuration to the Unix domain socket.
        This function will be used in case the script detects the agent running is of a version later than 1.28.11.
        """
        if self.SYSLOG_DAEMON != "":
            syslog_daemon_forwarding_keywords = {
                "rsyslog": ['omfwd', 'azuremonitoragent', 'LinkedList', 'tcp'],
                "syslog-ng": ['destination', 'd_azure_mdsd', 'log-fifo-size', 's_src', 'flow-control']}
            command_name = "verify_Syslog_daemon_forwarding_configuration"

            command_to_run = "sudo cat " + self.syslog_daemon_forwarding_path_new[self.SYSLOG_DAEMON]
            result_keywords_array = syslog_daemon_forwarding_keywords[self.SYSLOG_DAEMON]
            command_object = CommandVerification(command_name, command_to_run, result_keywords_array)
            command_object.run_full_test()
            if not command_object.is_successful:
                print_error(self.Syslog_daemon_not_forwarding_error.format(self.SYSLOG_DAEMON,
                                                                           self.syslog_daemon_forwarding_path_new[
                                                                               self.SYSLOG_DAEMON]))


    def run_all_verifications(self):
        """
        This function is only called by main and runs all the tests in this class
        """
        global FAILED_TESTS_COUNT
        if self.determine_syslog_daemon():
            self.verify_syslog_daemon_listening()
            if IS_AGENT_VERSION_UPDATED:
                self.verify_syslog_daemon_forwarding_configuration_post_1_28()
            else:
                self.verify_syslog_daemon_forwarding_configuration_pre_1_28()
        else:
            mock_command = CommandVerification(self.command_name, "")
            mock_command.print_result_to_prompt()
            print_error(self.No_Syslog_daemon_error_message)
            FAILED_TESTS_COUNT += 1


class OperatingSystemVerifications:
    """
    This class is for general operating system verifications
    """
    # CONSTANTS
    SELINUX_DOCUMENTATION = "https://access.redhat.com/documentation/red_hat_enterprise_linux/8/html/using_selinux/changing-selinux-states-and-modes_using-selinux#changing-selinux-modes_changing-selinux-states-and-modes"
    SELINUX_RUNNING_ERROR_MESSAGE = "Detected SELinux running on the machine. The agent version running on the machine is outdated and does not support ingestion with hardening." \
                                    "Please update to the latest Agent version or disable SELINUX by running: the command \'setenforce 0\'." \
                                    "This will disable SELinux temporarily, as it can harm the data ingestion. In order to disable it permanently please follow this documentation- {}".format(
        SELINUX_DOCUMENTATION)
    IPTABLES_BLOCKING_TRAFFIC_ERROR_MESSAGE = "Iptables might be blocking incoming traffic to the agent." \
                                              " Please verify there are no firewall rules blocking incoming traffic to port {} and run again."
    FULL_DISK_ERROR_MESSAGE = "There is less than 1 GB of free disk space left on this machine." \
                              " Having a full disk can harm the agent functionality and eventually cause data loss" \
                              " Please free disk space on this machine and run again."

    def verify_selinux_state(self):
        """
        Verify SELinux is not in enforcing mode, which can harm the events' forwarding to the agent.
        """
        command_name = "verify_selinux_state"
        command_to_run = "sudo getenforce 2> /dev/null; if [ $? != 0 ]; then echo 'Disabled'; fi"
        result_keywords_array = ["Enforcing"]
        command_object = CommandVerification(command_name, command_to_run, result_keywords_array)
        if StrictVersion(AGENT_VERSION) < StrictVersion(AGENT_MIN_HARDENING_VERSION):
            command_object.run_full_test(True)
            if not command_object.is_successful:
                print_error(self.SELINUX_RUNNING_ERROR_MESSAGE)
        else:
            command_object.is_successful = True
            command_object.print_result_to_prompt()

    def verify_iptables(self):
        """
        Verify there is no firewall rule in the iptables blocking the Syslog daemon or agent incoming ports
        """
        command_name = "verify_iptables_policy_permissive"
        command_to_run = "sudo iptables -S | grep \\\\-P | grep -E 'INPUT|OUTPUT'"
        result_keywords_array = ["DROP", "REJECT"]
        policy_command_object = CommandVerification(command_name, command_to_run, result_keywords_array)
        policy_command_object.run_full_test(exclude=True)
        if policy_command_object.is_successful == "Skip":
            print_warning(policy_command_object.command_result_err)
            return True
        command_name = "verify_iptables_rules_permissive_514"
        command_to_run = "sudo iptables -S | grep -E '514' | grep INPUT"
        rules_command_object = CommandVerification(command_name, command_to_run, result_keywords_array)
        rules_command_object.run_full_test(exclude=True)
        if (not rules_command_object.is_successful or (not policy_command_object.is_successful and (
                not rules_command_object.is_successful or rules_command_object.command_result == ""))):
            print_warning(self.IPTABLES_BLOCKING_TRAFFIC_ERROR_MESSAGE.format('514'))
        if IS_AGENT_VERSION_UPDATED:
            command_name = "verify_iptables_rules_permissive_28330"
            command_to_run = "sudo iptables -S | grep -E '28330' | grep INPUT"
            rules_command_object = CommandVerification(command_name, command_to_run, result_keywords_array)
            rules_command_object.run_full_test(exclude=True)
            if (not rules_command_object.is_successful or (not policy_command_object.is_successful and (
                    not rules_command_object.is_successful or rules_command_object.command_result == ""))):
                print_warning(self.IPTABLES_BLOCKING_TRAFFIC_ERROR_MESSAGE.format('28330'))

    def verify_free_disk_space(self):
        """
        Verify there is enough free disk space on the machine for the event forwarding to work as expected. The minimum is set to 1 GB
        """
        minimal_free_space_kb = 1048576
        command_name = "verify_free_disk_space"
        command_to_run = "sudo df --output=avail / | head -2 | tail -1"
        command_object = CommandVerification(command_name, command_to_run)
        command_object.run_command()
        if int(command_object.command_result) < minimal_free_space_kb:
            command_object.run_full_verification(should_fail=True)
            print_error(self.FULL_DISK_ERROR_MESSAGE)
        else:
            command_object.is_successful = True
            command_object.document_result()

    def run_all_verifications(self):
        """
        This function is only called by main and runs all the tests in this class
        """
        self.verify_selinux_state()
        self.verify_iptables()
        self.verify_free_disk_space()


class IncomingEventsVerifications:
    """
    This class is for sending and capturing CEF events in the incoming stream of events to the syslog daemon port
    """
    # CONSTANTS
    FIXED_CEF_MESSAGE = "0|TestCommonEventFormat|MOCK|common=event-format-test|end|TRAFFIC|1|rt=$common=event-formatted-receive_time deviceExternalId=0002D01655 src=1.1.1.1 dst=2.2.2.2 sourceTranslatedAddress=1.1.1.1 destinationTranslatedAddress=3.3.3.3 cs1Label=Rule cs1=CEF_TEST_InternetDNS"
    FIXED_CISCO_MESSAGE = "Deny inbound TCP src inet:1.1.1.1 dst inet:2.2.2.2"
    FIXED_FTD_MESSAGE = "Teardown dynamic UDP translation from inside:10.51.100.1/54453 to outside:10.0.2.3/54453 duration 0:00:00"
    FIXED_SYSLOG_MESSAGE = "Started Daily apt upgrade and clean activities"
    STREAM_MESSAGE = {"cef": FIXED_CEF_MESSAGE, "asa": FIXED_CISCO_MESSAGE, "ftd": FIXED_FTD_MESSAGE, "syslog": FIXED_SYSLOG_MESSAGE}
    IDENT_NAME = {"cef": "CEF", "asa": "%ASA-7-106010", 'ftd': "%FTD-6-305012", 'syslog': "systemd"}
    TCPDUMP_NOT_INSTALLED_ERROR_MESSAGE = "Notice that \'tcpdump\' is not installed in your Linux machine.\nWe cannot monitor traffic without it.\nPlease install \'tcpdump\'."
    LOGGER_NOT_INSTALLED_ERROR_MESSAGE = "Warning: Could not execute \'logger\' command. This means that no mock message was sent to your workspace."
    LINUX_HARDENING_DOC = "https://learn.microsoft.com/he-il/azure/azure-monitor/agents/agents-overview#linux-hardening-standards"

    @staticmethod
    def check_stream_in_line(line, ident):
        """
        Validate there are incoming events for the relevant stream.
        :param line: a text line from the tcpdump stream
        :param ident: The message tag to look for in the message line.
        :return: True if the stream exists in the line. Otherwise, false.
        """
        if ident in line:
            return True
        return False

    def incoming_logs_validations(self, mock_message=False):
        """
        Validate that there is incoming traffic of the stream type
        :param mock_message: Tells if to generate mock messages
        :return: True if successfully captured events of the relevant stream.
        """
        tcpdump_time_restriction = 10
        start_seconds = int(round(time.time()))
        end_seconds = int(round(time.time()))
        mock_message_counter = 0
        command_name = "listen_to_incoming_events"
        command_to_run = "sudo tcpdump -A -l -ni any port 514 -vv"
        result_keywords_array = [STREAM_SCENARIO.upper()]
        command_object = CommandVerification(command_name, command_to_run, result_keywords_array)
        print("Attempting to capture events using tcpdump. This could take up to " + str(
            tcpdump_time_restriction) + " seconds.")
        tcp_dump = subprocess.Popen(command_object.command_to_run, shell=True, stdout=subprocess.PIPE,
                                    stderr=subprocess.STDOUT)
        line = str(tcp_dump.stdout.readline().decode('utf-8').strip("\n"))
        # Handle command not found
        if "command not found" in line:
            print(self.TCPDUMP_NOT_INSTALLED_ERROR_MESSAGE)
            command_object.command_result = line
            command_object.run_full_verification()
            return False
        poll_obj = select.poll()
        poll_obj.register(tcp_dump.stdout, select.POLLIN)
        while (end_seconds - start_seconds) < tcpdump_time_restriction:
            if mock_message and mock_message_counter < 10:
                # Sending mock messages
                mock_message_counter += 1
                self.send_message_local(514, 1)
            poll_result = poll_obj.poll(0)
            if poll_result:
                line = tcp_dump.stdout.readline().decode('utf-8').strip("\n")
                if self.check_stream_in_line(line, STREAM_SCENARIO.upper()):
                    command_object.command_result = line
                    command_object.run_full_verification()
                    print_ok("Found {0} in stream. Please verify {0} events arrived at your workspace".format(
                        STREAM_SCENARIO.upper()))
                    return True
            end_seconds = int(round(time.time()))
        print_error("Could not locate {0} message in tcpdump. Please verify {0} events can be sent to the machine and"
                    " there is not firewall blocking incoming traffic".format(STREAM_SCENARIO.upper()))
        if mock_message:
            print_warning("In case hardening is in place please refer to this documentation in order to verify it's configured correctly- "
                       "{}".format(self.LINUX_HARDENING_DOC))
        command_object.command_result = str(line)
        command_object.run_full_verification()
        return False

    def send_message_local(self, port, amount):
        """
        Generate local CEF events in a given amount to a given port
        :param port: A destination port to send the events
        :param amount: The amount of events to send
        """
        try:
            for index in range(0, amount):
                command_tokens = ["logger", "-p", "local4.warn", "-t", self.IDENT_NAME[STREAM_SCENARIO],
                                  self.STREAM_MESSAGE[STREAM_SCENARIO], "--rfc3164", "-P", str(port), "-n", "127.0.0.1"]
                logger = subprocess.Popen(command_tokens, stdout=subprocess.PIPE)
                o, e = logger.communicate()
                if e is not None:
                    print("Error could not send mock message")
        except OSError:
            print(self.LOGGER_NOT_INSTALLED_ERROR_MESSAGE)

    def run_all_verifications(self):
        """
        This function is only called by main and runs all the tests in this class
        """
        if not self.incoming_logs_validations():
            print_notice("\nGenerating mock events and trying again")
            self.incoming_logs_validations(mock_message=True)


class SystemInfo:
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
        "agent_log_snip_err": ["sudo tail -n 100 /var/opt/microsoft/azuremonitoragent/log/mdsd.err"],
        "agent_log_snip_warn": ["sudo tail -n 100 /var/opt/microsoft/azuremonitoragent/log/mdsd.warn"],
        "agent_log_snip_info": ["sudo tail -n 100 /var/opt/microsoft/azuremonitoragent/log/mdsd.info"],
        "is_AMA__running_from_boot": ["sudo systemctl list-unit-files --type=service | grep azuremonitoragent"],
        "AMA_service_status": ["sudo systemctl status azuremonitoragent"],
        "DCR_config_dir": ["sudo ls -la /etc/opt/microsoft/azuremonitoragent/config-cache/configchunks/"],
        "messages_log_snip": ["sudo tail -n 15 /var/log/messages"],
        "syslog_log_snip": ["sudo tail -n 15 /var/log/syslog"],
        "top_processes": ["sudo top -bcn1 -w512 | head -n 20"],
    }

    @staticmethod
    def format_collect_command(command_object):
        """
        Format a collect command details in a built-in format
        """
        return str(
            DELIMITER + "command: " + str(command_object.command_name) + '\n' + "output:\n" + str(
                command_object.command_result) + DELIMITER).replace(
            '%', '%%').replace('\\n', '\n')

    @staticmethod
    def trace_activation():
        flag = '-T 0x1002'
        file_path = '/etc/default/azuremonitoragent'
        # Check if the flag already exists
        check_if_trace_exists = "sed -n '/^MDSD_OPTIONS=.*{}/p' {}".format(flag, file_path)
        flag_exists = subprocess.call(check_if_trace_exists, shell=True) == 0
        agent_restart_command = "sudo systemctl restart azuremonitoragent"
        if not flag_exists:
            # Add the flag using sed
            sed_command = "sed -i 's/\\(MDSD_OPTIONS=\".*\\)\"/\\1 {}\"/' {}".format(flag, file_path)
            subprocess.call(sed_command, shell=True)
            subprocess.call(agent_restart_command, shell=True)
        # Sleep for 10 seconds
        time.sleep(10)
        # Remove the flag using sed
        sed_command = "sed -i 's/ {}//' {}".format(flag, file_path)
        subprocess.call(sed_command, shell=True)
        subprocess.call(agent_restart_command, shell=True)

    def append_content_to_file(self, command_object, file_path=LOG_OUTPUT_FILE):
        """
        :param command_object: consists of the name and the output
        :param file_path: a file to share the commands outputs
        """
        output = self.format_collect_command(command_object)
        cef_get_info_file = open(file_path, 'a')
        try:
            cef_get_info_file.write(output)
        except Exception:
            print(str(command_object.command_name) + "was not documented successfully")
        cef_get_info_file.close()

    def handle_commands(self):
        """
        This function handles the whole command flow from running to documenting.
        """
        self.trace_activation()
        for command_name in self.commands_dict.keys():
            command_object = CommandVerification(command_name, self.commands_dict[command_name])
            command_object.run_command()
            self.append_content_to_file(command_object)


def verify_root_privileges():
    """
    Verify user has root privileges that required to execute this script
    """
    o, e = subprocess.Popen(['id', '-u'], stdout=subprocess.PIPE, stderr=subprocess.STDOUT).communicate()
    if int(o) != 0:
        print_error(
            "This script must be run in elevated privileges since some of the tests require root privileges")
        exit()


def find_dcr_cloud_environment():
    """
    Use the agent config on the machine to determine the cloud environment we are running in
    """
    command_to_run = "if grep -qs \"azure.cn\" {0}; then echo \"MK\"; elif grep -qs \"azure.us\" {0}; then echo \"Gov\"; else echo \"Prod\"; fi".format(
        AGENT_CONF_FILE)
    try:
        command_result, command_result_err = subprocess.Popen(command_to_run, shell=True,
                                                              stdout=subprocess.PIPE,
                                                              stderr=subprocess.STDOUT).communicate()
        machine_env = command_result.decode('utf-8').strip("\n")
        return machine_env if machine_env is not None else DEFAULT_MACHINE_ENV
    except Exception:
        return DEFAULT_MACHINE_ENV


def getargs():
    """
    Get execution args using argparse lib
    """
    global STREAM_SCENARIO
    parser = argparse.ArgumentParser()
    parser.add_argument('collect', nargs='?',
                        help='runs the script in collect mode. Useful in case you want to open a ticket.')
    parser.add_argument('--CEF', '--cef', action='store_true', default=False,
                        help='run the troubleshooting script for the CEF scenario.')
    parser.add_argument('--ASA', '--asa', action='store_true', default=False,
                        help='run the troubleshooting script for the Cisco ASA scenario.')
    parser.add_argument('--FTD', '--ftd', action='store_true', default=False,
                        help='run the troubleshooting script for the Cisco FTD scenario.')
    parser.add_argument('--SYSLOG', '--syslog', action='store_true', default=False,
                        help='run the troubleshooting script for the Syslog scenario.')
    args = parser.parse_args()
    if args.ASA:
        STREAM_SCENARIO = "asa"
    elif args.FTD:
        STREAM_SCENARIO = "ftd"
    elif args.SYSLOG:
        STREAM_SCENARIO = "syslog"
    else:
        STREAM_SCENARIO = "cef"
    return args


def print_scenario(args):
    """
    param: args: the arguments returned from the getargs function
    """
    if list(vars(args).values()).count(True) > 1:
        print_error("More than 1 stream provided. Please run the script again with only one scenario.\n"
                    "For more information run 'python Sentinel_AMA_troubleshoot.py -h'. Exiting.")
        sys.exit(1)
    else:
        print_notice("The scenario chosen is: {}".format(STREAM_SCENARIO.upper()))


def main():
    args = getargs()
    verify_root_privileges()
    subprocess.Popen(['rm', '-f', LOG_OUTPUT_FILE],
                     stdout=subprocess.PIPE, stderr=subprocess.STDOUT).communicate()
    print_scenario(args)
    if args.collect:
        print_notice("Starting to collect data. This may take a couple of seconds")
        machine_env = find_dcr_cloud_environment()
        time.sleep(2)
        system_info = SystemInfo()
        system_info.handle_commands()
        print(
            "Finished collecting data \nIn order to open a support case please browse: {}".format(
                PATH_FOR_CSS_TICKET[machine_env]))
        with open(LOG_OUTPUT_FILE, 'a') as file:
            file.write('*' * 10 + 'FINISHED COLLECTION' + '*' * 10)
        time.sleep(1)

    class_tests_array = [
        (AgentInstallationVerifications(), "Starting validation tests for AMA"),
        (DCRConfigurationVerifications(), "Starting validation tests for data collection rules"),
        (SyslogDaemonVerifications(), "Starting validation tests for the Syslog daemon"),
        (OperatingSystemVerifications(), "Starting validation tests for the operating system"),
        (IncomingEventsVerifications(), "Starting validation tests for capturing incoming events")]
    print_notice("\nStarting to run the validation script for the {} scenario".format(STREAM_SCENARIO))
    time.sleep(1)
    print_notice("Please validate you are sending messages to the agent machine")
    for class_test in class_tests_array:
        print_notice("\n----- {} {}".format(class_test[1], '-' * (60 - len(class_test[1]))))
        verification_object = class_test[0]
        verification_object.run_all_verifications()
    if NOT_RUN_TESTS_COUNT > 0:
        print_warning("\nTotal amount of tests that failed to run: " + str(NOT_RUN_TESTS_COUNT))
    if WARNING_TESTS_COUNT > 0:
        print_warning("\nTotal amount of tests that ended with a warning status is: " + str(WARNING_TESTS_COUNT))
    if FAILED_TESTS_COUNT > 0:
        print_error("\nTotal amount of failed tests is: " + str(FAILED_TESTS_COUNT))
    else:
        print_ok("All tests passed successfully")
    print_notice("This script generated an output file located here - {}"
                 "\nPlease review it if you would like to get more information on failed tests.".format(
        LOG_OUTPUT_FILE))
    if not args.collect:
        print_notice(
            "\nIf you would like to open a support case please run this script with the \'collect\' feature flag in order to collect additional system data for troubleshooting."
            "\'python Sentinel_AMA_troubleshoot.py [STREAM_OPTION] collect\'")


if __name__ == '__main__':
    main()
