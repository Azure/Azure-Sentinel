import subprocess

FAILED_TESTS_COUNT = 0
# parent test example: DCR verifications:
# sub tests of permissions/file existence.
commands_dict = {
    "verify_ama_agent_service_is_running": ["netstat -lnpvt | grep mdsd", ["mdsd"]],
    "verify_ama_agent_process_is_running": ["ps -ef | grep mdsd | grep -v grep", ["mdsd", "azuremonitoragent"]],
    "verify_DCR_exists": ["ls -l /etc/opt/microsoft/azuremonitoragent/config-cache/configchunks/", [".json"]],
    "verify_DCR_content_has_CEF_stream": [
        "grep -ri \"SECURITY_CEF_BLOB\" /etc/opt/microsoft/azuremonitoragent/config-cache/configchunks/",
        ["SECURITY_CEF_BLOB"]]
}


# Add output file with logs from command- consider merging with the get info script.
# Steps will have sub steps and the output log will contain explanations of what the test ran (command wise), and what was the failure check
# Classes with different verifications for example that inherit from the parent class of HandleCommand
class ColorfulPrint:
    def __init__(self):
        pass

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
                 is_successful=False,
                 response_message=""):
        self.command_name = command_name
        self.command_to_run = command_to_run
        self.result_keywords_array = result_keywords_array
        self.command_result = command_result
        self.command_result_err = command_result_err
        self.is_successful = is_successful
        self.response_message = response_message

    """
    Need to add a section for complicated commands.
    """

    def run_command(self):
        try:
            self.command_result, self.command_result_err = subprocess.Popen(self.command_to_run, shell=True,
                                                                            stdout=subprocess.PIPE,
                                                                            stderr=subprocess.STDOUT).communicate()
        except Exception:
            self.command_result_err = "Error processing command"

    def is_command_successful(self):
        if self.command_result_err == None:
            for key_word in self.result_keywords_array:
                if key_word not in self.command_result:
                    print(self.command_name + "-----> Failure")
                    global FAILED_TESTS_COUNT
                    FAILED_TESTS_COUNT += 1
                    return False
            self.is_successful = True
            print(self.command_name + "-----> Success")
            return True
        print(self.command_name + "-----> Could not run this test")

    def run_test(self):
        self.run_command()
        self.is_command_successful()

    def print_result(self):
        if self.is_successful:
            self.print_ok(self.command_name + "-------> Success")
        else:
            self.print_error(self.command_name + "-------> Failure")


class AgentInstallationVerifications(BasicCommand):
    def __init__(self, command_name, command_to_execute, expected_result):
        self.command_name = command_name
        self.command_to_execute = command_to_execute
        self.expected_result = expected_result

    def run_basic_verification(self, command_name):
        command_object = BasicCommand(command_name, commands_dict[command_name][0], commands_dict[command_name][1])
        command_object.run_test()
        command_object.print_result()

    def verify_agent_service_is_listening(self):
        command_name = "verify_ama_agent_service_is_running"
        self.run_basic_verification(command_name)

    def verify_agent_process_is_running(self):
        command_name = "verify_ama_agent_process_is_running"
        self.run_basic_verification(command_name)

    def verify_error_log_empty(self):
        agent_verification_object = AgentInstallationVerifications("verify_error_log", "cat /var/log/syslog | wc -l", 0)


class DCRConfigurationVerifications(BasicCommand):

    def run_basic_verification(self, command_name):
        command_object = BasicCommand(command_name, commands_dict[command_name][0], commands_dict[command_name][1])
        command_object.run_test()
        command_object.print_result()

    def verify_DCR_exists(self):
        command_name = "verify_ama_agent_service_is_running"
        self.run_basic_verification(command_name)
        if not self.command_object.is_successful:
            self.command_object.print_error(
                "Could not detect any DCR running on the machine. Please create one using the following steps and try again:")

    def verify_DCR_content_has_CEF_stream(self):
        command_name = "verify_DCR_content_has_CEF_stream"
        self.run_basic_verification(command_name)
        if not self.command_object.is_successful:
            self.command_object.print_error(
                "Could not detect the CEF stream in any of the running DCR's on this machine. Please create a DCR with the CEF stream using the following guide and try again:")


def main():
    printer = ColorfulPrint()
    printer.print_notice("Note this script should be run in elevated privileges")
    printer.print_notice("Please validate you are sending CEF messages to agent machine.")
    # Create agent_verification object
    agent_verifications = AgentInstallationVerifications()
    agent_verifications.verify_agent_service_is_listening()
    agent_verifications.verify_agent_process_is_running()
    # Create dcr_verification object
    dcr_verification = DCRConfigurationVerifications()
    dcr_verification.verify_DCR_exists()
    dcr_verification.verify_DCR_content_has_CEF_stream


if __name__ == '__main__':
    main()
