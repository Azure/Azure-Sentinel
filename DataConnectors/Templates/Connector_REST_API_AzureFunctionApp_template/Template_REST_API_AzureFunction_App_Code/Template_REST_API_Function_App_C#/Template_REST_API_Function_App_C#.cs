// <#  
//     Title:          Azure Function App TEMPLATE - <PROVIDER NAME APPLIANCE NAME> API Ingestion to Microsoft Sentinel   
//     Language:       C#
//     Version:        1.0
//     Last Modified:  09/03/2023
//     Comment:        Inital Release

//     DESCRIPTION:    The following C# Function App code is an example of a data connector to pull logs from your <PROVIDER NAME APPLIANCE NAME> API, transform the data logs into a Microsoft Sentinel acceptable format (JSON) and POST the logs to the 
//                     Microsoft Sentinel workspace using the Azure Log Analytics Data Collector API. Refer this example to create a file with specific code needed to authenticate to the <PROVIDER NAME APPLIANCE NAME> API and format the data received into JSON format.
// #>

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
            dynamic output = new ExpandoObject();
            output.properties = new ExpandoObject();
            output.properties.title = "Cluster: " + alert.clusterName;
            output.properties.status = ((string)alert.alertState).Equals("kOpen", StringComparison.OrdinalIgnoreCase) ? "New" : "Closed";
            output.properties.severity = "Medium";

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
                    output.properties.title += ". Object: " + prop.value;
                    WriteData(id + "\\" + (string)prop.key, (string)prop.value, log);
                    break;
                case 3:
                    output.properties.title += ". Source: " + prop.value;
                    break;
                case 12:
                    sev = long.Parse((string)prop.value);

                    if (sev >= 70)
                        output.properties.severity = "High";
                    else if (sev < 30)
                        output.properties.severity = "Low";
                    else
                        output.properties.severity = "Medium";
                    break;
                }
                i++;
                if (i == 13) break;
            }
            output.properties.Description = alert.alertDocument.alertDescription + ". Alert cause: " + alert.alertDocument.alertCause + ". Anomaly Strength: " + sev + ". Additional Info: " + alert.alertDocument.alertHelpText + ". Helios ID: " + alert.id;

            lock (queueLock)
            {
                outputQueueItem.Add(JsonConvert.SerializeObject(output));
            }

            return Task.CompletedTask;
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
                string apiKey = GetSecret("ApiKey", log);
                string blobKey = Environment.GetEnvironmentVariable("Workspace") + "\\" + apiKey;
                bool hasException = false;

                try
                {
                    startDateUsecs = long.Parse(GetData(blobKey, log));
                }
                catch (Exception ex)
                {
                    hasException = true;
                    WriteData(blobKey, endDateUsecs.ToString(), log);
                    log.LogError("apiKey Exception --> 2 " + apiKey);
                    log.LogError("blobKey Exception --> 2 " + blobKey);
                    log.LogError("Exception --> 2 " + ex.Message);
                }

                if (startDateUsecs == 0 || hasException)
                {
                    TestAlertToQueue(outputQueueItem);
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

        private static void TestAlertToQueue([Queue("cohesity-incidents"), StorageAccount("AzureWebJobsStorage")] ICollector<string> outputQueueItem)
        {
            dynamic output = new ExpandoObject();
            output.properties = new ExpandoObject();
            output.properties.title = "Test Incident";
            output.properties.Description = "This is a test incident that confirms that the installation has completed correctly.";
            output.properties.severity = "Low";

            lock (queueLock)
            {
                outputQueueItem.Add(JsonConvert.SerializeObject(output));
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
