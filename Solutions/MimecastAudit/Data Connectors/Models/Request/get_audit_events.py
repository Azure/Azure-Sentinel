
class GetAuditEventsRequest:
    def __init__(self, start_datetime, end_datetime, token):
        self.payload = {'data': [{
            'startDateTime': start_datetime,
            'endDateTime': end_datetime
        }],
                        'meta': {
                            'pagination': {
                                'pageSize': 500
                            }
                        }
                    }
        if token:
            self.payload.update({"meta": {"pagination": {"pageToken": token}}})
