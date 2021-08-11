Scheduled CSV Exports to Email
----
Author:  Matt Egen 

mattegen@microsoft.com

<a href="https://twitter.com/FlyingBlueMonki?ref_src=twsrc%5Etfw" class="twitter-follow-button" data-show-count="true">Follow @FlyingBlueMonki on Twitter</a>

Do you have a need to run scheduled exports of data from your Azure Sentinel environment?  If so, this is the Playbook for you!  Running on a daily recurrence trigger it exports data from Azure Sentinel on a daily/weekly/monthly scheudule as a .csv file via SMTP email connection using a WatchList() as the data source for the reports

#Connectors and Prerequisites#
##SMTP Email##
This Playbook uses the built in SMTP connector for Azure Logic Apps.  Unlike the built-in Outlook mail connector, you do not need to have an O365 account to send email via the SMTP connector, but you need to do some configuration and make some decisions.  If you're using O365, you can send email via your public facing SMTP server endpoint (See:  https://docs.microsoft.com/en-us/exchange/mail-flow-best-practices/how-to-set-up-a-multifunction-device-or-application-to-send-email-using-microsoft-365-or-office-365 for more details. You will need to decided if you are going to need to send #authenticated# or #unauthenticated# email. For example, if the email your sending is going to an internal only email address, then you can send it unauthenticated and do not even need a mailbox in O365.  However, if you want to send an email to an address outside of your domain, then you can only send it as an authenticated user and that will require that the user account have a mailbox. 
##Watchlist##
A sample of such watchlist is provided in this folder as an example. Please use it to generate your watchlist. The playbook is configured to query it by this watchlist column names.

[![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FFlyingBlueMonkey%2FAzure-Sentinel%2Fmaster%2FPlaybooks%2FExport-Report-CSV%2Fazuredeploy.json)
