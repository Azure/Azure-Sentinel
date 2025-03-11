from ..Helpers.date_helper import DateHelper
from ..Models.Enum.siem_types import SiemTypes
import logging


class SiemParser:

    def __init__(self):
        self.date_helper = DateHelper()

    def parse(self, logs):
        parsed_logs = []
        if logs:
            for log in logs:
                if 'checkpoints' in log:
                    continue
                log_type = log['logType'].strip()
                if log_type == SiemTypes.TYPE_AV:
                    parsed_logs.append(self.parse_av_event(log))
                elif log_type == SiemTypes.TYPE_DELIVERY:
                    parsed_logs.append(self.parse_delivery_event(log))
                elif log_type == SiemTypes.TYPE_PROCESS:
                    parsed_logs.append(self.parse_process_event(log))
                elif log_type == SiemTypes.TYPE_RECEIPT:
                    parsed_logs.append(self.parse_receipt_event(log))
                elif log_type == SiemTypes.TYPE_TTP_URL:
                    parsed_logs.append(self.parse_ttp_url_event(log))
                elif log_type == SiemTypes.TYPE_TTP_IMPERSONATION:
                    parsed_logs.append(self.parse_ttp_impersonation_event(log))
                elif log_type == SiemTypes.TYPE_TTP_ATTACHMENT:
                    parsed_logs.append(self.parse_ttp_attachment_event(log))
                elif log_type == SiemTypes.TYPE_TTP_IEP:
                    parsed_logs.append(self.parse_ttp_iep_event(log))
                elif log_type == SiemTypes.TYPE_JOURNAL:
                    parsed_logs.append(self.parse_journal_event(log))
                elif log_type == SiemTypes.TYPE_SPAMEVENTTHREAD:
                    parsed_logs.append(self.parse_spameventthread(log))
                else:
                    parsed_logs.append(self.parse_other_event(log))

        return parsed_logs

    def parse_av_event(self, event):
        """ Parse a single AV event
        :param event: event to be parsed (single line in log)
        :return: parsed event
        """
        category = 'mail_av'
        event_id = 'mail_av'
        timestamp = self.date_helper.convert_from_mimecast_format(event['datetime'])
        event.update({'mimecastEventId': event_id, 'mimecastEventCategory': category, 'time_generated': timestamp})

        return event

    def parse_delivery_event(self, event):
        """ Parse a single Delivery event
        Based on:
        - Delivered (is the mail delivered at all)
        - UseTls (was tls used)
        :param event: event to be parsed (single line in log)
        :return: parsed event
        """
        delivered = event['Delivered'] if 'Delivered' in event else None
        use_tls = event['UseTls'] if 'UseTls' in event else None
        if delivered is not None:
            if delivered == 'true':
                if use_tls == 'Yes':
                    event_id = 'mail_delivery_delivered'
                else:
                    event_id = 'mail_delivery_delivered_notls'
            else:
                event_id = 'mail_delivery_not_delivered'
        else:
            event_id = 'mail_delivery_other'
        category = 'mail_delivery'
        timestamp = self.date_helper.convert_from_mimecast_format(event['datetime'])
        event.update({'mimecastEventId': event_id, 'mimecastEventCategory': category, 'time_generated': timestamp})

        return event

    def parse_process_event(self, event):
        """ Parse a single Process event
        Based on:
        - Act (action)
        :param event: event to be parsed (single line in log)
        :return: parsed event
        """
        action = event['Act'] if 'Act' in event else None
        if action == 'Acc':
            event_id = 'mail_process_accepted'
        elif action == 'Hld':
            event_id = 'mail_process_held'
        elif action == 'Sdbx':
            event_id = 'mail_process_sandboxed'
        elif action == 'Rty':
            event_id = 'mail_process_retried'
        elif action == 'Bnc':
            event_id = 'mail_process_bounced'
        else:
            event_id = 'mail_process_other'
        category = 'mail_process'
        timestamp = self.date_helper.convert_from_mimecast_format(event['datetime'])
        event.update({'mimecastEventId': event_id, 'mimecastEventCategory': category, 'time_generated': timestamp})

        return event

    def parse_receipt_event(self, event):
        """ Parse a single Receipt event
        Based on:
        - Act (action)
        - TlsVer (TLS version)
        - Virus (was there a virus in a mail)
        - SpamInfo (is mail a spam)
        :param event: event to be parsed (single line in log)
        :return: parsed event
        """
        action = event['Act'] if 'Act' in event else None
        tls_version = event['TlsVer'] if 'TlsVer' in event else None
        is_virus = True if 'Virus' in event else False
        is_spam = False if 'SpamInfo' not in event or event['SpamInfo'] == '[]' else True
        if is_virus:
            event_id = 'mail_receipt_virus'
        elif is_spam:
            event_id = 'mail_receipt_spam'
        elif action == 'Rej':
            event_id = 'mail_receipt_rejected'
        elif action == 'Ign':
            event_id = 'mail_receipt_ignored'
        elif action == 'Bnc':
            event_id = 'mail_receipt_bounced'
        elif tls_version is not None and tls_version.startswith('TLSv1'):
            event_id = 'mail_receipt_received'
        elif action == 'Acc' and (tls_version is None or
                                  not tls_version.startswith('TLSv1')):
            event_id = 'mail_receipt_received_notls'
        else:
            event_id = 'mail_receipt_other'
        category = 'mail_receipt'

        timestamp = self.date_helper.convert_from_mimecast_format(event['datetime'])
        event.update({'mimecastEventId': event_id, 'mimecastEventCategory': category, 'time_generated': timestamp})

        return event

    def parse_ttp_url_event(self, event):
        """ Parse a single TTP URL event
        :param event: event to be parsed (single line in log)
        :return: parsed event
        """
        event_id = 'mail_ttp_url'
        category = 'mail_ttp_url'
        timestamp = self.date_helper.convert_from_mimecast_format(event['datetime'])
        event.update({'mimecastEventId': event_id, 'mimecastEventCategory': category, 'time_generated': timestamp})

        return event

    def parse_ttp_impersonation_event(self, event):
        """ Parse a single TTP Impersonation event
        :param event: event to be parsed (single line in log)
        :return: parsed event
        """
        event_id = 'mail_ttp_impersonation'
        category = 'mail_ttp_impersonation'
        timestamp = self.date_helper.convert_from_mimecast_format(event['datetime'])
        event.update({'mimecastEventId': event_id, 'mimecastEventCategory': category, 'time_generated': timestamp})

        return event

    def parse_ttp_attachment_event(self, event):
        """ Parse a single TTP Attachment event
        :param event: event to be parsed (single line in log)
        :return: parsed event
        """
        event_id = 'mail_ttp_attachment'
        category = 'mail_ttp_attachment'
        timestamp = self.date_helper.convert_from_mimecast_format(event['datetime'])
        event.update({'mimecastEventId': event_id, 'mimecastEventCategory': category, 'time_generated': timestamp})

        return event

    def parse_ttp_iep_event(self, event):
        """ Parse a single TTP IEP event
        :param event: event to be parsed (single line in log)
        :return: parsed event
        """
        event_id = 'mail_ttp_iep'
        category = 'mail_ttp_iep'
        timestamp = self.date_helper.convert_from_mimecast_format(event['datetime'])
        event.update({'mimecastEventId': event_id, 'mimecastEventCategory': category, 'time_generated': timestamp})

        return event

    def parse_journal_event(self, event):
        """Parse a single Journaling event.
        :param event: event to be parsed (single line in log)
        :return: parsed event
        """
        event_id = 'mail_journal'
        category = 'mail_journal'
        timestamp = self.date_helper.convert_from_mimecast_format(event['datetime'])
        event.update({'mimecastEventId': event_id, 'mimecastEventCategory': category, 'time_generated': timestamp})

        return event

    def parse_spameventthread(self, event):
        """Parse a single Spameventthread event.
        :param event: event to be parsed (single line in log)
        :return: parsed event
        """

        event_id = 'mail_spameventthread'
        category = 'mail_spameventthread'
        timestamp = self.date_helper.convert_from_mimecast_format(event['datetime'])
        event.update({'mimecastEventId': event_id, 'mimecastEventCategory': category, 'time_generated': timestamp})

        return event

    def parse_other_event(self, event):
        """ Parse a single event that we don't expect
        :param event: event to be parsed (single line in log)
        :event_type: name of event type from response header
        :return: parsed event as unicode
        """
        event_id = 'other_{0}'.format(event['logType'])
        category = 'other'
        logging.warning('Unexpected log type: "{0}"'.format(event['logType']))
        timestamp = self.date_helper.convert_from_mimecast_format(event['datetime'])
        event.update({'mimecastEventId': event_id, 'mimecastEventCategory': category, 'time_generated': timestamp})

        return event
