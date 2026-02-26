from ..Helpers.date_helper import DateHelper


class TTPImpersonationParser:
    def __init__(self):
        self.date_helper = DateHelper()

    def parse(self, logs):
        for log in logs:
            if "checkpoints" in log:
                continue
            event_id = "ttp_impersonation"
            category = "ttp_impersonation"
            timestamp = self.date_helper.convert_from_mimecast_format(log["eventTime"])
            log.update({"mimecastEventId": event_id, "mimecastEventCategory": category, "time_generated": timestamp})

        return logs
