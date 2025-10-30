using System;
using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;
using Azure;
using Azure.Identity;
using Azure.Monitor.Query;
using Azure.Monitor.Query.Models;

namespace SampleDataIngestTool
{
    public class LogAnalyticsCheck
    {
        private static string _clientId = "";
        private static string _clientSecret = "";
        private static string _domain = "";
        private static string _workspaceId = "";

        public LogAnalyticsCheck()
        {
        }

        public async Task<bool> RunLAQuery(string tableName)
        {
            try
            {
                // Get credentials from config.txt
                Dictionary<string, string> credentials = new AppConfig().GetCredentials();
                _workspaceId = credentials["workspaceId"];
                _clientId = credentials["clientId"];
                _clientSecret = credentials["clientSecret"];
                _domain = credentials["domain"];

                var credential = new ClientSecretCredential(_domain, _clientId, _clientSecret);
                var logsClient = new LogsQueryClient(credential);

                // Get a list of table names in your workspace
                var distinctTablesQuery = "search * | distinct $table";
                Response<LogsQueryResult> response = 
                    await logsClient.QueryWorkspaceAsync(_workspaceId, distinctTablesQuery, QueryTimeRange.All);
                LogsTable table = response.Value.Table;

                IEnumerable<string> tableNames = from row in table.Rows
                                                 let columnValue = row.GetString("$table")
                                                 where columnValue.EndsWith("_CL")
                                                 select columnValue;

                // Get custom table name
                tableName = tableName.Replace(".json", "");

                // Check if the custom table name exists in the list
                if (!tableNames.Contains(tableName))
                    return false;
                else
                {
                    // Check if there's any data in the table for last 7 days
                    var query = $"{tableName} | limit 10";
                    var timeRange = new QueryTimeRange(TimeSpan.FromDays(7));
                    Response<LogsQueryResult> results = 
                        await logsClient.QueryWorkspaceAsync(_workspaceId, query, timeRange);
                    int tableCount = results.Value.AllTables.Count;

                    return tableCount > 0;
                }
            }
            catch (Exception ex)
            {
                throw new Exception("Calling Log Analytics error " + ex.Message);
            }
        }
    }
}