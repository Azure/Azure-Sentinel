# Get-MDATPVulnerabilities
author: Wayne Lee

This playbook will retrieve the list of vulnerabilities from the Microsoft Defender ATP API for the host entity

## Setup

### 1. Create an Azure AD App from Azure AD App Registrations

### 2. Configure the App API Permissions

   * Enable Machine.Read.All and Vulnerability.Read.All permissions from the WindowsDefenderATP API

### 3. Generate a secret and store it
	
### 4. Deploy ARM template
	
### 5. Upload the Word template to your preferred Sharepoint library
	
### 6. Edit Playbook Configure connectors

   * Ensure all functions have been configured with their appropriate connectors

      * Azure Sentinel
	   * Azure Key Vault (Be sure to also select the secret for the App ID we created)
	   * Microsoft Defender ATP
	   * Sharepoint Online
      * Word Online
   

   * Setup HTTP connector

	   * Provide the client/app ID of the app you registered.
      * If you are an MSSP and need to configure the tenant ID, just go under the Parameters section of the playbook and change the default value of tenantId
	
### 7. Populate Microsoft Word Template

   * Set the Location and Document Library of where you stored the Word template. The VulnDetails parameter should automatically be populated with vulnarray.
	
### 8. Create WordDoc on Sharepoint 

   * Set the Site Address and Folder Path. Filename is named after current UTC time followed by the hostname.
	
### 9. Convert Word doc to PDF 

   * Set the Location and Document Library of where the Word file is stored. If you have stored it in the standard Documents library, the expression in File should be able to dynamically retrieve it.
	
### 10. Create PDF

   * Set the Site Address and Folder Path to export the PDF. Filename has been configured to use the same format as the Word doc
	
### 11. Create link to PDF
	
   * Set Site address and Library name. The default sharing permissions are limited to the people in your organization, with View-only access.
	
### Optional  - Customizing comment field

   * You can customize the comment field under Add comment to incident (V2) to include more details
