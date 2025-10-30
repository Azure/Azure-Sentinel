

# Audit Sentinel Detection Rules

### Prerequisites : [Configure Audit in Microsoft Sentinel](https://learn.microsoft.com/en-us/azure/sentinel/enable-monitoring)

### Purpose : Detection / Analytics are directly changed in the production instace at times due to several reaons.

 + As the DevOps workflow is not set up.
 + Due to urgency.

Here is KQL query to idetify such scenarios and an azure function developed in KQL which can be used to display the changes.

### Demo - [Audit Sentinel Detection Rules](https://www.youtube.com/watch?v=v7XQSBnzfHg)

Query


```
_SentinelAudit()
| where SentinelResourceType =="Analytic Rule" and Description == "Create or update analytics rule."
| extend SentinelResourceId = tostring(ExtendedProperties.ResourceId)
| project TimeGenerated, SentinelResourceName, Status, Description, SentinelResourceKind, ExtendedProperties
| extend query_ = tostring(parse_json(tostring(parse_json(tostring(ExtendedProperties.UpdatedResourceState)).properties)).query)
| extend CallerName_ = tostring(ExtendedProperties.CallerName)
| extend CallerIpAddress_ = tostring(ExtendedProperties.CallerIpAddress)
| summarize arg_max(TimeGenerated,*) by query_, CallerIpAddress_, CallerName_, SentinelResourceName
| project TimeGenerated, CallerName_, CallerIpAddress_,SentinelResourceName, query_
| order by SentinelResourceName

```

Now, while we can use this query in our KQL queries and then it will also be useful to have this as a deployable template.

Here is the code for ARM Template

```
{
  "$schema": "https://schema.management.azure.com/schemas/2019-08-01/deploymentTemplate.json#",
  "contentVersion": "1.0.0.0",
  "parameters": {
    "workspaceName": {
      "type": "String"
    },
    "location": {
      "type": "String"
    }
  },
  "resources": [
    {
      "type": "Microsoft.OperationalInsights/workspaces",
      "apiVersion": "2017-03-15-preview",
      "name": "[parameters('workspaceName')]",
      "location": "[parameters('location')]",
      "resources": [
        {
          "type": "savedSearches",
          "apiVersion": "2020-08-01",
          "name": "AuditSentinelAnalytics",
          "dependsOn": [
            "[concat('Microsoft.OperationalInsights/workspaces/', parameters('workspaceName'))]"
          ],
          "properties": {
            "etag": "*",
            "displayName": "AuditSentinelAnalytics",
            "category": "Security",
            "FunctionAlias": "AuditSentinelAnalytics",
            "query": "_SentinelAudit() | where SentinelResourceType ==\"Analytic Rule\" and Description == \"Create or update analytics rule.\" | extend SentinelResourceId = tostring(ExtendedProperties.ResourceId) | project TimeGenerated, SentinelResourceName, Status, Description, SentinelResourceKind, ExtendedProperties | extend query_ = tostring(parse_json(tostring(parse_json(tostring(ExtendedProperties.UpdatedResourceState)).properties)).query) | extend CallerName_ = tostring(ExtendedProperties.CallerName) | extend CallerIpAddress_ = tostring(ExtendedProperties.CallerIpAddress) | summarize arg_max(TimeGenerated,*) by query_, CallerIpAddress_, CallerName_, SentinelResourceName | project TimeGenerated, CallerName_, CallerIpAddress_,SentinelResourceName, query_ | order by SentinelResourceName",
            "version": 1
          }
        }
      ]
    }
  ]
}
```

And you can easily deploy

[![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FTools%2FAudit-Sentinel-Detection%2Fazuredeploy.json)


{
"support": {
"name": "NA",
"email": "samik.n.roy@gmail.com",
"link": "https://github.com/samikroy"
}
} 
