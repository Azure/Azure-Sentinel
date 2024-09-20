using Microsoft.Azure.Storage;
using Microsoft.Azure.Storage.Blob;
using System;
using System.Collections.Generic;
using System.Text;

// https://blogs.msdn.microsoft.com/windowsazurestorage/2011/08/02/windows-azure-storage-logging-using-logs-to-track-storage-requests/

namespace HoneyBucketLogParser
{
    class LogDownloader
    {
        private const string LogStartTime = "StartTime";
        private const string LogEndTime = "EndTime";

        public static List<CloudBlob> DownloadStorageLogs(string connectionString, string serviceName, DateTime startTimeOfSearch, DateTime endTimeOfSearch)
        {
            var account = CloudStorageAccount.Parse(connectionString);
            var blobClient = account.CreateCloudBlobClient();
            return ListLogFiles(blobClient, serviceName, startTimeOfSearch.ToUniversalTime(), endTimeOfSearch.ToUniversalTime());
        }

        /// <summary>
        /// Given service name, start time for search and end time for search, creates a prefix that can be used
        /// to efficiently get a list of logs that may match the search criteria
        /// </summary>
        /// <param name="service"></param>
        /// <param name="startTime"></param>
        /// <param name="endTime"></param>
        /// <returns></returns>
        private static string GetSearchPrefix(string service, DateTime startTime, DateTime endTime)
        {
            StringBuilder prefix = new StringBuilder("$logs/");

            prefix.AppendFormat("{0}/", service);

            // if year is same then add the year
            if (startTime.Year == endTime.Year)
            {
                prefix.AppendFormat("{0}/", startTime.Year);
            }
            else
            {
                return prefix.ToString();
            }

            // if month is same then add the month
            if (startTime.Month == endTime.Month)
            {
                prefix.AppendFormat("{0:D2}/", startTime.Month);
            }
            else
            {
                return prefix.ToString();
            }

            // if day is same then add the day
            if (startTime.Day == endTime.Day)
            {
                prefix.AppendFormat("{0:D2}/", startTime.Day);
            }
            else
            {
                return prefix.ToString();
            }

            // if hour is same then add the hour
            if (startTime.Hour == endTime.Hour)
            {
                prefix.AppendFormat("log-{0:D2}00", startTime.Hour);
            }

            return prefix.ToString();
        }

        /// <summary>
        /// Given a service, start time, end time, provide list of log files
        /// </summary>
        /// <param name="blobClient"></param>
        /// <param name="serviceName">The name of the service interested in</param>
        /// <param name="startTimeForSearch">Start time for the search</param>
        /// <param name="endTimeForSearch">End time for the search</param>
        /// <returns></returns>
        private static List<CloudBlob> ListLogFiles(CloudBlobClient blobClient, string serviceName, DateTime startTimeForSearch, DateTime endTimeForSearch)
        {
            List<CloudBlob> selectedLogs = new List<CloudBlob>();

            // form the prefix to search. Based on the common parts in start and end time, this prefix is formed
            string prefix = GetSearchPrefix(serviceName, startTimeForSearch, endTimeForSearch);

            // List the blobs using the prefix
            IEnumerable<IListBlobItem> blobs = blobClient.ListBlobs(
                prefix,
                true,
                BlobListingDetails.Metadata);

            // iterate through each blob and figure the start and end times in the metadata
            foreach (IListBlobItem item in blobs)
            {
                CloudBlob log = item as CloudBlob;
                if (log != null)
                {
                    // we will exclude the file if the file does not have log entries in the interested time range.
                    DateTime startTime = DateTime.Parse(log.Metadata[LogStartTime]).ToUniversalTime();
                    DateTime endTime = DateTime.Parse(log.Metadata[LogEndTime]).ToUniversalTime();

                    bool exclude = (startTime > endTimeForSearch || endTime < startTimeForSearch);

                    if (!exclude)
                    {
                        selectedLogs.Add(log);
                    }
                }
            }

            return selectedLogs;
        }
    }
}
