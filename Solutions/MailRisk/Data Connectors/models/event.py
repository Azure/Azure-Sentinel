from .model import Model


class Event(Model):
    RESOURCE_URL = 'events'

    def __init__(self, id: int, event: str, email_id: int, created_at: str):
        self.id = id
        self.event = event
        self.email_id = email_id
        self.created_at = created_at

    @classmethod
    def from_json(cls, json_item):
        return cls(id=json_item['id'],
                   event=json_item['event'],
                   email_id=json_item['email_id'],
                   created_at=json_item['created_at'])

    def __str__(self):
        return self.event
