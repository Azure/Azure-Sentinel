"""This file contains methods for creating microsoft indicator and custom log table."""
import time
import json
import inspect
from ..SharedCode.utils import Utils
from ..SharedCode.logger import applogger
from ..SharedCode.cofense_intelligence_exception import CofenseIntelligenceException
from ..SharedCode import consts


class MicrosoftSentinel(Utils):
    """This class contains methods to create indicator into Microsoft Sentinel."""

    def __init__(self):
        """Initialize instance variable for class."""
        super().__init__(consts.COFENSE_TO_SENTINEL)
        self.bearer_token = self.auth_sentinel()

    async def create_indicator(self, indicator_data, session):
        """To create indicator into Microsoft Sentinel.

        Args:
            indicator_data (dict): Indicator data
            session (session object): aiohttp session object

        Raises:
            CofenseIntelligenceException: Cofense Exception
        """
        __method_name = inspect.currentframe().f_code.co_name
        try:
            threat_id = ""
            indicator_labels = indicator_data.get("properties", "").get("labels", "")
            if indicator_labels != "":
                threat_id = indicator_labels[0].split("-")[-1]
            retry_count_429 = 0
            retry_count_401 = 0
            while retry_count_429 <= 3 and retry_count_401 <= 1:
                create_indicator_url = consts.CREATE_SENTINEL_INDICATORS_URL.format(
                    subscriptionId=consts.AZURE_SUBSCRIPTION_ID,
                    resourceGroupName=consts.AZURE_RESOURCE_GROUP,
                    workspaceName=consts.AZURE_WORKSPACE_NAME,
                )
                headers = {
                    "Content-Type": "application/json",
                    "Authorization": "Bearer {}".format(self.bearer_token),
                }
                response = await session.post(
                    url=create_indicator_url,
                    headers=headers,
                    data=json.dumps(indicator_data),
                )
                if response.status >= 200 and response.status <= 299:
                    applogger.info(
                        "{}(method={}) : {} : Created the indicator with threatId- {}, status_code: {}.".format(
                            consts.LOGS_STARTS_WITH,
                            __method_name,
                            consts.COFENSE_TO_SENTINEL,
                            threat_id,
                            response.status,
                        )
                    )
                    return None
                elif response.status == 429:
                    applogger.error(
                        "{}(method={}) : {} : trying again error 429.".format(
                            consts.LOGS_STARTS_WITH,
                            __method_name,
                            consts.COFENSE_TO_SENTINEL,
                        )
                    )
                    retry_count_429 += 1
                    time.sleep(consts.SENTINEL_429_SLEEP)
                elif response.status == 401:
                    applogger.error(
                        "{}(method={}) : {} : Unauthorized, Invalid Credentials, trying again error-401.".format(
                            consts.LOGS_STARTS_WITH,
                            __method_name,
                            consts.COFENSE_TO_SENTINEL,
                        )
                    )
                    self.bearer_token = self.auth_sentinel(consts.COFENSE_TO_SENTINEL)
                    headers["Authorization"] = "Bearer {}".format(self.bearer_token)
                    retry_count_401 += 1
                else:
                    json_response = await response.json()
                    applogger.error(
                        "{}(method={}) : {} : url: {}, Status Code : {}: Error while\
                             creating Indicator, threatId-{}, Error:{}.".format(
                            consts.LOGS_STARTS_WITH,
                            __method_name,
                            consts.COFENSE_TO_SENTINEL,
                            create_indicator_url,
                            response.status,
                            threat_id,
                            json_response,
                        )
                    )
                    raise CofenseIntelligenceException()
            applogger.error(
                "{}(method={}) : {} : Max retries exceeded for microsoft sentinel, threatId-{}.".format(
                    consts.LOGS_STARTS_WITH,
                    __method_name,
                    consts.COFENSE_TO_SENTINEL,
                    threat_id,
                )
            )
            raise CofenseIntelligenceException()
        except CofenseIntelligenceException:
            applogger.error(
                "{}(method={}) : {} : Error generated while Creating Indicator, threatId-{}.".format(
                    consts.LOGS_STARTS_WITH,
                    __method_name,
                    consts.COFENSE_TO_SENTINEL,
                    threat_id,
                )
            )
            return indicator_data

        except Exception:
            applogger.error(
                "{}(method={}) : {} : Error generated while Creating Indicator, threatId-{}.".format(
                    consts.LOGS_STARTS_WITH,
                    __method_name,
                    consts.COFENSE_TO_SENTINEL,
                    threat_id,
                )
            )
            return indicator_data
