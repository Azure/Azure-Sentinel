# AWS Lambda Function to import S3 Files to Azure Sentinel
This Lambda function is desgined to read S3 Files on upload and send them to Azure Sentinel using the Log Analytics API.

## Deployment
### Machine Setup
To deploy this, you will need a machine prepared with the following:
 - PowerShell Core – I recommend PowerShell 7 [found here](https://github.com/PowerShell/PowerShell/releases)
 - .Net Core 3.1 SDK [found here](https://dotnet.microsoft.com/download) 
 - AWSLambdaPSCore module – You can install this either from the [PowerShell Gallery](https://www.powershellgallery.com/packages?q=AWSLambdaPSCore), or you can install it by using the following PowerShell Core shell command:  
```powershell
Install-Module AWSLambdaPSCore -Scope CurrentUser
```
See the documentation here https://docs.aws.amazon.com/lambda/latest/dg/powershell-devenv.html 

I recommend you review https://docs.aws.amazon.com/lambda/latest/dg/powershell-package.html to review the cmdlets that are part of AWSLambdaPSCore.

Note: If the environment uses a proxy, you may need to add the following to VSCode profile
```powershell
Added to VS Code profile:
$webclient=New-Object System.Net.WebClient
$webclient.Proxy.Credentials = [System.Net.CredentialCache]::DefaultNetworkCredentials
```
### Edit the script
You will need to add the workspace ID, Key and Custom Log file name:
1. Go to line 151 and edit the following:
```powershell
$workspaceId = "workspaceId"
$workspaceKey = "workspaceKey"
$CustomLogName = "CustomLog"
```
Note:  It is possible to put these in Lambda Environment Variables.  See [this](https://docs.aws.amazon.com/lambda/latest/dg/configuration-envvars.html) to add the environment variables.  If using env variables, comment out lines 151-153 and uncomment lines 154-156.  Ensure the env variable names match the names on these lines.

### Create AWS Role
The Lambda function will need an execution role defined that grants access to the S3 bucket and CloudWatch logs.  To create an execution role: 
1. Open the [roles](https://console.aws.amazon.com/iam/home#/roles) page in the IAM console. 
2. Choose Create role. 
3. Create a role with the following properties. 
 - Trusted entity – AWS Lambda. 
 - Permissions – AWSLambdaExecute. 
 - Role name – lambda-s3-role. 
 4. Add s3:GetObject and s3:Listbucket to the role.
 ```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "logs:*"
            ],
            "Resource": "arn:aws:logs:*:*:*"
        },
        {
            "Effect": "Allow",
            "Action": [
                "s3:GetObject"
            ],
            "Resource": "<bucketarn>/*"
        },
        {
            "Effect": "Allow",
            "Action": [
                "s3:ListBucket"
            ],
            "Resource": "<bucketarn>"
        }
    ]
}
 ```
The AWSLambdaExecute policy has the permissions that the function needs to manage objects in Amazon S3 and write logs to CloudWatch Logs.  Copy the arn of the role created as you will need it for the next step. 

### Create the Lambda Function
To deploy the PowerShell script, you can create a Package (zip file) to upload to the AWS console or you can use the Publish-AWSPowerShell cmdlet.
```powershell
Publish-AWSPowerShellLambda -Name YourLambdaNameHere -ScriptPath <path>/S3Event.ps1 -Region <region> -IAMRoleArn <arn of role created earlier> -ProfileName <profile>
```
You might need –ProfileName if your configuration of .aws/credentials file doesn't contain a default.  See this document for information on setting up your AWS credentials. 

### Edit the Lambda Trigger
1. Once created, login to the AWS console.   In Find services, search for Lambda.  Click on Lambda.
![Picture1](./Graphics/Picture1.png)
2. Click on the lambda function name you used with the cmdlet. Click Add Trigger 
![Picture2](./Graphics/Picture2.png)
3. Select S3.  Select the bucket.  Acknowledge the warning at the bottom.  Click Add. 
![Picture3](./Graphics/Picture3.png)
4. Your lambda function is ready to send data to Log Analytics.   

### Test the function
1. To test your function, upload a support file to the S3 bucket defined in the trigger. 
![Picture4](./Graphics/Picture4.png)
2. To see the logs, go the Lambda function.  Click Monitoring tab.  Click view logs in CloudWatch. 
![Pciture5](./Graphics/Picture5.png)
3. In CloudWatch, you will see each log stream from the runs.  Select the latest.   
![Picture6](./Graphics/Picture6.png)
4. Here you can see anything from the script from the Write-Host cmdlet. 
![Picture7](./Graphics/Picture7.png)
5. Go to portal.azure.com and verify your data is in the custom log. 
![Picture8](./Graphics/Picture8.png)

  
