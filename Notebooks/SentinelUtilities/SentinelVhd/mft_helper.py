"""
MFT Helper:
This module is consisted of 3 classes:
    MFT Helper which knows MFT, 
    MFT controller which takes user actions and renders corresponding widgets, and 
    MFT Model Helper which knows the MFT data object.

It has dependency on .NET libraries:
System
System.Collections
System.Runtime
Microsoft.Azure.Storage.Common
Microsoft.Azure.Storage.Blob
Microsoft.Azure.KeyVault.Core
Newtonsoft.Json
Microsoft.Azure.CIS.DiskLib
Microsoft.Azure.CIS.DiskLib.Ntfs
Microsoft.Azure.CIS.DiskLib.Vhd
Microsoft.Azure.CIS.DiskLib.Vhd.Accessors
PyHelper
"""

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
import pandas as pd
import ipywidgets as widgets
from ipywidgets import Button, GridBox, Layout, ButtonStyle
import System
from System import *
from System.Collections.Generic import *
from Newtonsoft.Json import *
from Microsoft.Azure.CIS.DiskLib import *
from Microsoft.Azure.CIS.DiskLib.Ntfs import *
from Microsoft.Azure.CIS.DiskLib.Vhd import *
from Microsoft.Azure.CIS.DiskLib.Vhd.Accessors import *
from MftExportUtilityLib import *
from .mft_view_helper import *
from .file_helper import *

class MFTHelper(object):
    p1 = 'Partition1'
    p2 = 'Partition2'
    p3 = 'Partition3'
    p4 = 'Partition4'
    root_segment_low = "0x5"
    
    def __init__(self, segment_start, sas_url, partition = None):
        self.uri = Uri(sas_url)
        self.sas_url = sas_url
        r = Reader(PageBlobReader.Create(self.uri))
        self.mbr = r.GetMasterBootRecord()
        self.root = None
        if segment_start is None: segment_start = self.root_segment_low
        self.segment = segment_start
        self.root_segment_low = self.root_segment_low
        self.selected_partition = partition
        
        if partition is not None:
            if partition == self.p1:
                part = self.mbr.Partition1
            elif partition == self.p2:
                part = self.mbr.Partition2
            elif partition == self.p3:
                part = self.mbr.Partition3
            elif partition == self.p4:
                part = self.mbr.Partition4            
            self.scan_partition(part)

    def get_partitions(self):
        return [{self.p1 : hex(self.mbr.Partition1.PartitionType)},
                {self.p2 : hex(self.mbr.Partition2.PartitionType)},
                {self.p3 : hex(self.mbr.Partition3.PartitionType)},
                {self.p4 : hex(self.mbr.Partition4.PartitionType)}]
     
    def scan_partition(self, partition):
        ntfs_accessor = PageBlobReader.Create(self.uri, partition.LBAFirstSector *512)
        self.ntfs = NtfsData(ntfs_accessor)
        
        i = 0
        for mft_entry in self.ntfs.Mft:
            if i < int(self.segment,16): 
                i += 1
                continue
            self.root = mft_entry
            break


