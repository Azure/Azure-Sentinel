from Helpers.date_helper import DateHelper


class AuditParser:

    def __init__(self):
        self.date_helper = DateHelper()

    def parse(self, logs):
        category = "audit"
        for log in logs:
            event_id = "audit_other"
            if 'checkpoints' in log:
                continue
            if log.get('category'):
                event_id = f"audit_{log['category'].replace('_logs', '')}"

            extra_info_pairs = log['eventInfo'].split(',')
            app = 'unknown'
            src = 'unknown'
            method = 'unknown'

            for pair in extra_info_pairs:
                if 'Application:' in pair:
                    app = pair.split(': ')[1]
                elif 'IP:' in pair:
                    src = pair.split(': ')[1]
                elif 'Method:' in pair:
                    method = pair.split(': ')[1]

            timestamp = self.date_helper.convert_from_mimecast_format(log['eventTime'])

            log.update({'mimecastEventId': event_id, 'mimecastEventCategory': category, 'time_generated': timestamp,
                        'app': app, 'src': src, 'method': method})

        return logs
