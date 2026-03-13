#  Copyright (c) Microsoft Corporation. All rights reserved.
#  Licensed under the MIT License.
from typing import Optional

from azure.functions.decorators.core import Setting

RETRY_POLICY = "retry_policy"


class RetryPolicy(Setting):

    def __init__(self,
                 strategy: str,
                 max_retry_count: str,
                 delay_interval: Optional[str] = None,
                 minimum_interval: Optional[str] = None,
                 maximum_interval: Optional[str] = None,
                 **kwargs):
        self.strategy = strategy
        self.max_retry_count = max_retry_count
        self.delay_interval = delay_interval
        self.minimum_interval = minimum_interval
        self.maximum_interval = maximum_interval
        super().__init__(setting_name=RETRY_POLICY)
