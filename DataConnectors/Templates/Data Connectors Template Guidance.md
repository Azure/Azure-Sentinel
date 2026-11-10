# Data Connectors Template Guidance

To make it easy to build and validate data connectors user experience, we have data connector json templates available for partners to use, validate and submit. This guide provides information on how to fill out the json templates.

The underlying json structure of any of the data connector template is the same, hence this connector template guidance is generalized for CEF, REST or Syslog data connector types in Microsoft Sentinel. There will be specific recommendations provided for different types as needed.

# How to use the json template?

Download the json template based on the data connector type and rename it to as &quot; **ProviderNameApplianceName.json**&quot; (no spaces while naming the JSON file). Now you can start updating the json template to customize it for your connector definition. At any point of updating the json, ensure the json is correctly formatted to avoid syntactical errors. It&#39;s recommended to use a json editor like VS Code for this purpose.

# Nomenclatures and Definitions

The following nomenclatures appear in the json templates. Note these accordingly to represent your data connector and fill these values accordingly in the template.

1. **PROVIDER NAME** – The name of the vendor who is building the data connector. For e.g. Microsoft, Symantec, Barracuda, etc.
2. **APPLIANCE NAME** – The name of the specific product whose logs or data is being sent to Microsoft Sentinel via this data connector.  For e.g. CloudGen Firewall (from Barracuda), Security Analytics (from Citrix), etc.
3. **DATATYPE\_NAME** – The name of the default table where the data / logs will be sent to. The location changes for each type of data connector. While naming these:
  1. Do **not** have spaces in the data type names.
  2. Represent both provider, appliance name and type of data [optionally] as a short name in the data type name. The goal is to be able to disambiguate different data types if there&#39;s going to be separate data types for different appliances from the same provider for different log types (like alerts, events, raw logs, network logs, etc.)
  3. For REST API data types, suffix an &#39;\_CL&#39; in the data type names for these for custom logs.
  4. Some connectors can have multiple data types. Ensure each data type is represented in relevant queries and workbooks while filling the template.

Log locations and examples of data type names:

- **CEF** – These logs land in the CommonSecurityLogs Log Analytics table. Examples of data type names are: TrendMicroDeepSecurity
- **REST API** – These logs land in the custom Log Analytics table. Example of data type names are: CitrixAnalytics\_SAlerts\_CL
- **Syslog** – These logs land in the Syslog Log Analytics table. Example of data type names are: BarracudaCloudGenFW

# How to fill the json template?

Refer to the following context for each property in the json template. The values for these properties in the json template are auto filled and need to be overwritten so that it&#39;s self-explanatory and easy to use.

1. **id** –A friendly unique identifier without spaces to identify the data connector – recommended format: ProviderNameApplianceName. This does **not** show up in the data connector UX.
2. **title** – The name of the connector – recommended format: PROVIDER NAME APPLIANCE NAME
3. **publisher** – The vendor who publishes the connector, or the PROVIDER NAME
4. **descriptionMarkdown** - Short description of ~50 words. See other data connectors for context
5. **graphQueries** - This is the base query of the graph that shows up in the data connector UX. The connector UX framework that consumes this json converts this query to return an array of &#39;{Time: String, Value: Number}&#39;. The default format for the query is filled in the template. Replace the DATATYPE\_NAME, PROVIDER NAME and APPLIANCE NAME in the applicable areas to form the query. If you have defined multiple data types for your connector, ensure you duplicate the graphQueries for each of the data types you have for your connector as shown below.

        "graphQueries": [
          {
              "metricName": "Total data received",
              "legend": "DATATYPE_NAME1",
              "baseQuery": "DATATYPE_NAME1"
          },
          {
              "metricName": "Total data received",
              "legend": "DATATYPE_NAME2",
              "baseQuery": "DATATYPE_NAME2"
          }
        ],

