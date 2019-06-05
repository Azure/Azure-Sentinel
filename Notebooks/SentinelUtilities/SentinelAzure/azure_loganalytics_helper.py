from azure.mgmt.loganalytics import LogAnalyticsManagementClient

class LogAnalyticsHelper(object):
    def __init__(self, la_client):
        self.la_client = la_client

    def get_workspace_name_list(self):
        return sorted([ws.name for ws in self.la_client.workspaces.list()])

    def get_workspace_id(self, workspace_name):
        workspace = next(ws for ws in self.la_client.workspaces.list() if ws.name == workspace_name)
        return workspace.customer_id
# end of the class
