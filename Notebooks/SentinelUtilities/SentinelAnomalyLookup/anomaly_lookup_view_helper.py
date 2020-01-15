# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
"""
Anomaly Lookup View Helper:
This module provides helper methods for UI components.
"""

from ipywidgets import Layout, ButtonStyle, IntProgress

class AnomalyLookupViewHelper():
    """ UI Helper class for Anomaly lookup """

    @staticmethod
    def define_int_progress_bar():
        """ define progress bar """
        # pylint: disable=line-too-long
        return IntProgress(value=0, min=0, max=10, step=1, description='Loading:', bar_style='success', orientation='horizontal', position='top')

    @staticmethod
    def define_button_style():
        """ define button style """
        return ButtonStyle(button_color='#FFF', font_color='blue')

    @staticmethod
    def define_button_layout():
        """ define button layout """
        return Layout(width='auto', height='27px', border='2px solid black')
