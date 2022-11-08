# SyncMSServiceTags

#### Problem : 
Azure Service Tags gets updated every now and then which is a list of IP addresses for Azure / Microsoft Data centers.
All the existing references need to be changed based on this as the URL for json file depends upon date.
E.g. – ServiceTags_Public_20220307.json
#### Solution : 
A GitHub workflow to run every 14days to check the latest version of the list and updates to a json file.
This file can a be a single source of reference across.

![image](https://user-images.githubusercontent.com/20562985/157929116-1fbe4697-c988-4cec-bd42-05c512f045a0.png)

Applicable References :


|Analytic Rule|Hunting Query|Workbook|
|-------------|-------------|---------|
|Azure Portal Signin from another Azure Tenant|Sign-Ins from Azure External Tenant|Can be good use case for SignIn Activities|
