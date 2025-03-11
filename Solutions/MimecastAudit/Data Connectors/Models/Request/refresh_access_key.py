class RefreshAccessKeyRequest:
    def __init__(self, email, expired_access_key):
        self.payload = {"data": [{"userName": email}]}
        if expired_access_key:
            self.payload['data'][0]['accessKey'] = expired_access_key
