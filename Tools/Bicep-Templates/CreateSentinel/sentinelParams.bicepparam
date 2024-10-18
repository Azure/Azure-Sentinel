using './Sentinel.bicep'

param workspaceName = 'demo7'
param retentionInDays = 90
param contentSolutions = [
  'Amazon Web Services'
  'Microsoft Entra ID'
  'Azure Logic Apps'
]
