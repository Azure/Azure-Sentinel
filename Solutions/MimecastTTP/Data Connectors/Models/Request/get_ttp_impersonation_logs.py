class GetTTPImpersonationLogsRequest:
    def __init__(self, from_date, to_date, token):
        self.payload = {
            "meta": {"pagination": {"pageSize": 500}},
            "data": [{"oldestFirst": True, "from": from_date, "to": to_date}],
        }
        if token:
            self.payload["meta"]["pagination"]["pageToken"] = token