class MFTController(object):
    def __init__(self, mft_helper, reset_path = True):
        self.root_segment_low = mft_helper.root_segment_low
        self.root = mft_helper.root
        self.selected_partition = mft_helper.selected_partition
        self.sas_url = mft_helper.sas_url
        if reset_path == True:
            self.path = [MFTViewHelper.content_type_breadcrumb, 'ROOT [{}]'.format(mft_helper.segment)]  
        
    def display(self):
        self.progress_bar = MFTViewHelper.define_int_progress_bar()
        self.nav_breadcrumbs = widgets.HBox()
        self.button_folders = widgets.VBox()
        self.button_files = widgets.VBox()
        self.table_files = widgets.VBox()
        self.box_folders = widgets.HBox()
        self.box_files = widgets.HBox()
        self.box_top = widgets.VBox()
        
        self.tab_details = widgets.Tab()
        
        self.update(None)
        return self.box_top
    
    def on_folder_click(self, button):
        self.button_description = button.description
        name, seg_num_low = self.parse_button_description(self.button_description)
        
        # Initialize the helper again
        self.progress_bar = MFTViewHelper.define_int_progress_bar()
        mft_helper = MFTHelper(seg_num_low, self.sas_url, self.selected_partition)
        self.__init__(mft_helper, False)
        
        # Build navigator path and update
        self.build_breadcrumb_path(self.button_description)
        self.update(seg_num_low)
        return self.box_top
    
    def on_file_click(self, button):
        self.button_description = button.description
        name, seg_num_low = self.parse_button_description(self.button_description)
        
        # Initialize the helper again
        self.progress_bar = MFTViewHelper.define_int_progress_bar()
        mft_helper = MFTHelper(seg_num_low, self.sas_url, self.selected_partition)
        self.__init__(mft_helper, False)
        
        self.update(seg_num_low, True)
        return self.box_top
    
    def update(self, seg_num_low, update_details_only = False): 
        display(self.progress_bar)
        self.progress_bar.value += 1
        if update_details_only == False:
            self.construct_breadcrumb(self.nav_breadcrumbs)
            self.progress_bar.value += 1
            self.process_button_data(self.button_folders, MFTViewHelper.content_type_folders)
            self.progress_bar.value += 2
            self.process_button_data(self.button_files, MFTViewHelper.content_type_files)
            self.progress_bar.value += 3
            self.process_tabular_data(self.table_files, MFTViewHelper.content_type_files)
            self.progress_bar.value += 1
        
        if seg_num_low is not None:
            self.process_tab_attrs(self.tab_details, seg_num_low)
            self.progress_bar.value += 1
        
        self.box_folders.children = [self.button_folders, self.tab_details]
        self.box_files.children = [self.button_files, self.table_files]
        self.box_top.children = [self.nav_breadcrumbs, self.box_folders, self.box_files]
        self.progress_bar.close()
        
    def construct_breadcrumb(self, box):
        buttons = []
        icon_type = 'play'
        buttons.append(MFTViewHelper.create_first_button(MFTViewHelper.content_type_breadcrumb, icon_type))
        
        for node in self.path[1:]:
            name, seg_num_low = self.parse_button_description(node)
            button = MFTViewHelper.create_button(MFTViewHelper.button_type_navigator, icon_type, name, seg_num_low)
            button.on_click(self.on_folder_click) 
            buttons.append(button)
        # End of for loop
            
        box.children = tuple(buttons)
        box.layout = MFTViewHelper.define_box_layout()
        
    def process_button_data(self, box, content_type):
        buttons = []
        icon_type = content_type.lower()[:-1]
        buttons.append(MFTViewHelper.create_first_button(content_type, icon_type))
        
        for node in self.root.Children:
            if content_type == MFTViewHelper.content_type_files:
                if node.IsDirectory: continue
            else:
                if not node.IsDirectory: continue
            if node.FileNameData.Flags == 2: continue

            button = MFTViewHelper.create_button(MFTViewHelper.button_type_content, icon_type, node.Name, hex(node.IndexEntry.FileReference.SegmentNumberLowPart))
            if content_type == MFTViewHelper.content_type_files: 
                button.on_click(self.on_file_click)
            else:
                button.on_click(self.on_folder_click)
                
            buttons.append(button)
        # End of for loop
        
        box.children = tuple(buttons)
        box.layout = MFTViewHelper.define_box_layout()

    def process_tabular_data(self, box, content_type):
        column_list, data_table = MFTModelHelper.get_summary_table_data(content_type, self.root.Children)
        
        df = pd.DataFrame(data_table, columns=column_list)
        box.children = tuple([widgets.HTML(MFTViewHelper.get_summary_table_style() + df.to_html(classes="df", escape=True))])
        box.layout = MFTViewHelper.define_box_layout()
        
    def parse_button_description(self, button_description):
        name = button_description.strip().split('[')[0].strip()
        seg_num_low = button_description.strip().split('[')[1][:-1].strip()

        return name, seg_num_low
    
    def build_breadcrumb_path(self, new_node):
        if new_node in self.path:
            index = self.path.index(new_node)
            self.path = self.path[:index + 1]
        else:
            self.path.append(new_node)

    def process_tab_attrs(self, tab_container, seg_num_low):
        tab_list = []
        outputs = []

        try:
            for mft_attr in self.root.Attributes:
                tab_list.append(str(mft_attr.TypeCode).replace('$', ''))
                output = widgets.Output() 
                selected_attr_list = MFTModelHelper.map_mftattr_to_attr_list(str(mft_attr.TypeCode).replace('$', ''))
                with output:
                    for select_attr in selected_attr_list:
                        val = getattr(mft_attr, select_attr)
                        print(select_attr + ': ' + str(FileHelper.convert_decimal_to_hexadecimal(select_attr, val)))
                # end of select attr_list loop

                outputs.append(output)
            # end of Attributes loop
        except:
            print(sys.exc_info()[1])
        
        tab_container.children = outputs
        for i in range(len(tab_list)): tab_container.set_title(i, tab_list[i])
        tab_container.layout = MFTViewHelper.define_box_layout()
        tab_container.selected_index = 0
        
