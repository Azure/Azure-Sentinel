# Steps to Configure Auth0 app
The following are steps to be followed in Auth0 App.

1. Please go to applications and select application from auth0 side, Please find below screen shot for reference :-

![](Images/Applications.png?raw=true)

2. Click on settings of the App and note down the credentials
<br>***a. Copy the domain
    b. Get the client id value
    c. Get the client secret***<br>

3. Under Application properties --> Select Application type as Machine to Machine. Please find below screen shot for reference :-

![](Images/ApplicationProperties.png?raw=true)

4. Under credentials tab --> Select client secret (Post). Please find below screen shot for reference :-

![](Images/Credentials.png?raw=true)

5. Under API tab, please make sure Authorized to scopes, Please find below screen shot for reference :-

![](Images/API.png?raw=true)

6. Please make sure the domain value under settings --> Environment Variables, please refer below screen shot for reference and other values are entered from the above step copied values and Domain should be  starts with https://,then click on Apply  and restart function app

![](Images/functionappvalues.png?raw=true)

