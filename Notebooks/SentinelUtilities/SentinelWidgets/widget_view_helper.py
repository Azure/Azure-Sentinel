# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
"""
Widget View Helper:
This module provides helper methods for UI controls and components.
"""

import os
import ipywidgets as widgets
from IPython.display import HTML

# pylint: disable-msg=R0904
# pylint: disable-msg=E0602
class WidgetViewHelper():
    """ This classes provides helper methods for UI controls and components. """

    def __init__(self):
        self.variable = None

    def set_env(self, env_dir, var):
        """ Set notebook environmental variable """
        val = None
        if var in env_dir.keys():
            val = env_dir[var]

        self.variable = var
        user_input = widgets.Text(value=val, description=var + ': ')
        user_input.observe(self.save_env, 'value')
        display(user_input)

    def save_env(self, val):
        """ Save notebook environmental variable """
        os.environ[self.variable] = val.new

    @staticmethod
    def set_env1(reset, env_dir, env_dict):
        """ Set notebook environmental variables """
        for key in env_dict.keys():
            user_input = ''
            if not reset and key in env_dir:
                env_dict[key] = env_dir[key]
                print(key + '=' + env_dir[key])
            else:
                user_input = widgets.Text(description=key + ': ')
                os.environ[key] = user_input.value
                env_dict[key] = user_input.value
        return env_dict

    @staticmethod
    def select_vm(compute):
        """ Select a VM """
        vm_names = sorted(list(vm.name for vm in list(compute.get_vm_list())))
        return widgets.Dropdown(options=vm_names, value=vm_names[0], description='VM:')

    @staticmethod
    def select_managed_disk(compute, vm_name):
        """ Select a managed disk """
        disk_list = compute.get_vm_disk_names(vm_name)
        return widgets.Dropdown(options=disk_list, value=disk_list[0], description='Disk:')

    @staticmethod
    def select_account_creation():
        """ Create a new account or use existing account """
        storage_account_creation = ['Creating new account', 'Using exist account']
        return widgets.Dropdown(options=storage_account_creation,
                                value=storage_account_creation[0],
                                description='Storage Account Creation:')

    @staticmethod
    def select_blob_container_creation():
        """ Create a new container or use existing container """
        blob_container_creation = ['Creating new container', 'Using exist container']
        return widgets.Dropdown(options=blob_container_creation,
                                value=blob_container_creation[0],
                                description='Blob Container Creation:')

    @staticmethod
    def select_os():
        """ Select Windows or Linux """
        os_type_list = ['Windows', 'Linux']
        return widgets.Dropdown(options=os_type_list, value=os_type_list[0], description='OS Type:')

    @staticmethod
    def check_storage_account_name_availability(storage):
        """ Check if a storage account name is available to use """
        # usert input storage account name
        storage_account_name = input('Storage Account Name:')
        name_availability = storage.is_storage_account_name_available(storage_account_name)
        return storage_account_name if name_availability.name_available else None

    @staticmethod
    def create_storage_account_and_get_key(storage,
                                           storage_account_name,
                                           resource_group_for_storage):
        """ Create storage account """
        storage_location = input('Storage Location:')
        storage.create_storage_account_async(
            storage_account_name,
            resource_group_for_storage,
            **{'storage_location' : storage_location})
        return storage.get_storage_account_key(storage_account_name, resource_group_for_storage)

    @staticmethod
    def select_storage_account(storage, resource_group_for_storage):
        """ Select a storage account """
        storage_account_list = storage.get_storage_account_names(resource_group_for_storage)
        return widgets.Dropdown(options=storage_account_list,
                                value=storage_account_list[0],
                                description='Existing Storage Accounts:')

    @staticmethod
    def select_blob_container(storage, resource_group_for_storage, storage_account_name):
        """ Select a blob container """
        blob_container_list = storage.get_container_name_list(resource_group_for_storage,
                                                              storage_account_name,
                                                              None)
        return widgets.Dropdown(options=blob_container_list,
                                value=blob_container_list[0],
                                description='Blob Containers:')

    @staticmethod
    def select_log_analytics_workspace(loganalytics):
        """ Select a LA workspace """
        workspace_name_list = loganalytics.get_workspace_name_list()
        return widgets.Dropdown(options=workspace_name_list,
                                value=workspace_name_list[0],
                                description='Workspace:')

    @staticmethod
    def select_multiple_tables(anomaly_lookup):
        """ Select data tables """
        table_list = anomaly_lookup.query_table_list()
        tables = sorted(table_list.TableName.tolist())
        return widgets.SelectMultiple(options=tables,
                                      row=len(tables),
                                      value=[],
                                      description='Tables:')

    @staticmethod
    def generate_upload_container_path(storage, os_type, sas_expiration_in_days):
        """ Generate a upload container path """
        sas_url = storage.generate_blob_container_sas_url(sas_expiration_in_days)
        upload_container_path = storage.build_upload_container_path(os_type, sas_url)
        return upload_container_path

    @staticmethod
    # pylint: disable=line-too-long
    def get_vm_extension_properties(os_type, upload_container_path, user_id=None):
        """ Get VM extensions properties """
        if os_type == 'Windows':
            command_to_execute = 'powershell -File installNotebookExtension.ps1 "{0}" >> out.txt'.format(upload_container_path)
            file_list = ['https://sentinelnotebooks.blob.core.windows.net/piwindowsstorage/installNotebookExtension.ps1',
                         'https://sentinelnotebooks.blob.core.windows.net/piwindowsstorage/piextension.zip']
        elif os_type == 'Linux':
            command_to_execute = './piondemand.sh "' + upload_container_path + '"'
            file_list = ['https://sentinelnotebooks.blob.core.windows.net/pilinuxstorage/release/ondemand/stable/piondemand.sh',
                         'https://sentinelnotebooks.blob.core.windows.net/pilinuxstorage/release/ondemand/stable/pilinux.ondemand.tar.bz2']

        elif os_type == 'DSVM':
            command_to_execute = './azureforensics.sh {0}'.format(user_id)
            file_list = ['https://sentinelnotebooks.blob.core.windows.net/forensicsnotebooks/azureforensics.sh',
                         'https://sentinelnotebooks.blob.core.windows.net/forensicsnotebooks/vhdexplorer.tar']

        return command_to_execute, file_list

    @staticmethod
    def define_int_progress_bar():
        """ Define a progress bar """
        return widgets.IntProgress(value=0,
                                   min=0,
                                   max=10,
                                   step=1,
                                   description='Loading:',
                                   bar_style='success',
                                   orientation='horizontal',
                                   position='top')

    @staticmethod
    # pylint: disable=line-too-long
    def copy_to_clipboard(url, text_body, label_text):
        """ Copy text to Clipboard """
        html_str = (
            """<!DOCTYPE html>
            <html><body>
            <input  id="sentinel_text_for_copy" type="text" readonly style="font-weight: bold; border: none; width:1px;" size = '"""
            + str(len(text_body))
            + """' value='"""
            + text_body
            + """'>
            <a target="_new" href="javascript:void(0);" onclick="sentinel_copy()">""" + label_text + """</a>
            <script>
            var sentinel_win = null
            function sentinel_copy() {
                var copyText = document.getElementById("sentinel_text_for_copy");
                copyText.select();
                document.execCommand("copy");

                var w = screen.width - 300;
                var h = screen.height - 300;
                params = 'width='+w+',height='+h
                sentinel_win = window.open('"""
                        + url
                        + """', 'sentinel_win', params);
            }

            </script>
            </body></html>"""
        )

        return html_str

    @staticmethod
    # pylint: disable=line-too-long
    def construct_url_for_log_analytics_logs(tenant_domain,
                                             subscription_id,
                                             resource_group,
                                             workspace_name):
        """ Generate URL for LA logs """
        return 'https://ms.portal.azure.com/#@{0}/resource/subscriptions/{1}/resourceGroups/{2}/providers/Microsoft.OperationalInsights/workspaces/{3}/logs'.format(tenant_domain, subscription_id, resource_group, workspace_name)

    @staticmethod
    # pylint: disable=undefined-variable
    def display_html(inner_html):
        """ Display HTML """
        display(HTML(inner_html))

    @staticmethod
    def pick_start_and_end_date():
        """ Pick dates """
        start_date = widgets.DatePicker(description='Pick a start date', disabled=False)
        end_date = widgets.DatePicker(description='Pick a end date', disabled=False)
        # pylint: disable=undefined-variable
        display(start_date)
        # pylint: disable=undefined-variable
        display(end_date)
        return start_date, end_date

    @staticmethod
    # pylint: disable=line-too-long
    # pylint: disable=undefined-variable
    def select_multiple_items(label, item_name):
        """ Select multiple items """
        label_item = widgets.Label(value=label)
        items = widgets.Textarea(value='', placeholder='One per line: \n 0x7ae3 \n 0x7ae6', description=item_name, disabled=False, rows=5)
        display(label_item)
        display(items)
        return items
