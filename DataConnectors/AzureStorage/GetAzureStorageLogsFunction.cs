// Copyright (c) Microsoft Corporation.
// Licensed under the MIT license.
#region Includes
using System;
using System.Collections.Concurrent;
using System.Collections.Generic;
using System.Globalization;
using System.IO;
using System.Linq;
using System.Text;
using System.Threading;
using System.Threading.Tasks;
using CsvHelper;
using CsvHelper.Configuration;
using Microsoft.Azure.Storage;
using Microsoft.Azure.Storage.Blob;
using Microsoft.Azure.WebJobs;
using Microsoft.Extensions.Logging; 
#endregion

namespace HoneyBucketLogParser
{
    /// <summary>
    /// Represents a LogMessage from Azure Storage Diagnostics
    /// </summary>
    [Serializable]
    public class LogMessage
    {
        public string RequestTime;
        public string OriginIP;
        public string URL;
        public string RequestType;
        public string UserAgent;

        public override bool Equals(object obj)
        {
            if (obj is LogMessage)
            {
                var otherLog = obj as LogMessage;
                return this.RequestTime == otherLog.RequestTime &&
                       this.RequestType == otherLog.RequestTime &&
                       this.OriginIP == otherLog.OriginIP &&
                       this.URL == otherLog.URL &&
                       this.UserAgent == otherLog.UserAgent;
            }
            return false;
        }

        public override int GetHashCode()
        {
            return (RequestTime + URL + RequestType + OriginIP.ToString()).GetHashCode();
        }
    }

