"""Create dossier job and check job status."""

import inspect
import time
from random import randrange
from ..SharedCode.infoblox_exception import InfobloxException
from ..SharedCode import consts
from ..SharedCode.logger import applogger
from ..SharedCode.utils import Utils


class DossierCreateJob(Utils):
    """Class for creating dossier job and check job status."""

    def __init__(self, type_of_data, target):
        """Init class for create dossier job."""
        super().__init__(consts.DOSSIER_ORCHESTRATOR_FUNCTION_NAME)
        self.authenticate_infoblox_api()
        self.check_environment_var_exist(
            [
                {"API_Token": consts.API_TOKEN},
            ]
        )
        self.type_of_data = type_of_data
        self.target = target

    def get_dossier_job_id(self, source_list):
        """Retrieve the job ID for a dossier creation job.

        Args:
            source_list (list): A list of data sources for the dossier creation.

        Returns:
            str: The job ID retrieved from the response JSON.
        """
        __method_name = inspect.currentframe().f_code.co_name
        try:
            url = consts.BASE_URL.format(consts.DOSSIER_ENDPOINTS["Create_Post"])
            body = {
                "target": {
                    "one": {
                        "type": self.type_of_data,
                        "target": self.target,
                        "sources": source_list,
                    }
                }
            }
            response_json = self.make_dossier_call(url=url, method="POST", headers=self.headers, body=body)
            job_id = response_json.get("job_id")
            applogger.info(
                self.log_format.format(
                    consts.LOGS_STARTS_WITH,
                    __method_name,
                    self.azure_function_name,
                    "Job ID: {}".format(job_id),
                )
            )
            return job_id
        except InfobloxException:
            raise InfobloxException()
        except KeyError as key_error:
            applogger.error(
                self.log_format.format(
                    consts.LOGS_STARTS_WITH,
                    __method_name,
                    self.azure_function_name,
                    "Key error : Error-{}".format(key_error),
                )
            )
            raise InfobloxException()
        except Exception as error:
            applogger.error(
                self.log_format.format(
                    consts.LOGS_STARTS_WITH,
                    __method_name,
                    self.azure_function_name,
                    "Unexpected error : Error-{}".format(error),
                )
            )
            raise InfobloxException()

    def check_job_status(self, job_id):
        """Check the status of a job by polling the Infoblox API.

        Args:
            job_id (str): The ID of the job to check the status for.

        Returns:
            bool: True if the job status is successfully retrieved.
        """
        __method_name = inspect.currentframe().f_code.co_name
        try:
            url = consts.BASE_URL.format(consts.DOSSIER_ENDPOINTS["Status"]).format(job_id)
            status = "pending"
            secs = 0
            while status == "pending":
                response_json = self.make_dossier_call(url, method="GET", headers=self.headers)
                status = response_json.get("status")
                applogger.info(
                    self.log_format.format(
                        consts.LOGS_STARTS_WITH,
                        __method_name,
                        self.azure_function_name,
                        "Job is still pending, time = {} Secs".format(secs),
                    )
                )
                sleep_time = randrange(2, 10)
                secs += sleep_time
                time.sleep(sleep_time)
            applogger.info(
                self.log_format.format(
                    consts.LOGS_STARTS_WITH,
                    __method_name,
                    self.azure_function_name,
                    "Job status success",
                )
            )
            return True
        except InfobloxException:
            raise InfobloxException()
        except Exception as error:
            applogger.error(
                self.log_format.format(
                    consts.LOGS_STARTS_WITH,
                    __method_name,
                    self.azure_function_name,
                    "Unexpected error : Error-{}".format(error),
                )
            )
            raise InfobloxException()
