using System;
using System.Collections.Generic;
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
            try
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

                //get custom table name
                var path = new SampleDataPath();
                var dirPath = path.GetDirPath();
                tableName = tableName.Replace(dirPath, "").Replace(".json", "");

                //get a list of table names in your workspace
                var tableNameList = new List<string>();
                string query = @"search * | distinct $table";
                var result = laClient.Query(query).Tables;
                foreach (var table in result)
                {
                    var rows = table.Rows;
                    foreach (var r in rows)
                    {
                        var customFileName = r[0];
                        if (customFileName.EndsWith("_CL"))
                        {
                            tableNameList.Add(customFileName);
                        }
                    }
                }

                //check if the custom table name exists in the list
                if (tableNameList.Contains(tableName) == false)
                {
                    return false;
                }
                else
                {
                    //check if there's any data in the table for last 7 days
                    string query1 = tableName
                               + @"| where TimeGenerated > ago(7d)
                             | limit 10";
                    var results = laClient.Query(query1);
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
            catch (Exception ex)
            {
                throw new Exception("Calling Log Analytics Error " + ex.Message);
            }
        }
    }
}