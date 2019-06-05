import clr
clr.AddReference("System")
clr.AddReference("System.Collections")
clr.AddReference("System.Runtime")
clr.AddReference("Microsoft.Azure.Storage.Common")
clr.AddReference("Microsoft.Azure.Storage.Blob")
clr.AddReference("Microsoft.Azure.KeyVault.Core")
clr.AddReference("Newtonsoft.Json")
clr.AddReference("Microsoft.Azure.CIS.DiskLib")
clr.AddReference("Microsoft.Azure.CIS.DiskLib.Ntfs")
clr.AddReference("Microsoft.Azure.CIS.DiskLib.Vhd")
clr.AddReference("Microsoft.Azure.CIS.DiskLib.Vhd.Accessors")
clr.AddReference("PyHelper")

import sys
import clr
import os
import json
from datetime import datetime,timedelta
import ipywidgets as widgets
import System
from System import *
from System.Collections.Generic import *
from Newtonsoft.Json import *
from Microsoft.Azure.CIS.DiskLib import *
from Microsoft.Azure.CIS.DiskLib.Ntfs import *
from Microsoft.Azure.CIS.DiskLib.Vhd import *
from Microsoft.Azure.CIS.DiskLib.Vhd.Accessors import *
from MftExportUtilityLib import *

class FileHelper(object):
    def download_file(file_segment, ntfs):
        return MftExportUtil.DownloadFile(ntfs, int(file_segment, 16))[0]

    def download_file_internal(file_segment, ntfs):
        return MftExportUtil.DownloadFile(ntfs, int(file_segment, 16))[0]

    def download_files(file_segment_list, ntfs):
        progress_bar = FileHelper.define_int_progress_bar(len(file_segment_list))
        display(progress_bar)
        file_path_list = []
        for file in file_segment_list:
            file_path = FileHelper.download_file(file, ntfs)
            file_path_list.append(file_path)
            progress_bar.value += 1
        progress_bar.close()
        return file_path_list
    
    def display_file(file_path):
        with open(file_path, 'r', encoding="utf8", errors='ignore') as f:
            contents = f.read()
            print(contents)

    def convert_windows_file_time(win_time):
        if win_time == 0 : return ''
        
        dt = win_time / 10
        return datetime(1601, 1, 1) + timedelta(microseconds=dt)
    
    def convert_decimal_to_hexadecimal(attr_name, val):
        if isinstance(val, (int, float)) == False or isinstance(val, (bool)) == True or 'time' in attr_name: 
            return val
        else:
            return "0x{:02x}".format(val)

    def define_int_progress_bar(max_step):
        return widgets.IntProgress(value=0, min=0, max=max_step, step=1, description='Downloading:', bar_style='success', orientation='horizontal', position='top')