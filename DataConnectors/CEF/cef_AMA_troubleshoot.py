import subprocess

results_status_dict = {}
recommended_fixes_dict = {"check_if_agent_is_running": "install the agent and try again"}
general_warning_array = []
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
            print(self.command_name + "-----> Success")
            return True
        print(self.command_name + "-----> Could not run this test")

    def run_test(self):
        self.run_command()
        self.is_test_successful()


def verify_agent_installation():
    command_name = "verify_ama_agent_service_is_running"
    command_object = HandleCommand(command_name, commands_dict[command_name][0], commands_dict[command_name][1])
    command_object.run_test()
    command_name = "verify_ama_agent_process_is_running"
    command_object = HandleCommand(command_name, commands_dict[command_name][0], commands_dict[command_name][1])
    command_object.run_test()


def main():
    verify_agent_installation()
    print("The total number of failed requests is: %s" % FAILED_TESTS_COUNT)


if __name__ == '__main__':
    main()
