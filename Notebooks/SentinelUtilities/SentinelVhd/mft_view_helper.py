"""
MFT View Helper:
This module provides helper methods for UI components.
"""

import ipywidgets as widgets
from ipywidgets import Button, GridBox, Layout, ButtonStyle, IntProgress

class MFTViewHelper(object): 
    button_type_content = 'content'
    button_type_navigator = 'navigator'
    
    content_type_folders = 'FOLDERS'
    content_type_files = 'FILES'
    content_type_breadcrumb = 'FOLDERS VIEWED'
    
    def get_summary_table_style():
        return '''<style> .df th { text-align:center; font-size:large; padding-left:10px; padding-right:10px}  tbody tr:nth-child(even) { background-color: #f2f2f2; } td { padding-left: 10px; padding-right: 5px; }</style>'''
        
    def define_box_layout():
        return  Layout(display='flex', align_items='flex-start', border='solid', margin='5px')
    
    def define_button_layout(button_type):
        if button_type == MFTViewHelper.button_type_content:
            return Layout(width='auto', height='25px')
        elif button_type == MFTViewHelper.button_type_navigator:
            return Layout(width='auto', height='27px', border='2px solid black')
    
    def define_button_style(button_type):
        if button_type == MFTViewHelper.button_type_content:
            return ButtonStyle(button_color='#FFF', font_color='blue')
        elif button_type == MFTViewHelper.button_type_navigator:
            return ButtonStyle(button_color='#d0d0ff')
    
    def create_first_button(content_type, icon_type):
        if content_type == MFTViewHelper.content_type_folders:
            tooltip = 'Click to get lists of the subfolders and files under this folder'
        elif content_type == MFTViewHelper.content_type_files:
            tooltip = 'Click to get details of the file'
        elif content_type == MFTViewHelper.content_type_breadcrumb:
            tooltip = 'Click to go back to the folder' 
        
        return widgets.Button(description=content_type + ' :', \
                              disabled=True, \
                              layout=Layout(width='auto', height='27px'), \
                              icon=icon_type, \
                              style=ButtonStyle(align_content='center', font_weight='bold'), \
                              tooltip = tooltip)
    
    def create_button(button_type, icon_type, name, seg_num_low):
        button = widgets.Button(description=name.strip() + ' [' + seg_num_low + ']', \
                    layout=MFTViewHelper.define_button_layout(button_type), \
                    style=MFTViewHelper.define_button_style(button_type),
                    icon=icon_type)
        return button
    
    def define_int_progress_bar():
        return widgets.IntProgress(value=0, min=0, max=10, step=1, description='Loading:', bar_style='success', orientation='horizontal', position='top')