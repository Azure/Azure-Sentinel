### This solution is deprecated. It is not recommended to use this.
#### Please reference the out of box functionality for [long term retention via Azure Log Analytics.](https://learn.microsoft.com/en-us/azure/azure-monitor/logs/data-retention-archive?tabs=portal-3%2Cportal-1%2Cportal-2)


~~Description:~~
~~This Playbook runs on a daily schedule and moves 89 day old logs per data type to Blob storage in hourly incremements. The result of this Playbook is a structured file explorer within a data container in Azure that allows for easy file exploration and the ability to query the data from storage within a Log Analytics workspace.~~

~~To deploy the template:~~
~~- Go to the Azure Portal~~
~~- In the top search bar, type deploy~~
~~- Choose 'deploy a custom template'~~
~~- Choose 'Build my own template in the editor'~~
~~- Copy and paste the JSON from the GitHub template~~
~~- Click save~~
~~- Enter your resource group, workspace name, workspace subscription ID, workspace resource group, your email address, the name of the storage account that is going to be created, the SKU for the storage account, the storage account type, and a name for the container that is going to be built~~
~~- Leave the name as is unless you would like to change it~~
~~- Enter the names of the table that you do not want to back up to storage. We recommend any tables that you do not find useful or that are noisy. An example would be Heartbeat. The format should be 'Table1', 'Table2', etc~~
~~- Click purchase~~

~~You will need to authenticate a connection for Azure Monitor within the Playbook:~~

~~- Click on the Azure Monitor actions~~
~~- Chances are that the connection didn't establish, click the information icon next to the connection name to authorize the connection, it will bring up a login screen~~
~~- Log in to your account~~
~~- Confirm that the subscription, resource group, and workspace are all correct based on what you entered for the template~~
~~- Make sure that the container that you named is listed under the Azure Blob option so that the logs are routed properly when the Playbook is run~~

