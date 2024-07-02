from datetime import datetime

DATETIME_FORMAT = "%Y-%m-%dT%H:%M:%S.%fZ"

class ProcessingStatus:
    def __init__(self, is_failure: bool, is_timeout: bool):
        self.is_failure = is_failure
        self.is_timeout = is_timeout


class QueueMessage:
    def __init__(self, message_body, queue_dequeue_count, max_queue_message_retries):
        self.max_queue_message_retries = max_queue_message_retries
        self.queue_dequeue_count = queue_dequeue_count
        self.message_body = message_body
        self.message_id = message_body.get('message_id')
        self.project = message_body.get('project')
        self.log_store = message_body.get('log_store')
        self.start_time = message_body.get('start_time')
        self.end_time = message_body.get('end_time')
        dequeue_count_str = message_body.get('dequeue_count')

        self.dequeue_count = 1
        if dequeue_count_str is not None:
            self.dequeue_count = int(dequeue_count_str)


    def validate(self):
        if (self.dequeue_count >= self.max_queue_message_retries or self.queue_dequeue_count >= self.max_queue_message_retries):
            return (False, "The queue message reached its max allowed re-try attempts. Not retrying it again. message_body: {}".format(self.message_body))

        if (self.project == "" or self.project is None or self.log_store == "" or self.log_store is None or self.start_time == "" or self.start_time is None or self.end_time == "" or self.end_time is None):
            return (False, "One of the queue message properties was missing or empty, could not perform operation. message_body: {}".format(self.message_body))
        
        try:
            self.start_time_dt = datetime.strptime(self.start_time, DATETIME_FORMAT)
            self.end_time_dt = datetime.strptime(self.end_time, DATETIME_FORMAT)
        except ValueError as e:
            return (False, "Invalid date format in the queue message. Error: {}. message_body: {}".format(str(e), self.message_body))

        if self.start_time_dt >= self.end_time_dt or self.end_time_dt > datetime.utcnow():
            return (False, "The time range included in the queue message was incorrect, could not perform operation. message_body: {}".format(self.message_body))
        
        return (True, None)