using Azure.Identity;
using Azure.Security.KeyVault.Secrets;
using Microsoft.Azure.WebJobs;
using Microsoft.Extensions.Logging;
using Microsoft.WindowsAzure.Storage;
using Newtonsoft.Json;
using System.Collections.Generic;
using System.Collections;
using System.Dynamic;
using System.IO;
using System.Net.Http;
using System.Text;
using System.Threading.Tasks;
using System;

namespace Helios2Sentinel
{
    public class IncidentProducer
    {
        private static readonly string keyVaultName = Environment.GetEnvironmentVariable("keyVaultName");
        private static readonly string azureWebJobsStorage = Environment.GetEnvironmentVariable("AzureWebJobsStorage");
        private static readonly object queueLock = new object();
        private static readonly string containerName = "cohesity-extra-parameters";
        private static readonly string lastRequestDetailsBlobKey = Environment.GetEnvironmentVariable("Workspace") + "\\last-request-details";
        private static readonly HashSet<String> alertPropertiesRequired =
            new HashSet<String>() {"entityId", "cid", "jobId",
                                    "jobInstanceId", "jobStartTimeUsecs",
                                    "object", "source", "anomalyStrength"};
        private static readonly HashSet<String> alertPropertiesPersisted =
            new HashSet<String>() {"entityId", "cid", "jobId",
                                    "jobInstanceId", "jobStartTimeUsecs",
                                    "object"};
        private static readonly string anomalyIngestAlertName = "DataIngestAnomalyAlert";


        // Encapsulates the details regarding the Helios request for alerts.
        // NOTE: This data is persisted on Azure Storage. Please make sure any
        // changes to the class do not break backward compatibility.
        class RequestDetails {
            [JsonProperty("alertIds")]
            public HashSet<String> alertIds;

            public string ToJson() {
                return JsonConvert.SerializeObject(this);
            }

            public static RequestDetails FromJson(string jsonStr) {
                return JsonConvert.DeserializeObject<RequestDetails>(jsonStr);
            }
        }

        // Returns the start time (in microseconds) to be used for perodic
        // fetch of Helios alerts.
        private static long GetPeriodicFetchStartTimeUsecs(ILogger log)
        {
            DateTime startTime = DateTime.Now;
            try
            {
                startTime = startTime.AddHours(long.Parse(Environment.GetEnvironmentVariable("periodicFetchHoursAgo")));
            }
            catch (Exception ex)
            {
                startTime = startTime.AddHours(-24);
                log.LogError("Exception --> 1 " + ex.Message);
                log.LogInformation("Defaulting periodicFetchHoursAgo to -24");
            }
            return ((DateTimeOffset)startTime).ToUnixTimeMilliseconds() * 1000;
        }

        // Returns the start time (in microseconds) to be used for first bulk
        // fetch of Helios alerts.
        private static long GetFirstFetchStartTimeUsecs(ILogger log)
        {
            DateTime previousDateTime = DateTime.Now;
            try
            {
                previousDateTime = previousDateTime.AddDays(long.Parse(Environment.GetEnvironmentVariable("startDaysAgo")));
            }
            catch (Exception ex)
            {
                previousDateTime = previousDateTime.AddDays(-30);
                log.LogError("Exception --> 1 " + ex.Message);
            }
            return ((DateTimeOffset)previousDateTime).ToUnixTimeMilliseconds() * 1000;
        }

        private static long GetCurrentUnixTime()
        {
            return ((DateTimeOffset)DateTime.Now).ToUnixTimeMilliseconds() * 1000;
        }

