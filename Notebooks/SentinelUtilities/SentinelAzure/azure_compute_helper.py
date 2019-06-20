"""
Azure Compute Helper:
This module provides helper methods to initialize and manipulate ComputeClient object.
VM, VM Extension, and VM snapshots are the focal points.
"""

from azure.mgmt.compute.models import DiskCreateOption
from azure.mgmt.compute import ComputeManagementClient
import azure.mgmt.compute.models
import json
import pandas as pd
import requests



class VMExtensionProperties:
    def __init__(self):
        self.api_version = ''
        self.command_key = 'commandToExecute'
        self.command_to_execute = ''
        self.type_handler_version = ''
        self.type_publisher = ''
        self.resource_type = 'virtualMachines'
        self.extension_type = ''
        self.file_uris = []
        self.protected_settings = {}
        self.settings = {}

class WindowsVMExtensionProperties(VMExtensionProperties):
    def __init__(self, command_to_execute, file_uris):
        super(WindowsVMExtensionProperties, self).__init__()
        self.api_version = '2018-06-01'
        self.command_to_execute = command_to_execute
        self.type_handler_version = '1.9'
        self.type_publisher = 'Microsoft.Compute'
        self.extension_type = 'CustomScriptExtension'
        self.file_uris = file_uris
        self.protected_settings[self.command_key] = command_to_execute
        self.settings['fileUris'] = file_uris

class LinuxVMExtensionProperties(VMExtensionProperties):
    def __init__(self, command_to_execute, file_uris):
        super(LinuxVMExtensionProperties, self).__init__()
        self.api_version = '2015-06-15'
        self.command_to_execute = command_to_execute
        self.type_handler_version = '2.0'
        self.type_publisher = 'Microsoft.Azure.Extensions'
        self.extension_type = 'CustomScript'
        self.file_uris = file_uris
        self.protected_settings[self.command_key] = command_to_execute
        self.settings['fileUris'] = file_uris

