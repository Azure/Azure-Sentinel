# Tasks-Repository
author: Benji Kovacevic

This solution contains Tasks Repository Watchlist and Playbook that are used to assign tasks automaticlly based on incident title. <br>
This solution is explained in details in this blog - <a href="https://techcommunity.microsoft.com/t5/microsoft-sentinel-blog/create-tasks-repository-in-microsoft-sentinel/ba-p/4038563">Create Tasks Repository in Microsoft Sentinel</a>.

# Prerequisites
Permissions
1.	Watchlist:<br>
Permission needed to deploy: Microsoft Sentinel Contributor
2.	Playbook:<br>
Permission needed to deploy: Logic App Contributor<br>
Permission needed to assign RBAC to managed identity: User Access Administrator or Owner on Resource Group where Microsoft Sentinel is
3.	Automation rule:<br>
Permission needed to create: Microsoft Sentinel Responder


# Quick Deployment
1. Deploy Tasks Repository watchlist using ARM template<br>
[![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FTools%2FTasks-Repository%2FTasksRepositoryWatchlistTemplate.json)

, or using <a href="https://github.com/Azure/Azure-Sentinel/blob/master/Tools/Tasks-Repository/TasksRepository.csv">raw CSV file</a> and following instructions on how to <a href="https://learn.microsoft.com/azure/sentinel/watchlists-create">create watchlist manually</a>.
<br>
<strong>Note:</strong><br>
When creating watchlist manually, use TasksRepository for alias, or this field will need to be updated in the playbook after deploying it. Also, map SearchKey to IncidentTitle column as playbook is using it as well.

2. Deploy a playbook<br>
[![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FTools%2FTasks-Repository%2Fazuredeploynmi.json)
[![Deploy to Azure Gov](https://raw.githubusercontent.com/Azure/azure-quickstart-templates/master/1-CONTRIBUTION-GUIDE/images/deploytoazuregov.png)](https://portal.azure.us/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FTools%2FTasks-Repository%2Fazuredeploynmi.json)
<br><br>

3. Final step is to create an automation rule that will run on incident creation on all incidents, and as an action will run playbook.

- Title: Tasks repository<br>
- Trigger: When incident is created<br>
- Actions: Run playbook -> TasksRepository<br>

![automation rule screenshot](./images/automationrule.png)<br>

# Post-deployment
1. Assign Microsoft Sentinel Responder role to the managed identity. To do so, choose Identity blade under Settings of the Logic App.
2. Open Edit mode of the playbook, and add managed identity to Azure Monitor Logs action
![playbook screenshot](./images/AMLConnection1.png)<br>
![playbook screenshot](./images/AMLConnection2.png)<br>
For Connection Name enter: Azuremonitorlogs-TasksRepository<br>
For Authentication Type choose: Logic Apps Managed Identity<br>
![playbook screenshot](./images/AMLConnection3.png)<br>
Select Create New, and then Save the playbook.<br>
3. Add tasks to the Tasks Repository watchlist.
<strong>Note</strong>: 
When adding additional tasks, there is a format that should be used so that playbook can map tasks title and description field. Each tasks filed should look like Tasks title, unique separator |^|, followed by Tasks description. Unique separator |^| is used in playbook to separate title and description of the tasks into its appropriate fields. In watchlist example, in column Task01 we can see example - Task 1|^|Task description.
