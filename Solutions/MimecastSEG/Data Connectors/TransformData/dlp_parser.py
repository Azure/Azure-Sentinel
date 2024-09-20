from ..Helpers.date_helper import DateHelper


class DLPParser:

    def __init__(self):
        self.date_helper = DateHelper()

    def parse(self, logs):
        for log in logs:
            event_id = f"data_leak_prevention_{log.get('action')}"
            category = "data_leak_prevention"
            timestamp = self.date_helper.convert_from_mimecast_format(log['eventTime'])
            log.update({'mimecastEventId': event_id, 'mimecastEventCategory': category, 'time_generated': timestamp})

        return logs