class ComputeHelper:
    def __init__(self, compute_client, resource_group):
        self.compute_client = compute_client
        self.resource_group = resource_group

    def get_vm_disk_names(self, vm_name):
        vm = self.compute_client.virtual_machines.get(self.resource_group, vm_name, expand='instanceView')
    
        if vm is not None and vm.instance_view is not None:
            return [d.name for d in vm.instance_view.disks]
        else:
            return []

    def create_snapshot_async(self, **kwargs):
        managed_disk = self.compute_client.disks.get(self.resource_group, kwargs['selected_disk'])

        async_snapshot_creation = self.compute_client.snapshots.create_or_update(
            self.resource_group,
            kwargs['snapshot_name'],
            {
                'location': managed_disk.location,
                'creation_data': {
                    'create_option': 'Copy',
                    'source_uri': managed_disk.id
                }
            }
        )

        return async_snapshot_creation.result()

    def generate_snapshot_sas_url_async(self, **kwargs):
        async_snapshot_export = self.compute_client.snapshots.grant_access(
            self.resource_group,
            kwargs['snapshot_name'],
            'read',
            kwargs['int_seconds'])

        result = async_snapshot_export.result()
        return result.access_sas

    def create_snapshot_and_generate_sas_url(self, **kwargs):
        snapshot = self.create_snapshot_async(**kwargs)
        if snapshot is not None and snapshot.provisioning_state == 'Succeeded':
            return self.generate_snapshot_sas_url_async(**kwargs)

    def get_vm_list(self):
        return self.compute_client.virtual_machines.list_all()

    def get_vm_and_vm_extensions(self, vm_name):
        vm = self.compute_client.virtual_machines.get(self.resource_group, vm_name, expand='instanceView')

        if (vm is not None):
            return vm, vm.instance_view.extensions
        else:
            return None, None

    def get_vm(self, vm_name):
        return self.compute_client.virtual_machines.get(self.resource_group, vm_name)

    def has_vm_extensions(self, vm):
        try:
            return vm.instance_view.extensions is not None
        except:
            return False
    
    def get_customscript_extensions(self, vm):
        try:
            exts = vm.instance_view.extensions
            if exts is not None:
                return list(ext for ext in exts if ext.type == 'Microsoft.Azure.Extensions.CustomScript')
            else:
                return None
        except:
            return None
    
    def delete_vm_extension_async(self, vm_name, vm_extension_name):
        async_vm_extension_delete = self.compute_client.virtual_machine_extensions.delete(self.resource_group, vm_name, vm_extension_name)
        return async_vm_extension_delete.result()

    def check_vm_extension_installability(self, vm):
        if self.has_vm_agent(vm) == False:
            return False, 'No guest agent on the VM, VM Extension cannot be installed'
        else:
            exts = self.get_customscript_extensions(vm)
            if exts is not None:
                return False, 'VM has custom script extension installed already, need to delete the VM extension first to continue'
            else:
                return True, ""

    def has_vm_agent(self, vm):
        try:
            return vm.instance_view.vm_agent is not None
        except:
            return False

    def initialize_vm_extension(self, vm_extension_properties, vm_location):
        vm_extension = azure.mgmt.compute.models.VirtualMachineExtension(
            location = vm_location,
            publisher = vm_extension_properties.type_publisher,
            virtual_machine_extension_type = vm_extension_properties.extension_type,
            type_handler_version = vm_extension_properties.type_handler_version,
            auto_upgrade_minor_version = True,
            settings = vm_extension_properties.settings,
            protected_settings = vm_extension_properties.protected_settings
        )
        return vm_extension

    def create_vm_extension_async(self, vm_name, vm_extension_name, vm_extension):
        async_vm_extension_creation = self.compute_client.virtual_machine_extensions.create_or_update(
            self.resource_group,
            vm_name,
            vm_extension_name,
            vm_extension
        )
        return async_vm_extension_creation.result()

    def get_uploaded_result(self, upload_container_path):
        try:
            response = requests.get(upload_container_path)
            response.encoding = response.apparent_encoding
            start_of_json = response.text.index('{')
            raw_json = response.text[start_of_json::]
            return json.loads(raw_json)
        except Exception as e:
            print(e)
            return None

    def create_availability_set(self):
        avset_params = {
            'location': vm_location,
            'sku': { 'name': 'Aligned' },
            'platform_fault_domain_count': 3
        }
        availability_set_result = this.compute_client.availability_sets.create_or_update(
            group_name,
            'myAVSet',
            avset_params
        )

    def create_vm(self, nic, **kwargs):
        create_vm_async = self.compute_client.virtual_machines.create_or_update(
            self.resource_group,
            kwargs['vm_name'],
            azure.mgmt.compute.models.VirtualMachine(
                location = kwargs['vm_location'],
                os_profile = azure.mgmt.compute.models.OSProfile(
                    admin_username = kwargs['user_name'],
                    admin_password = kwargs['password'],
                    computer_name = kwargs['vm_name'],
                ),
                hardware_profile = azure.mgmt.compute.models.HardwareProfile(
                    vm_size = azure.mgmt.compute.models.VirtualMachineSizeTypes.standard_b2s
                ),
                network_profile=azure.mgmt.compute.models.NetworkProfile(
                    network_interfaces=[
                        azure.mgmt.compute.models.NetworkInterfaceReference(
                            id=nic.id,
                            primary=True
                        ),
                    ],
                ),
                storage_profile=azure.mgmt.compute.models.StorageProfile(
                    os_disk=azure.mgmt.compute.models.OSDisk(
                        caching=azure.mgmt.compute.models.CachingTypes.none,
                        create_option=azure.mgmt.compute.models.DiskCreateOptionTypes.from_image,
                        name=kwargs['snapshot_name'],
                        os_type = kwargs['os_type'],
                        vhd=azure.mgmt.compute.models.VirtualHardDisk(
                            uri='https://{0}.blob.core.windows.net/{1}/forensics.vhd'.format(kwargs['stroage_account_name'], kwargs['blob_container_name'])
                        ),
                        image=azure.mgmt.compute.models.VirtualHardDisk(
                            uri='https://{0}.blob.core.windows.net/{1}/abcd.vhd'.format(kwargs['stroage_account_name'], kwargs['blob_container_name'])
                        ),
                    ),
                ),
            ),
        )
        create_vm_async.wait()

    def delete_vm_async(self, vm_name):
        async_vm_delete = self.compute_client.virtual_machines.delete(self.resource_group, vm_name)
        return async_vm_delete.result()
        #async_vm_delete.wait()

# end of the class
