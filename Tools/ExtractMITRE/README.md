# ExtractMITRE
## Extract MITRE ATT&amp;CK information

This command will generate a CSV file containing the information about all the Azure Sentinel MITRE tactics and techniques being used.

Make sure you are logged into Azure and are in the correct subscription before running:

`Connect-AZAccount`

`Select-AzSubscription -SubscriptionId <Subscription GUID>`

## Examples

### Create a file named "mitrerules.csv" containing all the active rule's MITRE information
`Export-AzSentineMITREtoCSV -WorkspaceName "workspacename" -ResourceGroupName "rgname"`

### Create a file named "test.csv" that will contain all the active rule's MITRE information
`Export-AzSentineMITREtoCSV -WorkspaceName "workspacename" -ResourceGroupName "rgname" -fileName "test"`

### Create a file named "mitrerules.csv" containing all the rule's MITRE information, including those rules that are disabled
`Export-AzSentineMITREtoCSV -WorkspaceName "workspacename" -ResourceGroupName "rgname" -IncludeDisabled $true`

### Create a file named "simulated.csv" containing those rule templates that will cover techniques which have no rules covering them
`Export-AzSentineMITREtoCSV -WorkspaceName "workspacename" -ResourceGroupName "rgname" -fileName "simulated" -ShowZeroSimulatedRuleTemplates $true`

### Create a file named "simulated.csv" containing those rule templates that will cover techniques and have not been used yet.
`Export-AzSentineMITREtoCSV -WorkspaceName "workspacename" -ResourceGroupName "rgname" -fileName "simulated" -ShowAllSimulatedRuleTemplates $true`

