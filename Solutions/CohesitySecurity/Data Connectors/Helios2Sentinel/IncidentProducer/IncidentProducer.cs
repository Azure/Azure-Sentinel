using Azure.Identity;
using Azure.Security.KeyVault.Secrets;
using Helios2Sentinel;
using Microsoft.AspNetCore.Http;
using Microsoft.AspNetCore.Mvc;
using Microsoft.Azure.WebJobs.Extensions.Http;
using Microsoft.Azure.WebJobs.Host;
using Microsoft.Azure.WebJobs;
using Microsoft.Extensions.Configuration;
using Microsoft.Extensions.Logging;
using Microsoft.WindowsAzure.Storage;
using Newtonsoft.Json.Converters;
using Newtonsoft.Json.Linq;
using Newtonsoft.Json;
using System.Collections.Generic;
using System.Collections;
using System.Dynamic;
using System.IO;
using System.Net.Http.Headers;
using System.Net.Http;
using System.Net;
using System.Text.Json;
using System.Text;
using System.Threading.Tasks;
using System;

namespace Helios2Sentinel
{
    public class IncidentProducer
    {
        private static string keyVaultName = Environment.GetEnvironmentVariable("keyVaultName");
        private static string azureWebJobsStorage = Environment.GetEnvironmentVariable("AzureWebJobsStorage");
        private static readonly object queueLock = new object();
        private static string containerName = "cohesity-extra-parameters";

        public static long GetPreviousUnixTime(ILogger log)
        {
            DateTime previousDateTime = DateTime.Now;
            try
            {
                previousDateTime = previousDateTime.AddDays(long.Parse(Environment.GetEnvironmentVariable("startDaysAgo")));
            }
            catch  (Exception ex)
            {
                previousDateTime = previousDateTime.AddDays(-30);
                log.LogError("Exception --> 1 " + ex.Message);
            }
            return ((DateTimeOffset)previousDateTime).ToUnixTimeMilliseconds() * 1000;
        }

        public static long GetCurrentUnixTime()
        {
            return ((DateTimeOffset)DateTime.Now).ToUnixTimeMilliseconds() * 1000;
        }

        public static Task ParseAlertToQueue(
            [Queue("cohesity-incidents"), StorageAccount("AzureWebJobsStorage")] ICollector<string> outputQueueItem,
            dynamic alert, ILogger log)
        {
            string title = "Cluster: " + alert.clusterName;
            string severity = "Medium";

            string id = alert.id;
            int i = 0;
            long sev = 70;

            foreach (var prop in alert.propertyList)
            {
                switch (i)
                {
                case 0:
                case 4:
                case 7:
                case 10:
                case 11:
                    WriteData(id + "\\" + (string)prop.key, (string)prop.value, log);
                    break;
                case 1:
                    title += ". Object: " + prop.value;
                    WriteData(id + "\\" + (string)prop.key, (string)prop.value, log);
                    break;
                case 3:
                    title += ". Source: " + prop.value;
                    break;
                case 12:
                    sev = long.Parse((string)prop.value);

                    if (sev >= 70)
                        severity = "High";
                    else if (sev < 30)
                        severity = "Low";
                    else
                        severity = "Medium";
                    break;
                }
                i++;
                if (i == 13) break;
            }
            string description = alert.alertDocument.alertDescription + ". Alert cause: " + alert.alertDocument.alertCause + ". Anomaly Strength: " + sev + ". Additional Info: " + alert.alertDocument.alertHelpText + ". Helios ID: " + alert.id;

            dynamic incident = ConstructIncident(title, description, severity);
            lock (queueLock)
            {
                outputQueueItem.Add(JsonConvert.SerializeObject(incident));
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

            try
            {
                string blobKey = Environment.GetEnvironmentVariable("Workspace") + "\\last-request-end-time-usecs";
                bool hasException = false;

                try
                {
                    startDateUsecs = long.Parse(GetData(blobKey, log));
                }
                catch (Exception ex)
                {
                    hasException = true;
                    WriteData(blobKey, endDateUsecs.ToString(), log);
                    log.LogError("blobKey Exception --> " + blobKey);
                    log.LogError("Exception --> " + ex.Message);
                }

                if (startDateUsecs == 0 || hasException)
                {
                    log.LogInformation("Adding welcome alert to the queue");
                    AddWelcomeAlertToQueue(outputQueueItem);
                    startDateUsecs = GetPreviousUnixTime(log);
                }

                log.LogInformation("startDateUsecs --> " + startDateUsecs);

                log.LogInformation("endDateUsecs --> " + endDateUsecs.ToString());

                string requestUriString = $"https://helios.cohesity.com/mcm/alerts?alertCategoryList=kSecurity&alertStateList=kOpen&startDateUsecs={startDateUsecs}&endDateUsecs={endDateUsecs}";
                log.LogInformation("requestUriString --> " + requestUriString);
                using HttpClient client = new ();
                client.DefaultRequestHeaders.Accept.Clear();
                client.DefaultRequestHeaders.Add("apiKey", GetSecret("ApiKey", log));
                await using Stream stream = await client.GetStreamAsync(requestUriString);
                StreamReader reader = new StreamReader(stream);
                dynamic alerts = JsonConvert.DeserializeObject(reader.ReadToEnd());

                var tasks = new List<Task>();

                foreach (var alert in alerts)
                {
                    tasks.Add(Task.Run(async () =>
                    {
                        await ParseAlertToQueue(outputQueueItem, alert, log);
                    }));
                }
                Task t = Task.WhenAll(tasks);
                try
                {
                    t.Wait();
                }
                catch { }

                if (!hasException && t.Status == TaskStatus.RanToCompletion)
                {
                    WriteData(blobKey, endDateUsecs.ToString(), log);
                }
                log.LogInformation("new startDateUsecs --> " + endDateUsecs.ToString());
            }
            catch  (Exception ex)
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
            catch  (Exception ex)
            {
                log.LogError("secretName Exception --> 4 " + secretName);
                log.LogError("kvUri Exception --> 4 " + kvUri);
                log.LogError("Exception --> 4 " + ex.Message);
                return  null;
            }
        }
    }
}
