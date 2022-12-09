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

namespace Helios2Sentinel
{
    public class IncidentProducer
    {
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

        public static void ParseAlertToQueue(
            [Queue("%CohesityQueueName%"), StorageAccount("AzureWebJobsStorage")] ICollector<string> outputQueueItem,
            dynamic alert)
        {
            dynamic output = new ExpandoObject();
            output.properties = new ExpandoObject();
            output.properties.Description = alert.alertDocument.alertDescription + ". Alert cause: " + alert.alertDocument.alertCause + ". Additional Info: " + alert.alertDocument.alertHelpText + ". Helios ID: " + alert.id;
            output.properties.title = "Cluster: " + alert.clusterName;
            output.properties.status = ((string)alert.alertState).Equals("kOpen", StringComparison.OrdinalIgnoreCase) ? "New" : "Closed";
            output.properties.severity = "Medium";

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
                case 1:
                    output.properties.title += ". Object: " + prop.value;
                    break;
                case 3:
                    output.properties.title += ". Source: " + prop.value;
                    break;
                }
                i++;
                if (i == 13) break;
            }
            outputQueueItem.Add(JsonConvert.SerializeObject(output));
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
                using HttpClient client = new ();
                client.DefaultRequestHeaders.Accept.Clear();
                client.DefaultRequestHeaders.Add("apiKey", System.Environment.GetEnvironmentVariable("apiKey"));
                await using Stream stream = await client.GetStreamAsync(requestUriString);
                StreamReader reader = new StreamReader(stream);
                dynamic alerts = JsonConvert.DeserializeObject(reader.ReadToEnd());

                var tasks = new List<Task>();

                foreach (var alert in alerts)
                {
                    tasks.Add(Task.Run( () =>
                    {
                        ParseAlertToQueue(outputQueueItem, alert);
                    }));
                }
                Task t = Task.WhenAll(tasks);
                try
                {
                    t.Wait();
                }
                catch {}

                if (t.Status == TaskStatus.RanToCompletion)
                {
                db.StringSet(redisKey, endDateUsecs.ToString());
            }
            }
            catch (Exception ex)
            {
                log.LogError("Exception --> 3 " + ex.Message);
            }
        }
    }
}
