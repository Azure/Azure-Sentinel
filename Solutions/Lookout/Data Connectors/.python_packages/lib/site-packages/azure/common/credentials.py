#-------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
#--------------------------------------------------------------------------

import os.path
import time
try:
    from azure.core.credentials import AccessToken as _AccessToken
except ImportError:
    _AccessToken = None


def get_cli_profile():
    """Return a CLI profile class.

    .. versionadded:: 1.1.6

    :return: A CLI Profile
    :rtype: azure.cli.core._profile.Profile
    :raises: ImportError if azure-cli-core package is not available
    """

    try:
        from azure.cli.core._profile import Profile
        from azure.cli.core._session import ACCOUNT
        from azure.cli.core._environment import get_config_dir
    except ImportError:
        raise ImportError("You need to install 'azure-cli-core' to load CLI credentials")


    azure_folder = get_config_dir()
    ACCOUNT.load(os.path.join(azure_folder, 'azureProfile.json'))
    return Profile(storage=ACCOUNT)


class _CliCredentials(object):
    """A wrapper of CLI credentials type that implements the azure-core credential protocol AND
    the msrestazure protocol.

    :param cli_profile: The CLI profile instance
    :param resource: The resource to use in "msrestazure" mode (ignored otherwise)
    """

    _DEFAULT_PREFIX = "/.default"

    def __init__(self, cli_profile, resource):
        self._profile = cli_profile
        self._resource = resource
        self._cred_dict = {}

    def _get_cred(self, resource):
        if not resource in self._cred_dict:
            credentials, _, _ = self._profile.get_login_credentials(resource=resource)
            self._cred_dict[resource] = credentials
        return self._cred_dict[resource]

    def get_token(self, *scopes, **kwargs):  # pylint:disable=unused-argument
        if _AccessToken is None:  # import failed
            raise ImportError("You need to install 'azure-core' to use CLI credentials in this context")

        if len(scopes) != 1:
            raise ValueError("Multiple scopes are not supported: {}".format(scopes))
        scope = scopes[0]
        if scope.endswith(self._DEFAULT_PREFIX):
            resource = scope[:-len(self._DEFAULT_PREFIX)]
        else:
            resource = scope

        credentials = self._get_cred(resource)
        _, token, fulltoken = credentials._token_retriever()  # pylint:disable=protected-access

        return _AccessToken(token, int(fulltoken['expiresIn'] + time.time()))

    def signed_session(self, session=None):
        credentials = self._get_cred(self._resource)
        return credentials.signed_session(session)


def get_azure_cli_credentials(resource=None, with_tenant=False):
    """Return Credentials and default SubscriptionID of current loaded profile of the CLI.

    Credentials will be the "az login" command:
    https://docs.microsoft.com/cli/azure/authenticate-azure-cli

    Default subscription ID is either the only one you have, or you can define it:
    https://docs.microsoft.com/cli/azure/manage-azure-subscriptions-azure-cli

    .. versionadded:: 1.1.6

    :param str resource: The alternative resource for credentials if not ARM (GraphRBac, etc.)
    :param bool with_tenant: If True, return a three-tuple with last as tenant ID
    :return: tuple of Credentials and SubscriptionID (and tenant ID if with_tenant)
    :rtype: tuple
    """
    profile = get_cli_profile()
    cred, subscription_id, tenant_id = profile.get_login_credentials(resource=resource)
    cred = _CliCredentials(profile, resource)
    if with_tenant:
        return cred, subscription_id, tenant_id
    else:
        return cred, subscription_id


try:
    from msrest.authentication import (
        BasicAuthentication,
        BasicTokenAuthentication,
        OAuthTokenAuthentication
    )
except ImportError:
    raise ImportError("You need to install 'msrest' to use this feature")

try:
    from msrestazure.azure_active_directory import (
        InteractiveCredentials,
        ServicePrincipalCredentials,
        UserPassCredentials
    )
except ImportError:
    raise ImportError("You need to install 'msrestazure' to use this feature")
