import os


VERSION = '1.0.1'
SIEM_NAME = 'SentinelAddon'
XDR_HOSTS = {
    'us': 'https://api.xdr.trendmicro.com',
    'eu': 'https://api.eu.xdr.trendmicro.com',
    'in': 'https://api.in.xdr.trendmicro.com',
    'jp': 'https://api.xdr.trendmicro.co.jp',
    'sg': 'https://api.sg.xdr.trendmicro.com',
    'au': 'https://api.au.xdr.trendmicro.com',
    'uae': 'https://api.uae.xdr.trendmicro.com/',
}


def get_workspace_id():
    return os.environ['workspaceId']


def get_workspace_key():
    return os.environ['workspaceKey']


def get_api_tokens():
    is_key_vault_enabled = (
        os.getenv('keyVaultUrl')
        and os.getenv('keyVaultIdentityClientId')
        and os.getenv('clpIds')
    )
    if is_key_vault_enabled:
        # get tokens from key vault
        from azure.keyvault.secrets import SecretClient
        from azure.identity import DefaultAzureCredential

        clp_ids = list(filter(None, os.getenv('clpIds').split(',')))
        credential = DefaultAzureCredential(
            managed_identity_client_id=os.getenv('keyVaultIdentityClientId')
        )
        client = SecretClient(vault_url=os.getenv('keyVaultUrl'), credential=credential)

        return [client.get_secret(get_secret_name(clp_id)).value for clp_id in clp_ids]
    else:
        return list(filter(None, os.environ.get('apiTokens', '').split(',')))


def get_xdr_host_url():
    xdr_host_url = os.environ.get('xdrHostUrl')
    return xdr_host_url or XDR_HOSTS[os.environ['regionCode']]


def get_storage_connection_string():
    return os.environ['AzureWebJobsStorage']


def get_max_workbench_query_minutes():
    return int(os.environ.get('maxWorkbenchQueryMinutes', 60))


def get_default_workbench_query_minutes():
    return int(os.environ.get('defaultWorkbenchQueryMinutes', 5))


def get_max_oat_query_minutes():
    return int(os.environ.get('maxOatQueryMinutes', 30))


def get_default_oat_query_minutes():
    return int(os.environ.get('defaultOatQueryMinutes', 5))


def get_oat_query_time_buffer_minutes():
    return int(os.environ.get('defaultOatQueryTimeBufferMinutes', 15))


def get_datetime_format():
    return '%Y-%m-%dT%H:%M:%S.000Z'


def get_wb_log_type():
    return 'TrendMicro_XDR_WORKBENCH'


def get_health_check_log_type():
    return 'TrendMicro_XDR_Health_Check'


def get_oat_health_check_log_type():
    return 'TrendMicro_XDR_OAT_Health_Check'


def get_rca_log_type():
    return 'TrendMicro_XDR_RCA_Result'


def get_rca_task_log_type():
    return 'TrendMicro_XDR_RCA_Task'


def get_oat_log_type():
    return 'TrendMicro_XDR_OAT'


def get_user_agent():
    return f'TMXDR{SIEM_NAME}/{VERSION}'


def get_secret_name(clp_id):
    return f'tmv1-entity-{clp_id}'
