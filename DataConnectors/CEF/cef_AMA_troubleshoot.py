import subprocess
import time
import select

LOG_OUTPUT_FILE = "/tmp/cef_troubleshooter_output_file"
FAILED_TESTS_COUNT = 0


class ColorfulPrint:
    '''
    This class is in order to print text in color according to the severity level.
    '''

    def print_error(self, input_str):
        '''
        Print given text in red color for Error text
        :param input_str:
        '''
        print("\033[1;31;40m" + input_str + "\033[0m")

    def print_ok(self, input_str):
        '''
        Print given text in green color for Ok text
        :param input_str:
        '''
        print("\033[1;32;40m" + input_str + "\033[0m")

    def print_warning(self, input_str):
        '''
        Print given text in yellow color for warning text
        :param input_str:
        '''
        print("\033[1;33;40m" + input_str + "\033[0m")

    def print_notice(self, input_str):
        '''
        Print given text in white background
        :param input_str:
        '''
        print("\033[0;30;47m" + input_str + "\033[0m")


class BasicCommand(ColorfulPrint):
    '''
    This class is for creating a command object. The object has execution, validation and documentation functions
    '''

    def __init__(self, command_name, command_to_run, result_keywords_array=[], command_result=None,
                 command_result_err=None,
                 is_successful=False):
        self.command_name = command_name
        self.command_to_run = command_to_run
        self.result_keywords_array = result_keywords_array
        self.command_result = command_result
        self.command_result_err = command_result_err
        self.is_successful = is_successful

    def __repr__(self):
        '''
        Printing the command details in a built in format
        '''
        delimiter = "\n" + "-" * 20 + "\n"
        return str(
            delimiter + "command name: " + str(self.command_name) + '\n' + "command to run: " + str(
                self.command_to_run) + '\n' +
            "command output: " + str(self.command_result) + '\n' + "command error output: " + str(
                self.command_result_err) + '\n' +
            "command array verification: " + str(self.result_keywords_array) + '\n' + "Is successful: " + str(
                self.is_successful) +
            delimiter).replace(
            '%',
            '%%')

    def run_command(self):
        '''
        Running the bash commands using the subprocess library
        :return:
        '''
        try:
            self.command_result, self.command_result_err = subprocess.Popen(self.command_to_run, shell=True,
                                                                            stdout=subprocess.PIPE,
                                                                            stderr=subprocess.STDOUT).communicate()
        except Exception:
            self.command_result_err = "Error processing command"

    def is_command_successful(self, exclude=False):
        '''
        Verifying the command output indicates success. It's done by searching for key words in the result
        :param exclude: If true, will verify the key words do not exist in the command result
        :return: True if successful otherwise False.
        '''
        global FAILED_TESTS_COUNT
        if self.command_result_err is None and self.command_result is not None:
            for key_word in self.result_keywords_array:
                if exclude:
                    if key_word in self.command_result:
                        self.is_successful = False
                        FAILED_TESTS_COUNT += 1
                        return False
                elif key_word not in self.command_result:
                    self.is_successful = False
                    FAILED_TESTS_COUNT += 1
                    return False
            self.is_successful = True
            return True
        self.is_successful = False
        FAILED_TESTS_COUNT += 1
        return False

    def print_result_to_prompt(self):
        '''
        Printing the tests' name and success status to the customer's prompt
        '''
        max_length = 47
        if self.is_successful:
            self.print_ok(self.command_name + "-" * (max_length - len(self.command_name)) + "> Success")
        else:
            self.print_error(self.command_name + "-" * (max_length - len(self.command_name)) + "> Failure")

    def log_result_to_file(self):
        '''
        Logging each test to a log file that can be used for troubleshooting. Is done by the use of the object repr function
        :return:
        '''
        output = self.__repr__()
        output_file = open(LOG_OUTPUT_FILE, 'a')
        try:
            output_file.write(output)
        except Exception:
            print(str(self.command_name.command) + "was not documented successfully")
        output_file.close()

    def run_full_test(self, exclude=False):
        '''
        A simple way to run a full test- executing the command, validating it's result, printing it to the prompt and logging it to a file
        :param exclude: A parameter given to the is_command_successful function.
        '''
        self.run_command()
        self.is_command_successful(exclude)
        self.print_result_to_prompt()
        self.log_result_to_file()

    def run_full_verification(self, exclude=False):
        '''
        A simple way to run only the verification on documentation steps of the test.
        Can be used in case some special commands are not run using the run_command function
        :param exclude: A parameter given to the is_command_successful function.
        '''
        self.is_command_successful(exclude)
        self.print_result_to_prompt()
        self.log_result_to_file()


