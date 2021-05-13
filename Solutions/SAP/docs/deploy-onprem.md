# Deploy the Azure Sentinel SAP logs connector on-premises

This article describes how to deploy the Azure Sentinel logs connector on an on-premises machine.

**Note**: If you're looking to deploy on Azure instead, see [Deploy the Azure Sentinel SAP logs connector on Azure](deploy-azure.md).

**Copyright (c) Microsoft Corporation**.  This preview software is Microsoft Confidential, and is subject to your Non-Disclosure Agreement with Microsoft.  You may use this preview software internally and only in accordance with the Azure preview terms, located at [Preview terms](https://azure.microsoft.com/support/legal/preview-supplemental-terms/).  Microsoft reserves all other rights.


## Deploy the SAP logs connector on-premises

Before you start, review the [Azure Sentinel SAP logs connector requirements](prereqs.md) to ensure that your system complies.

1. Download the latest SAP NW RFC SDK zip file from [SAPNWRFCSDK](https://launchpad.support.sap.com/#/softwarecenter/template/products/_APP=00200682500000001943&_EVENT=DISPHIER&HEADER=Y&FUNCTIONBAR=N&EVENT=TREE&NE=NAVIGATE&ENR=01200314690100002214&V=MAINT) > **SAP NW RFC SDK** > **SAP NW RFC SDK 7.50** > **nwrfc750X_X-xxxxxxx.zip**.

    **Important**: You'll need your SAP user sign-in information in order to access the SDK, and you must download the SDK that matches your operating system. Make sure to select the **LINUX ON X86_64 65BIT** option.
2. Create a folder with a relevant name and copy the systemconfig.ini from the "template folder" and the sdk zip file.

ex:

```bash
git clone <current repo>
mkdir /home/$(pwd)/sapcon/<sap-sid>/
cp <azuresentinel4sap>/template/systemconfig.ini /home/$(pwd)/sapcon/<sap-sid>/
cp <**nwrfc750X_X-xxxxxxx.zip**> /home/$(pwd)/sapcon/<sap-sid>/
```

3. Edit the **systemconfig.ini** file with the required system information as instructed by the embedded comments.

    To test your configuration, add the user and password to the configuration file as well. For running systems, we recommend you use the **env.list** file, or Docker secrets as shown in the example below.

    A template **systemconfig.ini** file is available under the [Template] folder of this repository. For example, see [Template: template\systemconfig.ini](#template-templatesystemconfigini).

    **Note**: Enter your time zone in GMT format, such as: `GMT+0`,`GMT+1`,`GMT-1`

4. Define the logs that are set to Azure Sentinel using the instructions in the **systemconfig.ini** file. For example, see [below](#define-the-sap-logs-that-are-sent-to-azure-sentinel).

5. Define the following additional configurations using the instructions in the **systemconfig.ini** file:

    - Whether to extract the user email address from the logs
    - Whether to retry failed API calls
    - Whether to include cexal audit logs

    For example, see [below](#additional-sal-logs-connector-configurations).

6. Save your updated **systemconfig.ini** file in the [sapcon] directory on your machine. 

7. Create a temporary **env.list** file with any required credentials. Once your Docker container is running correctly, make sure to delete this file.

    Run:

    ```bash
    ##############################################################
    ##############################################################
    # env.list template
    SAPADMUSER=<SET_SAPCONTROL_USER>
    SAPADMPASSWORD=<SET_SAPCONTROL_PASS>
    ABAPUSER=SET_ABAP_USER>
    ABAPPASS=<SET_ABAP_PASS>
    JAVAUSER=<SET_JAVA_OS_USER>
    JAVAPASS=<SET_JAVA_OS_USER>
    ##############################################################
    ```

    **Note**: This configuration has each Docker container connecting to a specific ABAP system.

8. Download the predefined Docker image with the credentials that you have received from your Microsoft representative and run the container. 
Run:

    ```bash
    echo <mcr token> | docker login -u <mcr user> --password-stdin sentinel4sapprivateprview.azurecr.io 
    docker pull sentinel4sapprivateprview.azurecr.io/sapcon:latest
    docker run --env-file=<env.list_location> -d -v /home/$(pwd)/sapcon/<sap-sid>/:/sapcon-app/sapcon/config/system --name sapcon-<sid> sapcon
    rm -f <env.list_location>
    ```

## Upgrade your SAP logs connector

This section describes the script you should run if you already have an Azure Sentinel SAP logs connector Docker container running, and want to upgrade the version. 


Create a temporary **env.list** file with any required credentials. Once your Docker container is running correctly, make sure to delete this file.

    Run:

    ```bash
    ##############################################################
    ##############################################################
    # env.list template
    SAPADMUSER=<SET_SAPCONTROL_USER>
    SAPADMPASSWORD=<SET_SAPCONTROL_PASS>
    ABAPUSER=SET_ABAP_USER>
    ABAPPASS=<SET_ABAP_PASS>
    JAVAUSER=<SET_JAVA_OS_USER>
    JAVAPASS=<SET_JAVA_OS_USER>
    ##############################################################
    ```

    **Note**: This configuration has each Docker container connecting to a specific ABAP system.

Run:

    ```bash
    echo <mcr token> | docker login -u <mcr user> --password-stdin sentinel4sapprivateprview.azurecr.io 
    docker pull sentinel4sapprivateprview.azurecr.io/sapcon:latest
    docker stop sapcon-<sid> 
    docker container rm sapcon-<sid> 
    docker run --env-file=<env.list_location> -d -v /home/$(pwd)/sapcon/<sap-sid>/:/sapcon-app/sapcon/config/system --name sapcon-<sid> sapcon
    rm -f <env.list_location>
    ```


## Reference


### Template: template\systemconfig.ini

The following code shows a sample **systemconfig.ini** file:

```Python
[Secrets Source]
secrets = '<DOCKER_RUNTIME/AZURE_KEY_VAULT/DOCKER_SECRETS/DOCKER_FIXED>'
keyvault = '<SET_YOUR_AZURE_KEYVAULT>'
intprefix = '<SET_YOUR_PREFIX>'

[ABAP Central Instance]
##############################################################
# Define the following values according to your server configuration.
ashost = <SET_YOUR_APPLICATION_SERVER_HOST>
mshost = <SET_YOUR_MESSAGE_SERVER_HOST> - #In case different then App
##############################################################
group = <SET_YOUR_LOGON_GROUP>
msserv = <SET_YOUR_MS_SERVICE> - #Required only if the message server service is not defined as sapms<SYSID> in /etc/services
sysnr = <SET_YOUR_SYS_NUMBER>
user = <SET_YOUR_USER>
##############################################################
# Enter your password OR your X509 SNC parameters
passwd = <SET_YOUR_PASSWORD>
snc_partnername = <SET_YOUR_SNC_PARTNER_NAME>
snc_lib = <SET_YOUR_SNC_LIBRARY_PATH>
x509cert = <SET_YOUR_X509_CERTIFICATE>
##############################################################
sysid = <SET_YOUR_SYSTEM_ID>
client = <SET_YOUR_CLIENT>

[Azure Credentials]
loganalyticswsid = <SET_YOUR_LOG_ANALYTICS_WORKSPACE_ID>
publickey = <SET_YOUR_PUBLIC_KEY>

[File Extraction ABAP]
osuser = <SET_YOUR_SAPADM_LIKE_USER>
##############################################################
# Enter your password OR your X509 SNC parameters
ospasswd = <SET_YOUR_SAPADM_PASS>
x509pkicert = <SET_YOUR_X509_PKI_CERTIFICATE>
##############################################################
appserver = <SET_YOUR_SAPCTRL_SERVER>
instance = <SET_YOUR_SAP_INSTANCE>
abapseverity = <SET_ABAP_SEVERITY>
abaptz = <SET_ABAP_TZ>

[File Extraction JAVA]
javaosuser = <SET_YOUR_JAVAADM_LIKE_USER>
##############################################################
# Enter your password OR your X509 SNC parameters
javaospasswd = <SET_YOUR_JAVAADM_PASS>
javax509pkicert = <SET_YOUR_X509_PKI_CERTIFICATE>
##############################################################
javaappserver = <SET_YOUR_JAVA_SAPCTRL_SERVER>
javainstance = <SET_YOUR_JAVA_SAP_INSTANCE>
javaseverity = <SET_JAVA_SEVERITY>
javatz = <SET_JAVA_TZ>
```

### Define the SAP logs that are sent to Azure Sentinel

Use the following section of the **systemconfig.ini** file to define the logs that are sent to Azure Sentinel. 

```Python
##############################################################
# Enter True OR False for each log to send those logs to Azure Sentinel
[Logs Activation Status]
ABAPAuditLog = True
ABAPJobLog = True
ABAPSpoolLog = True
ABAPSpoolOutputLog = True
ABAPChangeDocsLog = True
ABAPAppLog = True
ABAPWorkflowLog = True
ABAPCRLog = True
ABAPTableDataLog = False
# ABAP SAP Control Logs - Retrieved by using SAP Conntrol interface and OS Login
ABAPFilesLogs = False
SysLog = False
ICM = False
WP = False
GW = False
# Java SAP Control Logs - Retrieved by using SAP Conntrol interface and OS Login
JAVAFilesLogs = False
##############################################################
```

### Additional SAL logs connector configurations

Use the following section of the **systemconfig.ini** file to define the logs that are sent to Azure Sentinel. 

```Python
##############################################################
[Connector Configuration]
extractuseremail = True
apiretry = True
auditlogforcexal = False
auditlogforcelegacyfiles = False
timechunk = 60
##############################################################
```


[initsetup.sh]: ../initsetup.sh
<!-- [configgen]: ./ConfigGen.md -->
[previewterms]: https://azure.microsoft.com/en-us/support/legal/preview-supplemental-terms/
[SAPNWRFCSDK]: https://launchpad.support.sap.com/#/softwarecenter/template/products/_APP=00200682500000001943&_EVENT=DISPHIER&HEADER=Y&FUNCTIONBAR=N&EVENT=TREE&NE=NAVIGATE&ENR=01200314690100002214&V=MAINT

<!-- ## Next steps

Continue with [Configure the Azure Sentinel SAP logs connector](config-gen.md). -->