# ZoomReports

## Solution Information

| Attribute | Value |
|:------------------------|:------|
| **Publisher** | Microsoft Corporation |
| **Support Tier** | Microsoft |
| **Support Link** | [https://support.microsoft.com/](https://support.microsoft.com/) |
| **Categories** | domains |
| **First Published** | 2022-05-23 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/ZoomReports](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/ZoomReports) |

## Data Connectors

This solution provides **1 data connector(s)**:

- [Zoom Reports](../connectors/zoom.md)

## Tables Reference

This solution uses **1 table(s)**:

| Table | Used By Connectors | Used By Content |
|-------|-------------------|----------------|
| [`Zoom_CL`](../tables/zoom-cl.md) | [Zoom Reports](../connectors/zoom.md) | Workbooks |

## Content Items

This solution includes **2 content item(s)**:

| Content Type | Count |
|:-------------|:------|
| Workbooks | 1 |
| Parsers | 1 |

### Workbooks

| Name | Tables Used |
|:-----|:------------|
| [ZoomReports](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/ZoomReports/Workbooks/ZoomReports.json) | [`Zoom_CL`](../tables/zoom-cl.md) |

### Parsers

| Name | Description | Tables Used |
|:-----|:------------|:------------|
| [Zoom](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/ZoomReports/Parsers/Zoom.yaml) | - | - |

## Additional Documentation

> 📄 *Source: [ZoomReports/README.md](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/ZoomReports/README.md)*

# Deploy a Function App for collecting Zoom data into Azure Sentinel
This function app will be used to get the zoom reports.

## Configure your Zoom API app.
You also need to configure your Zoom account. To do this go to https://marketplace.zoom.us/ and log in with a user who has admin access to your Zoom account i.e. by signin to zoom with your credentials i.e. username/password & zoom verfication code.
1. Select ‘Develop’ in the top right hand corner and click ‘Build App’.
2. Select ‘Server to Server Oauth App’ as your app type.
3. Give your app a name.
4. Fill out the required Basic Information and click continue.
5. App credentials: View your account ID, client ID and client secret. You'll use these credentials to authenticate with Zoom.so copy these credentials
6. Under the Feature Tab enable the ‘Event Subscriptions’ toggle ,Please make sure to disble it.
7. Scopes: Choose Add Scopes to search for and add all scope for  Report, Marketplace, Billing, Meeting and User.
8. Activation: Your app should be activated. If you see errors that prevent activation, please address them. You will not be able to generate an access token to make API calls unless your app is activated.

Once you have done the above steps
1. Get the App credentials from step 5 i.e. account ID, client ID and client secret use it in during deployment.

If you run into issues while creating for [Server to Server Oauth App](https://developers.zoom.us/docs/internal-apps/create/) .

## Release Notes

| **Version** | **Date Modified (DD-MM-YYYY)** | **Change History**                          |
|-------------|--------------------------------|---------------------------------------------|
| 3.0.5       | 29-08-2024                     | Updated the python runtime version to 3.11  | 
| 3.0.4       | 26-04-2024                     | Repackaged for fix on parser in maintemplate to have old parsername and parentid                    |
| 3.0.3       | 18-04-2024                     | Repackaged for fix on parser in maintemplate                    |
| 3.0.2       | 10-04-2024                     | Added Azure Deploy button for government portal deployments                    |
| 3.0.1       | 04-12-2023                     | Authentication changes for zoom reports with server to server **Oauth app**     | 
| 3.0.0       | 04-07-2023                     | Fixed broken links for **Data Connector** & Added **Workbook** in Solution content      |

---

**Browse:**

- [← Back to Solutions Index](../solutions-index.md)
- [Connectors Index](../connectors-index.md)
- [Tables Index](../tables-index.md)
