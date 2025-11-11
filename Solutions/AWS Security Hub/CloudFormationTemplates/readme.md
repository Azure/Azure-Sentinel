# AWS Security Hub Findings Data Connector

This guide provides instructions for configuring the AWS Security Hub Findings Data Connector to ingest data into Microsoft Sentinel.

## Prerequisites

Before configuring the connector, ensure the following:

1. You have an active AWS account with permissions to create resources using CloudFormation.
2. You have access to Microsoft Sentinel with appropriate permissions.

## Deployment Steps

### Step 1: Deploy CloudFormation Templates

1. Download the CloudFormation templates from this folder:
   - [OIDCWebIdProvider.json](OIDCWebIdProvider.json)
   - [SecurityHubResourcesAndConfig.json](SecurityHubResourcesAndConfig.json)

2. Navigate to the [AWS CloudFormation Stacks](https://console.aws.amazon.com/cloudformation/home) page.

3. Deploy the templates in the following order:
   - **OIDCWebIdProvider.json**:
     - Click "Create stack".
     - Select "With new resources".
     - Choose "Upload a template file" and upload the `OIDCWebIdProvider.json` file.
     - Follow the prompts to create the stack.
   - **SecurityHubResourcesAndConfig.json**:
     - Click "Create stack".
     - Select "With new resources".
     - Choose "Upload a template file" and upload the `SecurityHubResourcesAndConfig.json` file.
     - Follow the prompts to create the stack.

4. After the stacks are created, note the following outputs:
   - **Role ARN**
   - **SQS Queue URL**

### Step 2: Configure the Connector in Microsoft Sentinel

1. Open Microsoft Sentinel and go to the **Data Connectors** page.

2. Search for and select the **AWS Security Hub Findings** connector.

3. Click **Add new collector** and provide the following details:
   - **Role ARN**: Enter the Role ARN from the CloudFormation stack output.
   - **Queue URL**: Enter the SQS Queue URL from the CloudFormation stack output.

4. Click **Connect** to enable the connector.

## Additional Information

- For more details on connecting data sources, refer to the [Microsoft Sentinel documentation](https://docs.microsoft.com/azure/sentinel/connect-data-sources).
- For troubleshooting or support, contact [Microsoft Support](https://support.microsoft.com).