#-------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
#--------------------------------------------------------------------------

def get_cli_active_cloud():
    """Return a CLI active cloud.

    .. versionadded:: 1.1.6

    :return: A CLI Cloud
    :rtype: azure.cli.core.cloud.Cloud
    :raises: ImportError if azure-cli-core package is not available
    """

    try:
        from azure.cli.core.cloud import get_active_cloud
    except ImportError:
        raise ImportError("You need to install 'azure-cli-core' to load CLI active Cloud")
    return get_active_cloud()

