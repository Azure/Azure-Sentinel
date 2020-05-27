Description:
This Playbook runs on a daily schedule and moves 89 day old logs per data type to Blob storage either in hourly incremements or daily blocks. The results of this Playbook is a structured file explorer within a data container in Azure that allows for easy file exploration and the ability to query the data from storage within a Log Analytics workspace.

To deploy the template: 
- Go to the Azure Portal
- In the top search bar, type deploy
- Choose 'deploy a custom template'
- Choose 'Build my own template in the editor'
- Copy and paste the JSON from the Github template
- Click save
- Enter the subscription and resource gorup that you would like to use
- Leave the name as is unless you would like to change it
- Enter the names of the table sthat you do not want to back up to storage. We recommend any tables that you do not find useful or that are noisy. An example would be Heartbeat. The format should be 'Table1', 'Table2', etc
- Click purchase


You will need to make validate workspace and blob connections:

- Click on the Azure Monitor actions
- Authenticate your account if prompted
- Choose your workspace, resource group, set resource type to Log Analytics workspace, and choose your workspace (if you can't select the resource type, hit the x at the end of the box first)
- Click on the blob storage actions under the condition at the bottom, start with the brach for if true
- Authenticate your account to create the connnection to the API if prompted
- To set the connection, choose your storage account and give the connection a name
- Click create
- For the path name, make sure that the name is: /'YOUR BLOB NAME/ 'Dynamic content for data type'
- For the blob name, make sure that the name is: DataType-startDate-endDate.json

Repeat the process for the opposite branch but make sure that the file name to be DataType-StartDate-Daily.json

Note: 
- The Logic App will not save if there are any errors so make sure any issue is resolved before saving.
