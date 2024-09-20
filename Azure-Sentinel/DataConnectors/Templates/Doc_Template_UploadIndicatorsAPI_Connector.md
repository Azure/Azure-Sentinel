# Connect \<Provider Name\> Upload Indicators API to Microsoft Sentinel 

Partners (Providers) can use Connector_UploadIndicatorsAPI_template.json template to create a customized Upload Indicators API data connector for partners' solution.

Please replace the following placeholders in the template:
- DATA CONNECTOR ID: The id of the data connector. It will be used to differential with other data connectors.
- DATA CONNECTOR TITLE: The title of the data connector which will be shown in UI.
- PROVIDER NAME: Name of the partners. This will be used as the publisher of the data connector
- PROVIDER SOURCE SYSTEM NAME: The source system of the indicators sent to Microsoft Sentinel.

On top of the placeholders, partners can customize the instruction steps. For more information about Codeless Data Connector, please visit this page: https://learn.microsoft.com/azure/sentinel/create-codeless-connector?tabs=deploy-via-arm-template%2Cconnect-via-the-azure-portal
