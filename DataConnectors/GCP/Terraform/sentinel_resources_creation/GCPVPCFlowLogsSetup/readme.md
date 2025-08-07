# GCP VPC Flow Logs Data Connector Configuration Guide

For ingesting data into Microsoft Sentinel , We need few of the resources created/ready on google console , Which will be done with the help of terraform script.

### List of Resources required 

* Topic
* Subscription for the topic
* Workload identity pool
* Workload identity provider
* Service account with permissions to get and consume from subscription.

### Configurations steps
1. Select the project from where the VPC Flow logs has to be collected
2. Open the cloud shell , by clicking activate cloud shell button on the top right

   ![image](https://github.com/user-attachments/assets/1666158e-8295-4c2f-a8c7-16ede37b8fb1)
   
4. Open the Terraform script [GCPVPCFlowLogSetup](https://github.com/Azure/Azure-Sentinel/blob/master/DataConnectors/GCP/Terraform/sentinel_resources_creation/GCPVPCFlowLogsSetup/GCPVPCFlowLogSetup.tf) and copy its contents
5. Create a directory in your Cloud Shell environment, enter it, and create a new blank file.
   mkdir {directory-name} && cd {directory-name} && touch GCPVPCFlowLogSetup.tf
6. Open GCPVPCFlowLogSetup.tf in the Cloud Shell editor and paste the contents of the script file into it.
7. Once you pasted the content of terraform script , do remember to change the project id inside terrform script at line number 13 and then save it
   
   ![image](https://github.com/user-attachments/assets/e77ec777-ebad-4d6e-ba20-600a264c8967)
   
8. Initialize Terraform in the directory you created by typing the following command in the terminal

   _terraform init_
   
10. When you receive the confirmation message that Terraform was initialized, run the script by typing the following command in the terminal

    _terraform apply_
   
12. When asked if you want to create the resources listed, type yes
13. When the output from the script is displayed, save the resources parameters for later use.  
