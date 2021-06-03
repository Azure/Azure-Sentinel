# Guide to Building Azure Sentinel Data Experiences

This guide provides an overview of the different data connectivity options providers can enable in Azure Sentinel for customers with specific focus on build, validation steps and publishing process. Furthermore, the document covers technical details on opportunities to enable richer Azure Sentinel experiences.

### Bring your data in Azure Sentinel
![Bring your data to Azure Sentinel](https://github.com/Azure/Azure-Sentinel/blob/master/DataConnectors/Images/bring_data_to_AS.png)

1. **[Choose the data connector type](#Choose-the-data-connector-type)**  – Provider decides on the connector type planned to be built, depending on the planned customer experience and the existing ingestion mechanism(s) supported by the provider data source
2. **[Send data to Azure Sentinel](#Send-data-to-Azure-Sentinel)** – Provider follows the specific steps for the applicable data connector to establish the pipeline setup as POC, validate and see the data flow in Azure Sentinel
3. **[Build the connector](#Build-the-connector)** – Provider builds the connector using templates and guidance, validates and submits the data connector with query samples and documentation
4. **[Validate and sign off in production](#Validate-and-sign-off-in-production)** – Microsoft will deploy the connector after which provider validates the connector from an E2E customer standpoint in production under limited view before customers can discover the connector
5. **[Connector ships in public preview](#Connector-ships-in-public-preview)** – After provider signs off, Microsoft switches the connector to public preview - customers can discover the data connector in the gallery and try it

### Evolve your data experience

Provider can build workbooks, analytic data templates, hunting queries, investigation graph queries, logic app connectors, playbooks and more for an enhanced customer experience while using provider's data connector in Azure Sentinel as illustrated below. Refer to details in **[evolve the data experience](#evolve-the-data-experience)**.

![Evolve the data experience](https://github.com/Azure/Azure-Sentinel/blob/master/DataConnectors/Images/evolve_data_experience.png)

# Bring your data in Azure Sentinel

## Choose the data connector type

There are three types of data connectors providers can build to stream their data into Azure Sentinel.

The following table lists these and provides a high-level overview to help providers decide.

| **Sentinel Log Ingestion Format** | **Customer Experience** | **Why choose?** |
| --- | --- | --- |
| CEF (Preferred) | <ul><li>Log information is automatically ingested into standard CEF schema.</li><li>KQL Queries use strongly typed and well-known CEF schema.</li><li>Little or no additional parsing required by your customers</li><li>Your data will be meaningful to many queries.</li><li>Multi-step configuration - Customer needs to set up a machine / Azure VM to run an agent to push logs into Sentinel </li></ul>|CEF results in the best query and analytics experience in Sentinel as it will appear as the well know CEF (CommonSecurityLog) schema as columns in the Sentinel Log tables.|
| REST API | <ul><li>Log information is automatically ingested into custom tables with your schema.</li><li>	Custom queries required to use your data.</li><li> Customer must learn your schema.</li><li>Simple configuration - Customer does not need to set up a machine / Azure VM to run the agent </li></ul>|When you have data that does not conform to CEF or RAW Syslog formats you can create custom tables.<p>You want strict control over schema mapping and column names in Sentinel tables on how you present your data.|
| Syslog (Least preferred) | <ul><li>RAW Syslog information is automatically ingested into simple log schema with a simple string.</li><li>	Queries are more complex as customers will need to parse the syslog messages using KQL Functions.</li><li>Multi-step configuration - Customer needs to set up a machine / Azure VM to run an agent to push logs into Sentinel </li></ul>|You only can emit RAW Syslog at this point.|

## Send Data to Azure Sentinel

Once you have decided on the type of data connector you plan to support, set the pipeline to send this data to Azure Sentinel as a POC before building the connector.  The process is described for each data connector type. Once you have a POC, send an email to [AzureSentinelPartner@microsoft.com](mailto:AzureSentinelPartner@microsoft.com) for the POC demo.

### REST API Connectors

1. Use the [Azure Monitor Data Collector API](https://docs.microsoft.com/azure/azure-monitor/platform/data-collector-api) to send data to Azure Log Analytics. [This blog](https://zimmergren.net/building-custom-data-collectors-for-azure-log-analytics/) covers step by step instructions with screenshots to do so. If on prem, open port 443 (HTTPS/TLS) on your environment to talk to Azure Sentinel.
2. Ensure the schema used for structuring the data in Log Analytics is locked. Any changes to the schema after the data connector is published will have a compatibility impact, hence need to have a new name for the connector data type.
3. Design a configuration mechanism in your product experience via product settings or via your product website, where your customers can go and enter the following information to send their logs into Log Analytics for Azure Sentinel.
    1. [**Required**] Azure Sentinel workspace ID
    1. [**Required**] Azure Sentinel primary key
    1. [**Optional**] Custom log name
    1. Any other specific dependency that may be needed to successfully establish connectivity
4. These logs will appear in a Custom Log Analytics table **CustomLogs** -> **&lt;log name&gt;** where the log name is what the customer provides in the above-mentioned step. Identify a default log name to handle the scenario where customer does not enter the custom log name.
5. Design and validate a few key queries that lands the value of the data stream using Kusto Query Language. Share these as sample queries in the data connector.

**Example connectors to refer to** : Symantec, Barracuda WAF

**Connector Validation Steps**

1. Test the actual customer experience and validate if data flows as expected and appears in the expected Azure Sentinel Log Analytics custom table provided.
2. If on prem, open port 443 (HTTPS/TLS) on your environment to talk to Azure Sentinel. Ensure this is documented in connector documentation (steps in following section) for your customers.
3. From a data quality perspective,
    1. Ensure the data you send is complete and contains the same fields available in your product.
    2. Ensure the data is valid and easy to query using Log Analytics.

### CEF Connector

To enable the CEF connector deploy a dedicated proxy Linux machine (VM or on premises) to support the communication between your security solution (the product that sends the CEF messages) and Azure Sentinel.

Enable the CEF connector as follows:

1. Go to **Azure Sentinel**
2. Open the **Data Connectors** page and choose the relevant connector and click **Open connector page**
3. Follow the CEF instructions below (also in the CEF connector documentation).

_1. Install and configure Linux Syslog agent_

Install and configure the Linux agent to collect your Common Event Format (CEF) Syslog messages and forward them to Azure Sentinel.

_1.1 Select a Linux machine_

Select or create a Linux machine that Azure Sentinel will use as the proxy between your security solution and Azure Sentinel this machine can be on your on-prem environment, Azure or other clouds.

_1.2 Install the CEF collector on the Linux machine_

Install the Microsoft Monitoring Agent on your Linux machine and configure the machine to listen on the necessary port and forward messages to your Azure Sentinel workspace.

Note:

1. Make sure that you have Python on your machine using the following command:

        python –version

2. You must have elevated permissions (sudo) on your machine <p>Run the following command to install and apply the CEF collector:

        sudo wget https://raw.githubusercontent.com/Azure/Azure-Sentinel/master/DataConnectors/CEF/cef\_installer.py&&sudo python cef\_installer.py [WorkspaceID]_ [Workspace Primary Key]

_2. Forward Common Event Format (CEF) logs to Syslog agent_

2.1 Set your security solution to send Syslog messages in CEF format to the proxy machine. This varies from product to product and follow the process for your product. There are couple of ways to choose from pushing your logs

1. The agent can collect logs from multiple sources but must be installed on dedicated machine per the following diagram
![collect logs](https://github.com/Azure/Azure-Sentinel/blob/master/DataConnectors/Images/syslog_step1.png)
2. Alternatively, you can deploy the agent manually on an existing Azure VM, on a VM in another cloud, or on an on-premises machine as shown in the diagram below
![deploy agent](https://github.com/Azure/Azure-Sentinel/blob/master/DataConnectors/Images/syslog_step2.png)
2.2 Make sure to send the logs to port 514 TCP on the machine&#39;s IP address.

2.3 Outline specific steps custom for sending your product logs along with link to your (partner) product documentation on how customers should configure their agent to send CEF logs from the respective product into Azure Sentinel.

**Example connectors to refer to** : ZScaler

**Connector Validation Steps**

Follow the instructions to validate your connectivity:

1. Open Log Analytics to check if the logs are received using the CommonSecurityLog schema.
Note: It may take about 20 minutes until the connection streams data to your workspace.
2. If the logs are not received, run the following connectivity validation script:
     1. Note:
        1. Make sure that you have Python on your machine using the following command:<p>
        _python –version_
        2. You must have elevated permissions (sudo) on your machine
     2. _sudo wget https://raw.githubusercontent.com/Azure/Azure-Sentinel/master/DataConnectors/CEF/cef\_troubleshoot.py&&sudo python cef\_troubleshoot.py [WorkspaceID]_
3. From a data quality perspective,
     1. Ensure the data you send is complete and contains the same fields available in your product.
     2. Ensure the data is valid and easy to query using Log Analytics.

4. Design and validate a few key queries that lands the value of the data stream using Kusto Query Language. Share these as sample queries in the data connector.

To use TLS communication between the security solution and the Syslog machine, you will need to configure the Syslog daemon (rsyslog or syslog-ng) to communicate in TLS: [Encrypting Syslog Traffic with TLS - rsyslog](https://www.rsyslog.com/doc/v8-stable/tutorials/tls_cert_summary.html), [Encrypting log messages with TLS – syslog-ng](https://support.oneidentity.com/technical-documents/syslog-ng-open-source-edition/3.22/administration-guide/60#TOPIC-1209298).

### Syslog Connector

**Note:** If your product supports CEF, the connection is more complete and you should choose CEF and follow the instructions in [Connecting data from CEF](https://docs.microsoft.com/azure/sentinel/connect-common-event-format) and data connector building steps detailed in the CEF connector section.

1. Follow the steps outlined in the [Connecting data from Syslog](https://docs.microsoft.com/azure/sentinel/connect-syslog) to use the Azure Sentinel syslog connector to connect your product.
2. Set your security solution to send Syslog messages to the proxy machine. This varies from product to product and follow the process for your product.
3. Outline specific steps custom for sending your product logs along with link to your (partner) product documentation on how customers should configure their agent to send Syslog logs from the respective product into Azure Sentinel.
4. Design and validate a few key queries that lands the value of the data stream using Kusto Query Language. Share these as sample queries in the data connector.
5. Build a parser based on Kusto function to ensure the query building experience is easy for customers working with the data connector.

**Example connectors to refer to** : Barracuda CWF

**Connector Validation Steps**

Follow the instructions to validate your connectivity:

1. Open Log Analytics to check if the logs are received using the Syslog schema.
Note: It may take about 20 minutes until the connection streams data to your workspace.
2. From a data quality perspective,
    1. Ensure the data you send is complete and contains the same fields available in your product.
    2. Ensure the data is valid and easily to query using Log Analytics.

## Build the connector

Once you have a working POC, you are ready to build, validate the data connector user experience and submit your connector and relevant documentation.

1. **Review the [data connector template guidance](https://github.com/Azure/Azure-Sentinel/blob/master/DataConnectors/Templates/Data%20Connectors%20Template%20Guidance.md)** - This is to help get familiarized with the nomenclature used in the templates and to enable filling out the json template easily.
2. **Use the template** - Download the right template for your data connector type from the following, rename the json file to ‘ProviderNameApplianceName.json’ (no spaces in name) and fill out the template per the guidance mentioned above.
   * [Connector_CEF_Template.json](https://github.com/Azure/Azure-Sentinel/blob/master/DataConnectors/Templates/Connector_CEF_template.json)
   * [Connector_REST_API_template.json](https://github.com/Azure/Azure-Sentinel/blob/master/DataConnectors/Templates/Connector_REST_API_template.json)
   * [Connector_Syslog_template.json](https://github.com/Azure/Azure-Sentinel/blob/master/DataConnectors/Templates/Connector_Syslog_template.json)
   * [DataConnector_API_AzureFunctionApp_template.json](https://github.com/Azure/Azure-Sentinel/blob/master/DataConnectors/Templates/Connector_REST_API_AzureFunctionApp_template/DataConnector_API_AzureFunctionApp_template.json)
3. **Validate the Connector UX** – Follow these steps to render and validate the connector UX you just built
    1.	The test utility can be accessed by this URL - https://portal.azure.com/?feature.BringYourOwnConnector=true
    2.  Go to Azure Sentinel -> Data Connectors 
    3.	Click the “import” button and select the json file you created as follows.
    ![Import button](https://github.com/Azure/Azure-Sentinel/blob/master/DataConnectors/Images/validateUX_stepc.png)
    4. The json file you just created is loaded (example as follows) - Validate connector UX by ensuring all links resolve appropriately with no errors (including query links) in both the main and ‘next steps’ page, check for content accuracy, grammar, typos and formatting.  Update the json as needed and reload to revalidate. 
    ![Validate connector](https://github.com/Azure/Azure-Sentinel/blob/master/DataConnectors/Images/validateUX_stepd.png)

>>**Note**: This json is loaded only in your session and not shared out. The logo won’t show up since it’s not part of the json. Connector logo will be included when Microsoft builds and deploys the data connector.

4. **Prepare sample data for validation and submission** – Plan to submit some real-world, sanitized sample data for your connectors that covers all types of logs, events, alerts, etc. depending on the data type. This is the test validation set that can be used to build other contribution types on top of this data connector. The format for this file can be json / csv (json preferred) file with the column names / property names adhering to the data type property names. The data file name needs to be the same name as the data type name. Submit the sample data file via a GitHub PR to the ['Sample data' folder](https://aka.ms/azuresentinelgithubsampledata) in the right subfolder - CEF / Syslog / Custom depending on the type of data connector.
5.	**Submit your data connector** - Follow the [general contribution guidelines for Azure Sentinel](https://aka.ms/sentinelgithubcontributionguidelines) to open a Pull Request (PR) to submit the data connector:
    1.	The json file in the ['Connectors' folder](https://aka.ms/azuresentinelgithubdataconnectors)
    2.	The sample data file in the right subfolder of ['Sample data' folder](https://aka.ms/azuresentinelgithubsampledata)
    3.	The company logo adhering to the following requirements in the ['Logo' folder](https://aka.ms/azuresentinelgithublogos)
        1.	Logo needs to be in SVG format and under 5 Kb
        2.	Ensure raw file of logo does **not** have any of the following: 
            * cls and style formats 
            * embedded png formats 
            * xmlns:xlink  
            * data-name
        3. Do not use xlink:href - use inline instead
        4. Do not use title tag
        5. If some properties in the logo have IDs (for e.g. <g id="layer0"...), then set these IDs as GUIDs so that these are uniquely identifiable across all Azure logo assets
        6. Logo scales well to fit in a 75 px square
        7. SVG code file is formatted well for readability
    4.  For Syslog data connector, the Kusto function parser is in the right subfolder (PROVIDERNAME) of ['Parsers' folder](https://aka.ms/sentinelgithubparsers)
    5.  If you are bringing in detections or hunting queries, requiredDataConnectors section of the YAML template must be populated.  Details of what to reference in the YAML template from the connector JSON are in the Query Style Guide under [requiredDataConnectors](https://github.com/Azure/Azure-Sentinel/wiki/Query-Style-Guide#requireddataconnectors)

6. **Prepare and submit your data connector documentation** – Besides Azure Sentinel gallery discoverability, the connectors can also be discovered out of product in documentation. 
    1.	Download one of the following templates depending on the type of data connector and <i>PROVIDER NAME APPLIANCE NAME.md</i> and fill out the template per the guidance mentioned in the template. Replace the guidance in the template with relevant steps.
    2. Validate the md file for formatting and ensure all links resolve appropriately. You can use VS Code or any other editor that supports md file editing.
      * [Doc_Template_CEF_Connector.md](https://github.com/Azure/Azure-Sentinel/blob/master/DataConnectors/Templates/Doc_Template_CEF_Connector.md)
      * [Doc_Template_REST_API_Connector.md](https://github.com/Azure/Azure-Sentinel/blob/master/DataConnectors/Templates/Doc_Template_REST_API_Connector.md)
      * [Doc_Template_Syslog_Connector.md](https://github.com/Azure/Azure-Sentinel/blob/master/DataConnectors/Templates/Doc_Template_Syslog_Connector.md)
    3. Once validated, email the md file to [AzureSentinelPartner@microsoft.com](mailto:AzureSentinelPartner@microsoft.com)

## Validate and sign off in production
Once the connector is deployed in production, we will share a link for you to privately access your data connector. Validate your connector:
1.	Ensure data flows as expected and the data appears in the expected format in the right Log Analytics table
2.	Ensure sample queries shared with the connector execute as expected and all the other queries that appear in the json file like the graphQueries, dataTypes etc. 
3.	Validate connector UX by ensuring all links resolve appropriately with no errors (including query links) in both the main and ‘next steps’ page, check for content accuracy, grammar, typos, formatting and logo rendering aspects. 
4.	If you have Kusto functions included / your sample queries and workbooks take a dependency on certain Kusto function, ensure those work as expected and that dependency is called out in the connector UX (in the Configuration at the beginning and in the next steps section of the connector as a banner)<p>
Once everything looks as expected, send an email to [AzureSentinelPartner@microsoft.com](mailto:AzureSentinelPartner@microsoft.com) of your sign off to get your connector shipped in public preview.

## Connector ships in public preview
Promote your connector to get installs and get customer feedback. Support connector issues reported by the customer. These can be in generic data flow aspects which you can handle on provider side. There may be connector UX issues or queries etc. issues that you can update by doing a PR on the respective file and inform [AzureSentinelPartner@microsoft.com](mailto:AzureSentinelPartner@microsoft.com) for deployment. 
### Exit criteria for connector GA
Once the data connector is in public preview for at least a month, send an email with the following info to [AzureSentinelPartner@microsoft.com](mailto:AzureSentinelPartner@microsoft.com) to get the connector to GA. 
*	The data connector has at least sample queries and workbooks to visualize and use the data effectively in Azure Sentinel. 
*	The data connector has at least 10 unique customers  
*	No major unresolved customer reported incidents with the data connector in a month after release
*   Support for government cloud (.us in addition to .com).

## Evolve the data experience 
### Workbooks 
[Follow the steps](https://aka.ms/azuresentinelgithubworkbooks) to build your workbook and submit your workbook json file, two screenshots of the workbook view one each in white and black background theme settings, logo and entry in the ‘workbooksMetadata.json’ file by a PR as mentioned in the instructions. 

### Analytic Rule Templates
[Follow the steps](https://github.com/Azure/Azure-Sentinel/wiki/Contribute-to-Sentinel-GitHub-Community-of-Queries) to build and submit your analytic rule template or detection pertaining to this data connector. Ensure to fill in the requiredDataConnectors parameter with the right data connector ID(s) to establish relation of this analytic rule template with the data connector. 

### Logic Apps Connectors
Build logic apps connectors to enable automation capabilities for customers in the following areas:
1.	Incident management – for e.g. assign a ticket to an analyst, keep ticket status in sync, …
2.	Enrichment and Investigation – for e.g. geo lookup for an IP, sending investigation emails, …
3.	Remediation – for e.g. block an IP address, block user access, isolate machine, …
4.	Any other automation capabilities unique to your appliance. 

Follow the steps in the Azure Logic Apps [building custom connectors documentation](https://docs.microsoft.com/connectors/custom-connectors/) to create, certify and ship an Azure Logic App connector. This not only discoverable for Azure Sentinel customers, but also visible in the Azure Logic Apps gallery for Azure Logic Apps and Microsoft Flow customers too. Inform [AzureSentinelPartner@microsoft.com](mailto:AzureSentinelPartner@microsoft.com) if you are thinking of building a custom connector for your security appliance.

## Other data experience options
Check out the [Azure Sentinel GitHub repo](https://aka.ms/threathunters) for more information on these.
