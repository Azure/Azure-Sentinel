



Please use the below button to deploy

[![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FPlaybooks%2FCreate%2520Incidents%2520with%2520Email%2Fazuredeploy.json)

### Deployment

Once deployed you can configure the connections as below

![image](https://user-images.githubusercontent.com/20562985/196198346-2dbde9ca-9812-4c49-a0e6-d3ebca777bb3.png)


### Configuration

1. Sentinel Connection

![image](https://user-images.githubusercontent.com/20562985/196175586-0fd33803-6fd3-4429-8af4-945c8a0c8511.png)


2. Office 365 Connection

![image](https://user-images.githubusercontent.com/20562985/196175803-51712fbb-1bb4-4279-9d96-64cc24bcf63f.png)

### Post configuration

Once configured, the logic app will look like this.

![image](https://user-images.githubusercontent.com/20562985/195930261-a883dbc0-37ff-401c-87a6-74d4eba7ffea.png)

### Test

Step 1: Send an email to the configure email

![image](https://user-images.githubusercontent.com/20562985/196176523-21e76ca7-705f-468e-beec-aa75b814f742.png)


Step 2: Incident created in Sentinel 

![image](https://user-images.githubusercontent.com/20562985/196183706-02062a9c-eea2-4fd1-9d57-4bf540456341.png)


### Use cases

SOC - In a organization there might be Security Incident / Suspicious activity occurring to the resources where Security is not tightened up yet. 
So an email address can be whistle blower here. A suspicious activity can be reported over a dedicated email address to create an incident and address the incident.


Thank you for using the tool.

