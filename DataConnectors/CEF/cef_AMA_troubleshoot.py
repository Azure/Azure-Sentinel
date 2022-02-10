import subprocess

LOG_OUTPUT_FILE = "/tmp/cef_troubleshooter_output_file"
FAILED_TESTS_COUNT = 0

class ColorfulPrint:

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

    def __init__(self, command_name, command_to_run, result_keywords_array=[], command_result="", command_result_err="",
                 is_successful=False):
        self.command_name = command_name
        self.command_to_run = command_to_run
        self.result_keywords_array = result_keywords_array
        self.command_result = command_result
        self.command_result_err = command_result_err
        self.is_successful = is_successful

    def __repr__(self):
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
        global FAILED_TESTS_COUNT
        try:
            self.command_result, self.command_result_err = subprocess.Popen(self.command_to_run, shell=True,
                                                                            stdout=subprocess.PIPE,
                                                                            stderr=subprocess.STDOUT).communicate()
        except Exception:
            self.command_result_err = "Error processing command"

    def is_command_successful(self, exclude):
        global FAILED_TESTS_COUNT
        if self.command_result_err is None:
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

    def print_result_to_prompt(self):
        max_length = 47
        if self.is_successful:
            self.print_ok(self.command_name + "-" * (max_length-len(self.command_name)) + "> Success")
        else:
            self.print_error(self.command_name + "-" * (max_length-len(self.command_name)) + "> Failure")

    def log_result_to_file(self):
        output = self.__repr__()
        output_file = open(LOG_OUTPUT_FILE, 'a')
        try:
            output_file.write(output)
        except Exception:
            print(str(self.command_name.command) + "was not documented successfully")
        output_file.close()

    def run_test(self, exclude=False):
        self.run_command()
        self.is_command_successful(exclude)
        self.print_result_to_prompt()
        self.log_result_to_file()


class AgentInstallationVerifications:

    def verify_agent_service_is_listening(self):
        command_name = "verify_ama_agent_service_is_running"
        command_to_run = "sudo netstat -lnpvt | grep mdsd"
        result_keywords_array = ["mdsd", "28130", "LISTEN", "tcp"]
        command_object = BasicCommand(command_name, command_to_run, result_keywords_array)
        command_object.run_test()
        if not command_object.is_successful:
            command_object.print_warning(
                "Could not detect an AMA service running and listening on the machine. Please verify the installation of the agent was successfult by "
                "following the steps in this manual- ###ADD HERE###")

    def verify_agent_process_is_running(self):
        command_name = "verify_ama_agent_process_is_running"
        command_to_run = "sudo ps -ef | grep mdsd | grep -v grep"
        result_keywords_array = ["mdsd", "azuremonitoragent"]
        command_object = BasicCommand(command_name, command_to_run, result_keywords_array)
        command_object.run_test()
        if not command_object.is_successful:
            command_object.print_warning(
                "Could not detect an AMA process running on the machine. Please verify the installation of the agent was successfult by "
                "following the steps in this manual- ###ADD HERE###")

    def verify_error_log_empty(self):
        # needs work
        command_name = "verify_error_log_empty"
        command_to_run = "if [ `cat /var/opt/microsoft/azuremonitoragent/log/mdsd.err | wc -l` -lt 50 ]; then echo \"True\"; else echo \"False\"; fi"
        result_keywords_array = ["True"]
        command_object = BasicCommand(command_name, command_to_run, result_keywords_array)
        command_object.run_test()
        if not command_object.is_successful:
            command_object.print_warning(
                "Detected multiple errors in the agent log file. Please review it by running this command "
                "\'tail -f /var/opt/microsoft/azuremonitoragent/log/mdsd.err\' and making sure there is nothing fatal")

    def verify_oms_not_running(self):
        command_name = "verify_oms_agent_not_running"
        command_to_run = "sudo netstat -lnpvt | grep ruby"
        result_keywords_array = ["25226", "LISTEN", "tcp"]
        command_object = BasicCommand(command_name, command_to_run, result_keywords_array)
        command_object.run_test(exclude=True)
        if not command_object.is_successful:
            command_object.print_warning(
                "Detected the OMS Agent running on your machine. If not necessary please remove it to avoid duplicated data in the workspace.")


class DCRConfigurationVerifications:

    def verify_DCR_exists(self):
        command_name = "verify_DCR_exists"
        command_to_run = "sudo ls -l /etc/opt/microsoft/azuremonitoragent/config-cache/configchunks/"
        result_keywords_array = [".json"]
        command_object = BasicCommand(command_name, command_to_run, result_keywords_array)
        command_object.run_test()
        if not command_object.is_successful:
            command_object.print_error("Could not detect any data collection rule on the machine. The data reaching this server will not be forwarded to any workspace.")


    def verify_DCR_content_has_CEF_stream(self):
        command_name = "verify_DCR_content_has_CEF_stream"
        command_to_run = "sudo grep -ri \"SECURITY_CEF_BLOB\" /etc/opt/microsoft/azuremonitoragent/config-cache/configchunks/"
        result_keywords_array = ["SECURITY_CEF_BLOB"]
        command_object = BasicCommand(command_name, command_to_run, result_keywords_array)
        command_object.run_test()
        if not command_object.is_successful:
            command_object.print_error("Could not detect any data collection rule for CEF data. No CEF events will be collected from this machine to any workspace.")
            return False
        return True

    def check_cef_multi_homing(self):
        command_name = "verify_DCR_exists"
        command_to_run = "sudo grep -ri \"SECURITY_CEF_BLOB\" /etc/opt/microsoft/azuremonitoragent/config-cache/configchunks/ | wc -l"
        command_object = BasicCommand(command_name, command_to_run)
        if not self.verify_DCR_content_has_CEF_stream():
            command_object.is_successful = True
            command_object.print_result_to_prompt()
            command_object.log_result_to_file()
        else:
            command_object.run_command()
            if int(command_object.command_result) > 1:
                command_object.print_warning("Detected multiple collection rules sending the CEF stream. This scenario is called multi-homing and will have effect on agent performance")