class AgentInstallationVerifications:
    '''
    This class is for agent related verifications
    '''

    def verify_agent_service_is_listening(self):
        '''
        Verifying the agent service called mdsd is listening on its default port
        '''
        command_name = "verify_ama_agent_service_is_running"
        command_to_run = "sudo netstat -lnpvt | grep mdsd"
        result_keywords_array = ["mdsd", "28130", "LISTEN", "tcp"]
        command_object = BasicCommand(command_name, command_to_run, result_keywords_array)
        command_object.run_full_test()
        if not command_object.is_successful:
            command_object.print_warning(
                "Could not detect an AMA service running and listening on the machine. Please verify the installation of the agent was successfult by "
                "following the steps in this manual- ###ADD HERE###")

    def verify_agent_process_is_running(self):
        '''
        Verifying the agent process is running
        '''
        command_name = "verify_ama_agent_process_is_running"
        command_to_run = "sudo ps -ef | grep mdsd | grep -v grep"
        result_keywords_array = ["mdsd", "azuremonitoragent"]
        command_object = BasicCommand(command_name, command_to_run, result_keywords_array)
        command_object.run_full_test()
        if not command_object.is_successful:
            command_object.print_warning(
                "Could not detect an AMA process running on the machine. Please verify the installation of the agent was successfult by "
                "following the steps in this manual- ###ADD HERE###")

    def verify_error_log_empty(self):
        '''
        Verify the agent log file doesn't have many errors- needs work
        '''
        # needs work
        command_name = "verify_error_log_empty"
        command_to_run = "if [ `cat /var/opt/microsoft/azuremonitoragent/log/mdsd.err | wc -l` -lt 50 ]; then echo \"True\"; else echo \"False\"; fi"
        result_keywords_array = ["True"]
        command_object = BasicCommand(command_name, command_to_run, result_keywords_array)
        command_object.run_full_test()
        if not command_object.is_successful:
            command_object.print_warning(
                "Detected multiple errors in the agent log file. Please review it by running this command "
                "\'tail -f /var/opt/microsoft/azuremonitoragent/log/mdsd.err\' and making sure there is nothing fatal")

    def verify_oms_not_running(self):
        '''
        Verify the old MMA agent is not running together with the new AMA agent.
        '''
        # what will we like the warning to be
        command_name = "verify_oms_agent_not_running"
        command_to_run = "sudo netstat -lnpvt | grep ruby"
        result_keywords_array = ["25226", "LISTEN", "tcp"]
        command_object = BasicCommand(command_name, command_to_run, result_keywords_array)
        command_object.run_full_test(exclude=True)
        if not command_object.is_successful:
            command_object.print_warning(
                "Detected the OMS Agent running on your machine. If not necessary please remove it to avoid duplicated data in the workspace.")