        private static Task ParseAlertToQueue(
            [Queue("cohesity-incidents"), StorageAccount("AzureWebJobsStorage")] ICollector<string> outputQueueItem,
            dynamic alert, ILogger log)
        {
            try
            {
                string id = alert.id;

                // Validate that this is an anomaly alert.
                if (((string)alert.alertDocument.alertName) != anomalyIngestAlertName) {
                    log.LogInformation("Skipping the alert with id " + id +
                                        " and name " + (string)alert.alertDocument.alertName +
                                        " as it is not an anomaly alert");
                    return Task.CompletedTask;
                }

                Dictionary<string, string> properties = new Dictionary<string, string>();


                // Parse all the properties into a dictionary.
                foreach (var prop in alert.propertyList)
                {
                    properties[(string)prop.key] = (string)prop.value;
                }

                // Validate that all the required properties are present.
                foreach (var key in alertPropertiesRequired)
                {
                    if (!properties.ContainsKey(key))
                    {
                        log.LogError("Invalid alert: Property " + key + " not present in alert " + id);
                        return Task.CompletedTask;
                    }
                }

                string title = "Cluster: " + alert.clusterName;
                title += properties["object"];
                title += ". Source: " + properties["source"];
                long sev = long.Parse(properties["anomalyStrength"]);
                string severity;

                if (sev >= 70)
                {
                    severity = "High";
                }
                else if (sev < 30)
                {
                    severity = "Low";
                }
                else
                {
                    severity = "Medium";
                }

                string description = alert.alertDocument.alertDescription +
                    ". Alert cause: " + alert.alertDocument.alertCause +
                    ". Anomaly Strength: " + sev +
                    ". Additional Info: " + alert.alertDocument.alertHelpText +
                    ". Helios ID: " + alert.id;

                // Persist the properties that maybe required for other operations in Sentinel.
                foreach (var key in alertPropertiesPersisted)
                {
                    WriteData(id + "\\" + key, properties[key], log);
                }

                dynamic incident = ConstructIncident(title, description, severity);
                lock (queueLock)
                {
                    outputQueueItem.Add(JsonConvert.SerializeObject(incident));
                }

            }
            catch (Exception ex)
            {
                log.LogError("Received exception while parsing alert --> " + ex.Message);
            }

            return Task.CompletedTask;
        }

        private static object ConstructIncident(string title, string description, string severity)
        {
            dynamic incidient = new ExpandoObject();
            incidient.properties = new ExpandoObject();
            incidient.properties.title = title;
            incidient.properties.description = description;
            incidient.properties.severity = severity;
            incidient.properties.status = "New";

            return incidient;
        }

        private static string GetData(string path, ILogger log)
        {
            if (CloudStorageAccount.TryParse(IncidentProducer.azureWebJobsStorage, out var storageAccount))
            {
                // Create the CloudBlobClient that represents the Blob storage endpoint for the storage account.
                var cloudBlobClient = storageAccount.CreateCloudBlobClient();
                var container = cloudBlobClient.GetContainerReference(containerName);
                var blobRef = container.GetBlockBlobReference(path);

                using (var ms = new MemoryStream())
                using (var sr = new StreamReader(ms))
                {
                    var task = blobRef.DownloadToStreamAsync(ms);
                    task.Wait();
                    ms.Position = 0;
                    return sr.ReadToEnd();
                }
            }
            else
            {
                throw new InvalidProgramException("Invalid format string");
            }
        }

        private static void WriteData(string path, string data, ILogger log)
        {
            if (CloudStorageAccount.TryParse(IncidentProducer.azureWebJobsStorage, out var storageAccount))
            {
                var cloudBlobClient = storageAccount.CreateCloudBlobClient();
                var container = cloudBlobClient.GetContainerReference(containerName);
                var blobRef = container.GetBlockBlobReference(path);
                var dataAsBytes = Encoding.UTF8.GetBytes(data);
                blobRef.UploadFromByteArrayAsync(dataAsBytes, 0, dataAsBytes.Length).Wait();
            }
            else
            {
                throw new InvalidProgramException("Invalid format string");
            }
        }

        // Returns the information stored about the last request to Helios
        // by querying Blob storage.
        private static RequestDetails GetLastRequestDetails(ILogger log)
        {
            var jsonDetails = GetData(lastRequestDetailsBlobKey, log);
            // log.LogInformation(jsonDetails);
            return RequestDetails.FromJson(jsonDetails);
        }

        // Writes the current request details to Blob storage.
        private static void WriteRequestDetails(dynamic alerts, ILogger log)
        {
            // Create a set of alert IDs from the alerts.
            HashSet<string> alertIds = new HashSet<string>();
            foreach (var alert in alerts)
            {
                alertIds.Add((string)alert.id);
            }

            RequestDetails details = new RequestDetails();
            details.alertIds = alertIds;

            // Convert the details into JSON and persist.
            var jsonDetails = details.ToJson();
            WriteData(lastRequestDetailsBlobKey, jsonDetails, log);
        }

        // Get the alerts IDs present in the last request.
        private static HashSet<string> GetLastRequestAlertIds(ILogger log)
        {
            var details = GetLastRequestDetails(log);
            return details.alertIds;
        }

