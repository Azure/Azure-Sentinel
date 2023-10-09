# AS-Make-GitHub-Repository-Private

Author: Accelerynt

For any technical questions, please contact info@accelerynt.com  

[![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fportal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FPlaybooks%2FAS-Make-GitHub-Repository-Private%2Fazuredeploy.json)
[![Deploy to Azure Gov](https://aka.ms/deploytoazuregovbutton)](https://portal.azure.us/#create/Microsoft.Template/uri/https%3A%2F%2Fportal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FPlaybooks%2FAS-Make-GitHub-Repository-Private%2Fazuredeploy.json)       

This playbook is intended to be run from a Microsoft Sentinel Incident. It will look up the GitHub repositories associated with the Incident Account Entities and make them private. A comment noting the affected GitHub repositories will be added to the Incident.

![MakeGitHubRepoPrivate_Demo_1](Images/MakeGitHubRepoPrivate_Demo_1.png)

![MakeGitHubRepoPrivate_Demo_2](Images/MakeGitHubRepoPrivate_Demo_2.png)

> **Note**
> Because there is currently no way to query GitHub repositories by name, this playbook loops through all GitHub repositories looking for a match. GitHub API responses are limited to a maximum of 100 items, so if your GitHub Organization has more than 100 repositories, you will need to add additional logic to this playbook to handle pagination.

#
### Requirements
                                                                                                                            
The following items are required under the template settings during deployment: 

* A [GitHub App](https://github.com/Azure/Azure-Sentinel/tree/master/Playbooks/AS-Make-GitHub-Repository-Private#install-the-github-app) with permissions to read and write on Administration for repositories in your GitHub Organization
* The [GitHub App Installation ID](https://github.com/Azure/Azure-Sentinel/tree/master/Playbooks/AS-Make-GitHub-Repository-Private#install-the-github-app)
* An [Encoded Private Key](https://github.com/Azure/Azure-Sentinel/tree/master/Playbooks/AS-Make-GitHub-Repository-Private#encode-the-private-key-for-storage-compatibility-in-azure-key-vault) for the GitHub App
* An [Azure Key Vault Secret](https://github.com/Azure/Azure-Sentinel/tree/master/Playbooks/AS-Make-GitHub-Repository-Private#create-an-azure-key-vault-secret) containing your encoded private key
* Install [Visual Studio Code](https://github.com/Azure/Azure-Sentinel/tree/master/Playbooks/AS-Make-GitHub-Repository-Private#configure-visual-studio-code) and configure it to deploy an Azure Function to your Azure tenant
* An [Azure Function App](https://github.com/Azure/Azure-Sentinel/tree/master/Playbooks/AS-Make-GitHub-Repository-Private#deploy-the-azure-function-app) that supports Node.js to deploy an Azure function to


# 
### Setup
                                                                                                                             
#### Install the GitHub App:

A GitHub App with read and write permissions on Administration for repositories is needed in order to perform the required 'Update a repository' action on your GitHub Organization's behalf. Accelerynt has developed a GitHub App with the aforementioned access, which you can install in your GitHub Organization.

Sign into a GitHub account that has owner access to your Organization, then navigate to the following page:

https://github.com/apps/as-update-github-repository

From there, click "**Install App**".

![MakeGitHubRepoPrivate_Install_GitHub_App_1](Images/MakeGitHubRepoPrivate_Install_GitHub_App_1.png)

Once the App has been installed, navigate to https://github.com/organizations/{YOUR_ORGANIZATION}/settings/apps/as-update-github-repository and take note of the App ID in the "**General**" section, as it will be needed for deployment.

The GitHub App installation ID will also be needed for deployment, and this is different than the App ID mentioned above. Once the App has been installed, navigate to the "**Install App**" tab on the left menu blade of the App settings. From there, you should see your Organization listed as installed. Click the gear icon, which will take you to the App installation settings page.

![MakeGitHubRepoPrivate_Install_GitHub_App_2](Images/MakeGitHubRepoPrivate_Install_GitHub_App_2.png)

Your App installation ID can be found in the URL of this page, as indicated.

![MakeGitHubRepoPrivate_Install_GitHub_App_3](Images/MakeGitHubRepoPrivate_Install_GitHub_App_3.png)

This GitHub App will need to authenticate as an installation using a private key. Once the App has been installed, navigate to the "**General**" tab on the left menu blade of the App settings and scroll down to the "**Private keys**" section. Click "**Generate a private key**".

![MakeGitHubRepoPrivate_Install_GitHub_App_4](Images/MakeGitHubRepoPrivate_Install_GitHub_App_4.png)

This will generate a new private key and the file will be downloaded automatically. This file will be needed in the next step.


#### Encode the Private Key for Storage Compatibility in Azure Key Vault:

To safeguard the GitHub private key, this playbook employs Azure Key Vault for its secure storage and access, preventing direct storage in the playbook itself. Azure Key Vault, a cloud service, is a secure repository for confidential data such as keys, passwords, and certificates. Storing the key directly in the script or application code can expose it, whereas Azure Key Vault mitigates this risk through centralized key management. The private key is stored as an Azure Key Vault Secret, as it's compatible with Logic App's current ability to only fetch Key Vault Secret values.

Line breaks within private key files can disrupt their storage in a key vault or a similar service. To prevent this, the private key file needs to be encoded into a single line of text. Use the PowerShell script "**Encode-Private-Key.ps1**", found in the repository's Encode-Private-Key folder, to conveniently select and encode your private key file for Azure Key Vault Secret storage compatibility.

![MakeGitHubRepoPrivate_Encode_Private_Key_1](Images/MakeGitHubRepoPrivate_Encode_Private_Key_1.png)


#### Create an Azure Key Vault Secret:

Navigate to the Azure Key Vaults page: https://portal.azure.com/#view/HubsExtension/BrowseResource/resourceType/Microsoft.KeyVault%2Fvaults

Navigate to an existing Key Vault or create a new one. From the Key Vault overview page, click the "**Secrets**" menu option, found under the "**Settings**" section. Click "**Generate/Import**".

![MakeGitHubRepoPrivate_Key_Vault_Create_Secret_1](Images/MakeGitHubRepoPrivate_Key_Vault_Create_Secret_1.png)

Choose a name for the secret, such as "**GitHub-App-Private-Key--Update-Repository**", and enter the encoded GitHub private key value copied from the [previous step](https://github.com/Azure/Azure-Sentinel/tree/master/Playbooks/AS-Make-GitHub-Repository-Private#encode-the-private-key-for-storage-compatibility-in-azure-key-vault) in the "**Value**" field. All other settings can be left as is. Click "**Create**". 

![MakeGitHubRepoPrivate_Key_Vault_Create_Secret_2](Images/MakeGitHubRepoPrivate_Key_Vault_Create_Secret_2.png)

Once your secret has been added to the vault, navigate to the "**Access policies**" menu option on the Key Vault page menu. Leave this page open, as you will need to return to it once the playbook has been deployed. See [Granting Access to Azure Key Vault](https://github.com/Azure/Azure-Sentinel/tree/master/Playbooks/AS-Make-GitHub-Repository-Private#granting-access-to-azure-key-vault).

![MakeGitHubRepoPrivate_Key_Vault_Create_Secret_3](Images/MakeGitHubRepoPrivate_Key_Vault_Create_Secret_3.png)


#### Configure Visual Studio Code:

This playbook utilizes an Azure Function to create a JSON Web Token (JWT), which is a required step in authenticating to GitHub as an application. This function can be reused for all API calls from Microsoft to GitHub, so if this step has already been completed during the deployment of another one of Accelerynt's GitHub playbooks, it can be skipped along with the [Deploy the Azure Function App](https://github.com/Azure/Azure-Sentinel/tree/master/Playbooks/AS-Make-GitHub-Repository-Private#deploy-the-azure-function-app) step. Otherwise, the Azure Function included in this repository will need to be deployed to your Azure tenant before it can be used. This Azure Function relies on the Node.js libraries "**jsonwebtoken**" and "**date-fns**". These libraries are not included in Node.js by default, which is why they must be installed in an IDE housing the CreateJWT project and then deployed to Azure.

> **Note**
> Simply recreating the file structure from this repository in Azure will not actually install the libraries required for the Azure Function; the function must be deployed from an IDE, so that the dependent library packages are recreated and properly installed. Any IDE can be used for this, but this documentation will outline the process using Visual Studio Code (VS Code).

If you have not already, download and install VS Code from the official website: https://code.visualstudio.com/download

Once VS Code has been installed, open it, and navigate to the Extensions view by clicking on the Extensions icon on the left menu blade. 

![MakeGitHubRepoPrivate_Configure_VSCode_1](Images/MakeGitHubRepoPrivate_Configure_VSCode_1.png)

In the Extensions view, search for the following extensions and install them:
* **Azure Account**: This extension provides a single Azure login and subscription filtering experience for all other Azure extensions. It makes Azure's Cloud Shell service available in VS Code's integrated terminal.
* **Azure Functions**: This extension helps in creating, testing, and deploying Azure Functions directly from VS Code. This includes the creation of new Function Apps within your Azure account.

![MakeGitHubRepoPrivate_Configure_VSCode_2](Images/MakeGitHubRepoPrivate_Configure_VSCode_2.png)

After the extensions have been installed, sign in to your Azure Account. Click on the Azure icon that now appears in the Activity Bar. Under the "**Resources**" section, click "**Sign in to Azure...**". 

![MakeGitHubRepoPrivate_Configure_VSCode_3](Images/MakeGitHubRepoPrivate_Configure_VSCode_3.png)

You will be prompted to sign into your account via web browser. Follow the prompts and use your Azure credentials to log in.

![MakeGitHubRepoPrivate_Configure_VSCode_4](Images/MakeGitHubRepoPrivate_Configure_VSCode_4.png)

Once you have successfully authenticated, your Azure email will be displayed in the bottom left corner of the VS Code window.

Next, you will need to create an Azure Function project using the code included in this GitHub repo. Create a folder on your computer for the Azure Function to be housed and label it "**CreateJWT**". Next, in VS Code, hover your mouse over the "**Workspace**" section in the Azure pane on the left. Click the "**Create Function**" icon. Select the "**CreateJWT**" folder you just created from the open dialogue window.

![MakeGitHubRepoPrivate_Configure_VSCode_5](Images/MakeGitHubRepoPrivate_Configure_VSCode_5.png)

From the command palette in the tope-center area of the window, select "**JavaScript**" as the programming language, then select "**Model V3**" for your JavaScript programming model.

![MakeGitHubRepoPrivate_Configure_VSCode_6](Images/MakeGitHubRepoPrivate_Configure_VSCode_6.png)

Select "**HTTP trigger**" for the project's function and enter "**CreateJWT**" for the function name.

![MakeGitHubRepoPrivate_Configure_VSCode_7](Images/MakeGitHubRepoPrivate_Configure_VSCode_7.png)

Select "**Function**" for the Authorization level, then after selecting the window to open your project in and granting trust, you will be able to view the "**CreateJWT**" project in the explorer pane of the left side of the window. The "**index.js**" file should be opened by default.

![MakeGitHubRepoPrivate_Configure_VSCode_8](Images/MakeGitHubRepoPrivate_Configure_VSCode_8.png)

>**Note**
> If you decide to use a different name for the function, you will need to do a -Find + Replace All- for "**CreateJWT**" in the azuredeploy.json file before deployment.

Replace the contents of "**index.js**" in VS Code with the contents of "**CreateJWT.js**" located in the CreateJWT-Function folder of this repository.

![MakeGitHubRepoPrivate_Configure_VSCode_9](Images/MakeGitHubRepoPrivate_Configure_VSCode_9.png)

Finally, the Node.js packages used in index.js need to be installed. Download and install the latest versions of Node.js and npm from the official website: https://nodejs.org/en/download

Next, in VS Code, click "**Terminal**" from the top menu and select "**New Terminal**".

![MakeGitHubRepoPrivate_Configure_VSCode_10](Images/MakeGitHubRepoPrivate_Configure_VSCode_10.png)

In the terminal window, run the commands "**node -v**" and "**npm -v**" to verify that the latest versions were properly installed.

Next, run the commands "**npm install jsonwebtoken**" and "**npm install date-fns**". The packages will be automatically added to the dependencies in the "**package.json**" file once they have been successfully installed.

![MakeGitHubRepoPrivate_Configure_VSCode_11](Images/MakeGitHubRepoPrivate_Configure_VSCode_11.png)

After installing the required packages, the Azure Function can be deployed.


#### Deploy the Azure Function App:

In order to deploy an Azure Function, there must be an existing Azure Function App supporting the language used in the Azure function. If there is an existing Function App that supports Node.js in your Azure tenant, you can skip the first part of this step. Otherwise, you need to create a new Function App in your Azure tenant before deploying your Function.

Click on the Azure icon in the left side Activity Bar in VS Code. Select the resource you will deploy this playbook to, and then right click on "**Azure Function**" and select "**Create Function App in Azure...**".

![MakeGitHubRepoPrivate_Deploy_Azure_Function_1](Images/MakeGitHubRepoPrivate_Deploy_Azure_Function_1.png)

VS Code will guide you through the process. You will need to provide a globally unique name for your Function App, select a runtime, and choose an operating system. When asked for the runtime, select the latest available runtime for Node.js.

![MakeGitHubRepoPrivate_Deploy_Azure_Function_2](Images/MakeGitHubRepoPrivate_Deploy_Azure_Function_2.png)

The Azure Function can now be deployed to the Azure Function App from VS Code. 

Click back to the Explorer icon in the left side Activity Bar and right-click inside your project folder, then select "**Deploy to Function App...**". 

![MakeGitHubRepoPrivate_Deploy_Azure_Function_3](Images/MakeGitHubRepoPrivate_Deploy_Azure_Function_3.png)

Follow the prompts to choose your subscription and the Function App to which you want to deploy to. Take note of the name of the Function App, as it will be needed for deployment.

Once the deployment is complete, the Function can be accessed from your Azure tenant by the playbook. You can view your Function by navigating to https://portal.azure.com/#view/HubsExtension/BrowseResource/resourceType/Microsoft.Web%2Fsites/kind/functionapp and selecting the Function App your Function was deployed to.

![MakeGitHubRepoPrivate_Deploy_Azure_Function_4](Images/MakeGitHubRepoPrivate_Deploy_Azure_Function_4.png)


#
### Deployment                                                                                                         
                                                                                                        
To configure and deploy this playbook:
 
Open your browser and ensure you are logged into your Microsoft Sentinel workspace. In a separate tab, open the link to our playbook on the Accelerynt Security GitHub Repository:

https://github.com/Accelerynt-Security/AS-Make-GitHub-Repository-Private

[![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fportal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FPlaybooks%2FAS-Make-GitHub-Repository-Private%2Fazuredeploy.json)
[![Deploy to Azure Gov](https://aka.ms/deploytoazuregovbutton)](https://portal.azure.us/#create/Microsoft.Template/uri/https%3A%2F%2Fportal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FPlaybooks%2FAS-Make-GitHub-Repository-Private%2Fazuredeploy.json)                                             

Click the "**Deploy to Azure**" button at the bottom and it will bring you to the custom deployment template.

In the **Project Details** section:

* Select the "**Subscription**" and "**Resource Group**" from the dropdown boxes you would like the playbook deployed to.  

In the **Instance Details** section:   

* **Playbook Name**: This can be left as "**AS-Make-GitHub-Repository-Private**" or you may change it.

* **GitHub Organization Name**: Enter the name of your GitHub Organization

* **GitHub App ID**: Enter the name of your GitHub App ID noted in [Install the GitHub App](https://github.com/Azure/Azure-Sentinel/tree/master/Playbooks/AS-Make-GitHub-Repository-Private#install-the-github-app)

* **GitHub App Installation ID**: Enter the name of your GitHub App Installation ID noted in [Install the GitHub App](https://github.com/Azure/Azure-Sentinel/tree/master/Playbooks/AS-Make-GitHub-Repository-Private#install-the-github-app)

* **Function App Name**: Enter the name of your Azure Function App noted in [Deploy the Azure Function App](https://github.com/Azure/Azure-Sentinel/tree/master/Playbooks/AS-Make-GitHub-Repository-Private#deploy-the-azure-function-app)

* **Key Vault Name**: Enter the name of the Key Vault referenced in [Create an Azure Key Vault Secret](https://github.com/Azure/Azure-Sentinel/tree/master/Playbooks/AS-Make-GitHub-Repository-Private#create-an-azure-key-vault-secret).

* **Secret Name**: Enter the name of the Key Vault Secret created in [Create an Azure Key Vault Secret](https://github.com/Azure/Azure-Sentinel/tree/master/Playbooks/AS-Make-GitHub-Repository-Private#create-an-azure-key-vault-secret).

Towards the bottom, click on "**Review + create**". 

![MakeGitHubRepoPrivate_Deploy_1](Images/MakeGitHubRepoPrivate_Deploy_1.png)

Once the resources have validated, click on "**Create**".

![MakeGitHubRepoPrivate_Deploy_2](Images/MakeGitHubRepoPrivate_Deploy_2.png)

The resources should take around a minute to deploy. Once the deployment is complete, you can expand the "**Deployment details**" section to view them.
Click the one corresponding to the Logic App.

![MakeGitHubRepoPrivate_Deploy_3](Images/MakeGitHubRepoPrivate_Deploy_3.png)


#
### Granting Access to Azure Key Vault

Before the Logic App can run successfully, the Key Vault connection created during deployment must be granted access to the Key Vault Secret storing your GitHub private key.

From the Key Vault "**Access policies**" page, click "**Create**".

![MakeGitHubRepoPrivate_Key_Vault_Access_1](Images/MakeGitHubRepoPrivate_Key_Vault_Access_1.png)

Select the "**Get**" checkbox in the "**Secret permissions**" section. Then click "**Next**".

![MakeGitHubRepoPrivate_Key_Vault_Access_2](Images/MakeGitHubRepoPrivate_Key_Vault_Access_2.png)

From the "**Principal**" page, paste "**AS-Make-GitHub-Repository-Private**", or the alternative playbook name you used, into the search box and click the option that appears. Click "**Next**".

![MakeGitHubRepoPrivate_Key_Vault_Access_3](Images/MakeGitHubRepoPrivate_Key_Vault_Access_3.png)

Click "**Next**" in the application section. Then from the "**Review + create**" page, click "**Create**".

![MakeGitHubRepoPrivate_Key_Vault_Access_4](Images/MakeGitHubRepoPrivate_Key_Vault_Access_4.png)


#
### Microsoft Sentinel Contributor Role

After deployment, you will need to give the system assigned managed identity the "**Microsoft Sentinel Contributor**" role. This will enable the Logic App to add comments to Incidents. Navigate to the Log Analytics Workspaces page and select the same workspace the playbook is located in:

https://portal.azure.com/#view/HubsExtension/BrowseResource/resourceType/Microsoft.OperationalInsights%2Fworkspaces

Select the "**Access control (IAM)**" option from the menu blade, then click "**Add role assignment**".

![MakeGitHubRepoPrivate_Add_Contributor_Role_1](Images/MakeGitHubRepoPrivate_Add_Contributor_Role_1.png)

Select the "**Microsoft Sentinel Contributor**" role, then click "**Next**".

![MakeGitHubRepoPrivate_Add_Contributor_Role_2](Images/MakeGitHubRepoPrivate_Add_Contributor_Role_2.png)

Select the "**Managed identity**" option, then click "**Select Members**". Under the subscription the Logic App is located, set the value of "**Managed identity**" to "**Logic app**". Next, enter "**AS-Make-GitHub-Repository-Private**", or the alternative playbook name used during deployment, in the field labeled "**Select**". Select the playbook, then click "**Select**".

![MakeGitHubRepoPrivate_Add_Contributor_Role_3](Images/MakeGitHubRepoPrivate_Add_Contributor_Role_3.png)

Continue on to the "**Review + assign**" tab and click "**Review + assign**".

![MakeGitHubRepoPrivate_Add_Contributor_Role_4](Images/MakeGitHubRepoPrivate_Add_Contributor_Role_4.png)


#
### Updating Node.js Packages for Azure Functions

As part of maintaining a robust and secure application, it's essential to regularly update the Node.js packages that your Azure Function relies on. There are several reasons for this:

* **Security Fixes**: Developers frequently release updates to their packages to address discovered vulnerabilities. Keeping your packages up to date ensures you benefit from these fixes and reduces your application's risk exposure.

* **Bug Fixes and Improved Functionality**: Updates often contain bug fixes or enhancements to functionality, stability, and performance. Regularly updating packages can provide your application with these benefits.

* **Compatibility**: If you're updating your Node.js runtime or other packages, you need to keep all packages updated to ensure compatibility and prevent breaking changes.

As a general guideline, you should review and test for updates at least once per month. More frequent checks can be performed if your function has higher security requirements or is particularly sensitive to bugs in the underlying packages. Automated tools exist to help manage these updates.

You can update the dependent libraries for your Azure Function in VS Code by executing the commands "**npm update date-fns**" and "**npm update jsonwebtoken**" within your "**CreateJWT**" project directory in the integrated terminal. Redeploy the Function to Azure afterwards.