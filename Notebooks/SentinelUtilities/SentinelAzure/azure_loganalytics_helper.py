# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
"""
Azure LogAnalytics Helper:
This module provides helper methods to initialize and 
manipulate LogAnalyticsManagementClient object.
Workspace is the focal point.
"""


class LogAnalyticsHelper():
    """ Helper class for Log Analytics """

    def __init__(self, la_client):
        self.la_client = la_client

    def get_workspace_name_list(self):
        """ retrieve L.A. workspace names as a list """
        return sorted([ws.name for ws in self.la_client.workspaces.list()])

    def get_workspace_id(self, workspace_name):
        """ retrieve L.A. workspace id based on workspace name """
        workspace = next(ws for ws in self.la_client.workspaces.list() if ws.name == workspace_name)
        return workspace.customer_id
# end of the class
