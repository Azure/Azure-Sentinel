using System;
using Microsoft.Azure.WebJobs;
using Microsoft.Extensions.Logging;
using System.Threading.Tasks;
using Varonis.Sentinel.Functions.LogAnalytics;
using Varonis.Sentinel.Functions.DatAlert;
using Varonis.Sentinel.Functions.Helpers;
using System.Linq;
using System.Text.Json;

namespace Varonis.Sentinel.Functions
{
    public class FetchDataFunction
    {
        [FunctionName("VaronisSaaS")]
        public async Task Run([TimerTrigger("0 * * * * *")]TimerInfo timer, ILogger log)
        {
            try
            {
                var hostname = Environment.GetEnvironmentVariable("VaronisFQDN_IP");
                var datalertApiKey = Environment.GetEnvironmentVariable("VaronisApiKey");
                var logAnalyticsKey = Environment.GetEnvironmentVariable("LogAnalyticsKey");
                var logAnalyticsWorkspace = Environment.GetEnvironmentVariable("LogAnalyticsWorkspace");

                var firstFetchTimeStr = Environment.GetEnvironmentVariable("AlertRetrievalStart");
                var severities = Environment.GetEnvironmentVariable("AlertSeverity");
                var threatModelName = Environment.GetEnvironmentVariable("ThreatDetectionPolicies");
                var status = Environment.GetEnvironmentVariable("AlertStatus");
                var maxAlerts = int.TryParse(Environment.GetEnvironmentVariable("MaxAlertRetrieval"), out var maxvalue)
                    ? maxvalue
                    : 1000;

                var baseUri = new Uri($"https://{hostname}");

                var client = new DatAlertClient(baseUri, datalertApiKey, log);
                var storage = new LogAnalyticsCollector(logAnalyticsKey, logAnalyticsWorkspace, log);

                if (timer.IsPastDue)
                {
                    log.LogWarning("Timer is running late!");
                }

                var minDate = DateTime.MinValue.ToUniversalTime();

                var last = timer.ScheduleStatus.Last.ToUniversalTime();
                var lastUpdated = timer.ScheduleStatus.LastUpdated.ToUniversalTime();
                var next = timer.ScheduleStatus.Next.ToUniversalTime().AddSeconds(-1);

                log.LogInformation($"Schedule status: {last}, {lastUpdated}, {next}");

                if (!string.IsNullOrWhiteSpace(firstFetchTimeStr))
                {
                    var firstDate = CustomParser.ParseDate(firstFetchTimeStr);

                    if (last <= firstDate)
                    {
                        lastUpdated = firstDate;
                        next = DateTime.Now;
                    }
                }

                log.LogInformation($"Varonis host name: {hostname}; LogAnalytics Key: {logAnalyticsKey.Substring(0, 5)}...;" +
                    $" LogAnalytics Workspace: {logAnalyticsWorkspace}; Time: {DateTime.Now}");

                var interval = timer.ScheduleStatus.Next - timer.ScheduleStatus.Last;

                var parameters = new DatAlertParams(lastUpdated, next, severities, threatModelName, status, maxAlerts);
                var alerts = await client.GetDataAsync(parameters);

                if (!alerts.Any())
                {
                    log.LogInformation("Request was successful, but data is empty");
                    return;
                }

                var data = JsonSerializer.Serialize(alerts);

                log.LogInformation($"Data was received successfully: {data.Substring(0, data.Length > 15 ? 15 : data.Length)}...");
                await storage.PublishAsync(data);
            }
            catch (Exception ex) 
            {
                log.LogError($"{ex.Message} {ex.InnerException?.Message}");
                throw;
            }
        }
    }
}
