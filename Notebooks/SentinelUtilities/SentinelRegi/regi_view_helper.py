"""
Regi View Helper:
This module provides helper methods for UI components.
"""

import ipywidgets as widgets
from ipywidgets import Button, GridBox, Layout, ButtonStyle, IntProgress

class RegiViewHelper(object): 
    button_type_content = 'content'
    button_type_navigator = 'navigator'
    
    root_path = 'ROOT'
    
    content_type_keys = 'KEYS'
    content_type_values = 'VALUES'
    content_type_breadcrumb = 'KEYS VIEWED'
            
    def get_summary_table_style():
        return '''<style> .df th { text-align:center; font-size:large; padding-left:10px; padding-right:10px}  tbody tr:nth-child(even) { background-color: #f2f2f2; } td { padding-left: 10px; padding-right: 5px; }</style>'''

    def define_box_layout():
        return  Layout(display='flex', align_items='flex-start', border='solid', margin='5px')
    
    def define_button_layout(button_type):
        if button_type == RegiViewHelper.button_type_content:
            return Layout(width='auto', height='25px')
        elif button_type == RegiViewHelper.button_type_navigator:
            return Layout(width='auto', height='27px', border='2px solid black')
        
    def define_icon(content_type):
        if content_type == RegiViewHelper.content_type_keys:
            return 'key'
        elif content_type == RegiViewHelper.content_type_values:
            return 'list'
        elif content_type == RegiViewHelper.content_type_breadcrumb:
            return 'play'
    
    def define_button_style(button_type):
        if button_type == RegiViewHelper.button_type_content:
            return ButtonStyle(button_color='#FFF', font_color='blue')
        elif button_type == RegiViewHelper.button_type_navigator:
            return ButtonStyle(button_color='#d0d0ff')
    
    def create_first_button(content_type, icon_type):
        if content_type == RegiViewHelper.content_type_keys:
            tooltip = 'Click to get lists of the subkeys and values under this subkey'
        elif content_type == RegiViewHelper.content_type_values:
            tooltip = 'Click to get details of the value'
        elif content_type == RegiViewHelper.content_type_breadcrumb:
            tooltip = 'Click to go back to the key' 
        
        return widgets.Button(description=content_type + ' :', \
                              disabled=True, \
                              layout=Layout(width='auto', height='27px'), \
                              icon=icon_type, \
                              style=ButtonStyle(align_content='center', font_weight='bold'), \
                              tooltip = tooltip)
    
    def create_button(button_type, icon_type, path):
        return widgets.Button(description=path, \
                    layout=RegiViewHelper.define_button_layout(button_type), \
                    style=RegiViewHelper.define_button_style(button_type),
                    icon=icon_type)
    
    def define_value_table_columns():
        return ['Name', 'Type', 'Data']
    
    def define_int_progress_bar():
        return widgets.IntProgress(value=0, min=0, max=10, step=1, description='Loading:', bar_style='success', orientation='horizontal', position='top')