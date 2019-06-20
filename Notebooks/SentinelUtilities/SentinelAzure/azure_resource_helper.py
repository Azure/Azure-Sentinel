"""
Azure Resource Helper:
This module provides helper methods to initialize and manipulate ResourceManagementClient object.
Resource Group is the focal point.
"""

from azure.mgmt.resource import ResourceManagementClient

class ResourceHelper:
    def __init__(self, resource_client, resource_group):
        self.resource_client = resource_client
        self.resource_group = resource_group

    def create_resource_group(self, resource_group_location):
        resource_group_params = { 'location': resource_group_location }
        create_resource_group_async = self.resource_client.resource_groups.create_or_update(
            self.resource_group, 
            resource_group_params
        )

# end of the class
