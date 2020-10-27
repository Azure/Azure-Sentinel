import subprocess
import sys

oms_agent_field_mapping_configuration = "/opt/microsoft/omsagent/plugin/filter_syslog_security.rb"
oms_agent_service_control = "/opt/microsoft/omsagent/bin/service_control"


def print_ok(input_str):
    print("\033[1;32;40m" + input_str + "\033[0m")


def print_error(input_str):
    print("\033[1;31;40m" + input_str + "\033[0m")


def print_notice(input_str):
    print("\033[0;30;47m" + input_str + "\033[0m")


def change_events_timegenerated():
    """
    :return: True if successfully changed the TimeGenerated configuration
    """
    grep = subprocess.Popen(["grep", "-i", "'Timestamp' => OMS::Common::fast_utc_to_iso8601_format(Time.now.utc),",
                             oms_agent_field_mapping_configuration], stdout=subprocess.PIPE)
    o, e = grep.communicate()
    if not o or e is not None:
        print_error("Couldn't locate TimeGenerated configuration set to log collection time")
    else:
        print_notice(
            "Ateempting to change TimeGenerated configuration setting to log creation time instead of log collection time")
        sed = subprocess.Popen(["sed", "-i", "s|'Timestamp' => OMS::Common::fast_utc_to_iso8601_format(Time.now.utc),"
                                             "|'Timestamp' => OMS::Common::fast_utc_to_iso8601_format(Time.at(time).utc),|g",
                                oms_agent_field_mapping_configuration])
        o, e = sed.communicate()
        if e is not None:
            print_error("Failed to change log TimeGenerated configuration")
            return False
        print_ok("Successfully changed log TimeGenerated configuration to log creation time")
        return True


def restart_omsagent(workspace_id):
    print_notice("Attempting to restart the OMS agent")
    agent_restart = subprocess.Popen(["sudo", oms_agent_service_control, "restart", workspace_id])
    o, e = agent_restart.communicate()
    if e is not None:
        print_error("Failed to restart the OMS agent")
        return False
    print_ok("Successfully restart the OMS agent")
    return True


def main():
    print_notice("Note this script should be run in elevated privileges")
    if len(sys.argv) != 2:
        print_error("The installation script is expecting 1 arguments:")
        print_error("\t1) workspace id")
        return
    else:
        workspace_id = sys.argv[1]

    if change_events_timegenerated():
        if restart_omsagent(workspace_id=workspace_id):
            print_ok("Finished successfully")


if __name__ == '__main__':
    main()
