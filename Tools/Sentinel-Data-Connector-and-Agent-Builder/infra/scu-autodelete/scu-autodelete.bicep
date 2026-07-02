// =============================================================================
// SCU Auto-Delete automation — server-side teardown engine (Phase 5A Option 1)
// =============================================================================
// Deploys a Consumption Logic App that, given a one-shot HTTP start request,
// waits server-side until the SCU delete deadline, then deletes the dedicated
// SCU resource group (removing the capacity) and emails the developer. Because
// the wait + delete run entirely in Azure, the teardown survives the developer
// powering off / sleeping / disconnecting their workstation — unlike the local
// `nohup bash sleep` timer (Phase 5A Option 2).
//
// Cost target: < $0.50 / month for ~300 sessions. Consumption Logic App is
// billed per action (~$0.000025 each), no storage account, no idle charge while
// the run is just waiting on a Delay action. ACS Email is ~free at this volume.
//
// Notifications + RG delete both authenticate with the Logic App's
// system-assigned managed identity (no secrets at rest):
//   - ARM RG delete  -> audience https://management.azure.com   (RBAC on the RG, granted per-session)
//   - ACS email send -> audience https://communication.azure.com (Contributor on the ACS resource, granted here)
//
// Deploy with scripts/Setup-ScuAutoDelete.ps1 (one-time per subscription).
// NOTE: This template is authored for `az bicep build` correctness; it has not
// been live deploy-tested from the dev workstation — run Setup once in-tenant.
// =============================================================================

targetScope = 'resourceGroup'

@description('Azure region for the Logic App (any region; ACS is global).')
param location string = resourceGroup().location

@description('Short prefix for resource names. Lowercase alphanumerics.')
@minLength(3)
@maxLength(16)
param namePrefix string = 'scuauto'

@description('ACS data residency. Must match your geo, e.g. United States, Europe, UK, Australia.')
@allowed([
  'United States'
  'Europe'
  'UK'
  'Australia'
])
param acsDataLocation string = 'United States'

@description('Display name used on the donotreply sender username.')
param senderDisplayName string = 'Sentinel SCU Auto-Delete'

var contributorRoleId = subscriptionResourceId('Microsoft.Authorization/roleDefinitions', 'b24988ac-6180-42a0-ab88-20f7382dd24c')
var emailServiceName = '${namePrefix}-email'
var communicationName = '${namePrefix}-acs'
var workflowName = '${namePrefix}-reaper'

// -------- ACS Email: service + Azure-managed domain + sender ----------------
resource emailService 'Microsoft.Communication/emailServices@2023-04-01' = {
  name: emailServiceName
  location: 'global'
  properties: {
    dataLocation: acsDataLocation
  }
}

resource managedDomain 'Microsoft.Communication/emailServices/domains@2023-04-01' = {
  parent: emailService
  name: 'AzureManagedDomain'
  location: 'global'
  properties: {
    domainManagement: 'AzureManaged'
    userEngagementTracking: 'Disabled'
  }
}

resource senderUsername 'Microsoft.Communication/emailServices/domains/senderUsernames@2023-04-01' = {
  parent: managedDomain
  name: 'donotreply'
  properties: {
    username: 'donotreply'
    displayName: senderDisplayName
  }
}

resource communicationService 'Microsoft.Communication/communicationServices@2023-04-01' = {
  name: communicationName
  location: 'global'
  properties: {
    dataLocation: acsDataLocation
    linkedDomains: [
      managedDomain.id
    ]
  }
}