class DCRConfigurationVerifications:
    '''
    This class is for data collection rules verifications
    '''

    def verify_DCR_exists(self):
        '''
        Verifying there is at least one dcr on the machine
        '''
        command_name = "verify_DCR_exists"
        command_to_run = "sudo ls -l /etc/opt/microsoft/azuremonitoragent/config-cache/configchunks/"
        result_keywords_array = [".json"]
        command_object = BasicCommand(command_name, command_to_run, result_keywords_array)
        command_object.run_full_test()
        if not command_object.is_successful:
            command_object.print_error(
                "Could not detect any data collection rule on the machine. The data reaching this server will not be forwarded to any workspace.")

    def verify_DCR_content_has_CEF_stream(self):
        '''
        Verifying there is a DCR on the machine for forwarding cef data
        '''
        command_name = "verify_DCR_content_has_CEF_stream"
        command_to_run = "sudo grep -ri \"SECURITY_CEF_BLOB\" /etc/opt/microsoft/azuremonitoragent/config-cache/configchunks/"
        result_keywords_array = ["SECURITY_CEF_BLOB"]
        command_object = BasicCommand(command_name, command_to_run, result_keywords_array)
        command_object.run_full_test()
        if not command_object.is_successful:
            command_object.print_error(
                "Could not detect any data collection rule for CEF data. No CEF events will be collected from this machine to any workspace.")
            return False
        return True

    def verify_CEF_dcr_has_valid_content(self):
        '''
        Verifying that the CE dcr on the machine has valid content with all necessary dcr components
        '''
        command_name = "verify_CEF_dcr_has_valid_content"
        command_to_run = "sudo grep -ri \"SECURITY_CEF_BLOB\" /etc/opt/microsoft/azuremonitoragent/config-cache/configchunks/ | head -1"
        result_keywords_array = ["stream", "kind", "syslog", "dataSources", "configuration", "facilityNames",
                                 "logLevels", "SecurityInsights", "endpoint", "channels", "sendToChannels", "ods-",
                                 "azure.com", "id"]
        command_object = BasicCommand(command_name, command_to_run, result_keywords_array)
        command_object.run_full_test()
        if not command_object.is_successful:
            command_object.print_error(
                "CEF DCR is not valid. Missing crucial DCR sections. Please follow the following documentation for more details- ")
            return False
        return True

    def check_cef_multi_homing(self):
        '''
        Counting the amount of DCRs forwarding CEF data in order to alert from multi-homing scenarios.
        '''
        command_name = "verify_DCR_exists"
        command_to_run = "sudo grep -ri \"SECURITY_CEF_BLOB\" /etc/opt/microsoft/azuremonitoragent/config-cache/configchunks/ | wc -l"
        command_object = BasicCommand(command_name, command_to_run)
        command_object.run_command()
        try:
            if int(command_object.command_result) > 1:
                command_object.run_full_verification()
                command_object.print_warning(
                    "Detected multiple collection rules sending the CEF stream. This scenario is called multi-homing and will have effect on ths agents' performance")
        except ValueError:
            command_object.is_successful = False
            command_object.print_result_to_prompt()
            command_object.log_result_to_file()

    def check_cef_dcr_content(self):
        '''
        Counting the amount of DCR's forwarding CEF data in order to alert from multi-homing scenarios.
        '''
        command_name = "verify_DCR_exists"
        command_to_run = "sudo grep -ri \"SECURITY_CEF_BLOB\" /etc/opt/microsoft/azuremonitoragent/config-cache/configchunks/ | wc -l"
        command_object = BasicCommand(command_name, command_to_run)
        command_object.run_command()
        try:
            if int(command_object.command_result) > 1:
                command_object.run_full_verification()
                command_object.print_warning(
                    "Detected multiple collection rules sending the CEF stream. This scenario is called multi-homing and will have effect on agent performance")
        except ValueError:
            command_object.is_successful = False
            command_object.print_result_to_prompt()
            command_object.log_result_to_file()


class SyslogDaemonVerifications:
    '''
    This class is for Syslog daemon related verifications
    '''
    SYSLOG_DAEMON = ""

    def determine_Syslog_daemon(self):
        '''
        This function is in order to determine what Syslog daemon is running on the machine (Rsyslog or Syslog-ng)
        '''
        is_Rsyslg_running = BasicCommand("find_Rsyslog_daemon",
                                         "if [ `ps -ef | grep rsyslog | grep -v grep | wc -l` -gt 0 ]; then echo \"True\"; else echo \"False\"; fi")
        is_Syslog_ng_running = BasicCommand("find_Syslog-ng_daemon",
                                            "if [ `ps -ef | grep syslog-ng | grep -v grep | wc -l` -gt 0 ]; then echo \"True\"; else echo \"False\"; fi")
        is_Rsyslg_running.run_command(), is_Syslog_ng_running.run_command()
        if is_Rsyslg_running.command_result == "True\n":
            self.SYSLOG_DAEMON = "rsyslog"
            return True
        elif is_Syslog_ng_running.command_result == "True\n":
            self.SYSLOG_DAEMON = "syslog-ng"
            return True
        is_Rsyslg_running.log_result_to_file()
        is_Syslog_ng_running.log_result_to_file()

    def verify_Syslog_daemon_listening(self):
        '''
        Verifying the Syslog daemon is listening on the default 514 port for incoming traffic
        '''
        command_name = "verify_Syslog_daemon_listening"
        command_to_run = "sudo netstat -lnpv | grep " + self.SYSLOG_DAEMON
        result_keywords_array = [self.SYSLOG_DAEMON, "LISTEN"]
        command_object = BasicCommand(command_name, command_to_run, result_keywords_array)
        if self.SYSLOG_DAEMON is not "":
            command_object.run_full_test()
            command_object.command_name = "verify_Syslog_daemon_listening_on_default_port"
            command_object.result_keywords_array = [self.SYSLOG_DAEMON, "LISTEN", ":514 "]
            command_object.run_full_test()
            if not command_object.is_successful:
                command_object.print_warning(
                    "Warning: the syslog daemon on the machine is listening to a non-default port")
        else:
            command_object.is_successful = False
            command_object.print_result_to_prompt()
            command_object.print_error(
                "No syslog daemon running on the machine. Please start one and re-run the script. The supported Syslog daemons are Rsyslog and Syslog-ng")
            command_object.log_result_to_file()

    def verify_Syslog_daemon_forwarding_configuration(self):
        '''
        Verify the syslog daemon forwarding configuration file has the correct forwarding configuration to the Unix domain socket.
        '''
        if self.SYSLOG_DAEMON is not "":
            syslog_daemon_forwarding_path = {"rsyslog": "/etc/rsyslog.d/10-azuremonitoragent.conf",
                                             "syslog-ng": "/etc/syslog-ng/conf.d/azuremonitoragent.conf"}
            syslog_daemon_forwarding_keywords = {
                "rsyslog": ['omuxsock', 'azuremonitoragent', 'OMUxSockSocket', 'OMUxSockDefaultTemplate'],
                "syslog-ng": ['destination', 'd_azure_mdsd', 'unix-dgram', 'azuremonitoragent', 'syslog', 'socket',
                              's_src']}
            command_name = "verify_Syslog_daemon_forwarding_configuration"
            command_to_run = "sudo cat " + syslog_daemon_forwarding_path[self.SYSLOG_DAEMON]
            result_keywords_array = syslog_daemon_forwarding_keywords[self.SYSLOG_DAEMON]
            command_object = BasicCommand(command_name, command_to_run, result_keywords_array)
            command_object.run_full_test()
            if not command_object.is_successful:
                command_object.print_error(self.SYSLOG_DAEMON + " configuration was found invalid")


