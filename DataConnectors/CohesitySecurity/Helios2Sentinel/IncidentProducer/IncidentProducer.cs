using Microsoft.AspNetCore.Http;
using Microsoft.AspNetCore.Mvc;
using Microsoft.Azure.WebJobs.Extensions.Http;
using Microsoft.Azure.WebJobs.Host;
using Microsoft.Azure.WebJobs;
using Microsoft.Extensions.Configuration;
using Microsoft.Extensions.Logging;
using Newtonsoft.Json.Linq;
using Newtonsoft.Json;
using StackExchange.Redis;
using System.Collections.Generic;
using System.Collections;
using System.IO;
using System.Net.Http.Headers;
using System.Net.Http;
using System.Net;
using System.Text.Json;
using System.Text;
using System.Threading.Tasks;
using System;
using System.Dynamic;
using Newtonsoft.Json.Converters;
using Microsoft.WindowsAzure.Storage;
using Helios2Sentinel;

namespace Helios2Sentinel
{
    public class IncidentProducer
    {
        private static readonly object queueLock = new object();
        private static Lazy<ConnectionMultiplexer> lazyConnection = CreateConnection();
        public static long GetPreviousUnixTime(ILogger log)
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

        public static long GetCurrentUnixTime()
        {
            return ((DateTimeOffset)DateTime.Now).ToUnixTimeMilliseconds() * 1000;
        }

        public static ConnectionMultiplexer Connection
        {
            get
            {
                return lazyConnection.Value;
            }
        }

        private static Lazy<ConnectionMultiplexer> CreateConnection()
        {
            return new Lazy<ConnectionMultiplexer>(() =>
            {
                return ConnectionMultiplexer.Connect(Environment.GetEnvironmentVariable("connectStr"));
            });
        }

        public static async Task ParseAlertToQueueAsync(
            [Queue("%CohesityQueueName%"), StorageAccount("AzureWebJobsStorage")] ICollector<string> outputQueueItem,
            dynamic alert, ILogger log)
        {
            dynamic output = new ExpandoObject();
            output.properties = new ExpandoObject();
            output.properties.Description = alert.alertDocument.alertDescription + ". Alert cause: " + alert.alertDocument.alertCause + ". Additional Info: " + alert.alertDocument.alertHelpText + ". Helios ID: " + alert.id;
            output.properties.title = "Cluster: " + alert.clusterName;
            output.properties.status = ((string)alert.alertState).Equals("kOpen", StringComparison.OrdinalIgnoreCase) ? "New" : "Closed";
            output.properties.severity = "Medium";

            string id = alert.id;
            int i = 0;

            foreach (var prop in alert.propertyList)
            {
                switch (i)
                {
                case 12:
                    long sev = long.Parse((string)prop.value);
                    if (sev >= 70)
                        output.properties.severity = "High";
                    else if (sev < 30)
                        output.properties.severity = "Low";
                    else
                        output.properties.severity = "Medium";
                    break;
                case 0:
                case 10:
                case 4:
                case 7:
                case 11:
                    TextWriter(id, (string)prop.key, (string)prop.value, log);
                    break;
                case 1:
                    output.properties.title += ". Object: " + prop.value;
                    TextWriter(id, (string)prop.key, (string)prop.value, log);
                    break;
                case 3:
                    output.properties.title += ". Source: " + prop.value;
                    break;
                }
                i++;
                if (i == 13) break;
            }

            lock (queueLock)
            {
                outputQueueItem.Add(JsonConvert.SerializeObject(output));
            }
        }

        private static void WriteData(string storageConnectionString, string containerName, string path, string data)
        {
            if (CloudStorageAccount.TryParse(storageConnectionString, out var storageAccount))
            {
                // Create the CloudBlobClient that represents the Blob storage endpoint for the storage account.
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

        private static void TextWriter(string incidentID, string param, string value, ILogger log)
        {
            try
            {
                const string container = "extra-parameters";
                string Blob = incidentID + "\\" + param; // ID unique to the incident
                var blobStorageConnectionString = Environment.GetEnvironmentVariable("BlobStorageConnectionString");
                var blobStorageKeys = Environment.GetEnvironmentVariable("BlobStorageAccountKeys");
                WriteData(blobStorageConnectionString, container, Blob, value);
            }
            catch (Exception ex)
            {
                log.LogError("Exception --> " + ex.Message);
            }
        }

        [FunctionName("IncidentProducer")]
        public static async Task RunAsync(
#if DEBUG
            [TimerTrigger("*/30 * * * * *")] TimerInfo myTimer,
#else
            [TimerTrigger("* */5 * * * *")]TimerInfo myTimer,
#endif
            [Queue("%CohesityQueueName%"), StorageAccount("AzureWebJobsStorage")] ICollector<string> outputQueueItem,
            ILogger log)
        {
            log.LogInformation($"C# Timer trigger function executed at: {DateTime.Now}");
            long startDateUsecs = 0;

            try
            {
                var db = Connection.GetDatabase();
                string apiKey = Environment.GetEnvironmentVariable("apiKey");
                string redisKey = Environment.GetEnvironmentVariable("workspace") + apiKey;

                try
                {
                    startDateUsecs = long.Parse(db.StringGet(redisKey));
                }
                catch (Exception ex)
                {
                    startDateUsecs = GetPreviousUnixTime(log);
                    log.LogError("Exception --> 2 " + ex.Message);
                }

                if (startDateUsecs == 0)
                {
                    startDateUsecs = GetPreviousUnixTime(log);
                }

                log.LogInformation("startDateUsecs --> " + startDateUsecs);

                long endDateUsecs = GetCurrentUnixTime();
                log.LogInformation("endDateUsecs --> " + endDateUsecs.ToString());

                string requestUriString = $"https://helios.cohesity.com/mcm/alerts?alertCategoryList=kSecurity&alertStateList=kOpen&startDateUsecs={startDateUsecs}&endDateUsecs={endDateUsecs}";
                log.LogInformation("requestUriString --> " + requestUriString);
                using HttpClient client = new ();
                client.DefaultRequestHeaders.Accept.Clear();
                client.DefaultRequestHeaders.Add("apiKey", System.Environment.GetEnvironmentVariable("apiKey"));
                await using Stream stream = await client.GetStreamAsync(requestUriString);
                StreamReader reader = new StreamReader(stream);
                dynamic alerts = JsonConvert.DeserializeObject(reader.ReadToEnd());

                foreach (var alert in alerts)
                {
                    await ParseAlertToQueueAsync(outputQueueItem, alert, log);
                }

                db.StringSet(redisKey, endDateUsecs.ToString());
                log.LogInformation("new startDateUsecs --> " + endDateUsecs.ToString());
            }
            catch (Exception ex)
            {
                log.LogError("Exception --> 3 " + ex.Message);
            }
        }
    }
}
