using System;
using System.Threading.Tasks;
using Microsoft.Azure.OperationalInsights;
using Microsoft.IdentityModel.Clients.ActiveDirectory;
using Microsoft.Rest.Azure.Authentication;

namespace SampleDataIngestTool
{
    public class LogAnalyticsCheck
    {
        static string clientId = "";
        static string clientSecret = "";
        static string customerId = "";
        static string domain = "";
        public LogAnalyticsCheck()
        {

        }

        public bool RunLAQuery(string tableName)
        {
            // Get credentials fron config.json
            var appConfig = new AppConfig();
            var credentials = appConfig.GetCredentials();
            customerId = credentials["workspaceId"];
            clientId = credentials["clientId"];
            clientSecret = credentials["clientSecret"];
            domain = credentials["domain"];

            var authEndpoint = "https://login.microsoftonline.com";
            var tokenAudience = "https://api.loganalytics.io/";

            var adSettings = new ActiveDirectoryServiceSettings
            {
                AuthenticationEndpoint = new Uri(authEndpoint),
                TokenAudience = new Uri(tokenAudience),
                ValidateAuthority = true
            };

            var creds = ApplicationTokenProvider.LoginSilentAsync(domain, clientId, clientSecret, adSettings).GetAwaiter().GetResult();

            var laClient = new OperationalInsightsDataClient(creds);
            laClient.WorkspaceId = customerId;

            tableName = "alcide_kaudit_activity_1_CL";
            string query = tableName
                           + @"| where TimeGenerated > ago(10d)
                             | limit 100";
            var results = laClient.Query(query);
            var tableCount = results.Tables.Count;
            if (tableCount > 0)
            {
                return true;
            }
            else
            {
                return false;
            }
        }
    }
}