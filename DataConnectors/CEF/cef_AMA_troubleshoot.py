import subprocess

FAILED_TESTS_COUNT = 0
commands_dict = {
    "verify_ama_agent_service_is_running": ["netstat -lnpvt | grep mdsd", ["mdsd"]],
    "verify_ama_agent_process_is_running": ["ps -ef | grep mdsd | grep -v grep", ["mdsd", "azuremonitoragent"]],
    "Verify_DCR_exists": ["ls -l /etc/opt/microsoft/azuremonitoragent/config-cache/configchunks/", [".json"]],
    "Verify_DCR_content_has_CEF_Stream": [
        "grep -ri \"SECURITY_CEF_BLOB\" /etc/opt/microsoft/azuremonitoragent/config-cache/configchunks/",
        ["SECURITY_CEF_BLOB"]]
}


class HandleCommand:
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

    def is_test_successful(self):
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
        self.is_test_successful()


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


def verify_agent_installation():
    command_name1 = "verify_ama_agent_service_is_running"
    command_object1 = HandleCommand(command_name1, commands_dict[command_name1][0], commands_dict[command_name1][1])
    command_object1.run_test()
    command_name2 = "verify_ama_agent_process_is_running"
    command_object2 = HandleCommand(command_name2, commands_dict[command_name2][0], commands_dict[command_name2][1])
    command_object2.run_test()
    if not command_object1.is_successful or not command_object2.is_successful:
        print_error(
            "Could not detect AMA running on the machine. Please install AMA using the following guide and try again")


def verify_dcr_configuration():
    command_name1 = "Verify_DCR_exists"
    command_object1 = HandleCommand(command_name1, commands_dict[command_name1][0], commands_dict[command_name1][1])
    command_object1.run_test()
    if not command_object1.is_successful:
        print_error(
            "Could not detect any DCR running on the machine. Please create one using the following steps and try again:")
    command_name2 = "Verify_DCR_content_has_CEF_Stream"
    command_object2 = HandleCommand(command_name2, commands_dict[command_name2][0], commands_dict[command_name2][1])
    command_object2.run_test()
    if not command_object2.is_successful:
        print_error(
            "Could not detect the CEF stream in any of the running DCR's on this machine. Please create a DCR with the CEF stream using the following guide and try again:")


def main():
    print_notice("Note this script should be run in elevated privileges")
    print_notice("Please validate you are sending CEF messages to agent machine.")
    verify_agent_installation()
    verify_dcr_configuration()
    print("The total number of failed requests is: %s" % FAILED_TESTS_COUNT)
    if FAILED_TESTS_COUNT == 0:
        print_ok("No errors were detected. Installation is successful")


if __name__ == '__main__':
    main()
