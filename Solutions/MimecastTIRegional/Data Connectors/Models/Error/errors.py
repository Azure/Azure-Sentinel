class BaseError(Exception):
    request_id = None

    def __init__(self, message, request_id=None):
        if request_id:
            self.request_id = request_id
        super(BaseError, self).__init__(message)


class MimecastRequestError(BaseError):
    pass


class ParsingError(MimecastRequestError):
    pass


class InvalidDataError(MimecastRequestError):
    pass


class GraphAPIRequestError(BaseError):
    pass
