import logging


class AuthenticationException(Exception):
    def __init__(self, status: int, message: str) -> None:
        self.status = status
        self.message = message
        self.s = f"AuthenticationException happend with status: {self.status}. Message: {self.message}"
        logging.error(self.s)

    def __str__(self) -> str:
        return self.s


class MissingCredentialsException(Exception):
    def __init__(self) -> None:
        self.s = "Missing credentials. Check if username and password are passed and correct."
        logging.error(self.s)

    def __str__(self) -> str:
        return self.s


class InvalidCredentialsException(AuthenticationException):
    def __init__(self, e: AuthenticationException) -> None:
        self.s = f"{e.status, e.message}. Failed to get token in init setup. Check your credentials."
        logging.error(self.s)

    def __str__(self) -> str:
        return self.s


class TokenRefreshException(AuthenticationException):
    def __init__(self, e: AuthenticationException) -> None:
        self.s = f"{e.status, e.message}. Failed to update access token. Refresh token may be invalid or expired."
        logging.error(self.s)

    def __str__(self) -> str:
        return self.s


# class ServiceClientResponseError(ClientResponseError):
#     def __init__(self, status, message,request_info, history):
#         self.s = "ServiceClientResponseError happend"
#         logging.error(self.s)
#         super().__init__(status=status, message=message,request_info=request_info, history=history)
#
#     def __str__(self):
#         return f"{self.s}"
