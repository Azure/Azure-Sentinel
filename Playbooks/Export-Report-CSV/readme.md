# Scheduled CSV Exports to Email
----
Author:  Matt Egen 

mattegen@microsoft.com

<a href="https://twitter.com/FlyingBlueMonki?ref_src=twsrc%5Etfw" class="twitter-follow-button" data-show-count="true">Follow @FlyingBlueMonki on Twitter</a>

Do you have a need to run scheduled exports of data from your Azure Sentinel environment?  If so, this is the Playbook for you!  Running on a daily recurrence trigger it exports data from Azure Sentinel on a daily/weekly/monthly schedule as a .csv file via SMTP email connection using a WatchList() as the data source for the reports

## Connectors and Prerequisites
----
###### SMTP Email

This Playbook uses the built in SMTP connector for Azure Logic Apps.  Unlike the built-in Outlook mail connector, you do not need to have an O365 account to send email via the SMTP connector, but you need to do some configuration and make some decisions.  If you're using O365, you can send email via your public facing SMTP server endpoint (See:  https://docs.microsoft.com/exchange/mail-flow-best-practices/how-to-set-up-a-multifunction-device-or-application-to-send-email-using-microsoft-365-or-office-365 for more details. You will need to decide if you are going to need to send *authenticated* or *unauthenticated* email. For example, if the email your sending is going to an internal only email address, then you can send it unauthenticated and do not even need a mailbox in O365.  However, if you want to send an email to an address outside of your domain, then you can **only** send it as an authenticated user and that will require that the user account have a mailbox. 

###### Watchlist
Report items are based on a schedule of daily, weekly, or monthly, stored in a watchlist called "Reporting".  The Playbook executes an Azure Monitor Logs query for the various reports using a query like this:  "\_GetWatchlist("Reporting") | where Schedule == "Daily"".  It then iterates through the returned values to run the reports and send the emails out.

###### Watchlist Structure
The watchlist has a set structure that you have to follow.  I've included a sample in this repo.  When you create your Watchlist, you'll want to also make sure to set the "SearchKey field" to "Schedule".
- Title:  The name of the report.  This is used in the subject line of the email, the body of the email, and as the filename for the .CSV attachment
- Schedule: The schedule to run the report.  Acceptable values: Daily, Weekly, Monthly (please note it is cAsE sEnSiTiVe)
- QueryBody:  The query you want to run to generate the report.  PLEASE NOTE:  You have to flatten the query in to one line by removing carriage returns / line feeds.  For example:
````
SigninLogs | where TimeGenerated >= ago(24h) | where UserPrincipalName == blah@blah.com.
````
Because of this you cannot use inline comments (e.g.: //my comment).
- Recipients:  A semicolon separated list of email recipients.  PLEASE NOTE:  If you are using unauthenticated email via O365, these must ALL be in your domain. Unauthenticated email via O365 cannot be sent to external recipients.


## Gotchas / Issues / Bugs
----
The following are some issues I’ve run into on this Playbook.  I am still working on more elegant solutions for them, but for now the workarounds seem to work.
##### Issue:  Azure Monitor Logs cannot be configured via a JSON template
I’m not sure if this is a technical limitation of the Azure Monitor Logs connector or if I am just doing something wrong, but while the template will correctly create the connector it will still give you an error and you will have to authorize the connector and then go into the Playbook and configure the connector to point to the correct subscription etc.  It is much much easier to open the Azure Monitor Logs connector from the Resource Group first , authorize the connector there, and then go into the Playbook to complete the configuration.  
 

##### Issue: SMTP Connector throws an error in the UX configuration
The SMTP connector really doesn’t like allowing you to configure unauthenticated email (or sometimes even any email) in the UX.  What I’ve found seems to work really well is to configure it using the template configuration (I’ve included fields for all of the relevant values (from, server, port, ssl, etc.) and then just leave it alone.  IF you do need to make changes though, configuring it in the Designer view seems to throw errors.  If you want to change it, again, using the Resource Group Edit API Connection seems to be the way to go and not get an error.


##### Issue:  O365 is categorizing my email as SPAM/PHISH and putting it in quarantine!
When you send the email through your public facing MX endpoint it's still subject to the same rules as any other email.  If the sending infrastructure (in this case Azure) isn't in your SPF records, then it will look a possible spoof and depending on your policy configuration, this may mean the emails will go to quarantine.  


[![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FPlaybooks%2FExport-Report-CSV%2Fazuredeploy.json)
