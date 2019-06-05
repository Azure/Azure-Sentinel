import os
import ipywidgets as widgets
from ipywidgets import Button, GridBox, Layout, ButtonStyle, IntProgress

class AnomalyLookupViewHelper(object): 
    def define_int_progress_bar():
        return widgets.IntProgress(value=0, min=0, max=10, step=1, description='Loading:', bar_style='success', orientation='horizontal', position='top')

    def define_button_style():
        return ButtonStyle(button_color='#FFF', font_color='blue')

    def define_button_layout():
        return Layout(width='auto', height='27px', border='2px solid black')
