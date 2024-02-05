'''
Do not import customized_logger or it would have circular import error
'''
import os

from shared_code.models.oat import RiskLevel

VERSION = '1.1.0'
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
        from azure.identity import DefaultAzureCredential
        from azure.keyvault.secrets import SecretClient

        clp_ids = set(filter(None, os.getenv('clpIds').split(',')))
        credential = DefaultAzureCredential(
            managed_identity_client_id=os.getenv('keyVaultIdentityClientId')
        )
        client = SecretClient(vault_url=os.getenv('keyVaultUrl'), credential=credential)

        tokens = []
        for clp_id in clp_ids:
            try:
                token = client.get_secret(get_secret_name(clp_id)).value
                tokens.append(token)
            except Exception as e:
                print(e)

        return tokens
    else:
        return set(filter(None, os.environ.get('apiTokens', '').split(',')))


def get_xdr_host_url():
    xdr_host_url = os.environ.get('xdrHostUrl')
    return xdr_host_url or XDR_HOSTS[os.environ['regionCode']]


def get_storage_connection_string():
    return os.environ['AzureWebJobsStorage']



def get_workbench_api_timeout_seconds():
    return int(os.environ.get('workbenchApiTimeoutSeconds', 70))


def get_max_workbench_query_minutes():
    return int(os.environ.get('maxWorkbenchQueryMinutes', 60))


def get_default_workbench_query_minutes():
    return int(os.environ.get('defaultWorkbenchQueryMinutes', 5))


def get_max_oat_query_minutes():
    return int(os.environ.get('maxOatQueryMinutes', 60))


def get_default_oat_query_minutes():
    return int(os.environ.get('defaultOatQueryMinutes', 5))


def get_oat_query_time_buffer_minutes():
    return int(os.environ.get('defaultOatQueryTimeBufferMinutes', 5))


def get_max_oat_data_retention_day():
    return int(os.environ.get('maxOatDataRetention', 7))


def get_oat_rows_bulk_count():
    return int(os.environ.get('oatRowsBulkCount', 1000))


def get_datetime_format():
    return '%Y-%m-%dT%H:%M:%S.000Z'


def get_oat_pipeline_datetime_format():
    return '%Y-%m-%dT%H:%M:%SZ'


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


def get_oat_config():
    return {
        'riskLevels': [
            RiskLevel.LOW,
            RiskLevel.MEDIUM,
            RiskLevel.HIGH,
            RiskLevel.CRITICAL,
        ],
        'hasDetail': True,
        'description': get_user_agent(),
    }


def get_oat_pipeline_task_queue_name():
    return 'oat-pipeline-task-queue'


def get_wb_list_queue_name():
    return 'workbench-list-queue'


def get_wb_detail_queue_name():
    return 'workbench-queue'


def get_execution_time():
    return {'primary': [5, 15, 25, 35, 45, 55], 'secondary': [0, 10, 20, 30, 40, 50]}


def get_max_proactive_retry_minutes():
    return int(os.environ.get('maxProactiveRetryMinutes', 60))


def get_proactive_retry_time_interval_minutes():
    return int(os.environ.get('proactiveRetryTimeIntervalMinutes', 8))


def get_retry_time_interval_minutes():
    return int(os.environ.get('retryTimeIntervalMinutes', 30))
