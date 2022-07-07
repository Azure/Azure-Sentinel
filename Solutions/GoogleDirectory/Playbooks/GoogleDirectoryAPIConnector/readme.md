# Google Directory Logic Apps Custom connector

<img src="./google_logo.svg" alt="drawing" width="20%"/><br>

This custom connector connects to [Google Directory Users API](https://developers.google.com/admin-sdk/directory/reference/rest/v1/users).

### Authentication methods this connector supports

*  OAuth2.0 authentication

### Configurations steps
1. Deploy the connector using **Deploy to Azure** button.
2. Create authorization credentials (see [instructions](https://developers.google.com/identity/protocols/oauth2/web-server#creatingcred)). As a redirection url, use the redirection url that you can find on the connector page (in Azure go to **Logic Apps Custom Connector** -> **GoogleDirectory** -> click **Edit** -> **Security** -> copy *Redirect URL*). If this is your first time creating a client ID, you can also configure your consent screen by clicking Consent Screen. (The [following procedure](https://support.google.com/cloud/answer/6158849?hl=en#userconsent) explains how to set up the Consent screen.) You won't be prompted to configure the consent screen after you do it the first time. Note that the scope `https://www.googleapis.com/auth/admin.directory.user` has to be enabled in the consent screen.
3. In Azure go to **Logic Apps Custom Connector** -> **GoogleDirectory** -> click **Edit** -> **Security** -> fill the *Client id* and *Client secret*, obtained in the previous step -> click **Update connector**.




## Actions supported by the connector

The connector supports all the actions of [Google Directory Users API](https://developers.google.com/admin-sdk/directory/reference/rest/v1/users).



### Deployment instructions 
1. Deploy the Custom Connector by clicking on "Deploy to Azure" button. This will take you to deplyoing an ARM Template wizard.

[![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FSolutions%2FGoogleDirectoryIAM%2FPlaybooks%2FGoogleDirectoryAPIConnector%2Fazuredeploy.json) [![Deploy to Azure](https://aka.ms/deploytoazuregovbutton)](https://portal.azure.us/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FSolutions%2FGoogleDirectory%2FPlaybooks%2FGoogleDirectoryAPIConnector%2Fazuredeploy.json)