class SyslogDaemonVerifications:
    SYSLOG_DAEMON = ""

    def determine_Syslog_daemon(self):
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
        # consider checking for only udp
        command_name = "verify_Syslog_daemon_listening"
        command_to_run = "sudo netstat -lnpv | grep " + self.SYSLOG_DAEMON
        result_keywords_array = [self.SYSLOG_DAEMON, "LISTEN"]
        command_object = BasicCommand(command_name, command_to_run, result_keywords_array)
        if self.SYSLOG_DAEMON is not "":
            command_object.run_test()
            command_object.command_name = "verify_Syslog_daemon_listening_on_default_port"
            command_object.result_keywords_array = [self.SYSLOG_DAEMON, "LISTEN", ":514 "]
            command_object.run_test()
            if not command_object.is_successful:
                command_object.print_warning(
                    "Warning: the syslog daemon on the machine is listening to a non-default port")
        else:
            command_object.is_successful = False
            command_object.print_result_to_prompt()
            command_object.print_error(
                "No syslog daemon running on the machine. Please start one and re-run the script.")
            command_object.log_result_to_file()


class OperatingSystemVerifications:

    def verify_selinux_disabled(self):
        command_name = "verify_selinux_disabled"
        command_to_run = "sudo getenforce"
        result_keywords_array = ["Enforcing"]
        command_object = BasicCommand(command_name, command_to_run, result_keywords_array)
        command_object.run_test(True)
        if not command_object.is_successful:
            command_object.print_error("Detected SELinux running on the machine. The agent does not support any form of hardenting,"
                                       "and having SELinux in Enforcing mode can harm the forwarding of data. Please disable SELinux and try again.")

    def verify_iptables(self):
        command_name = "verify_iptables_policy_permissive"
        command_to_run = "sudo iptables -S | grep \\\\-P | grep -E 'INPUT|OUTPUT'"
        result_keywords_array = ["DROP", "REJECT"]
        policy_command_object = BasicCommand(command_name, command_to_run, result_keywords_array)
        policy_command_object.run_test(exclude=True)
        command_name = "verify_iptables_rules_permissive"
        command_to_run = "sudo iptables -S | grep -E '28130|514' | grep INPUT"
        rules_command_object = BasicCommand(command_name, command_to_run, result_keywords_array)
        rules_command_object.run_test(exclude=True)
        if (not rules_command_object.is_successful or (not policy_command_object.is_successful and (
                not rules_command_object.is_successful or rules_command_object.command_result == ""))):
            policy_command_object.print_warning(
                "Iptables might be blocking incoming traffic to the agent. Please verify there are "
                "firewall rules blocking traffic and run again.")

    def verify_free_disk_space(self):
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


# print the output file path
def main():
    subprocess.Popen(['rm', LOG_OUTPUT_FILE, '2>', '/dev/null'],
                     stdout=subprocess.PIPE, stderr=subprocess.STDOUT).communicate()
    printer = ColorfulPrint()
    printer.print_notice("Note this script should be run in elevated privileges")
    printer.print_notice("Please validate you are sending CEF messages to agent machine.")
    # Create agent_verification object
    agent_verifications = AgentInstallationVerifications()
    agent_verifications.verify_agent_service_is_listening()
    agent_verifications.verify_error_log_empty()
    agent_verifications.verify_agent_process_is_running()
    agent_verifications.verify_oms_not_running()
    # Create dcr_verification object
    dcr_verification = DCRConfigurationVerifications()
    dcr_verification.verify_DCR_exists()
    dcr_verification.verify_DCR_content_has_CEF_stream()
    dcr_verification.check_cef_multi_homing()
    # Create Syslog daemon verification object
    syslog_verification = SyslogDaemonVerifications()
    syslog_verification.determine_Syslog_daemon()
    syslog_verification.verify_Syslog_daemon_listening()
    # Create operating system level verifications
    os_verification = OperatingSystemVerifications()
    os_verification.verify_selinux_disabled()
    os_verification.verify_iptables()
    os_verification.verify_free_disk_space()
    if FAILED_TESTS_COUNT > 0:
        printer.print_warning("Total amount of failed tests is: " + str(FAILED_TESTS_COUNT))
    else:
        printer.print_ok("All tests passed successfully")
    printer.print_notice("This script generated an output file located here - /tmp/cef_troubleshooter_output_file."
                         "\nPlease review if you would like to get more information on failed tests.")


if __name__ == '__main__':
    main()