class MFTModelHelper(object):
    def get_summary_table_data(content_type, mft_entries):
        data_table = []
        count = 0
        column_list = ["Offset", "Seg. Num.", "Size", "Created", "Accessed", "Modified", "Changed"]
        
        for node in mft_entries:
            count += 1
            if count > 10000: break
            if content_type == 'FILES':
                if node.IsDirectory: continue
            else:
                if not node.IsDirectory: continue
            if node.FileNameData.Flags == 2: continue

            data_table.append([node.DiskPhysicalOffset,
                              hex(node.IndexEntry.FileReference.SegmentNumberLowPart), 
                              node.FileNameData.FileSize, 
                              FileHelper.convert_windows_file_time(node.FileNameData.CreationTime),
                              FileHelper.convert_windows_file_time(node.FileNameData.LastAccessTime),
                              FileHelper.convert_windows_file_time(node.FileNameData.LastModificationTime),
                              FileHelper.convert_windows_file_time(node.FileNameData.LastChangeTime)])
            
        return column_list, data_table

    def map_mftattr_to_attr_list(type_code):
        # attrs for folder and files
        if str(type_code) == "StdInfo(0x10)":
            return ['CreationTime', 'LastModificationTime', 'LastChangeTime', 'LastAccessTime', 'FileAttributes', 'OwnerId', 'SecurityId', 'USN', 'HeaderClusterOffset', 'TypeCode', 'Name', 
                     'IsResident']
        # attrs for folder and files
        elif str(type_code) == 'FileName(0x30)':
            return ['FileReference', 'FileSize', 'CreationTime', 'LastModificationTime', 'LastChangeTime', 'LastAccessTime', 'FileAttributes', 'ReparsePointTag', 'FileNameLength',
                     'FileName', 'Flags', 'IsDirectory', 'IsViewIndex', 'HeaderClusterOffset', 'TypeCode', 'Name', 'IsResident']
        # attrs for folder
        elif str(type_code) == 'ObjectId(0x40)':
            return ['ObjectId', 'HeaderClusterOffset', 'TypeCode', 'Name', 'IsResident']
        # attrs for folder
        elif str(type_code) == 'IndexRoot(0x90)':
            return ['BlocksPerIndexBuffer', 'BytesPerIndexBuffer', 'CollationRule', 'IndexedAttributeType', 'HeaderClusterOffset', 'TypeCode', 'Name', 'IsResident']
        # attrs for folder
        elif str(type_code) == 'IndexRoot(0x90)':
            return ['BlocksPerIndexBuffer', 'BytesPerIndexBuffer', 'CollationRule', 'IndexedAttributeType', 'HeaderClusterOffset', 'TypeCode', 'Name', 'IsResident']
        # attrs for folder
        elif str(type_code) == 'IndexAlloc(0xa0)':
            return ['HeaderClusterOffset', 'TypeCode', 'Name', 'IsResident']
        # attrs for folder
        elif str(type_code) == 'Bitmap(0xb0)':
            return ['HeaderClusterOffset', 'TypeCode', 'Name', 'IsResident']
        # attrs for folder and files
        elif str(type_code) == 'LoggedUtilityStream(0x100)':
            return ['HeaderClusterOffset', 'TypeCode', 'Name', 'IsResident']
        # attrs for files
        elif str(type_code) == 'AttrList(0x20)':
            return ['HeaderClusterOffset', 'TypeCode', 'Name', 'IsResident']
        # attrs for files
        elif str(type_code) == 'Data(0x80)':
            return ['DataStream', 'LowestVcn', 'HighestVcn', 'Flags', 'DataSize', 'HeaderClusterOffset', 'TypeCode', 'Name', 'IsResident']
        # attrs for files
        elif str(type_code) == 'EAInfo(0xd0)':
            return ['PackedEASize', 'NeedEACount', 'UnpackedEASize', 'HeaderClusterOffset', 'TypeCode', 'Name', 'IsResident']
        # attrs for files
        elif str(type_code) == 'EA(0xe0)':
            return ['DataStream', 'RunList', 'HeaderClusterOffset', 'TypeCode', 'Name', 'IsResident']
        
