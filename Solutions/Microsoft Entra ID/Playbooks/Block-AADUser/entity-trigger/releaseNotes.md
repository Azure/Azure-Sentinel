### 1.1 Added manager notification action

-   Added action to check if the user has a manager assigned in the Microsoft Entra ID and notify the manager that the user is disabled<br>
    <strong>Note: Additional permissions must be assigned to the managed identity - Grant User.Read.All, User.ReadWrite.All, Directory.Read.All, Directory.ReadWrite.All. Full instructions available on https://github.com/Azure/Azure-Sentinel/tree/master/Playbooks/Block-AADUser</strong>
-   Update to readme file - stating what API permissions are needed to be assigned to the managed identity as well as updating info that this playbook is not supporting block of the admin users in Microsoft Entra ID

### 1.0

-   Initial version