class OperatingSystemVerifications:
    '''
    This class is for general operating system verifications
    '''

    def verify_selinux_disabled(self):
        '''
        Verify SELinux is not in enforcing mode, which can harm the events' forwarding to the agent.
        '''
        command_name = "verify_selinux_disabled"
        command_to_run = "sudo getenforce"
        result_keywords_array = ["Enforcing"]
        command_object = BasicCommand(command_name, command_to_run, result_keywords_array)
        command_object.run_full_test(True)
        if not command_object.is_successful:
            command_object.print_error(
                "Detected SELinux running on the machine. The agent does not support any form of hardening,"
                "and having SELinux in Enforcing mode can harm the forwarding of data. Please disable SELinux by running the commns \'setenforce 0\' and try again.")

    def verify_iptables(self):
        '''
        Verify there is no firewall rule in the iptables blocking the Syslog daemon or agent incoming ports
        '''
        command_name = "verify_iptables_policy_permissive"
        command_to_run = "sudo iptables -S | grep \\\\-P | grep -E 'INPUT|OUTPUT'"
        result_keywords_array = ["DROP", "REJECT"]
        policy_command_object = BasicCommand(command_name, command_to_run, result_keywords_array)
        policy_command_object.run_full_test(exclude=True)
        command_name = "verify_iptables_rules_permissive"
        command_to_run = "sudo iptables -S | grep -E '28130|514' | grep INPUT"
        rules_command_object = BasicCommand(command_name, command_to_run, result_keywords_array)
        rules_command_object.run_full_test(exclude=True)
        if (not rules_command_object.is_successful or (not policy_command_object.is_successful and (
                not rules_command_object.is_successful or rules_command_object.command_result == ""))):
            policy_command_object.print_warning(
                "Iptables might be blocking incoming traffic to the agent. Please verify there are "
                "firewall rules blocking traffic and run again.")

    def verify_free_disk_space(self):
        '''
        Verify there is enough free disk space on the machine for the event forwarding to work as expected. The minimal is set to 1 GB
        '''
        minimal_free_space_kb = 1048576
        command_name = "verify_free_disk_space"
        command_to_run = "sudo df --output=avail / | head -2 | tail -1"
        free_disk_object = BasicCommand(command_name, command_to_run)
        free_disk_object.run_command()
        if int(free_disk_object.command_result) < minimal_free_space_kb:
            free_disk_object.is_successful = False
            free_disk_object.print_result_to_prompt()
            free_disk_object.log_result_to_file()
            free_disk_object.print_error("There is less than 2 GB of free disk space left on this machine."
                                         "Having a full disk can harm the agent functionality and eventually cause data loss"
                                         "Please free disk space on this machine and run again.")
        else:
            free_disk_object.is_successful = True
            free_disk_object.print_result_to_prompt()
            free_disk_object.log_result_to_file()


