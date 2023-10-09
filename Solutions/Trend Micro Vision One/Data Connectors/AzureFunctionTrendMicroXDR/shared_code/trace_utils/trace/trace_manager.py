import threading
import uuid


class TraceManager:
    def __init__(self):
        self.local = threading.local()

    @property
    def trace_id(self):
        if not getattr(self.local, 'trace_id', None):
            self.local.trace_id = str(uuid.uuid4())
        return self.local.trace_id

    @property
    def task_id(self):
        if not getattr(self.local, 'task_id', None):
            self.local.task_id = str(uuid.uuid4())
        return self.local.task_id

    @trace_id.setter
    def trace_id(self, value):
        self.local.trace_id = value

    @task_id.setter
    def task_id(self, value):
        self.local.task_id = value


trace_manager = TraceManager()
