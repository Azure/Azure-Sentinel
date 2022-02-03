import subprocess

FAILED_TESTS_COUNT = 0
LOG_OUTPUT_FILE = "/tmp/cef_troubleshooter_output_file"

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
            delimiter + "command name: " + str(self.command_name) + '\n' + "command to run: " + str(self.command_to_run) + '\n' +
            "command output: " + str(self.command_result) + '\n' + "command error output: " + str(self.command_result_err) + '\n' +
            "command array verification: " + str(self.result_keywords_array) + '\n' + "Is successful: " + str(self.is_successful) +
            delimiter).replace(
            '%',
            '%%')

    def run_command(self):
        try:
            self.command_result, self.command_result_err = subprocess.Popen(self.command_to_run, shell=True,
                                                                            stdout=subprocess.PIPE,
                                                                            stderr=subprocess.STDOUT).communicate()
        except Exception:
            self.command_result_err = "Error processing command"

    def is_command_successful(self):
        if self.command_result_err is None:
            for key_word in self.result_keywords_array:
                if key_word not in self.command_result:
                    self.is_successful = False
                    return False
            self.is_successful = True
            return True

    def print_result_to_prompt(self):
        if self.is_successful:
            self.print_ok(self.command_name + "-------> Success")
        else:
            self.print_error(self.command_name + "-------> Failure")

    def log_result_to_file(self):
        output = self.__repr__()
        output_file = open(LOG_OUTPUT_FILE, 'a')
        try:
            output_file.write(output)
        except Exception:
            print(str(self.command_name.command) + "was not documented successfully")
        output_file.close()

    def run_test(self):
        self.run_command()
        self.is_command_successful()
        self.print_result_to_prompt()
        self.log_result_to_file()


class AgentInstallationVerifications:

    def verify_agent_service_is_listening(self):
        command_name = "verify_ama_agent_service_is_running"
        command_to_run = "netstat -lnpvt | grep mdsd"
        result_keywords_array = ["mdsd", "28130", "LISTEN", "tcp"]
        command_object = BasicCommand(command_name, command_to_run, result_keywords_array)
        command_object.run_test()

    def verify_agent_process_is_running(self):
        command_name = "verify_ama_agent_process_is_running"
        command_to_run = "ps -ef | grep mdsd | grep -v grep"
        result_keywords_array = ["mdsd", "azuremonitoragent"]
        command_object = BasicCommand(command_name, command_to_run, result_keywords_array)
        command_object.run_test()

    def verify_error_log_empty(self):
        command_name = "verify_error_log_empty"
        command_to_run = "if [ `cat /var/opt/microsoft/azuremonitoragent/log/mdsd.err | wc -l` -lt 50 ]; then echo \"True\"; else echo \"False\"; fi"
        result_keywords_array = ["True"]
        command_object = BasicCommand(command_name, command_to_run, result_keywords_array)
        command_object.run_test()


class DCRConfigurationVerifications:

    def verify_DCR_exists(self):
        command_name = "verify_DCR_exists"
        command_to_run = "ls -l /etc/opt/microsoft/azuremonitoragent/config-cache/configchunks/"
        result_keywords_array = [".json"]
        command_object = BasicCommand(command_name, command_to_run, result_keywords_array)
        command_object.run_test()

    def check_multi_homing(self):
        # not finished
        command_name = "verify_DCR_exists"
        command_to_run = "grep -ri \"SECURITY_CEF_BLOB\" /etc/opt/microsoft/azuremonitoragent/config-cache/configchunks/ | wc -l"
        result_keywords_array = [".json"]
        command_object = BasicCommand(command_name, command_to_run, result_keywords_array)
        command_object.run_test()

    def verify_DCR_content_has_CEF_stream(self):
        command_name = "verify_DCR_content_has_CEF_stream"
        command_to_run = "grep -ri \"SECURITY_CEF_BLOB\" /etc/opt/microsoft/azuremonitoragent/config-cache/configchunks/"
        result_keywords_array = ["SECURITY_CEF_BLOB"]
        command_object = BasicCommand(command_name, command_to_run, result_keywords_array)
        command_object.run_test()


class SyslogDaemonVerifications:
    SYSLOG_DAEMON = ""
    def determine_Syslog_daemon(self):
            is_Rsyslg_running = BasicCommand("find_Rsyslog_daemon", "if [ `ps -ef | grep rsyslog | grep -v grep | wc -l` -gt 0 ]; then echo \"True\"; else echo \"False\"; fi")
            is_Syslog_ng_running = BasicCommand("find_Syslog-ng_daemon", "if [ `ps -ef | grep syslog-ng | grep -v grep | wc -l` -gt 0 ]; then echo \"True\"; else echo \"False\"; fi")
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
        command_name = "verify_Syslog_daemon_listening"
        command_to_run = "netstat -lnpv | grep " + self.SYSLOG_DAEMON
        result_keywords_array = [self.SYSLOG_DAEMON, "LISTEN"]
        command_object = BasicCommand(command_name, command_to_run, result_keywords_array)
        if self.SYSLOG_DAEMON is not "":
            command_object.run_test()
        else:
            command_object.is_successful = False
            command_object.print_result_to_prompt()
            command_object.print_error("No syslog daemon running on the machine. Please start one and re-run the script.")
            command_object.log_result_to_file()



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
    # Create dcr_verification object
    dcr_verification = DCRConfigurationVerifications()
    dcr_verification.verify_DCR_exists()
    dcr_verification.verify_DCR_content_has_CEF_stream()
    # Create Syslog daemon verification object
    syslog_verification = SyslogDaemonVerifications()
    syslog_verification.determine_Syslog_daemon()
    syslog_verification.verify_Syslog_daemon_listening()
    printer.print_notice("The log output file is located here- " + LOG_OUTPUT_FILE)


if __name__ == '__main__':
    main()
