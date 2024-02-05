import requests
from requests.auth import HTTPBasicAuth
import config

from .model import Model
from .header import Header
from .attachment import Attachment
from .link import Link
from .assessment import Assessment


class Email(Model):
    RESOURCE_URL = 'emails'

    def __init__(self, message_id: str, size_bytes: int, subject: str, from_email: str, from_name: str, reply_to: str,
                 spam_score: int, spf: str, originating_ip: str,
                 reporter_domain: str, company_id: int, feedback_requested: bool, feedback_provided: bool,
                 reported_risk: int, category: str, risk: str, risk_source: str, sent_at: str, reported_at: str,
                 assessed_at: str, checked_at: str, content_status: str, id: int = None, links_count: int = None,
                 attachments_count: int = None):
        self.id = id
        self.message_id = message_id
        self.size_bytes = size_bytes
        self.subject = subject
        self.from_email = from_email
        self.from_name = from_name
        self.reply_to = reply_to
        self.spam_score = spam_score
        self.spf = spf
        self.originating_ip = originating_ip
        self._links_count_hard = links_count
        self.links = []
        self._attachments_count_hard = attachments_count
        self.attachments = []
        self.reporter_domain = reporter_domain
        self.company_id = company_id
        self.feedback_requested = feedback_requested
        self.feedback_provided = feedback_provided
        self.reported_risk = reported_risk
        self.category = category
        self.risk = risk
        self.risk_source = risk_source
        self.sent_at = sent_at
        self.reported_at = reported_at
        self.assessed_at = assessed_at
        self.checked_at = checked_at
        self.content_status = content_status
        self.headers = []
        self.assessments = []

    @property
    def links_count(self):
        if self._links_count_hard is not None:
            return self._links_count_hard

        return len(self.links)

    @links_count.setter
    def links_count(self, count):
        self._links_count_hard = count

    @property
    def attachments_count(self):
        if self._attachments_count_hard is not None:
            return self._attachments_count_hard

        return len(self.attachments)

    @attachments_count.setter
    def attachments_count(self, count):
        self._attachments_count_hard = count

    def is_content_ready(self):
        return self.content_status == 'received'

    def is_content_missing(self):
        return self.content_status == 'missing'

    def is_waiting_for_content(self):
        return self.content_status == 'pending'

    def may_receive_content_in_future(self):
        return self.content_status == 'pending' or self.content_status == 'unknown'

    @classmethod
    def get(cls, id: int):
        url = ''.join([cls.BASE_URL, cls.RESOURCE_URL, '/', id])
        response = requests.get(url,
                                auth=HTTPBasicAuth(config.API_KEY, config.API_SECRET),
                                verify=config.VERIFY_CERTIFICATE)

        return cls.from_json(response.json()['data'], True)

    @classmethod
    def from_json(cls, json_item, full=True):
        email = cls(message_id=json_item['message_id'], size_bytes=json_item['size_bytes'],
                    subject=json_item['subject'], from_email=json_item['from_email'], from_name=json_item['from_name'],
                    reply_to=json_item['reply_to'], spam_score=json_item['spam_score'], spf=json_item['spf'],
                    originating_ip=json_item['originating_ip'], reporter_domain=json_item['reporter_domain'],
                    company_id=json_item['company_id'], feedback_requested=json_item['feedback_requested'],
                    feedback_provided=json_item['feedback_provided'], reported_risk=json_item['reported_risk'],
                    category=json_item['category'], risk=json_item['risk'], risk_source=json_item['risk_source'],
                    sent_at=json_item['sent_at'], reported_at=json_item['reported_at'],
                    assessed_at=json_item['assessed_at'], checked_at=json_item['checked_at'], content_status=json_item['content_status'],
                    id=json_item['id'])

        if 'links_count' in json_item:
            email.links_count = json_item['links_count']

        if 'attachments_count' in json_item:
            email.attachments_count = json_item['attachments_count']

        if full:
            for header_json in json_item['headers']:
                email.headers.append(Header.from_json(header_json))

            for attachment_json in json_item['attachments']:
                email.attachments.append(Attachment.from_json(attachment_json))

            for link_json in json_item['links']:
                email.links.append(Link.from_json(link_json))

            for assessment_json in json_item['assessments']:
                email.assessments.append(Assessment.from_json(assessment_json))

        return email

    def __str__(self):
        return self.subject
