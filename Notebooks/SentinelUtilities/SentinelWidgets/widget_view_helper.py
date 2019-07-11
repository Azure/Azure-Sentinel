"""
Widget View Helper:
This module provides helper methods for UI controls and components.
"""

import os
import ipywidgets as widgets
from IPython.display import HTML

"""
Widget View Helper:
This module provides helper methods for UI controls and components.
"""
class WidgetViewHelper():
    def set_env(reset, env_dir, env_dict):
        for key in env_dict.keys():
            ip = ''
            if reset == False and key in env_dir:
                env_dict[key] = env_dir[key]
                print(key + '=' + env_dir[key])
            else:
                ip = input(key + ': ')
                os.environ[key] = ip
                env_dict[key] = ip
        return env_dict

    def select_vm(compute):
        vm_names = sorted(list(vm.name for vm in list(compute.get_vm_list())))
        return widgets.Dropdown(options=vm_names, value=vm_names[0], description='VM:')

    def select_managed_disk(compute, vm_name):
        disk_list = compute.get_vm_disk_names(vm_name)
        return widgets.Dropdown(options=disk_list, value=disk_list[0], description='Disk:')

    def select_account_creation():
        storage_account_creation = ['Creating new account', 'Using exist account']
        return widgets.Dropdown(options=storage_account_creation,
                                value=storage_account_creation[0],
                                description='Storage Account Creation:')

    def select_blob_container_creation():
        blob_container_creation = ['Creating new container', 'Using exist container']
        return widgets.Dropdown(options=blob_container_creation,
                                value=blob_container_creation[0],
                                description='Blob Container Creation:')

    def select_os():
        os_type_list = ['Windows', 'Linux']
        return widgets.Dropdown(options=os_type_list, value=os_type_list[0], description='OS Type:')

    def check_storage_account_name_availability(storage):
        # usert input storage account name
        storage_account_name = input('Storage Account Name:')
        name_availability = storage.is_storage_account_name_available(storage_account_name)
        return storage_account_name if name_availability.name_available == True else None

    def create_storage_account_and_get_key(storage,
                                           storage_account_name,
                                           resource_group_for_storage):
        storage_location = input('Storage Location:')
        async_storage_creation = storage.create_storage_account_async(
            storage_account_name,
            resource_group_for_storage,
            **{'storage_location' : storage_location})
        return storage.get_storage_account_key(storage_account_name, resource_group_for_storage)

    def select_storage_account(storage, resource_group_for_storage):
        storage_account_list = storage.get_storage_account_names(resource_group_for_storage)
        return widgets.Dropdown(options=storage_account_list,
                                value=storage_account_list[0],
                                description='Existing Storage Accounts:')

    def select_blob_container(storage, resource_group_for_storage, storage_account_name):
        blob_container_list = storage.get_container_name_list(resource_group_for_storage,
                                                              storage_account_name,
                                                              None)
        return widgets.Dropdown(options=blob_container_list,
                                value=blob_container_list[0],
                                description='Blob Containers:')

    def select_log_analytics_workspace(loganalytics):
        workspace_name_list = loganalytics.get_workspace_name_list()
        return widgets.Dropdown(options=workspace_name_list,
                                value=workspace_name_list[0],
                                description='Workspace:')

    def select_multiple_tables(anomaly_lookup):
        table_list = anomaly_lookup.query_table_list()
        tables = sorted(table_list.TableName.tolist())
        return widgets.SelectMultiple(options=tables,
                                      row=len(tables),
                                      value=[],
                                      description='Tables:')

    def generate_upload_container_path(storage, os_type, sas_expiration_in_days):
        sas_url = storage.generate_blob_container_sas_url(sas_expiration_in_days)
        upload_container_path = storage.build_upload_container_path(os_type, sas_url)
        return upload_container_path

    def get_vm_extension_properties(os_type, upload_container_path, user_id=None):
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

    def define_int_progress_bar():
        return widgets.IntProgress(value=0,
                                   min=0,
                                   max=10,
                                   step=1,
                                   description='Loading:',
                                   bar_style='success',
                                   orientation='horizontal',
                                   position='top')

    # Copy text to Clipboard
    def copy_to_clipboard(url, text_body, label_text):
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

    def construct_url_for_log_analytics_logs(tenant_domain,
                                             subscription_id,
                                             resource_group,
                                             workspace_name):
        return 'https://ms.portal.azure.com/#@{0}/resource/subscriptions/{1}/resourceGroups/{2}/providers/Microsoft.OperationalInsights/workspaces/{3}/logs'.format(tenant_domain, subscription_id, resource_group, workspace_name)

    def display_html(inner_html):
        display(HTML(inner_html))

    def pick_start_and_end_date():
        start_date = widgets.DatePicker(description='Pick a start date', disabled=False)
        end_date = widgets.DatePicker(description='Pick a end date', disabled=False)
        display(start_date)
        display(end_date)
        return start_date, end_date

    def select_multiple_items(label, item_name):
        label_item = widgets.Label(value=label)
        items = widgets.Textarea(value='', placeholder='One per line: \n 0x7ae3 \n 0x7ae6', description=item_name, disabled=False, rows=5)
        display(label_item)
        display(items)
        return items
