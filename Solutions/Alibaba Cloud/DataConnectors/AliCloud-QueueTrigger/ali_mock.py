import logging

class LogClient:
    def __init__(self, ali_endpoint, ali_access_key_id, ali_access_key, token):
        logging.getLogger().setLevel(logging.INFO)

    def list_project(self, size):
        projects_data = [
            {"projectName": "Project 1"},
            {"projectName": "Project 2"},
            {"projectName": "Project 3"}
        ]
        return Projects(projects_data)
    
    def list_logstores(self, request):
        return ListLogstoresResponse()

    def get_log_all(self, project, logstore, from_time, to_time, topic, query):
        return [ListLogsResponse(project, logstore),ListLogsResponse(project, logstore)]

class Projects:
    def __init__(self, projects):
        self.projects = projects

    def get_projects(self):
        return self.projects

class ListProjectsResponse:
    def get_logstores(self):
        return ['logstore_a', 'logstore_b', 'logstore_c', 'logstore_d']

class ListLogstoresRequest:
    def __init__(self,project):
        self.project = project

class ListLogstoresResponse:
    def get_logstores(self):
        return ['logstore_a', 'logstore_b', 'logstore_c', 'logstore_d']

class ListLogsResponse:
    def __init__(self,project, logstore):
        self.project = project
        self.logstore = logstore

    def get_logs(self):
        source = "{}-{}".format(self.project,self.logstore)
        log1 = LogRecord("a1",source,"a2")
        log2 = LogRecord("b1",source,"b2")
        log3 = LogRecord("c1",source,"c2")
        return [log1,log2,log3]

class LogRecord:
    def __init__(self, timestamp, source, contents):
        self.timestamp = timestamp
        self.source = source
        self.contents = contents