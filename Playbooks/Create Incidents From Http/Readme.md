



Please use the below button to deploy

[![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FPlaybooks%2FCreate%2520Incidents%2520From%2520Http%2Fazuredeploy.json)

### Deployment

Once deployed you can configure the connections as below

![image](https://github.com/samikroy/Azure-Sentinel/assets/20562985/752dbade-ccd6-48f4-883c-10efea7e0215)


### Configuration

1. Sentinel Connection

![image](https://user-images.githubusercontent.com/20562985/196175586-0fd33803-6fd3-4429-8af4-945c8a0c8511.png)


2. Office 365 Connection

![image](https://user-images.githubusercontent.com/20562985/196175803-51712fbb-1bb4-4279-9d96-64cc24bcf63f.png)

### Post configuration

Once configured, the logic app will look like this.

![image](https://github.com/samikroy/Azure-Sentinel/assets/20562985/3c239b3e-5808-4939-897e-8a36b536c90e)


### Assign Permission

Assign Microsoft Sentinel Contributor role to Logic App Identity so that it can generate incidents.

![image](https://github.com/samikroy/Azure-Sentinel/assets/20562985/3e22ed6b-91e4-4628-9f27-6f0b73a8ffb6)


### Test

Step 1: Make http request 

![image](https://github.com/samikroy/Azure-Sentinel/assets/20562985/b1b097f0-bbc1-4ae0-a1b1-6157dbeacd2d)


Step 2: Incident created in Sentinel 

![image](https://github.com/samikroy/Azure-Sentinel/assets/20562985/5484000e-8ee4-49c3-8bf6-1e401a4b6d73)



### Use cases
1. While using Microsoft Sentinel as a POC and using another SIEM as primary.
2. Run another SIEM in parallel and want forward incidents to Microsoft Sentinel.
3. Generating Incidents from external Systems.


Thank you for using the tool.

