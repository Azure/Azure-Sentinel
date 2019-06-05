import clr
clr.AddReference('Microsoft.Azure.CIS.Notebooks.LogHelper')
clr.AddReference('Microsoft.ApplicationInsights')
            
import os
import ipywidgets as widgets
from ipywidgets import Button, GridBox, Layout, ButtonStyle, IntProgress
from IPython.display import HTML
from Microsoft.Azure.CIS.Notebooks.LogHelper import *

class LogHelper(object): 
    def __init__(self, reset, env_dir, env_dict, notebook_name):
        self.logger = AILogger();
        self.user = ''
        self.pwd = ''
        self.tenant_domain = ''
        self.notebook_name = ''
        self.get_env(reset, env_dir, env_dict, notebook_name)

    def get_env(self, reset, env_dir, env_dict, notebook_name):
        self.notebook_name = notebook_name
        self.user = env_dir['USER']
        self.pwd = env_dir['PWD']
        if reset != True and 'tenant_domain' in env_dir:
            self.tenant_domain = env_dir['tenant_domain']
        elif 'tenant_domain' in env_dict:
            self.tenant_domain = env_dict['tenant_domain']

    def count_page_view(self):
        result = self.logger.CountNotebookExectued(self.tenant_domain, self.notebook_name, self.user, self.pwd)

    def provide_feedback(self, button):
        val = self.give_feedback.value
        if val:
            result = self.logger.ProvideFeedback(self.tenant_domain, self.notebook_name, self.user, self.pwd, val)
            if result == True: print('saved')

    def is_notebook_helpful(self, button):
        val = self.is_helpful.value
        if val:
            result = self.logger.IsNotebookHelpful(self.tenant_domain, self.notebook_name, self.user, self.pwd, val)
            if result == True: print('saved')

    def ask_is_helpful(self):
        label_helpful = widgets.Label(value='Is this notebook helpful?')
        self.is_helpful = widgets.RadioButtons( options=['Yes', 'No'], value=None, description='', disabled=False)
        save_helpful = widgets.Button(description='Save', disabled=False, style=self.define_button_style(), layout=self.define_button_layout(), icon='save')
        save_helpful.on_click(self.is_notebook_helpful)
        display(label_helpful)
        display(self.is_helpful)
        display(save_helpful)

    def ask_feedback(self):
        label_feedback = widgets.Label(value='Please let us know what do you think about this notebook (Limit to 500 characters, text only):')
        self.give_feedback = widgets.Textarea(layout =self.define_textarea_layout(), value='', placeholder='Thank you for your thoughts', description='', disabled=False, rows = 6)
        save_feedback = widgets.Button(description='Save', disabled=False, style=self.define_button_style(), layout=self.define_button_layout(), icon='save')
        save_feedback.on_click(self.provide_feedback)
        display(label_feedback)
        display(self.give_feedback)
        display(save_feedback)

    def define_button_style(self):
        return ButtonStyle(button_color='#FFF', font_color='blue')

    def define_button_layout(self):
        return Layout(width='auto', height='27px', border='2px solid black')

    def define_textarea_layout(self):
        return Layout(width='600px', border='solid')