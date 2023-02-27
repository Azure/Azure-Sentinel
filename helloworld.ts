
const fs = import("fs");
var message = 'Hello World';
console.log(message);

const ignoreFiles = ["azure-pipelines", "azureDeploy", "host.json", "proxies.json", "azuredeploy", "function.json"]
const requiredFolderFilesTag = JSON.parse('{"createUI": "description","data": "description","dataConnectors" : "descriptionMarkdown"}');
var fileContent = "{\n  \"$schema\": \"https://schema.management.azure.com/schemas/0.1.2-preview/CreateUIDefinition.MultiVm.json#\",\n  \"handler\": \"Microsoft.Azure.CreateUIDef\",\n  \"version\": \"0.1.2-preview\",\n  \"parameters\": {\n    \"config\": {\n      \"isWizard\": false,\n      \"basics\": {\n        \"description\": \"**Note:** _There may be [known issues](https://aka.ms/sentinelsolutionsknownissues) pertaining to this Solution, please refer to them before installing._\\n\\nThe [Alibaba Cloud](https://www.alibabacloud.com/product/log-service) solution provides the capability to retrieve logs Azure Sentinel from cloud applications using the Cloud API and store events into Microsoft Sentinel through the [REST API](https://aliyun-log-python-sdk.readthedocs.io/api.html). \\n \\n **Underlying Microsoft Technologies used:**\\n\\n This solution takes a dependency on the following technologies, and some of these dependencies either may be in [Preview](https://azure.microsoft.com/support/legal/preview-supplemental-terms/) state or might result in additional ingestion or operational costs: \\n \\n a. [Azure Monitor HTTP Data Collector API](https://docs.microsoft.com/azure/azure-monitor/logs/data-collector-api) \\n \\n b. [Azure Functions](https://azure.microsoft.com/services/functions/#overview)\\n\\n**Data Connectors:** 1, **Parsers:** 1\\n\\n[Learn more about Microsoft Sentinel](https://aka.ms/azuresentinel) | [Learn more about Solutions](https://aka.ms/azuresentinelsolutionsdoc)\",\n        \"subscription\": {\n          \"resourceProviders\": [\n            \"Microsoft.OperationsManagement/solutions\",\n            \"Microsoft.OperationalInsights/workspaces/providers/alertRules\",\n            \"Microsoft.Insights/workbooks\",\n            \"Microsoft.Logic/workflows\"\n          ]\n        },\n        \"location\": {\n          \"metadata\": {\n            \"hidden\": \"Hiding location, we get it from the log analytics workspace\"\n          },\n          \"visible\": false\n        },\n        \"resourceGroup\": {\n          \"allowExisting\": true\n        }\n      }\n    },\n    \"basics\": [\n      {\n        \"name\": \"getLAWorkspace\",\n        \"type\": \"Microsoft.Solutions.ArmApiControl\",\n        \"toolTip\": \"This filters by workspaces that exist in the Resource Group selected\",\n        \"condition\": \"[greater(length(resourceGroup().name),0)]\",\n        \"request\": {\n          \"method\": \"GET\",\n          \"path\": \"[concat(subscription().id,'/providers/Microsoft.OperationalInsights/workspaces?api-version=2020-08-01')]\"\n        }\n      },\n      {\n        \"name\": \"workspace\",\n        \"type\": \"Microsoft.Common.DropDown\",\n        \"label\": \"Workspace\",\n        \"placeholder\": \"Select a workspace\",\n        \"toolTip\": \"This dropdown will list only workspace that exists in the Resource Group selected\",\n        \"constraints\": {\n          \"allowedValues\": \"[map(filter(basics('getLAWorkspace').value, (filter) => contains(toLower(filter.id), toLower(resourceGroup().name))), (item) => parse(concat('{\\\"label\\\":\\\"', item.name, '\\\",\\\"value\\\":\\\"', item.name, '\\\"}')))]\",\n          \"required\": true\n        },\n        \"visible\": true\n      }\n    ],\n    \"steps\": [\n      {\n        \"name\": \"dataconnectors\",\n        \"label\": \"Data Connectors\",\n        \"bladeTitle\": \"Data Connectors\",\n        \"elements\": [\n          {\n            \"name\": \"dataconnectors1-text\",\n            \"type\": \"Microsoft.Common.TextBlock\",\n            \"options\": {\n              \"text\": \"This solution installs the data connector provides the capability to retrieve logs from cloud applications using the Cloud API and store events into Microsoft Sentinel through the REST API. After installing the solution, configure and enable this data connector by following guidance in Manage solution view.\"\n            }\n          },\n          {\n            \"name\": \"dataconnectors-parser-text\",\n            \"type\": \"Microsoft.Common.TextBlock\",\n            \"options\": {\n              \"text\": \"The solution installs a parser that transforms ingested data. The transformed logs can be accessed using the AliCloud Kusto Function alias.\"\n            }\n          },\n          {\n            \"name\": \"dataconnectors-link2\",\n            \"type\": \"Microsoft.Common.TextBlock\",\n            \"options\": {\n              \"link\": {\n                \"label\": \"Learn more about connecting data sources\",\n                \"uri\": \"https://docs.microsoft.com/azure/sentinel/connect-data-sources\"\n              }\n            }\n          }\n        ]\n      }\n    ],\n    \"outputs\": {\n      \"workspace-location\": \"[first(map(filter(basics('getLAWorkspace').value, (filter) => and(contains(toLower(filter.id), toLower(resourceGroup().name)),equals(filter.name,basics('workspace')))), (item) => item.location))]\",\n      \"location\": \"[location()]\",\n      \"workspace\": \"[basics('workspace')]\"\n    }\n  }\n}\n";
        
if (requiredFolderFilesTag)
{
    const hasIgnoredFile = ignoreFiles.filter(item => { return filePath.includes(item)}).length > 0
    const hasRequiredFolderFiles = requiredFolderFilesTag.filter(item => { return filePath.includes(item.key)}).length > 0

    if (!hasIgnoredFile && hasRequiredFolderFiles)
    {
        const searchText = "Azure Sentinel";
        const expectedText = "Microsoft Sentinel";
        var filePath = "Solutions/Alibaba Cloud/Package/createUiDefinition.json"

        var fileContentStringify = JSON.stringify(fileContent);
        console.log(fileContentStringify)
        var fileContentObj = JSON.parse(fileContentStringify);

    }
}


        var fileContentStringify = JSON.stringify(fileContent);
        console.log(fileContentStringify)
        var fileContentObj = JSON.parse(fileContentStringify);

        for (const tagName of validTags) 
        {
            if (filePath.includes("createUiDefinition.json"))
            {
                var tagContent = fileContentObj["parameters"]["config"]["basics"]["description"];
            }
            else
            {
                var tagContent = fileContentObj[tagName];
            }

            if (tagContent)
            {
                let hasAzureSentinelText = tagContent.toLowerCase().includes(searchText.toLowerCase());
                console.log("inside of if");
                if (hasAzureSentinelText) {
                    console.log(`Please update text from '${searchText}' to '${expectedText}' in '${tagName}' tag in the file '${filePath}'`);
                }
            }
        }