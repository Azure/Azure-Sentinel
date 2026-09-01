// =============================================================================
// Greenfield deployment: Log Analytics workspace + Microsoft Sentinel
// -----------------------------------------------------------------------------
// Deploys a new Log Analytics workspace and onboards Microsoft Sentinel onto it.
// Target scope: resource group.
//
// Resources (per Microsoft Learn):
//   - Microsoft.OperationalInsights/workspaces  @ 2025-07-01
//   - Microsoft.SecurityInsights/onboardingStates @ 2025-09-01  (extension
//     resource scoped to the workspace; must be named 'default')
//
// Sentinel requires a Log Analytics workspace; onboarding is done by placing an
// onboardingStates resource at the workspace scope. Microsoft recommends a 90-day
// retention to use all Sentinel functionality.
// =============================================================================

targetScope = 'resourceGroup'

@description('Name of the Log Analytics workspace. 4-63 chars; letters, numbers and hyphens; must start and end alphanumeric.')
@minLength(4)
@maxLength(63)
//@pattern('^[A-Za-z0-9][A-Za-z0-9-]*[A-Za-z0-9]$')
param workspaceName string

@description('Azure region for the workspace. Defaults to the resource group location.')
param location string = resourceGroup().location

@description('Workspace pricing SKU.')
@allowed([
  'PerGB2018'
  'CapacityReservation'
  'Free'
  'PerNode'
  'Premium'
  'Standalone'
  'Standard'
  'LACluster'
])
param skuName string = 'PerGB2018'

@description('Data retention in days. Microsoft recommends at least 90 for full Sentinel functionality. -1 = unlimited (Unlimited SKU only); max 730.')
@minValue(-1)
@maxValue(730)
param retentionInDays int = 90

@description('Sentinel onboarding CMK status flag. Set to true only if the underlying workspace is already backed by a customer-managed key (configured via a dedicated Log Analytics cluster + Key Vault). This does NOT configure workspace encryption itself.')
param sentinelCustomerManagedKey bool = false

@description('Tags to apply to the workspace.')
param tags object = {}

// -----------------------------------------------------------------------------
// Log Analytics workspace
// -----------------------------------------------------------------------------
resource workspace 'Microsoft.OperationalInsights/workspaces@2025-07-01' = {
  name: workspaceName
  location: location
  tags: tags
  properties: {
    sku: {
      name: skuName
    }
    retentionInDays: retentionInDays
  }
}

// -----------------------------------------------------------------------------
// Microsoft Sentinel onboarding (extension resource on the workspace)
// The onboardingStates resource must be named 'default'.
// -----------------------------------------------------------------------------
resource sentinelOnboarding 'Microsoft.SecurityInsights/onboardingStates@2025-09-01' = {
  scope: workspace
  name: 'default'
 properties: {
    customerManagedKey: sentinelCustomerManagedKey
  }
}

// -----------------------------------------------------------------------------
// Outputs
// -----------------------------------------------------------------------------
output workspaceId string = workspace.id
output workspaceName string = workspace.name
output workspaceCustomerId string = workspace.properties.customerId
output sentinelOnboardingId string = sentinelOnboarding.id
