class GetThreatIntelFeedRequest:
    def __init__(self, from_date, to_date, feed_type, token):
        self.payload = {
            "data": [{"compress": True, "fileType": "csv", "start": from_date, "end": to_date, "feedType": feed_type}]
        }
        if token:
            self.payload["data"][0].update({"token": token})