        [FunctionName("IncidentProducer")]
        public static async Task RunAsync(
#if DEBUG
            [TimerTrigger("*/30 * * * * *")] TimerInfo myTimer,
#else
            [TimerTrigger("0 */5 * * * *")]TimerInfo myTimer,
#endif
            [Queue("cohesity-incidents"), StorageAccount("AzureWebJobsStorage")] ICollector<string> outputQueueItem,
            ILogger log)
        {
            log.LogInformation($"C# Timer trigger function executed at: {DateTime.Now}");
            long startDateUsecs = 0;
            long endDateUsecs = GetCurrentUnixTime();
            HashSet<string> previousAlertIds = new HashSet<string>();

            try
            {
                bool hasException = false;
                try
                {
                    previousAlertIds = GetLastRequestAlertIds(log);
                }
                catch (Exception ex)
                {
                    hasException = true;
                    log.LogError("lastRequestDetailsBlobKey Exception --> " + lastRequestDetailsBlobKey);
                    log.LogError("Exception --> " + ex.Message);
                }

                if (hasException)
                {
                    startDateUsecs = GetFirstFetchStartTimeUsecs(log);
                }
                else
                {
                    startDateUsecs = GetPeriodicFetchStartTimeUsecs(log);
                }

                log.LogInformation("startDateUsecs --> " + startDateUsecs);
                log.LogInformation("endDateUsecs --> " + endDateUsecs.ToString());

                string requestUriString = $"https://helios.cohesity.com/mcm/alerts?alertCategoryList=kSecurity&alertStateList=kOpen&startDateUsecs={startDateUsecs}&endDateUsecs={endDateUsecs}";
                log.LogInformation("requestUriString --> " + requestUriString);
                using HttpClient client = new();
                client.DefaultRequestHeaders.Accept.Clear();
                client.DefaultRequestHeaders.Add("apiKey", GetSecret("ApiKey", log));
                await using Stream stream = await client.GetStreamAsync(requestUriString);
                StreamReader reader = new StreamReader(stream);
                string jsonResult = reader.ReadToEnd();
                // log.LogInformation("Helios response: " + jsonResult);
                dynamic alerts = JsonConvert.DeserializeObject(jsonResult);

                var tasks = new List<Task>();

                if (hasException)
                {
                    log.LogInformation("Adding welcome alert to the queue");
                    AddWelcomeAlertToQueue(outputQueueItem);
                }

                int alerts_received = 0;
                int alerts_skipped = 0;
                foreach (var alert in alerts)
                {
                    ++alerts_received;
                    // Skip adding this alert to the queue if we already saw
                    // this alert in the last request.
                    if (previousAlertIds.Contains(((string)alert.id)))
                    {
                        ++alerts_skipped;
                        log.LogInformation("Skipping alert " + ((string)alert.id) + " as this was seen in the last request");
                        continue;
                    }

                    tasks.Add(Task.Run(async () =>
                    {
                        await ParseAlertToQueue(outputQueueItem, alert, log);
                    }));
                }

                log.LogInformation("Alerts received: " + alerts_received.ToString() +
                                    ", Alerts skipped: " + alerts_skipped.ToString());
                Task t = Task.WhenAll(tasks);
                try
                {
                    t.Wait();
                }
                catch { }

                if (t.Status == TaskStatus.RanToCompletion)
                {
                    WriteRequestDetails(alerts, log);
                }
                else
                {
                    log.LogError("Some tasks did not finish successfully");
                }
            }
            catch (Exception ex)
            {
                log.LogError("Exception --> 3 " + ex.Message);
            }
        }

        private static void AddWelcomeAlertToQueue([Queue("cohesity-incidents"), StorageAccount("AzureWebJobsStorage")] ICollector<string> outputQueueItem)
        {
            string title = "Hello from Cohesity!";
            string description = "This is a test incident that confirms that the Cohesity function app installation has completed correctly. This is NOT a ransomware-related incident.";
            string severity = "Low";

            dynamic incident = ConstructIncident(title, description, severity);

            lock (queueLock)
            {
                outputQueueItem.Add(JsonConvert.SerializeObject(incident));
            }
        }

        private static string GetSecret(string secretName, ILogger log)
        {
            var kvUri = $"https://{IncidentProducer.keyVaultName}.vault.azure.net";
            try
            {
                var secretClient = new SecretClient(new Uri(kvUri), new DefaultAzureCredential());
                return secretClient.GetSecret(secretName).Value.Value;
            }
            catch (Exception ex)
            {
                log.LogError("secretName Exception --> 4 " + secretName);
                log.LogError("kvUri Exception --> 4 " + kvUri);
                log.LogError("Exception --> 4 " + ex.Message);
                return null;
            }
        }
    }
}
