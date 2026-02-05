"""This __init__ file will be called by Orchastrator function on manual trigger."""
from shared_code.logger import applogger
from shared_code.dataminrpulse_exception import DataminrPulseException
from .dataminrpulse_integration_settings import DataminrPulseConfigureSettings


def main(name):
    """Start Execution of Activity function.

    Args:
        name (dict): data received via manual trigger to add integration settings.

    Returns:
        str: setting_id on success or error message on failure.
    """
    try:
        applogger.info("Activity function called for manual trigger.")
        configuresettings = DataminrPulseConfigureSettings()
        settings_id = configuresettings.add_webhook_configuration_to_dataminr(
            name
        )
        return settings_id
    except DataminrPulseException as err:
        return (
            "Error while adding integration settings to Dataminr account. {}".format(
                err
            )
        )