class IncomingEventsVerifications:
    '''
    This class is for sending and capturing CEF events in the incoming stream of events to the syslog daemon port
    '''
    fixed_cef_message = "0|TestCommonEventFormat|MOCK|common=event-format-test|end|TRAFFIC|1|rt=$common=event-formatted-receive_time deviceExternalId=0002D01655 src=1.1.1.1 dst=2.2.2.2 sourceTranslatedAddress=1.1.1.1 destinationTranslatedAddress=3.3.3.3 cs1Label=Rule cs1=CEF_TEST_InternetDNS"

    def handle_tcpdump_line(self, line):
        '''
        Validate there are incoming CEF events.
        :param line: a text line from the tcpdump stream
        :return: True if CEF exists in the line. Otherwise false.
        '''
        if "CEF" in line:
            return True
        return False

    def incoming_logs_validations(self, mock_message=False):
        '''
        Validate that there is incoming traffic of CEF messages
        :param mock_message: Tells if to generate mock messages
        :return: True if successfully captured CEF events.
        '''
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
            print(
                "Notice that \'tcpdump\' is not installed in your Linux machine.\nWe cannot monitor traffic without it.\nPlease install \'tcpdump\'.")
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
                    command_object.print_ok(
                        "Found CEF events in stream. Please verify CEF events arrived at your workspace")
                    return True
            end_seconds = int(round(time.time()))
        command_object.print_error(
            "Could not locate \"CEF\" message in tcpdump. Please verify CEF events are being sent to the machine and there is not firewall blocking incoming traffic")
        command_object.command_result = str(line)
        command_object.run_full_verification()
        return False

    def send_cef_message_local(self, port, amount):
        '''
        Generate local CEF events in a given amount to a given port
        :param port: A destination port to send the events
        :param amount: The amount of events to send
        '''
        try:
            for index in range(0, amount):
                command_tokens = ["logger", "-p", "local4.warn", "-t", "CEF:", self.fixed_cef_message, "-P", str(port),
                                  "-n",
                                  "127.0.0.1"]
                logger = subprocess.Popen(command_tokens, stdout=subprocess.PIPE)
                o, e = logger.communicate()
                if e is not None:
                    print("Error could not send cef mock message")
        except OSError:
            print(
                "Warning: Could not execute \'logger\' command. This means that no mock message was sent to your workspace.")


def main():
    subprocess.Popen(['rm', LOG_OUTPUT_FILE, '2>', '/dev/null'],
                     stdout=subprocess.PIPE, stderr=subprocess.STDOUT).communicate()
    printer = ColorfulPrint()
    printer.print_notice("Note this script should be run in elevated privileges")
    printer.print_notice("Please validate you are sending CEF messages to agent machine.")
    # Create agent_verification object
    agent_verifications = AgentInstallationVerifications()
    printer.print_notice("---------------Starting validation tests for AMA--------------")
    agent_verifications.verify_agent_service_is_listening()
    agent_verifications.verify_error_log_empty()
    agent_verifications.verify_agent_process_is_running()
    agent_verifications.verify_oms_not_running()
    # Create dcr_verification object
    printer.print_notice("------Starting validation tests for data collection rules-----")
    dcr_verification = DCRConfigurationVerifications()
    dcr_verification.verify_DCR_exists()
    if dcr_verification.verify_DCR_content_has_CEF_stream():
        dcr_verification.verify_CEF_dcr_has_valid_content()
    dcr_verification.check_cef_multi_homing()
    # Create Syslog daemon verification object
    printer.print_notice("--------Starting validation tests for the Syslog daemon-------")
    syslog_daemon_verification = SyslogDaemonVerifications()
    syslog_daemon_verification.determine_Syslog_daemon()
    syslog_daemon_verification.verify_Syslog_daemon_listening()
    syslog_daemon_verification.verify_Syslog_daemon_forwarding_configuration()
    # Create operating system level verifications
    printer.print_notice("------Starting validation tests for the operating system------")
    os_verification = OperatingSystemVerifications()
    os_verification.verify_selinux_disabled()
    os_verification.verify_iptables()
    os_verification.verify_free_disk_space()
    # Create incoming events verification
    printer.print_notice("---Starting validation tests for capturing incoming events----")
    incoming_events = IncomingEventsVerifications()
    if not incoming_events.incoming_logs_validations():
        printer.print_notice("Generating CEF mock events and trying again")
        incoming_events.incoming_logs_validations(mock_message=True)
    if FAILED_TESTS_COUNT > 0:
        printer.print_error("Total amount of failed tests is: " + str(FAILED_TESTS_COUNT))
    else:
        printer.print_ok("All tests passed successfully")
    printer.print_notice("This script generated an output file located here - /tmp/cef_troubleshooter_output_file"
                         "\nPlease review if you would like to get more information on failed tests.")


if __name__ == '__main__':
    main()
