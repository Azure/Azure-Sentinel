import threading
import uuid


class TraceManager:
    def __init__(self):
        self.local = threading.local()

    @property
    def trace_id(self):
        return str(uuid.uuid4())

    @property
    def task_id(self):
        if not getattr(self.local, 'task_id', None):
            self.local.task_id = str(uuid.uuid4())
        return self.local.task_id

    @task_id.setter
    def task_id(self, value):
        self.local.task_id = value


trace_manager = TraceManager()
