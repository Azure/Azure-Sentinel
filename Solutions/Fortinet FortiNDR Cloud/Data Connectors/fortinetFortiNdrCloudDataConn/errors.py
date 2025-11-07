class BaseError(Exception):
    """Base class for metastream client errors"""

    def __init__(self, code, message):
        self.code = code
        self.message = message
        super().__init__(message)


class InputError(BaseError):
    """Exception raised for user input errors"""
    def __init__(self, message):
        super().__init__(code=0, message=message)


class ServerError(BaseError):
    """Exception raised for server side errors"""
    pass
