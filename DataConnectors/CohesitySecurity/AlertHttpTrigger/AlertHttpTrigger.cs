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
            DateTime previousDateTime = DateTime.Now.AddDays(long.Parse(Environment.GetEnvironmentVariable("startDaysAgo")));
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

        [FunctionName("func-cohesity-duplicate-alerts-filter-prod-003")]
        public static async Task<IActionResult> Run(
            [HttpTrigger(AuthorizationLevel.Function, "get", "post", Route = null)] HttpRequest req,
            ILogger log)
        {
            log.LogInformation("C# HTTP trigger function processed a request.");
            long startDateUsecs = 0;

            try
            {
                var db = Connection.GetDatabase();
                string apiKey = req.Query["apiKey"].ToString() != String.Empty
                                ? req.Query["apiKey"]
                                : Environment.GetEnvironmentVariable("apiKey");

                if (req.Query["resetRedis"] == "1")
                {
                    db.StringSet(apiKey, 0);
                }

                try
                {
                    startDateUsecs = long.Parse(db.StringGet(apiKey));
                }
                catch  (Exception ex)
                {
                    startDateUsecs = GetPreviousUnixTime();
                    log.LogError("Exception --> 1" + ex.Message);
                }

                if (startDateUsecs == 0)
                {
                    startDateUsecs = GetPreviousUnixTime();
                }

                log.LogInformation ("startDateUsecs --> " + startDateUsecs);

                long endDateUsecs = GetCurrentUnixTime();
                log.LogInformation ("endDateUsecs --> " + endDateUsecs.ToString());
                db.StringSet(apiKey, endDateUsecs.ToString());

                string requestUriString = $"https://helios.cohesity.com/mcm/alerts?alertCategoryList=kSecurity&alertStateList=kOpen&startDateUsecs={startDateUsecs}&endDateUsecs={endDateUsecs}";
                log.LogInformation("requestUriString --> " + requestUriString);
                using HttpClient client = new ();
                client.DefaultRequestHeaders.Accept.Clear();
                client.DefaultRequestHeaders.Add("apiKey", System.Environment.GetEnvironmentVariable("apiKey"));
                await using Stream stream = await client.GetStreamAsync(requestUriString);

                StreamReader reader = new StreamReader(stream);
                string text = reader.ReadToEnd();
                return new OkObjectResult(text);

            }
            catch  (Exception ex)
            {
                log.LogError("Exception --> 2" + ex.Message);
            }

            return new OkObjectResult("[]");
        }
    }
}
