# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
"""
Config Reader:
This module is used to read JSON config file populated by Azure Notebooks API.
"""

import json

# pylint: disable-msg=R0903
class ConfigReader:
    """ class to read configuration """

    # pylint: disable-msg=E0213
    def read_config_values(file_path):
        """ read configuration """
        with open(file_path) as json_file:
            if json_file:
                json_config = json.load(json_file)
                return (json_config["tenant_id"],
                        json_config["subscription_id"],
                        json_config["resource_group"],
                        json_config["workspace_id"],
                        json_config["workspace_name"])
        return None
