using Microsoft.Azure.WebJobs;
using Microsoft.Extensions.Logging;
using Newtonsoft.Json;
using System;
using System.Collections.Generic;
using System.Globalization;
using System.Threading.Tasks;
using Teams.CustomConnector.Common;
using Teams.CustomConnector.Models;
using Teams.CustomConnector.Sentinel;
using Teams.CustomConnector.StorageHandler;

namespace Teams.CustomConnector.Serverless
{

    /// <summary></summary>
    public static class EgressTeamsLogs
    {
        private static List<AuditDetailedReport> auditDetailedReports;
    
        /// <summary>
        /// Runs the specified my timer.
        /// </summary>
        /// <param name="myTimer">My timer.</param>
        /// <param name="log">The log.</param>
            [FunctionName("EgressTeamsLogs")]
        public static void Run([TimerTrigger("0 */10 * * * *")]TimerInfo myTimer, ILogger log)
        {
           
            log.LogInformation(Constants.RequestProcessingStarted);
           
            StorageHandler.StorageHandler storageHandler = new StorageHandler.StorageHandler(log);
            OperationDetails LastOperationDetails = null;

            try
            {
                log.LogInformation(Constants.RequestLastExecutionTime);
                
                //Fetch the last execution time and status
                LastOperationDetails = storageHandler.GetLastOperationDetailsFromLogsAsync(Environment.GetEnvironmentVariable(Constants.LogFileName)).Result;

                //if there is the first time or no info found
                if (LastOperationDetails?.LastRunEndTime == null)
                {

                    LastOperationDetails = new OperationDetails();

                    log.LogWarning(Constants.LastExecutionTimeNotFound);
                    try
                    {
                        //Fetch the info form configuration
                        //Start set to current time - connectioninterval 
                        LastOperationDetails.LastRunEndTime = DateTime.Parse(Environment.GetEnvironmentVariable(Constants.AuditLogExtractionStartDate));
                        LastOperationDetails.LastRunStartTime = LastOperationDetails.LastRunEndTime?.AddMinutes(-Convert.ToInt32(Environment.GetEnvironmentVariable(Constants.ConnectionIntervalInMinutes)));

                    }
                    catch (Exception)
                    {
                        //if no configuration is found , set the start time and end time
                        LastOperationDetails.LastRunEndTime = DateTime.UtcNow;
                        LastOperationDetails.LastRunStartTime = LastOperationDetails.LastRunEndTime?.AddMinutes(-Convert.ToInt32(Environment.GetEnvironmentVariable(Constants.ConnectionIntervalInMinutes)));
                        log.LogWarning(Constants.AuditLogExtractionStartDateMissing);
                    }
                }
                else
                {
                    LastOperationDetails.LastRunStartTime = LastOperationDetails.LastRunEndTime;
                    LastOperationDetails.LastRunEndTime = LastOperationDetails.LastRunEndTime?.AddMinutes(Convert.ToInt32(Environment.GetEnvironmentVariable(Constants.ConnectionIntervalInMinutes)));
                }

                log.LogInformation(Constants.OMSRequestProcessStarted);
                log.LogWarning($"Daterange set:  start time : { LastOperationDetails.LastRunStartTime} , endtime { LastOperationDetails.LastRunEndTime}");
                Teams.CustomConnector.Processor.Processor processor = new Processor.Processor(log);

                //fetch the details. 
                auditDetailedReports = processor.Process(LastOperationDetails.LastRunStartTime?.ToString("G", CultureInfo.InvariantCulture), LastOperationDetails.LastRunEndTime?.ToString("G", CultureInfo.InvariantCulture)).Result;

                log.LogInformation($"Total {auditDetailedReports.Count} of audit logs found");

                if (auditDetailedReports.Count > 0)
                {
                    //upload to the container
                    var reports = JsonConvert.SerializeObject(auditDetailedReports);
                    if (Convert.ToBoolean(Environment.GetEnvironmentVariable(Constants.EnableDirectInjestionToWorkSpace)))
                    {
                        string SentinelWkSpaceId = string.Empty;
                        string SentinelSharedkey = string.Empty;
                        if (Convert.ToBoolean(Environment.GetEnvironmentVariable(Constants.KeyVaultEnabled)))
                        {
                            SentinelWkSpaceId = KeyVaultHelper.GetKeyValueAsync(Constants.SentinelCustomerId).Result;
                            SentinelSharedkey = KeyVaultHelper.GetKeyValueAsync(Constants.SentinelSharedkey).Result;
                        }
                        else
                        {
                            SentinelWkSpaceId = Environment.GetEnvironmentVariable(Constants.SentinelCustomerId);
                            SentinelSharedkey = Environment.GetEnvironmentVariable(Constants.SentinelSharedkey);
                        }
                        AzureLogAnalyticsConnector azureLogAnalyticsConnector= new Sentinel.AzureLogAnalyticsConnector(SentinelWkSpaceId, SentinelSharedkey, "TeamsAuditLogs");
                        azureLogAnalyticsConnector.Post(reports);
                    }

                    if (Convert.ToBoolean(Environment.GetEnvironmentVariable(Constants.EnableArchiving)))
                    {
                        Task.Run(async () => await storageHandler.UploadDataToContainerAsync(OperationType.Data, LastOperationDetails.LastRunStartTime?.Ticks.ToString(), reports));
                    }
                }

                LastOperationDetails.IsLastRunSuccessful = true;

            }
            catch (Exception ex)
            {
                log.LogError(ex, Constants.OMSRequestProcessFailed);
                log.LogError($"{Constants.FatalError} , {ex.Message}  , {ex.InnerException.ToString()}");
                LastOperationDetails.IsLastRunSuccessful = false;
            }

            if (!LastOperationDetails.IsLastRunSuccessful)
            {
                LastOperationDetails.TotalFailCountSinceLastSuccessfulRun++;
            }
            else
                LastOperationDetails.TotalFailCountSinceLastSuccessfulRun = 0;

            //update the last run details. 
            LastOperationDetails.TotalAuditRecordsProcessed = auditDetailedReports.Count;
            LastOperationDetails.TotalRecordsProcessedInLifeTime += LastOperationDetails.TotalAuditRecordsProcessed;
            var opdetails = JsonConvert.SerializeObject(LastOperationDetails);
         
            Task.Run(() =>
            storageHandler.UploadDataToContainerAsync(OperationType.Log,
                                                        Environment.GetEnvironmentVariable(Constants.LogFileName),
                                                        opdetails));

            log.LogInformation(Constants.RequestProcessed);
        }
    }
}
