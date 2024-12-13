class GetTTPAttachmentLogsRequest:
    def __init__(self, from_date, to_date, token):
        self.payload = {
            "meta": {"pagination": {"pageSize": 500}},
            "data": [{"from": from_date, "to": to_date, "oldestFirst": True, "route": "all", "result": "all"}],
        }
        if token:
            self.payload["meta"]["pagination"]["pageToken"] = token
