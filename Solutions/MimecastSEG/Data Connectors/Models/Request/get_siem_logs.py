class GetSIEMLogsRequest:
    def __init__(self, file_format, token):
        self.payload = {
            'data': [
                {
                    'type': 'MTA',
                    'compress': True,
                    'fileFormat': file_format
                }
            ]
        }
        if token:
            self.payload['data'][0]['token'] = token
