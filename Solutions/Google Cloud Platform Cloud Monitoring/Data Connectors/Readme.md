#  Create OAuth 2.0 Credentials in Google Cloud for Microsoft Sentinel
 
This guide helps create the required **Client ID** and **Client Secret** in **Google Cloud Platform (GCP)** so logs can be securely sent to **Microsoft Sentinel** .
 

 
##  Prerequisites

- Access to **Google Cloud Console** at [https://console.cloud.google.com/](https://console.cloud.google.com/)
- Access to your organization's **Google Cloud Project**
 

 
 
##  Step-by-Step Instructions
 
### Step 1: Log In to Google Cloud Console
 
- Go to: [https://console.cloud.google.com/](https://console.cloud.google.com/)
- Sign in using your Google account.
- Choose the project (top menu bar).
 
 ### Step 2: Enable Required Services (APIs)
 
1. Go to: [https://console.cloud.google.com/apis/library](https://console.cloud.google.com/apis/library)
2. From the search box select below services and enable them respectively:
   - **Cloud Monitoring API**
   - **Cloud Logging API**
   - **IAM API**
 
### Step 3: Create OAuth 2.0 Credentials
 
1. Go to: [https://console.cloud.google.com/apis/credentials](https://console.cloud.google.com/apis/credentials)
2. Click **"Create Credentials"** → choose **"OAuth client ID"**
3. Choose **"Web application"** as the type
4. Give it a name: `Sentinel OAuth`
5. Scroll to **Authorized redirect URIs** and paste this link:"https://portal.azure.com/TokenAuthorize/ExtensionName/Microsoft_Azure_Security_Insights"
6. Click **"Create"**
   
### Step 4: Save the Credentials
 
After creation, you’ll see:
- A **Client ID**
- A **Client Secret**
 
 Copy both values and **save them securely**. You’ll need them for Microsoft Sentinel.
 
You can also click **"Download JSON"** to save them in a file.
 
### Step 5: Connecting Google Cloud Monitoring to Microsoft Sentinel

- Use the **Client ID** and **Client Secret** you just created.
- This will allow Sentinel to access the logs securely.
 
