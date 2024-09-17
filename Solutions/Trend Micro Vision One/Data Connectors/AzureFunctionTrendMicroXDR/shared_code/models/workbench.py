ALLOWED_WORKBENCH_COLUMN = [
    'priorityScore',
    'investigationStatus',
    'workbenchName',
    'workbenchId',
    'workbenchLink',
    'createdTime',
    'updatedTime',
    'severity',
    'modelId',
]

ALLOWED_WORKBENCH_DETAIL_COLUMN = [
    'alertProvider',
    'model',
    'description',
    'impactScope',
    'indicators',
    'matchedRules',
    'alertTriggerTimestamp',
    'workbenchCompleteTimestamp',
]

XDR_INDICATORS_COLUMN_NAME = {
    'ip': 'IPAddress',
    'detection_name': 'MalwareName',
    'filename': 'FileName',
    'fullpath': 'FileDirectory',
    'command_line': 'ProcessCommandLine',
    'domain': 'DomainName',
    'file_sha1': 'FileHashValue',
    'registry_key': 'RegistryKey',
    'registry_value_data': 'RegistryValue',
    'registry_value': 'RegistryValueName',
    'url': 'URL',
    'emailAddress': 'MailboxPrimaryAddress',
}

WB_OVERSIZED_FIELDS = [["indicators"], ["impactScope"]]
