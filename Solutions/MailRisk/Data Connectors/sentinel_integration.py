from mailrisk import emails_list, events_list
from sentinel_api import post_data
import datetime
import json
from collections import defaultdict
from copy import copy
from models.event_types import RISK_CHANGED, CONTENTS_RECEIVED, FEEDBACK_REQUESTED, EMAIL_REPORTED

ACTIVE_EVENT_TYPES = [RISK_CHANGED, CONTENTS_RECEIVED, FEEDBACK_REQUESTED, EMAIL_REPORTED]

# Fetch the relevant emails and send them to Azure Sentinel
def post_emails(email_ids_and_event_types: 'dict[int, list[str]]') -> bool: 
    email_ids = list(email_ids_and_event_types.keys())
    limit = len(email_ids)

    emails = emails_list(limit=limit, email_ids=','.join(str(id) for id in email_ids), enrich=True)

    emails_with_event_type = []
    for email in emails:
        event_types = email_ids_and_event_types[email.id]
        for event in event_types:
            # Skip emails that were reported as spam
            if event == EMAIL_REPORTED and email.reported_risk == 1:
                continue
            email.event_type = event
            emails_with_event_type.append(copy(email))

    body = json.dumps(emails_with_event_type, default=lambda model: model.__dict__)
    return post_data(body)


# Find new emails using the MailRisk API events
def get_new_email_ids_and_event_types(input, outputblob) -> 'dict[int, list[str]]':
    limit = 100

    if len(input) > 0:
        last_event_id = int(input)
        events = events_list(limit=limit, direction='asc', after_id=last_event_id)
    else:
        # If no email is posted yet, only happens on the first trigger or if storage is deleted.
        after = datetime.datetime.now() - datetime.timedelta(minutes=60)
        events = events_list(limit=limit, direction='asc', after=after)
        if len(events) == 0:
            after = datetime.datetime.now() - datetime.timedelta(hours=12)
            events = events_list(limit=limit, direction='asc', after=after)

    email_ids_and_event_types = defaultdict(list)
    if len(events) > 0:
        outputblob.set(str(events[-1].id))
        
        for event in events:
            if event.event in ACTIVE_EVENT_TYPES:
                email_ids_and_event_types[event.email_id].append(event.event) 
    
    return email_ids_and_event_types
