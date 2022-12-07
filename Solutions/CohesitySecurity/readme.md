# Cohesity SIEM/SOAR Integration with Sentinel
This is a Cohesity authored integration for use with Sentinel, Microsoft’s cloud-native security information and event manager (SIEM) platform, to enable Security Operators and ITOps the automation and operational simplicity to respond to threats and recover from ransomware incidents, from inside Sentinel. Below demonstrates the key workflows 
* Ransomware alerts into Sentinel via RESTful APIs integration
* Automatic Incidents with details of the alerts 
* Escalate to ITSM tool via included Playbook
* Initiate recovery of clean snapshot via included Playbook
* Closed loop integration closes out the alert in Helios via included Playbook

### Package Building and Validation Instructions
__Disclaimer:__ You can skip these steps and use one of the pre-built packages from [this directory](https://github.com/cohesity/Azure-Sentinel/tree/master/Solutions/CiscoUmbrella/Package). These steps are required _only_ if you'd like to revuild everything yourself.
1. Follow this [readme.md]("https://github.com/cohesity/Azure-Sentinel/tree/master/Solutions#readme") setup build prerequisites
2. Edit [cohesity.config](https://github.com/cohesity/Azure-Sentinel/tree/master/Solutions/CohesitySecurity/cohesity.config) to replace these values with your owm
* your_email_for_playbook@your_domain.com
* your_support_email@your_domain.com
* 11111111-2222-3333-4444-555555555555
3. Run [build.ps1](https://github.com/cohesity/Azure-Sentinel/blob/CohesitySecurity.internal/Solutions/CohesitySecurity/build.ps1) to build the package
4. Follow [readme.md](https://github.com/cohesity/Azure-Sentinel/tree/master/Solutions#readme) for post-build manual validation

## Deployment Prerequisites
1. Get your Helios API key by following the steps:
* Go to the Cohesity Helios [login page](https://helios.cohesity.com/login).
* Enter your credentials and select Log In. The Summary page is displayed.
* Navigate to Settings > Access Management. The Users tab is displayed.
* Select Add API Key. The API Key Details is displayed.
* Enter a name for the API key.
* Select Save. The API Key Token is displayed.
* Pu this key to [IncidentProducer/local.settings.json](https://github.com/cohesity/Azure-Sentinel/tree/master/DataConnectors/CohesitySecurity/Helios2Sentinel/IncidentProducer/local.settings.json)
`"Values": {
  ...
        "apiKey": "33e44eac-ce99-46df-7f4e-9ac39446a66f",
  ...
  }
`
2. Create your Sentinel [workspace](https://portal.azure.com/#view/HubsExtension/BrowseResource/resourceType/microsoft.securityinsightsarg%2Fsentinel) and  put the name to [IncidentProducer/local.settings.json](https://github.com/cohesity/Azure-Sentinel/tree/master/DataConnectors/CohesitySecurity/Helios2Sentinel/IncidentProducer/local.settings.json) and [IncidentConsumer/local.settings.json](https://github.com/cohesity/Azure-Sentinel/tree/master/DataConnectors/CohesitySecurity/Helios2Sentinel/IncidentConsumer/local.settings.json)
`
"Values": {
...
        "workspace": "my-workspace",
...
}
`    
4. [Register](https://portal.azure.com/#view/Microsoft_AAD_IAM/ActiveDirectoryMenuBlade/~/RegisteredApps) a client application in Azure Active Directory with the Contributor privileges ([steps](https://learn.microsoft.com/en-us/azure/healthcare-apis/register-application)).
* Save _Application (client) ID_, _Directory (tenant) ID_ and _Secret Value_ in [IncidentConsumer/local.settings.json](https://github.com/cohesity/Azure-Sentinel/tree/master/DataConnectors/CohesitySecurity/Helios2Sentinel/IncidentConsumer/local.settings.json)
`   
"Values": {
...
    "TenantId": "fa3d34bc-81d6-4a79-ade7-175d3c33c77e",
    "ClientId": "cf58a81b-bfc5-4942-9f5e-9cdc8d1d119c",
    "ClientKey": "Xzf8Q~SxY28H4UA6fd70bt39DB92xoweNC_RRc_x",
...
}
`
5. Create a new queue in [Azure Storage Accounts](https://portal.azure.com/#view/HubsExtension/BrowseResource/resourceType/Microsoft.Storage%2FStorageAccounts) ([steps](https://learn.microsoft.com/en-us/azure/storage/queues/storage-quickstart-queues-portal)).
* Save the connection string
6. Get your [subscription name](https://portal.azure.com/#view/Microsoft_Azure_Billing/SubscriptionsBlade)
7. Choose a [resource group](https://portal.azure.com/#view/HubsExtension/BrowseResourceGroups) that you're going to use and save the value

## Deployment instructions
1. Deploy the Custom Connector by clicking on "Deploy to Azure" button. This will take you to deploying an ARM Template wizard.

[![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template)
