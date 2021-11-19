
class GetThreatIntelFeedRequest:
    def __init__(self, start_date, end_date, feed_type):
        self.payload = {
            'data': [
                {
                    'compress': True,
                    'fileType': 'csv',
                    'start': start_date,
                    'end': end_date,
                    'feedType': feed_type
                }
            ]
        }