// -------- Logic App (Consumption) with system-assigned managed identity -----
// Workflow: start (HTTP) -> wait notifyAt -> warn email -> wait deleteAt ->
// safety guard (RG name ends in -scu-rg) -> delete RG (async, waits) -> confirm email.
resource workflow 'Microsoft.Logic/workflows@2019-05-01' = {
  name: workflowName
  location: location
  identity: {
    type: 'SystemAssigned'
  }
  properties: {
    state: 'Enabled'
    definition: {
      '$schema': 'https://schema.management.azure.com/providers/Microsoft.Logic/schemas/2016-06-01/workflowdefinition.json#'
      contentVersion: '1.0.0.0'
      parameters: {}
      triggers: {
        Start: {
          type: 'Request'
          kind: 'Http'
          inputs: {
            schema: {
              type: 'object'
              properties: {
                subscriptionId: { type: 'string' }
                resourceGroup: { type: 'string' }
                capacityName: { type: 'string' }
                deleteAt: { type: 'string' }
                notifyAt: { type: 'string' }
                email: { type: 'string' }
                acsEndpoint: { type: 'string' }
                senderAddress: { type: 'string' }
              }
              required: [
                'subscriptionId'
                'resourceGroup'
                'deleteAt'
                'notifyAt'
                'email'
                'acsEndpoint'
                'senderAddress'
              ]
            }
          }
        }
      }
      actions: {
        Wait_until_notify: {
          type: 'Wait'
          inputs: {
            until: {
              timestamp: '@triggerBody()?[\'notifyAt\']'
            }
          }
          runAfter: {}
        }
        Send_warning_email: {
          type: 'Http'
          inputs: {
            method: 'POST'
            uri: '@{triggerBody()?[\'acsEndpoint\']}/emails:send?api-version=2023-03-31'
            authentication: {
              type: 'ManagedServiceIdentity'
              audience: 'https://communication.azure.com'
            }
            body: {
              senderAddress: '@triggerBody()?[\'senderAddress\']'
              content: {
                subject: 'Your Security Copilot SCU will be deleted in ~10 minutes'
                plainText: 'Heads up: the Security Copilot SCU capacity \'@{triggerBody()?[\'capacityName\']}\' (resource group @{triggerBody()?[\'resourceGroup\']}) is scheduled to be deleted at @{triggerBody()?[\'deleteAt\']} UTC, about 10 minutes from now. If you are still testing, reply to your build agent with \'keep scu\' to extend, or do nothing to let it delete and stop billing.'
              }
              recipients: {
                to: [
                  {
                    address: '@triggerBody()?[\'email\']'
                  }
                ]
              }
            }
          }
          // Email is a courtesy: 202 is terminal success, never block teardown.
          operationOptions: 'DisableAsyncPattern'
          runAfter: {
            Wait_until_notify: [
              'Succeeded'
            ]
          }
        }
        Wait_until_delete: {
          type: 'Wait'
          inputs: {
            until: {
              timestamp: '@triggerBody()?[\'deleteAt\']'
            }
          }
          // Proceed even if the warning email failed/was skipped.
          runAfter: {
            Send_warning_email: [
              'Succeeded'
              'Failed'
              'Skipped'
              'TimedOut'
            ]
          }
        }
        Guard_dedicated_rg: {
          type: 'If'
          expression: {
            and: [
              {
                endsWith: [
                  '@triggerBody()?[\'resourceGroup\']'
                  '-scu-rg'
                ]
              }
            ]
          }
          actions: {
            Delete_resource_group: {
              type: 'Http'
              inputs: {
                method: 'DELETE'
                uri: 'https://management.azure.com/subscriptions/@{triggerBody()?[\'subscriptionId\']}/resourceGroups/@{triggerBody()?[\'resourceGroup\']}?api-version=2021-04-01'
                authentication: {
                  type: 'ManagedServiceIdentity'
                  audience: 'https://management.azure.com'
                }
              }
              // Keep async pattern ON: the action polls the Location header
              // until the RG delete (a long-running operation) truly finishes,
              // so the confirmation email reflects real completion.
              runAfter: {}
            }
            Send_confirmation_email: {
              type: 'Http'
              inputs: {
                method: 'POST'
                uri: '@{triggerBody()?[\'acsEndpoint\']}/emails:send?api-version=2023-03-31'
                authentication: {
                  type: 'ManagedServiceIdentity'
                  audience: 'https://communication.azure.com'
                }
                body: {
                  senderAddress: '@triggerBody()?[\'senderAddress\']'
                  content: {
                    subject: 'Your Security Copilot SCU has been deleted — billing stopped'
                    plainText: 'Done: the Security Copilot SCU capacity \'@{triggerBody()?[\'capacityName\']}\' and its dedicated resource group @{triggerBody()?[\'resourceGroup\']} have been deleted. SCU billing has stopped.'
                  }
                  recipients: {
                    to: [
                      {
                        address: '@triggerBody()?[\'email\']'
                      }
                    ]
                  }
                }
              }
              operationOptions: 'DisableAsyncPattern'
              runAfter: {
                Delete_resource_group: [
                  'Succeeded'
                ]
              }
            }
          }
          else: {
            actions: {
              Send_refused_email: {
                type: 'Http'
                inputs: {
                  method: 'POST'
                  uri: '@{triggerBody()?[\'acsEndpoint\']}/emails:send?api-version=2023-03-31'
                  authentication: {
                    type: 'ManagedServiceIdentity'
                    audience: 'https://communication.azure.com'
                  }
                  body: {
                    senderAddress: '@triggerBody()?[\'senderAddress\']'
                    content: {
                      subject: 'SCU auto-delete REFUSED — resource group name is not a dedicated SCU RG'
                      plainText: 'Safety guard tripped: resource group @{triggerBody()?[\'resourceGroup\']} does not end in \'-scu-rg\', so the auto-delete automation refused to delete it. No action was taken. Delete the SCU manually if needed.'
                    }
                    recipients: {
                      to: [
                        {
                          address: '@triggerBody()?[\'email\']'
                        }
                      ]
                    }
                  }
                }
                operationOptions: 'DisableAsyncPattern'
                runAfter: {}
              }
            }
          }
          runAfter: {
            Wait_until_delete: [
              'Succeeded'
            ]
          }
        }
      }
      outputs: {}
    }
  }
}

// -------- Let the Logic App MI send mail through the ACS resource ------------
resource acsRoleAssignment 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
  name: guid(communicationService.id, workflow.id, 'acs-contributor')
  scope: communicationService
  properties: {
    principalId: workflow.identity.principalId
    principalType: 'ServicePrincipal'
    roleDefinitionId: contributorRoleId
  }
}

// -------- Outputs (consumed by Setup-ScuAutoDelete.ps1) ---------------------
output workflowId string = workflow.id
output workflowName string = workflow.name
output miPrincipalId string = workflow.identity.principalId
output acsEndpoint string = 'https://${communicationService.name}.communication.azure.com'
output senderAddress string = 'donotreply@${managedDomain.properties.fromSenderDomain}'
output region string = location
