from typing import Dict, Union

from .utils.json_utils import add_attrib


class RetryOptions:
    """Retry Options.

    Defines retry policies that can be passed as parameters to various
    operations.
    """

    def __init__(
            self,
            first_retry_interval_in_milliseconds: int,
            max_number_of_attempts: int):
        self._first_retry_interval_in_milliseconds: int = \
            first_retry_interval_in_milliseconds
        self._max_number_of_attempts: int = max_number_of_attempts

        if self._first_retry_interval_in_milliseconds <= 0:
            raise ValueError("first_retry_interval_in_milliseconds value"
                             "must be greater than 0.")

    @property
    def first_retry_interval_in_milliseconds(self) -> int:
        """Get the first retry interval (ms).

        Must be greater than 0

        Returns
        -------
        int
            The value indicating the first retry interval
        """
        return self._first_retry_interval_in_milliseconds

    @property
    def max_number_of_attempts(self) -> int:
        """Get Max Number of Attempts.

        Returns
        -------
        int
            Value indicating the max number of attempts to retry
        """
        return self._max_number_of_attempts

    def to_json(self) -> Dict[str, Union[str, int]]:
        """Convert object into a json dictionary.

        Returns
        -------
        Dict[str, Any]
            The instance of the class converted into a json dictionary
        """
        json_dict: Dict[str, Union[str, int]] = {}

        add_attrib(
            json_dict,
            self,
            'first_retry_interval_in_milliseconds',
            'firstRetryIntervalInMilliseconds')
        add_attrib(
            json_dict,
            self,
            'max_number_of_attempts',
            'maxNumberOfAttempts')
        return json_dict
