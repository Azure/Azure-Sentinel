# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
"""
Version Management:
This module is used to validate installed Python packages
that are required by Azure Sentinel Notebooks.
"""

import sys
import pkg_resources

# pylint: disable-msg=R0903
class VersionInformation:
    """ object model for version information """
    name = ''
    current_version = ''
    required_version = ''
    requirement_met = False
    message = ''

# pylint: disable-msg=R0201
class ModuleVersionCheck:
    """ class implements version checking """

    # pylint: disable=line-too-long
    def validate_python(self, required_version):
        """ validating Python version """
        version = VersionInformation()
        version.name = 'Python'
        version.current_version = sys.version
        version.required_version = required_version
        version.requirement_met = sys.version_info >= tuple(int(x) for x in required_version.split("."))
        version.message = VersionInformation.name + required_version + ' is required' if not VersionInformation.requirement_met else ''
        return version

    # pylint: disable-msg=W0702
    def validate_installed_modules(self, module_list):
        """ validating installed modules' version """
        module_versions = []
        for mod_info in module_list:
            version = VersionInformation()
            version.name, version.required_version = mod_info.split(">=")
            try:
                pkg_resources.require(mod_info)
                version.requirement_met = True
            except:
                version.requirement_met = False
                try:
                    version.message = str(sys.exc_info()[0].report)
                except:
                    version.message = 'Unknown error'
            finally:
                if 'azure' in version.name and version.message.find("VersionConflict") >= 0:
                    version.requirement_met = True
                elif version.message == '' or version.message.find("DistributionNotFound") < 0:
                    version = self.get_version_information(version, mod_info)

            module_versions.append(version)
        return module_versions

    # pylint: disable-msg=W0613
    def get_version_information(self, version, mod_info):
        """ get version information """
        mod_list = pkg_resources.WorkingSet()
        items = list(filter(lambda x: x.project_name.startswith(version.name), mod_list))
        if not items:
            version.current_version = items[0].version
        return version

# end of the class
