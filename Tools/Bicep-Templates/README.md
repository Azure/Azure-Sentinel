# Azure Sentinel Quickstart ARM Templates

## Deploy using AZ

### Create the Resource Group

    az group create --location <location> --resource-group <resourceGroupName>

### Deploy the Bicep file

    az deployment group create --name testDeploy --template-file <BicepFile> --parameters <bicepParamFile> --resource-group <resourceGroupName>

### Example

    az group create --location eastus --resource-group testRG
    az deployment group create --name testDeploy --template-file .\sentinel.bicep --parameters .\sentinelParams.bicepparam --resource-group testRG


## Deploy using PowerShell

### Create the Resource Group

    New-AzResourceGroup -Name <testRG> -Location <location>

### Deploy the Bicep file

    New-AzResourceGroupDeployment -Name ExampleDeployment -ResourceGroupName <resourceGroupName> -TemplateFile <BicepFile> -TemplateParameterFile <bicepParamFile>

### Example

    New-AzResourceGroup -Name testRG -Location eastus
    New-AzResourceGroupDeployment -Name ExampleDeployment -ResourceGroupName testRG -TemplateFile .\sentinel.bicep -TemplateParameterFile .\sentinelParams.bicepparam

    