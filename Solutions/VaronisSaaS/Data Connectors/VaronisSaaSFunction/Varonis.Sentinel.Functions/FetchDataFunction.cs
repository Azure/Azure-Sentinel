using System;
using Microsoft.Azure.WebJobs;
using Microsoft.Extensions.Logging;
using System.Threading.Tasks;
using Varonis.Sentinel.Functions.LogAnalytics;
using Varonis.Sentinel.Functions.DatAlert;
using System.Linq;
using System.Text.Json;
using Microsoft.Extensions.Configuration;
using Varonis.Sentinel.Functions.State;

namespace Varonis.Sentinel.Functions
{
    public class FetchDataFunction
    {
        private readonly IConfiguration _config;

        public FetchDataFunction(IConfiguration config)
        {
            _config = config;
        }

        [FunctionName("VaronisSaaS")]
        public async Task Run([TimerTrigger("0 * * * * *")]TimerInfo timer, ILogger log)
        {
            try
            {
                var hostname = Environment.GetEnvironmentVariable("VaronisFQDN_IP");
                var datalertApiKey = Environment.GetEnvironmentVariable("VaronisApiKey");
                var logAnalyticsKey = Environment.GetEnvironmentVariable("LogAnalyticsKey");
                var logAnalyticsWorkspace = Environment.GetEnvironmentVariable("LogAnalyticsWorkspace");

                var firstFetchTime = int.TryParse(Environment.GetEnvironmentVariable("AlertRetrievalStart"), out var maxdays)
                    ? maxdays
                    : 30;
                var severities = Environment.GetEnvironmentVariable("AlertSeverity");
                var threatModelName = Environment.GetEnvironmentVariable("ThreatDetectionPolicies");
                var status = Environment.GetEnvironmentVariable("AlertStatus");
                const int maxAlerts = 1000;

                var baseUri = hostname.StartsWith("http") 
                    ? new Uri(hostname)
                    : new Uri($"https://{hostname}");

                var client = new DatAlertClient(baseUri, datalertApiKey, log);
                var storage = new LogAnalyticsCollector(logAnalyticsKey, logAnalyticsWorkspace, log);
                var stateService = new BlobStateSaver(_config["AzureWebJobsStorage"]);
                await stateService.Init();

                if (timer.IsPastDue)
                {
                    log.LogWarning("Timer is running late!");
                }

                log.LogInformation($"Varonis host name: {hostname}; LogAnalytics Key: {logAnalyticsKey.Substring(0, 5)}...;" +
                    $" LogAnalytics Workspace: {logAnalyticsWorkspace}; Time: {DateTime.Now}");

                var from = await stateService.GetLastDate();
                var parameters = GetParams(from, firstFetchTime, severities, threatModelName, status);
                log.LogInformation($"Fetching alerts with params: start - {parameters.Start}. end - {parameters.End}" +
                                   $" severity - {parameters.AlertSeverity}. policies - {parameters.ThreatDetectionPolicies}." +
                                   $" status - {parameters.AlertStatus}");

                var alerts = await client.GetDataAsync(parameters);

                if (!alerts.Any())
                {
                    log.LogInformation("Request was successful, but data is empty");
                    return;
                }

                var dateTimeToSave = DateTime.MinValue;
                foreach (var alert in alerts)
                {
                    if (alert.IngestTime > dateTimeToSave)
                    {
                        dateTimeToSave = alert.IngestTime;
                    }
                }

                await stateService.SaveLastDate(dateTimeToSave.AddSeconds(1));

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

        private static DatAlertParams GetParams(DateTime? from, int firstFetchTime, string severities,
            string threatModelName, string status)
        {
            const int maxAlerts = 1000;
            var next = DateTime.UtcNow;
            const int maxGap = 7;
            if (from != null)
            {
                if (next - from > TimeSpan.FromDays(maxGap))
                {
                    from = next.AddDays(-maxGap);
                }
            }
            else
            {
                from = next.AddDays(-firstFetchTime);
            }

            return new DatAlertParams(from.Value, next, severities, threatModelName, status, maxAlerts);
        }
    }
}