1. **sampleQueries** – These queries can be used by customers to derive the most benefit from the data connector. Specify title for the query to outline what the query does and a custom working KQL query for the same. Multiple sample queries can be provided by just copy-pasting the current structure and expanding as needed as shown below.

          "sampleQueries": [
            {
                "description": "One-line title for your sample query 1",
                "query": "Kusto Query 1"
            },
            {
              "description": "One-line title for your sample query 2",
              "query": "Kusto Query 2"
            },
            {
              "description": "One-line title for your sample query 3",
              "query": "Kusto Query 3"
            },
          ]

1. **dataTypes** – The format in which the data shows up in the logs for the connector. For CEF the data type is CEF format while for REST API the data type represents the data schema of the logs. Follow the guidance [nomenclatures and definitions section](#nomenclatures-and-definitions) for naming this. A data type is identified by its name which is the DATATYPE\_NAME and lastDataReceivedQuery which is the KQL query that represents the last data received query from the specific data table.<p>
A data connector can have multiple data types and these can be represented by copy pasting the current data type section to have name and lastDataReceivedQuery as shown below:

          "dataTypes": [
            {
                "name": "DATATYPE_NAME",
                "lastDataReceivedQuery": "DATATYPE_NAME\n            | summarize Time = max(TimeGenerated)\n            | where isnotempty(Time)"
            },
            {
                "name": "CommonSecurityLog (DATATYPE_NAME)",
                "lastDataReceivedQuery": "\nCommonSecurityLog\n| where DeviceVendor == \"PROVIDER NAME\"\n| where DeviceProduct == \"APPLIANCE NAME\"\n\n            | summarize Time = max(TimeGenerated)\n            | where isnotempty(Time)"
            },
            {
                "name": "Syslog(DATATYPE_NAME)",
                "lastDataReceivedQuery": "DATATYPE_NAME\n            | summarize Time = max(TimeGenerated)\n            | where isnotempty(Time)"
            }
        ]

1. **connectivityCriterias** – The criteria that defines whether the data connector is connected or not. These are KQL queries and are pre-filled. Replace the DATATYPE\_NAME appropriately to get the query working for the data connector. Additional connectivity criteria can be specified as needed for custom scenarios and the connector will show as connected only if **all** the criteria are met.
2. **availability** – Represents whether the connector is generally available. Do **not** update this property value.
3. **permissions** – Represents the required permissions needed for the data connector to be enabled or connected. For e.g. write permissions to the workspace is needed for connector to be enabled, etc. These appear in the connector UX in the prerequisites section. This property value need **not** be updated and can remain as-is.
4. **instructionSteps** – These are the specific instructions to connect to the data connector.
  * For CEF and Syslog, leverage the existing text as-is and add anything custom as needed.
  * For REST API, either provide a link to your website/documentation that outlines the onboarding guidance to send data to Microsoft Sentinel **or** provide detailed guidance for customers to send data to Microsoft Sentinel.
  * If Connector is dependent on Kusto Function (Parser), **additionalRequirementBanner** and **instruction step** about Parser need to be added in Connector. <p>
  
# What is the format for redirection/Short links?
1. Redirection link for **Parser** - https://aka.ms/sentinel-[connectorid]-parser
2. Redirection link for **AzureDeploy** - https://aka.ms/sentinel-[connectorid]-azuredeploy
3. Redirection link for **Raw .zip file** link to download the package - https://aka.ms/sentinel-[connectorid]-functionapp
4. Redirection link for **RAW run.ps1** for function manual deployment - https://aka.ms/sentinel-[connectorid]-functioncode


Expand and add multiple instructions as needed by adding more title and description elements in this block.

## Storage Blob CCF V2 template

Use `Connector_StorageBlob_CCF_templateV2.json` for Storage Blob connectors that
authenticate with the first-party application using `ManagedServicePrincipal`.
Keep the first-party application ID in the service-principal control; the
tenant-local principal selected by that control receives the collector's blob
and queue role assignments. Replace the solution, table, stream, and other
authoring placeholders before deploying.

### Multiple connections

The connector page uses `DataConnectorsGrid` to display
`properties.addOnAttributes.friendlyName`, with `DeleteConnector` as the row
action. An **Add Connection** `ContextPane` of type `DataConnectorsContextPane`
contains the connection form in its own `instructionSteps`; it replaces the
single-connection toggle.

The required `friendlyName` parameter is the connection alias. The workspace
resource ID, connector definition, and alias determine a stable suffix used for
the connector, metadata, notification/dead-letter queues, event subscription,
and data-flow deployment. Use a different alias for each connection and keep it
unchanged on retries. This isolates connections even when they use the same
storage account or different containers/folders within it. Overlapping source
filters can cause duplicate ingestion.

The connector request includes `StorageAccountSubscriptionId` and
`StorageAccountResourceGroupName` as well as its queue URLs, allowing the storage
account to be in a different subscription or resource group from the workspace.
The connector waits for the storage-side deployment to finish before creation.

### Managed-identity Event Grid delivery

The Event Grid system topic has a system-assigned identity. When supplying an
existing topic name, the deployment reads the topic, validates that its source
is the selected storage account, and preserves its location, source, topic
type, tags, attached user-assigned identities, and existing system-assigned
principal while enabling system-assigned identity.

There can be only one system topic per storage account. If a topic already
exists, including one created by an earlier connection, supply its exact name.
Leave the field empty only to create a topic; the generated topic name is
stable per storage account. Connections share the topic but have separate
event subscriptions and queues.

The `eventGridRbacMode` parameter supports:

- `CreateRoleAssignment` (default): grant **Storage Queue Data Message Sender**
  (`c6a89b2d-59bc-44d0-9896-0f6e12d7b80a`) to the topic's system-assigned
  identity at **storage-account scope**, then create the event subscription.
- `UseExistingRoleAssignment`: skip creating that sender grant. Use this only
  when the same system-assigned principal already has the required
  storage-account permission; permissions are not discovered or repaired.

Both modes configure `deliveryWithResourceIdentity` with `SystemAssigned` and
`EventGridSchema`. The event subscription waits for topic preparation and, in
Create mode, the sender-role deployment. It retains the container/folder
`Microsoft.Storage.BlobCreated` filter.

The Event Grid identity only sends queue messages. The separate first-party
collector retains **Storage Blob Data Contributor** on the selected container
and **Storage Queue Data Contributor** on each connection's queues. Collector
role-assignment names remain derived from normalized scope, tenant-local
principal ID, and role-definition ID. Deployments remain incremental; changing
an alias creates new connection resources rather than renaming or removing
previous ones.

The deployer needs resource deployment permissions and role-assignment write
permissions at the relevant storage scope. Register `Microsoft.EventGrid` in
the storage subscription. RBAC propagation may take up to ten minutes: for a
managed-identity authorization error, wait and retry with the same values
instead of recreating the topic or its identity.

This template does not change storage networking or Network Security Perimeter
configuration. Configure any required network access separately; see
[Enable network security](https://learn.microsoft.com/azure/sentinel/enable-storage-network-security).

## Next steps

Currently in preview, you can also publish your data connector as a Microsoft Sentinel solution. 

Microsoft Sentinel solutions provide an in-product experience for central discoverability, single-step deployment, and enablement of end-to-end product and/or domain and/or vertical scenarios in Microsoft Sentinel. For example, use solutions to deliver your data connector packaged with related analytics rules, workbooks, playbooks, and more. 

**Tip**: If your solution is being published to the content hub, also open a PR to have it listed in our [content hub catalog](https://docs.microsoft.com/azure/sentinel/sentinel-solutions-catalog). On the docs page, click Edit to open your PR.

For more information, see the [Microsoft Sentinel solution overview](https://docs.microsoft.com/azure/sentinel/sentinel-solutions) and our [Guide to Building Microsoft Sentinel Solutions](https://github.com/Azure/Azure-Sentinel/tree/master/Solutions#readme).
