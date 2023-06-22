from .model import Model


class Link(Model):
    # SIC: Attachment is a sub-resource under emails
    RESOURCE_URL = 'emails'

    def __init__(self, url: str, text: str, hostname: str):
        self.url = url
        self.text = text
        self.hostname = hostname

    @classmethod
    def from_json(cls, json_item):
        return cls(url=json_item['url'],
                   text=json_item['text'],
                   hostname=json_item['hostname'])

    def __str__(self):
        return self.url
