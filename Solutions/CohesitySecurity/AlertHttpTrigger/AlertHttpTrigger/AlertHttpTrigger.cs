using Microsoft.AspNetCore.Http;
using Microsoft.AspNetCore.Mvc;
using Microsoft.Azure.WebJobs.Extensions.Http;
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

namespace AlertHttpTrigger
{
    public static class AlertHttpTrigger
    {
        private static Lazy<ConnectionMultiplexer> lazyConnection = CreateConnection();

        public static long GetPreviousUnixTime()
        {
            DateTime previousDateTime = DateTime.Now.AddDays(-30);
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
                return ConnectionMultiplexer.Connect($"cohesity.redis.cache.windows.net:6380,password=cUdpmdeSMkF7NSFnnfPdloHQius2y52ivAzCaAe9akI=,ssl=True,abortConnect=False");
            });
        }

        [FunctionName("func-cohesity_duplicate_alerts_filter-prod-002")]
        public static async Task<IActionResult> Run(
            [HttpTrigger(AuthorizationLevel.Function, "get", "post", Route = null)] HttpRequest req,
            ILogger log)
        {
            log.LogInformation("C# HTTP trigger function processed a request.");
            long startDateUsecs = 0;

            try
            {
                var db = Connection.GetDatabase();
                var key = "cUdpmdeSMkF7NSFnnfPdloHQius2y52ivAzCaAe9akI=";

                try
                {
                    startDateUsecs = long.Parse(db.StringGet(key));
                }
                catch  (Exception ex)
                {
                    startDateUsecs = GetPreviousUnixTime();
                    log.LogError("Exception: " + ex.Message);
                }

                if (startDateUsecs == 0)
                {
                    startDateUsecs = GetPreviousUnixTime();
                }

                log.LogInformation ("startDateUsecs --> " + startDateUsecs);

                long endDateUsecs = GetCurrentUnixTime();
                db.StringSet(key, endDateUsecs.ToString());

                string requestUriString = $"https://helios.cohesity.com/mcm/alerts?alertCategoryList=kSecurity&alertStateList=kOpen&startDateUsecs={startDateUsecs}&endDateUsecs={endDateUsecs}";
                using HttpClient client = new ();
                client.DefaultRequestHeaders.Accept.Clear();
                client.DefaultRequestHeaders.Add("apiKey", System.Environment.GetEnvironmentVariable("apiKey"));
                await using Stream stream = await client.GetStreamAsync(requestUriString);

                StreamReader reader = new StreamReader(stream);
                string text = reader.ReadToEnd();

                if (!string.IsNullOrEmpty(text) && !string.IsNullOrWhiteSpace(text) && !text.Trim().Equals("[]"))
                {
                    log.LogInformation("requestUriString --> " + requestUriString);
                }

                return new OkObjectResult(text);

            }
            catch  (Exception ex)
            {
                log.LogError("Exception: " + ex.Message);
            }

            return new OkObjectResult("[]");
        }
    }
}
