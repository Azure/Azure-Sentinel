import pandas as pd
from IPython.display import display, HTML
import ipywidgets as widgets
from ipywidgets import Button, GridBox, Layout, ButtonStyle, IntProgress
from .regi_view_helper import *

class RegiController(object):
    def __init__(self, regi_helper):
        self.root = regi_helper.root
        self.regi_helper = regi_helper
        self.path = [RegiViewHelper.define_icon(RegiViewHelper.content_type_breadcrumb), '']
        
    def display(self):
        self.progress_bar = RegiViewHelper.define_int_progress_bar()
        self.nav_breadcrumbs = widgets.HBox()
        self.button_keys = widgets.VBox()
        self.value_details = widgets.VBox()
        self.box_data = widgets.HBox()
        self.box_top = widgets.VBox()
        
        self.update()
        return self.box_top
    
    def on_key_click(self, button):                       
        # reset the current key
        self.progress_bar = RegiViewHelper.define_int_progress_bar()
        self.regi_helper.set_current_key(button.description)
        
        # Build navigator path and update
        self.build_breadcrumb_path(button.description)
        
        self.update()
        return self.box_top
    
    def update(self): 
        display(self.progress_bar)
        self.progress_bar.value += 1
        self.construct_breadcrumb(self.nav_breadcrumbs)
        self.progress_bar.value += 2
        self.process_button_data(self.button_keys, RegiViewHelper.content_type_keys) 
        self.progress_bar.value += 3
        self.process_tabular_data(self.value_details)
        self.progress_bar.value += 3
        
        self.box_data.children = [self.button_keys, self.value_details]
        self.box_top.children = [self.nav_breadcrumbs, self.box_data]
        self.progress_bar.close()
        
    def process_button_data(self, box, content_type):
        buttons = []
        buttons.append(RegiViewHelper.create_first_button(content_type, RegiViewHelper.define_icon(content_type)))

        for key_name, key_path in self.regi_helper.get_current_subkey_name_path_tuples():
            button = RegiViewHelper.create_button(RegiViewHelper.button_type_content, RegiViewHelper.define_icon(content_type), key_path)
            if content_type == RegiViewHelper.content_type_values: 
                button.on_click(self.on_value_click)
            else:
                button.on_click(self.on_key_click)
                
            buttons.append(button)
        # End of for loop
        
        box.children = tuple(buttons)
        box.layout = RegiViewHelper.define_box_layout()
    
    def process_tabular_data(self, box):
        data_table = []
        try:
            if self.regi_helper.current_key.values_number() != 0:  
                for value in self.regi_helper.get_value_list():
                    data_table.append([value.name(), value.value_type_str(), value.value()])
                # end of Value loop
        except:
            print(sys.exc_info()[1])
        
        pd.set_option('display.max_colwidth', -1)
        df = pd.DataFrame(data_table, columns=RegiViewHelper.define_value_table_columns())
        box.children = tuple([widgets.HTML(RegiViewHelper.get_summary_table_style() + df.to_html(classes="df", escape=True))])
        box.layout = RegiViewHelper.define_box_layout()
        
    def build_breadcrumb_path(self, new_key):
        if new_key in self.path:
            index = self.path.index(new_key)
            self.path = self.path[:index + 1]
        else:
            self.path.append(new_key)

    def construct_breadcrumb(self, box):
        buttons = []
        icon_type = RegiViewHelper.define_icon(RegiViewHelper.content_type_breadcrumb)
        buttons.append(RegiViewHelper.create_first_button(RegiViewHelper.content_type_breadcrumb, icon_type))
        
        for key_path in self.path[1:]:
            button = RegiViewHelper.create_button(RegiViewHelper.button_type_navigator, icon_type, key_path)
            button.on_click(self.on_key_click) 
            buttons.append(button)
        # End of for loop
            
        box.children = tuple(buttons)
        box.layout = RegiViewHelper.define_box_layout()