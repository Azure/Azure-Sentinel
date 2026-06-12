# URL Entity Analyzer - Microsoft Sentinel Playbook

Activating the 'Deploy' button initiates the deployment of an Azure Logic App integrated with Microsoft Sentinel MCP Actions, utilizing a Microsoft Sentinel entity trigger.
The Logic App is configured to run manually when a URL entity is selected in a Sentinel incident. This Logic App analyzes suspicious URLs and provides detailed security insights including classification, analysis results, and recommendations.

![Deployment](./images/deployment.png)

**Important Note:** As of now, this playbook only works when triggered from the **Microsoft Sentinel portal in Azure**. It is not currently supported in the Defender portal.

The playbook can be manually triggered when:
- A URL entity is identified in a Microsoft Sentinel incident
- Security analysts need detailed analysis of suspicious URLs
- Automated threat intelligence is required for URL-based investigations

After the analysis is complete, the MCP Entity Analyzer conducts a comprehensive investigation of the URL entity and automatically adds a detailed comment to the incident with:
- **Classification**: Security classification of the URL
- **Entity Type**: Confirmation of the URL entity type
- **Analysis Result**: Detailed security analysis findings
- **Recommendation**: Security recommendations based on the analysis
- **Disclaimer**: AI-generated analysis disclaimer
- **Data Sources**: List of data sources used in the analysis

### Prerequisites

Prior to beginning the installation process, it's crucial to confirm that you have met the following prerequisites:
- The user deploying this Logic App needs to have a **Contributor Role**
- The user has permissions to access **Microsoft Sentinel** workspace
- You have the **Workspace ID** for your Sentinel environment
- The **SentinelMCP connector** is available in your environment
- Access to **Microsoft Sentinel portal in Azure** (not Defender portal)

### Parameters

During deployment, you'll need to provide:
- **PlaybookName**: Name for the Logic App (default: "Entity-analyzer-Url-Trigger")
- **lookBackDays**: Number of days to look back for entity analysis (default: 10 days)
- **workspaceId**: Your Microsoft Sentinel workspace ID (required)

### Deployment 

To deploy the URL Entity Analyzer Logic App:
1. Press on the Deploy button below
2. Select your subscription and resource group (use the same tenant where Microsoft Sentinel is configured)
3. Provide the required Workspace ID parameter
4. Configure the lookBackDays parameter if needed (default is 10 days)



[![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FSolutions%2FSentinelSOARessentials%2FPlaybooks%2FUrl-Trigger-Entity-Analyzer%2Fazuredeploy.json)
[![Deploy to Azure Gov](https://raw.githubusercontent.com/Azure/azure-quickstart-templates/master/1-CONTRIBUTION-GUIDE/images/deploytoazuregov.png)](https://portal.azure.us/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FSolutions%2FSentinelSOARessentials%2FPlaybooks%2FUrl-Trigger-Entity-Analyzer%2Fazuredeploy.json)

### Post Deployment

After successful deployment:
- The Logic App will be automatically enabled and ready to use
- **Authenticate the connections**: Go to the Logic App → API connections and authenticate:
  - **Microsoft Sentinel connection**: Authenticate with a user that has Sentinel permissions
  - **SentinelMCP connection**: Authenticate with Microsoft Sentinel MCP permissions
- The playbook will be available to run manually from incident entities
- Results will be automatically added as comments to the relevant incidents

![Logic App Designer](./images/logicapp_dis.png)

### How to Run the Playbook

To manually trigger the URL Entity Analyzer:

1. Navigate to **Microsoft Sentinel** in the Azure portal
2. Go to **Incidents** and open an incident containing URL entities
3. Click on the **Entities** tab
4. Select a **URL entity** from the list
5. Click on **Run playbook** button in the top right
6. Select **Entity-analyzer-Url-Trigger** from the playbook list
7. The analysis will run and results will be added as a comment to the incident

![Run Playbook](./images/trigger.png)

### How It Works

1. **Manual Trigger**: The Logic App is manually triggered when a security analyst selects a URL entity in a Sentinel incident and runs the playbook
2. **Analysis**: The URL is sent to Microsoft Sentinel's MCP Entity Analyzer for comprehensive analysis using the SentinelMCP connector
3. **Processing**: The analysis results are formatted into a readable table format with emojis and proper formatting
4. **Output**: A detailed comment is automatically added to the incident containing:
   - Security classification of the URL
   - Detailed analysis results
   - Security recommendations
   - Data sources used
   - AI-generated disclaimer

### Sample Output

The playbook generates a formatted table comment in the incident with sections like:

| 🔍 **Section** | Details |
|---|---|
| 🏷️ **Classification** | Malicious/Suspicious/Benign |
| 🕵️ **Entity Type** | Url |
| 🔎 **Analysis Result** | Detailed security findings |
| ✅ **Recommendation** | Security recommendations |
| ⚠️ **Disclaimer** | 🤖 AI-generated analysis notice |
| 📂 **Data Sources** | List of threat intelligence sources |

### Use Cases

This playbook is ideal for:
- **Phishing Investigations**: Analyze suspicious URLs from phishing emails
- **Malware Analysis**: Investigate URLs associated with malware campaigns
- **Threat Intelligence**: Enrich incidents with automated URL reputation analysis
- **Security Operations Center (SOC)**: Reduce manual analysis time for URL-based threats
- **Incident Response**: Quick assessment of URL entities during active investigations
- **On-Demand Analysis**: Run analysis only when needed for specific URL entities

### Troubleshooting

- Ensure both API connections are properly authenticated
- Verify the Workspace ID is correct for your Sentinel environment
- Check that Microsoft Sentinel MCP is enabled and accessible
- Confirm the SentinelMCP connector is available in your region
- Review the Logic App run history for any failed executions
- Verify the URL entity is properly formatted in the incident
- **Important**: Make sure you're running the playbook from the **Azure Sentinel portal**, not the Defender portal
- Ensure the incident contains a valid URL entity before attempting to run the playbook