    /// <summary>
    /// Function to get Azure Storage logs, parse the results and add to an Azure Sentinel Workspace.
    /// </summary>
    public static class GetAzureStorageLogsFunction
    {
        /// <summary>
        /// Gets data from Azure Blob storage
        /// </summary>
        /// <param name="storageConnectionString">The Azure blob storage connections string</param>
        /// <param name="containerName">The name of the container</param>
        /// <param name="path">The path to the blob</param>
        /// <returns>File contents</returns>
        private static string GetData(string storageConnectionString, string containerName, string path)
        {
            if (CloudStorageAccount.TryParse(storageConnectionString, out var storageAccount))
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

        /// <summary>
        /// Writes data to Azure Blob storage
        /// </summary>
        /// <param name="storageConnectionString">The Azure blob storage connections string</param>
        /// <param name="containerName">The name of the container</param>
        /// <param name="path">The path to the blob</param>
        /// <param name="data">The data to write</param>
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

        [FunctionName("GetAzureStorageLogsFunction")]
        public static void Run([TimerTrigger("0 * * * * *")]TimerInfo myTimer, ILogger log)
        {
            try
            {
                const string Format = @"<version-number>;<request-start-time>;<operation-type>;<request-status>;<http-status-code>;<end-to-end-latency-in-ms>;<server-latency-in-ms>;<authentication-type>;<requester-account-name>;<owner-account-name>;<service-type>;<request-url>;<requested-object-key>;<request-id-header>;<operation-count>;<requester-ip-address>;<request-version-header>;<request-header-size>;<request-packet-size>;<response-header-size>;<response-packet-size>;<request-content-length>;<request-md5>;<server-md5>;<etag-identifier>;<last-modified-time>;<conditions-used>;<user-agent-header>;<referrer-header>;<client-request-id>";
                const string ConnectionStringFormat = "DefaultEndpointsProtocol=https;AccountName={0};AccountKey={1};EndpointSuffix=core.windows.net";
                const string container = "statedata";
                const string Blob = "state";
                const string FormatString = "yyyy-MM-ddTHH:mm:ss.fffffffZ";
                const string LogAnalyticsTableName = "HoneyBucketLogs";

                log.LogInformation($"C# Timer trigger function executed at: {DateTime.Now}");

                var blobStorageConnectionString = Environment.GetEnvironmentVariable("BlobStorageConnectionString");
                var blobStorageKeys = Environment.GetEnvironmentVariable("BlobStorageAccountKeys");
                var logAnalyticsKey = Environment.GetEnvironmentVariable("LogAnalyticsKey");
                var logAnalyticsWorkspace = Environment.GetEnvironmentVariable("LogAnalyticsWorkspace");

                log.LogInformation("BlobStorageConnectionString " + blobStorageConnectionString);
                log.LogInformation("BlobStorageAccountKeys " + blobStorageKeys);
                log.LogInformation("LogAnalyticsKey " + logAnalyticsKey);
                log.LogInformation("LogAnalyticsWorkspace " + logAnalyticsWorkspace);

                foreach (var setting in new string[] { logAnalyticsWorkspace, logAnalyticsKey, blobStorageKeys, blobStorageConnectionString })
                {
                    if (string.IsNullOrWhiteSpace(setting) || setting.StartsWith("http") || setting.StartsWith("@Microsoft.KeyVault"))
                    {
                        log.LogError("Invalid setting detected " + setting);
                        log.LogError("Please see https://docs.microsoft.com/en-us/azure/app-service/app-service-key-vault-references");
                        throw new InvalidOperationException("Invalid setting");
                    }
                }

                // according to the docs here: https://docs.microsoft.com/en-us/azure/storage/common/storage-analytics-logging
                // it can take up to an hour for logs to hit blob storage. As such need to keep a list of timestamps of the last
                // entry we've seen
                var lastLogEntryProcessedTime = new ConcurrentDictionary<string, DateTime>();

                try
                {
                    var lastReadTimeStr = GetData(blobStorageConnectionString, container, Blob);
                    log.LogInformation("Read time as " + lastReadTimeStr);

                    lastReadTimeStr.Split(";").ToList().ForEach(x =>
                    {
                        var split = x.Split('='); lastLogEntryProcessedTime.TryAdd(split[0], DateTime.ParseExact(split[1], FormatString, null));
                    });
                }
                catch (Exception ex)
                {
                    log.LogError(ex, "Could not get or parse state, did you forget to create the state file? "+ex.GetType().Name);
                }

                var fields = Format.Split(';');
                var fieldList = fields.Select(x => x.Substring(1, x.Length - 2)).ToList();

                var config = new CsvConfiguration(CultureInfo.InvariantCulture)
                {
                    Delimiter = ";",
                    Escape = '"',
                    IgnoreQuotes = false,
                    HasHeaderRecord = false,
                };

                // build a list of storage accounts to pull the diagnostic logs from
                var connections = blobStorageKeys
                    .Split(";")
                    .ToList()
                    .ConvertAll(x =>
                    {
                        var unameKeyStr = x.Split(':');
                        var kvp = new KeyValuePair<string, string>(unameKeyStr[0], unameKeyStr[1]);
                        if (!lastLogEntryProcessedTime.ContainsKey(kvp.Key))
                        {
                            lastLogEntryProcessedTime.TryAdd(kvp.Key, DateTime.UtcNow.AddDays(-2));
                        }
                        return kvp;
                    });

                log.LogInformation($"Getting streams for " + connections.Count + " connections");

                var whiteListedIps = new ConcurrentDictionary<string, byte>();
                var honeybucketrawlogs = new ConcurrentBag<LogMessage>();
                var rawLogMessages = new ConcurrentBag<Tuple<string, string>>();

                // Here we create two tasks
                // * getLogsTask - Get logs from blob storage
                // * processLogsTask - Convert logs to CSV entries and process

                var getLogsTask = Task.Run(() =>
                {
                    Parallel.ForEach(connections, (connection) =>
                    {
                    // By storing some state we can massively reduce the amount of log processing we do, here
                    // we only retrieve logs that are recent
                    var from = lastLogEntryProcessedTime[connection.Key].AddHours(-1);
                        var to = DateTime.UtcNow.AddHours(1);

                        var blobs = LogDownloader.DownloadStorageLogs(
                            string.Format(ConnectionStringFormat, connection.Key, connection.Value),
                            "blob",
                            from, // don't want to miss any logs
                            to);

                        log.LogInformation(string.Format("Getting {0} log from {1} to {2}", connection.Key, from, to));

                        foreach (var blob in blobs)
                        {
                        // There is no point downloading more logs if the output queue is still full of data to process
                        // we need to back off here and wait for the queue to reduce.
                        while (rawLogMessages.Count >= 1000)
                            {
                                var rand = new Random();
                            // back off a random time in ms.
                            Task.Delay(rand.Next(0, 1000)).Wait();
                            }

                            try
                            {
                                using (var reader = new StreamReader(blob.OpenRead())) // underlying stream is closed by StreamReader
                            {
                                    var text = reader.ReadToEnd();
                                    rawLogMessages.Add(new Tuple<string, string>(connection.Key, text));
                                }
                            }
                            catch (Exception ex)
                            {
                                log.LogError(ex, "Error in getLogsTask: " + ex.Message);
                            }
                        }

                        log.LogInformation(string.Format("Finished getting {0} log from {1} to {2}", connection.Key, from, to));
                    });
                });

                var processLogsTask = Task.Run(() =>
                {
                    while (!getLogsTask.IsCompleted)
                    {
                        while (rawLogMessages.TryTake(out Tuple<string, string> value))
                        {
                            using (var sr = new StringReader(value.Item2))
                            using (var csv = new CsvReader(sr, config))
                            {
                                while (csv.Read())
                                {
                                    var logentry = new List<KeyValuePair<string, string>>();
                                    for (int c = 0; c < fieldList.Count(); c++)
                                    {
                                        logentry.Add(new KeyValuePair<string, string>(fieldList[c], csv.GetField(c)));
                                    }

                                //request-start-time
                                var requestTime = logentry.Where(x => x.Key == "request-start-time").First().Value;
                                    var requestDateTime = DateTime.ParseExact(requestTime, FormatString, null);

                                // first check to ensure we are not processing any old log entries
                                // if we are we can bail out here
                                if (requestDateTime <= lastLogEntryProcessedTime[value.Item1])
                                    {
                                        return;
                                    }

                                    lastLogEntryProcessedTime.AddOrUpdate(
                                        value.Item1,
                                        requestDateTime,
                                        (key, oldValue) =>
                                        {
                                            if (requestDateTime > oldValue)
                                            {
                                                return requestDateTime;
                                            }
                                            else
                                            {
                                                return requestDateTime;
                                            }
                                        }
                                    );

                                // now we have a full logentry to process
                                var operationType = logentry.Where(x => x.Key == "operation-type").First().Value;

                                    switch (operationType)
                                    {
                                        case "PutBlob":
                                            var ip = logentry.Where(x => x.Key == "requester-ip-address").Select(kvp => kvp.Value.Substring(0, kvp.Value.IndexOf(':'))).First();
                                            whiteListedIps.TryAdd(ip, 0);
                                            break;
                                        case "ListBlobs":
                                        case "ListContainers":
                                        case "GetBlob":
                                        case "GetBlobProperties":
                                        case "GetContainerProperties":
                                        case "GetContainerACL":
                                            var msg = new LogMessage()
                                            {
                                                RequestTime = requestTime,
                                                URL = logentry.Where(x => x.Key == "request-url").First().Value,
                                                OriginIP = logentry.Where(x => x.Key == "requester-ip-address").Select(kvp => kvp.Value.Substring(0, kvp.Value.IndexOf(':'))).First(),
                                                RequestType = logentry.Where(x => x.Key == "operation-type").First().Value,
                                                UserAgent = logentry.Where(x => x.Key == "user-agent-header").First().Value
                                            };

                                            if (whiteListedIps.ContainsKey(msg.OriginIP))
                                            {
                                            // already whitelisted
                                            break;
                                            }

                                        //authentication-type
                                        var authtype = logentry.Where(x => x.Key == "authentication-type").First().Value;

                                        // Microsoft Azure Storage Explorer actively enumerates all the files in the
                                        // bucket & generates a lot of log entries. We want to ignore this because if someone has my sub in their
                                        // list and opens up this tool then I get a load of FPs
                                        if (msg.UserAgent.Contains("Microsoft Azure Storage Explorer") && authtype == "authenticated")
                                            {
                                                whiteListedIps.TryAdd(msg.OriginIP, 0);
                                            }
                                        // ignore any queries for $log or with null user agents. This is internal
                                        else if (msg.URL.Contains("$log") || string.IsNullOrWhiteSpace(msg.UserAgent))
                                            {
                                                whiteListedIps.TryAdd(msg.OriginIP, 0);
                                            }
                                            else
                                            {
                                                honeybucketrawlogs.Add(msg);
                                            }
                                            break;
                                        default:
                                            break;
                                    }
                                }
                            }
                        }
                    }
                });

                // Runs the tasks until they complete and add the results to Azure Sentinel
                using (var exitEvent = new ManualResetEvent(false))
                {
                    var processResultsTask = Task.Run(() =>
                    {
                        while (!processLogsTask.IsCompleted && honeybucketrawlogs.Count >= 0)
                        {
                            exitEvent.WaitOne(30 * 1000);

                            List<LogMessage> messages = new List<LogMessage>();
                            while (honeybucketrawlogs.TryTake(out LogMessage message))
                            {
                                messages.Add(message);
                            }

                            var listOfIps = messages.Where(x => !whiteListedIps.ContainsKey(x.OriginIP)).Distinct().ToList();

                            if (listOfIps.Count() != 0)
                            {
                                listOfIps.Select(x => x.OriginIP).Distinct().ToList().ForEach(x => log.LogInformation($"Found: " + x));

                                log.LogInformation($"Sending to LogAnalytics");

                                var collector = new HTTPDataCollectorAPI.Collector(
                                    logAnalyticsWorkspace,
                                    logAnalyticsKey);

                                try
                                {
                                    var task = collector.Collect(LogAnalyticsTableName, listOfIps);
                                    task.Wait();
                                }
                                catch (Exception ex)
                                {
                                    log.LogError($"Couldn't send to LA", ex);
                                    return;
                                }
                            }
                        }
                    });

                    getLogsTask.Wait();
                    processLogsTask.Wait();
                    exitEvent.Set();
                    processResultsTask.Wait();
                }

                log.LogInformation($"Finished parsing logs");

                // Create a new state entry so we can be sure we only process the minimum amount of data
                var lastReadStr = string.Join(";", lastLogEntryProcessedTime.ToList().ConvertAll(x => x.Key + "=" + x.Value.ToString(FormatString)));

                if (string.IsNullOrWhiteSpace(lastReadStr))
                {
                    log.LogError($"The state string is bad! skipping");
                }
                else
                {
                    WriteData(blobStorageConnectionString, container, Blob, lastReadStr);
                }
            }
            catch (Exception ex)
            {
                log.LogError(ex, "An unexpected exception occured");
            }
        }
    }
}
