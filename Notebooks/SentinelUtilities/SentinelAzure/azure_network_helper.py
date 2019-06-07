"""
Azure Network Helper:
This module provides helper methods to initialize and manipulate NetworkManagementClient object.
"""

from azure.mgmt.network import NetworkManagementClient

class NetworkHelper:
    def __init__(self, network_client, nic_name):
        self.network_client = network_client
        self.nic_name = nic_name
    
    def get_nic(self, resource_group):
        return self.network_client.network_interfaces.get(
            resource_group, 
            self.nic_name
        )

    def prepare_network_for_vm_creation(self, resource_group, vm_location):
        self.create_public_ip_address(resource_group, vm_location)
        self.create_vnet(resource_group, vm_location)
        self.create_subnet(resource_group)
        self.create_nic(resource_group, vm_location)

    def create_public_ip_address(self, resource_group, vm_location):
        public_ip_addess_params = {
            'location': vm_location,
            'public_ip_allocation_method': 'Dynamic'
        }
        creation_result = self.network_client.public_ip_addresses.create_or_update(
            resource_group,
            'myIPAddress',
            public_ip_addess_params
        )

        return creation_result.result()

    def create_vnet(self, resource_group, vm_location):
        vnet_params = {
            'location': vm_location,
            'address_space': {
                'address_prefixes': ['10.0.0.0/16']
            }
        }
        creation_result = self.network_client.virtual_networks.create_or_update(
            resource_group,
            'myVNet',
            vnet_params
        )
        return creation_result.result()

    def create_subnet(self, resource_group):
        subnet_params = {
            'address_prefix': '10.0.0.0/24'
        }
        creation_result = self.network_client.subnets.create_or_update(
            resource_group,
            'myVNet',
            'mySubnet',
            subnet_params
        )

        return creation_result.result()

    def create_nic(self, resource_group, vm_location):
        subnet_info = self.network_client.subnets.get(
            resource_group, 
            'myVNet', 
            'mySubnet'
        )
        publicIPAddress = self.network_client.public_ip_addresses.get(
            resource_group,
            'myIPAddress'
        )
        nic_params = {
            'location': vm_location,
            'ip_configurations': [{
                'name': 'myIPConfig',
                'public_ip_address': publicIPAddress,
                'subnet': {
                    'id': subnet_info.id
                }
            }]
        }
        creation_result = self.network_client.network_interfaces.create_or_update(
            resource_group,
            self.nic_name,
            nic_params
        )

        return creation_result.result()

# end of the class
