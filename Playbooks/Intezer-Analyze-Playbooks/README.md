# Integrating Microsoft Sentinel with Intezer

This guide outlines the integration between Microsoft Sentinel and [Intezer](https://intezer.com/). 

Intezer automatically monitors, investigates, and triages security alerts 24/7 for your team. Using automated analysis, smart recommendations, and auto-remediation, it saves your team from time wasted on false positives, repetitive analysis tasks, and an excess of escalated alerts. Integrating with Microsoft Sentinel can further enhance your security operations and efficiency.

In this repository, you'll find playbooks to guide you through the integration process.

For assistance, please contact Intezer's support team at [support@intezer.com](mailto:support@intezer.com).

## Playbook Descriptions

### Playbook 1: Update Incident - Intezer Alert Webhook
**Trigger:** HTTP request after Intezer finishes processing an alert.

Assuming you've [connected Microsoft Defender to Intezer](https://support.intezer.com/hc/en-us/articles/7431169050652), this playbook triggers whenever Intezer completes alert processing. It appends a context-specific comment to the corresponding incident in Microsoft Sentinel, linking insights from Intezer.

### Playbook 2: Submit Intezer Alert - Incident Triggered
**Trigger:** Creation of a new incident in Microsoft Sentinel.

This playbook forwards the details of a new Microsoft Sentinel incident, including associated file hashes and network artifacts, to Intezer for analysis and processing.

### Playbook 3: Submit Intezer Scan File Hash - Incident Triggered
**Trigger:** Creation of a new incident in Microsoft Sentinel.

This playbook extracts file hashes from the Microsoft Sentinel incident, then forwards them to Intezer for in-depth analysis. A comment containing Intezer's verdict is appended back to the incident, ensuring that all relevant information is accessible in one place.

### Playbook 4: Submit Intezer Scan URL - Incident Triggered
**Trigger:** Creation of a new incident in Microsoft Sentinel.

This playbook extracts associated URLs from the Microsoft Sentinel incident, then forwards them to Intezer for in-depth analysis. A comment containing Intezer's verdict is appended back to the incident, ensuring that all relevant information is accessible in one place.

## Quick Deployment
> **_Important note:_**  Please note that deploying requires manual setup before and after, including prerequisites and postrequisites. Ensure that the individual performing the deployment in the Azure environment has powerful permissions.

Before deploying, please review the [deployment prerequisites](#deployment-prerequisites).

[![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2Fintezer%2Fmicrosoft-sentinel-integration%2Fmain%2Fplaybooks%2Fazuredeploy.json)
<br/>
![Image Alt Text](.github/assets/images/sentinel-11.png)

After deployment, please review the [deployment postrequisites](#deployment-postrequisites).

### Deployment Prerequisites
1. Extracting Your Microsoft Sentinel Workspace Name and Workspace ID:
   - Navigate to **Microsoft Sentinel** in the Azure portal:  
     ![Image Alt Text](.github/assets/images/sentinel-1.png)
   - Select your Microsoft Sentinel workspace:  
     ![Image Alt Text](.github/assets/images/sentinel-2.png)
   - Go to **Settings**:  
     ![Image Alt Text](.github/assets/images/sentinel-3.png)
   - Select **Workspace Settings**:  
     ![Image Alt Text](.github/assets/images/sentinel-4.png)
   - Under the **Essentials** section, locate your workspace name and workspace ID. Keep this information for later use:  
     ![Image Alt Text](.github/assets/images/sentinel-5.png)

2. Setting Up Azure Vault for Holding Intezer API Key:
   - Go to **Key Vaults** in the Azure portal:  
     ![Image Alt Text](.github/assets/images/sentinel-6.png)
   - Create a new vault, choosing a unique name for the **Key Vault Name** and keeping it for later use:  
     ![Image Alt Text](.github/assets/images/sentinel-32.png)
     ![Image Alt Text](.github/assets/images/sentinel-33.png)
   - Access your created vault and create a new secret named **intezer-sentinel-api-key** to hold your Intezer API key:  
     ![Image Alt Text](.github/assets/images/sentinel-9.png)
     ![Image Alt Text](.github/assets/images/sentinel-10.png)

### Deployment Postrequisites
After submitting the custom deployment, you need to perform some actions in your Azure environment.

1. Activate playbooks by setting up Automation rules for logic app playbooks triggered by new incident creation in Microsoft Sentinel (Playbooks 2, 3, and 4)
   - Navigate to **Microsoft Sentinel** in the Azure portal:  
     ![Image Alt Text](.github/assets/images/sentinel-1.png)
   - Select your Microsoft Sentinel workspace:  
     ![Image Alt Text](.github/assets/images/sentinel-2.png)
   - On the left menubar, under Configuration, select **Automation**:<br/>
   ![Image Alt Text](.github/assets/images/sentinel-29.png)

   - Click **Create** and then **Automation rule**:<br/>
   ![Image Alt Text](.github/assets/images/sentinel-30.png)

   - Enter an **Automation rule name** and choose the **When incident is created** trigger. In the Actions section, choose **Run playbook** and select the playbook you want to activate, then click Save. Each automation rule is connected to one playbook, so if you want to activate more than one playbook, you will need to create an automation rule for each one of them.
   
      **Note:** You only need to configure the playbooks you want to use; you don't need to activate all three options if you don't need to.
   ![Image Alt Text](.github/assets/images/sentinel-31.png)

2. Grant Permissions to Microsoft Sentinel Created Playbooks:
   - Navigate to **Microsoft Sentinel** in the Azure portal:  
     ![Image Alt Text](.github/assets/images/sentinel-1.png)
   - Select your Microsoft Sentinel workspace:  
     ![Image Alt Text](.github/assets/images/sentinel-2.png)
   - Go to **Settings**:  
     ![Image Alt Text](.github/assets/images/sentinel-3.png)
   - Select **Workspace Settings**:  
     ![Image Alt Text](.github/assets/images/sentinel-4.png)
   - In the left menu, choose **Access Control (IAM)**:  
     ![Image Alt Text](.github/assets/images/sentinel-12.png)
   - Click **Add**, then **Add Role Assignment**:  
     ![Image Alt Text](.github/assets/images/sentinel-13.png)
   - Under the Role tab, in the Job Function Rules tab, search and select **Microsoft Sentinel Responder**, then click Next:  
     ![Image Alt Text](.github/assets/images/sentinel-14.png)
   - Click **+ Select Members** and add the four logic app playbooks created during the deployment process, then click **Review + Assign**:  
     ![Image Alt Text](.github/assets/images/sentinel-15.png)
     ![Image Alt Text](.github/assets/images/sentinel-16.png)

3. Grant Permissions to the Created Azure Vault:
   - During the prerequisites stage, you created an Azure vault that holds the "intezer-sentinel-api-key." After deploying logic app playbooks, ensure that the vault has permissions to read secrets during a run.
   - Go to **Key Vaults** in the Azure portal:  
     ![Image Alt Text](.github/assets/images/sentinel-6.png)
   - Select the vault you created in the prerequisites. Choose **Access policies**:  
     ![Image Alt Text](.github/assets/images/sentinel-34.png)
   - Click **Add Access Policy**, then press **Select all** under secret permissions:  
     ![Image Alt Text](.github/assets/images/sentinel-37.png)
     ![Image Alt Text](.github/assets/images/sentinel-35.png)
    - Choose each one of the created playbooks. Note that you can't choose all of the playbooks at once, so you need to do that process for each playbook you want to activate.
    ![Image Alt Text](.github/assets/images/sentinel-36.png)

4. (Relevant only for **Update Incident - Intezer Alert Webhook**) Enable the Monitor Logs API Connection:
   - Navigate to **Logic apps** in the Azure portal:  
     ![Image Alt Text](.github/assets/images/sentinel-25.png)

   - Search and select **UpdateIncident-IntezerAlert-Webhook** logic app:<br/>
     ![Image Alt Text](.github/assets/images/sentinel-26.png)

    - On the left menu bar, select **Logic app designer**:<br/>
     ![Image Alt Text](.github/assets/images/sentinel-27.png)

    - Click on the **Connections** step, the one with the warning:<br/>
    ![Image Alt Text](.github/assets/images/sentinel-38.png)

    - Click on **Add new**:<br/>
    ![Image Alt Text](.github/assets/images/sentinel-39.png)

    - Enter a generic connection name and click **Sign in**:<br/>
    ![Image Alt Text](.github/assets/images/sentinel-40.png)

    - After submitting the connection, click **Save** on the left menu:<br/>
    ![Image Alt Text](.github/assets/images/sentinel-41.png)

5. (Relevant only for **Update Incident - Intezer Alert Webhook**) - Register the HTTP trigger.
    - The logic app is fired using an HTTP request every time Intezer alert is done processing Microsoft Defender alert.
    The logic app generates a unique HTTP route for your playbook, which you need to provide to support@intezer.com to register the alerts traffic.

   - Navigate to **Logic apps** in the Azure portal:  
     ![Image Alt Text](.github/assets/images/sentinel-25.png)

   - Search and select **UpdateIncident-IntezerAlert-Webhook** logic app:<br/>
     ![Image Alt Text](.github/assets/images/sentinel-26.png)

    - On the left menu bar, select **Logic app designer**:<br/>
     ![Image Alt Text](.github/assets/images/sentinel-27.png)

    - Open the first stage **When a HTTP request is received** and copy the generated HTTP POST URL. You need to provide it to support@intezer.com:<br/>
     ![Image Alt Text](.github/assets/images/sentinel-28.png)
