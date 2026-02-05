using Azure.Identity;
using Azure.Monitor.Ingestion;
using Azure.Monitor.Query;
using Microsoft.Extensions.Logging;
using Sentinel.Constants;
using Sentinel.DTOs;
using Sentinel.Extensions;
using Sentinel.Helpers;
using Veeam.AC.VBR.ApiClient.Api.v1_2_rev1.Models;

namespace Sentinel.Managers
{
    public class LogAnalyticsManagerImpl : ILogAnalyticsManager
    {
        private readonly string _dceMalwareEventsEndpoint;
        private readonly string _dcrMalwareEventsImmutableId;
        private readonly string _malwareEventsStreamName;

        private readonly string _dceBestPracticeAnalysisEndpoint;
        private readonly string _dcrBestPracticeAnalysisImmutableId;
        private readonly string _bestPracticeAnalysisStreamName;

        private readonly string _dceAuthorizationEventsEndpoint;
        private readonly string _dcrAuthorizationEventsImmutableId;
        private readonly string _authorizationEventsStreamName;

        private readonly string _dceTriggeredAlarmEndpoint;
        private readonly string _dcrTriggeredAlarmImmutableId;
        private readonly string _triggeredAlarmStreamName;

        private readonly string _dceCowareFindingsEndpoint;
        private readonly string _dcrCowareFindingsImmutableId;
        private readonly string _cowareFindingsStreamName;

        private readonly string _dceSessionDataEndpoint;
        private readonly string _dcrSessionDataEndpoint;
        private readonly string _sessionDataStreamName;

        private readonly string _veeamEarliestEventTime;
        private readonly string _covewareEarliestEventTime;

        private readonly string _workspaceId;
        private readonly ILogger<LogAnalyticsManagerImpl> _logger;


        public LogAnalyticsManagerImpl(ILogger<LogAnalyticsManagerImpl> logger)
        {
            _dceMalwareEventsEndpoint = Environment.GetEnvironmentVariable(EnvironmentVariablesConstants.DceMalwareEventsEndpointLabel) ?? throw new ArgumentNullException(nameof(_dceMalwareEventsEndpoint), $"Calling {EnvironmentVariablesConstants.DceMalwareEventsEndpointLabel} not found");
            _dcrMalwareEventsImmutableId = Environment.GetEnvironmentVariable(EnvironmentVariablesConstants.DcrMalwareEventsIdLabel) ?? throw new ArgumentNullException(nameof(_dcrMalwareEventsImmutableId), $"Calling {EnvironmentVariablesConstants.DcrMalwareEventsIdLabel} not found");
            _malwareEventsStreamName = Environment.GetEnvironmentVariable(EnvironmentVariablesConstants.MalwareEventsStreamNameLabel) ?? throw new ArgumentNullException(nameof(_malwareEventsStreamName), $"Calling {EnvironmentVariablesConstants.MalwareEventsStreamNameLabel} not found");

            _dceBestPracticeAnalysisEndpoint = Environment.GetEnvironmentVariable(EnvironmentVariablesConstants.DceBestPracticeAnalysisEndpointLabel) ?? throw new ArgumentNullException(nameof(_dceBestPracticeAnalysisEndpoint), $"Calling {EnvironmentVariablesConstants.DceBestPracticeAnalysisEndpointLabel} not found");
            _dcrBestPracticeAnalysisImmutableId = Environment.GetEnvironmentVariable(EnvironmentVariablesConstants.DcrBestPracticeAnalysisIdLabel) ?? throw new ArgumentNullException(nameof(_dcrBestPracticeAnalysisImmutableId), $"Calling {EnvironmentVariablesConstants.DcrBestPracticeAnalysisIdLabel} not found");
            _bestPracticeAnalysisStreamName = Environment.GetEnvironmentVariable(EnvironmentVariablesConstants.BestPracticeAnalysisStreamNameLabel) ?? throw new ArgumentNullException(nameof(_bestPracticeAnalysisStreamName), $"Calling {EnvironmentVariablesConstants.BestPracticeAnalysisStreamNameLabel} not found");

            _dceAuthorizationEventsEndpoint = Environment.GetEnvironmentVariable(EnvironmentVariablesConstants.DceAuthorizationEventsEndpointLabel) ?? throw new ArgumentNullException(nameof(_dceAuthorizationEventsEndpoint), $"Calling {EnvironmentVariablesConstants.DceAuthorizationEventsEndpointLabel} not found");
            _dcrAuthorizationEventsImmutableId = Environment.GetEnvironmentVariable(EnvironmentVariablesConstants.DcrAuthorizationEventsIdLabel) ?? throw new ArgumentNullException(nameof(_dcrAuthorizationEventsImmutableId), $"Calling {EnvironmentVariablesConstants.DcrAuthorizationEventsIdLabel} not found");
            _authorizationEventsStreamName = Environment.GetEnvironmentVariable(EnvironmentVariablesConstants.AuthorizationEventsStreamNameLabel) ?? throw new ArgumentNullException(nameof(_authorizationEventsStreamName), $"Calling {EnvironmentVariablesConstants.AuthorizationEventsStreamNameLabel} not found");

            _dceTriggeredAlarmEndpoint = Environment.GetEnvironmentVariable(EnvironmentVariablesConstants.DceTriggeredAlarmEndpointLabel) ?? throw new ArgumentNullException(nameof(_dceTriggeredAlarmEndpoint), $"Calling {EnvironmentVariablesConstants.DceTriggeredAlarmEndpointLabel} not found");
            _dcrTriggeredAlarmImmutableId = Environment.GetEnvironmentVariable(EnvironmentVariablesConstants.DcrTriggeredAlarmIdLabel) ?? throw new ArgumentNullException(nameof(_dcrTriggeredAlarmImmutableId), $"Calling {EnvironmentVariablesConstants.DcrTriggeredAlarmIdLabel} not found");
            _triggeredAlarmStreamName = Environment.GetEnvironmentVariable(EnvironmentVariablesConstants.TriggeredAlarmStreamNameLabel) ?? throw new ArgumentNullException(nameof(_triggeredAlarmStreamName), $"Calling {EnvironmentVariablesConstants.TriggeredAlarmStreamNameLabel} not found");

            _dceCowareFindingsEndpoint = Environment.GetEnvironmentVariable(EnvironmentVariablesConstants.DceCowareFindingsEndpointLabel) ?? throw new ArgumentNullException(nameof(_dceCowareFindingsEndpoint), $"Calling {EnvironmentVariablesConstants.DceCowareFindingsEndpointLabel} not found");
            _dcrCowareFindingsImmutableId = Environment.GetEnvironmentVariable(EnvironmentVariablesConstants.DcrCowareFindingsIdLabel) ?? throw new ArgumentNullException(nameof(_dcrCowareFindingsImmutableId), $"Calling {EnvironmentVariablesConstants.DcrCowareFindingsIdLabel} not found");
            _cowareFindingsStreamName = Environment.GetEnvironmentVariable(EnvironmentVariablesConstants.CowareFindingsStreamNameLabel) ?? throw new ArgumentNullException(nameof(_cowareFindingsStreamName), $"Calling {EnvironmentVariablesConstants.CowareFindingsStreamNameLabel} not found");

            _dceSessionDataEndpoint = Environment.GetEnvironmentVariable(EnvironmentVariablesConstants.DceSessionDataEndpointLabel) ?? throw new ArgumentNullException(nameof(_dceSessionDataEndpoint), $"Calling {EnvironmentVariablesConstants.DceSessionDataEndpointLabel} not found");
            _dcrSessionDataEndpoint = Environment.GetEnvironmentVariable(EnvironmentVariablesConstants.DcrSessionDataIdLabel) ?? throw new ArgumentNullException(nameof(_dcrSessionDataEndpoint), $"Calling {EnvironmentVariablesConstants.DcrSessionDataIdLabel} not found");
            _sessionDataStreamName = Environment.GetEnvironmentVariable(EnvironmentVariablesConstants.SessionDataStreamNameLabel) ?? throw new ArgumentNullException(nameof(_sessionDataStreamName), $"Calling {EnvironmentVariablesConstants.SessionDataStreamNameLabel} not found");

            _workspaceId = Environment.GetEnvironmentVariable(EnvironmentVariablesConstants.WorkspaceIdLabel) ?? throw new ArgumentNullException(nameof(_workspaceId), $"Calling {EnvironmentVariablesConstants.WorkspaceIdLabel} not found");

            _veeamEarliestEventTime = Environment.GetEnvironmentVariable(EnvironmentVariablesConstants.VeeamEarliestEventLabel) ?? throw new ArgumentNullException(nameof(_veeamEarliestEventTime), $"Calling {EnvironmentVariablesConstants.VeeamEarliestEventLabel} not found");
            _covewareEarliestEventTime = Environment.GetEnvironmentVariable(EnvironmentVariablesConstants.CovewareEarliestEventTimeLabel) ?? throw new ArgumentNullException(nameof(_covewareEarliestEventTime), $"Calling {EnvironmentVariablesConstants.CovewareEarliestEventTimeLabel} not found");

            _logger = logger;
        }

        public async Task SaveMalwareEventsToCustomTableAsync(List<MalwareEventsDTO> malwareEventsDtos, string vbrHostName)
        {
            _logger.LogInformation($"Calling {nameof(SaveMalwareEventsToCustomTableAsync)}");

            var credential = new DefaultAzureCredential();
            var ingestionClient = new LogsIngestionClient(new Uri(_dceMalwareEventsEndpoint), credential);

            if (malwareEventsDtos.Count > 0)
            {
                _logger.LogInformation($"{malwareEventsDtos.Count} malware events detected on {vbrHostName}, ingesting them all to {_malwareEventsStreamName} using {_dcrMalwareEventsImmutableId}");
                await ingestionClient.UploadAsync(_dcrMalwareEventsImmutableId, _malwareEventsStreamName, malwareEventsDtos);
            }
            else
                _logger.LogInformation($"No malware events for {vbrHostName} will be ingested, because they are already present in the {_malwareEventsStreamName} table.");
        }

        public async Task SaveBestPracticeAnalysisToCustomTableAsync(List<BestPracticeAnalysisDTO> analysisDTOs, string vbrHostName)
        {
            _logger.LogInformation($"Calling {nameof(SaveBestPracticeAnalysisToCustomTableAsync)}");

            var credential = new DefaultAzureCredential();
            var ingestionClient = new LogsIngestionClient(new Uri(_dceBestPracticeAnalysisEndpoint), credential);

            if (analysisDTOs.Count != 0)
            {
                await ingestionClient.UploadAsync(_dcrBestPracticeAnalysisImmutableId, _bestPracticeAnalysisStreamName, analysisDTOs);

                _logger.LogInformation($"Ingested {analysisDTOs.Count} events for {vbrHostName} to {_bestPracticeAnalysisStreamName} table");
            }
            else
                _logger.LogInformation($"No Best Practice Analysis for {vbrHostName} will be ingested, because they are already present in the {_bestPracticeAnalysisStreamName} table.");
        }

        public async Task<DateTime> GetLatestDateTimeIngested(string vbrHostName, IngestedStreamType ingestedStreamType)
        {
            _logger.LogInformation($"{nameof(GetLatestDateTimeIngested)} called for {ingestedStreamType}");

            var client = new LogsQueryClient(new DefaultAzureCredential());

            var queryParams = BuildQueryInfo(ingestedStreamType);

            var hostName = ingestedStreamType switch
            {
                IngestedStreamType.TriggeredAlarms => "VoneHostName",
                IngestedStreamType.CovewareFindings => "CovewareHostName",
                _ => "VbrHostName"
            };

            var kustoQuery = $"""
                              {queryParams.TableName}
                              | where {hostName} == '{vbrHostName}'
                              | summarize LatestDetectionTime = max(todatetime({queryParams.TimeColumn}))
                              | extend LatestDetectionTimeString = format_datetime(LatestDetectionTime, '{LogAnalyticsConstants.DefaultTimeFormat}')
                              | project LatestDetectionTimeString
                              """;

            var result = await client.QueryWorkspaceAsync(_workspaceId, kustoQuery, LogAnalyticsConstants.DefaultQueryTimeSpan);

            _logger.LogInformation($"Executing kusto query: {kustoQuery}");

            var table = result.Value.Table;

            if (table.Rows.Count == 0 || table.Rows[0].Count == 0 || table.Rows[0][0] is not object cell)
            {
                _logger.LogInformation($"No {ingestedStreamType} found for {vbrHostName}");

                var earliestEvent =
                    ingestedStreamType switch
                    {
                        IngestedStreamType.CovewareFindings => DateTime.Parse(_covewareEarliestEventTime),
                        _ => DateTime.Parse(_veeamEarliestEventTime)
                    };
                return earliestEvent;
            }

            var dateString = cell.ToString();

            if (string.IsNullOrEmpty(dateString))
            {
                _logger.LogInformation($"No {ingestedStreamType} found for {vbrHostName} withing the Log Analytic Workspace");
                var earliestEvent =
                    ingestedStreamType switch
                    {
                        IngestedStreamType.CovewareFindings => DateTime.Parse(_covewareEarliestEventTime),
                        _ => DateTime.Parse(_veeamEarliestEventTime)
                    };
                return earliestEvent;
            }

            _logger.LogInformation($"Last {ingestedStreamType} time for {vbrHostName} = '{dateString}'");

            var dt = DateTimeParser.ParseExactUniversal(dateString);

            return dt;
        }

        public async Task SaveCovewareFindingsToCustomTableAsync(List<CovewareFindingDTO> dtos, string covewareHostName)
        {
            _logger.LogInformation($"Calling {nameof(SaveCovewareFindingsToCustomTableAsync)}");

            var credential = new DefaultAzureCredential();
            var ingestionClient = new LogsIngestionClient(new Uri(_dceCowareFindingsEndpoint), credential);

            if (dtos.Count > 0)
            {
                _logger.LogInformation($"{dtos.Count} Coveware findings detected on {covewareHostName}, ingesting them all to {_cowareFindingsStreamName} using {_dcrCowareFindingsImmutableId}");
                await ingestionClient.UploadAsync(_dcrCowareFindingsImmutableId, _cowareFindingsStreamName, dtos);
            }
            else
                _logger.LogInformation($"No Coveware findings for {covewareHostName} will be ingested, because they are already present in the {_cowareFindingsStreamName} table.");
        }

        public async Task SaveSessionDataAsync(SessionModelDTO sessionModelDTO, string vbrHostName)
        {
            _logger.LogInformation($"Calling {nameof(SaveSessionDataAsync)}");

            // Check if session with sessionId already exists for provided vbrHostName
            var client = new LogsQueryClient(new DefaultAzureCredential());
            var sessionTableName = GetTableName(_sessionDataStreamName);

            var kustoQuery = $"""
                              datatable(Id:string)["{sessionModelDTO.Id}"]
                              | join kind=anti ({sessionTableName} | where VbrHostName == '{vbrHostName}' | project Id) on Id
                              """;

            var result = await client.QueryWorkspaceAsync(_workspaceId, kustoQuery, LogAnalyticsConstants.DefaultQueryTimeSpan);

            _logger.LogInformation($"Executing kusto query: {kustoQuery}");

            var table = result.Value.Table;

            // If no rows returned, session already exists - do nothing
            if (table.Rows.Count == 0)
            {
                _logger.LogInformation($"Session {sessionModelDTO.Id} already exists for {vbrHostName}, skipping ingestion.");
                return;
            }

            // Session doesn't exist, proceed with ingestion
            var credential = new DefaultAzureCredential();
            var ingestionClient = new LogsIngestionClient(new Uri(_dceSessionDataEndpoint), credential);

            _logger.LogInformation($"Ingesting session {sessionModelDTO.Id} for {vbrHostName} to {_sessionDataStreamName} using {_dcrSessionDataEndpoint}");
            await ingestionClient.UploadAsync(_dcrSessionDataEndpoint, _sessionDataStreamName, new[] { sessionModelDTO });
        }

        private QueryInfo BuildQueryInfo(IngestedStreamType ingestedStreamType)
        {
            return ingestedStreamType switch
            {
                IngestedStreamType.MalwareEvents => new QueryInfo { TableName = GetTableName(_malwareEventsStreamName), TimeColumn = QueryConstants.DetectionTimeUtc },
                IngestedStreamType.BestPracticeAnalysis => new QueryInfo { TableName = GetTableName(_bestPracticeAnalysisStreamName), TimeColumn = QueryConstants.EndTime },
                IngestedStreamType.AuthorizationEvents => new QueryInfo { TableName = GetTableName(_authorizationEventsStreamName), TimeColumn = QueryConstants.CreationTime },
                IngestedStreamType.TriggeredAlarms => new QueryInfo { TableName = GetTableName(_triggeredAlarmStreamName), TimeColumn = QueryConstants.TriggeredTime },
                IngestedStreamType.CovewareFindings => new QueryInfo { TableName = GetTableName(_cowareFindingsStreamName), TimeColumn = QueryConstants.EventTime },
                _ => throw new NotImplementedException($"Unsupported stream type: {ingestedStreamType}")
            };
        }

        private string GetTableName(string streamName)
        {
            var prefix = "Custom-";

            if (!streamName.StartsWith(prefix))
                throw new ArgumentException($"{streamName} not start with '{prefix}'"); // should never happen

            return streamName.Substring(prefix.Length);
        }

        public async Task SaveAuthorizationEventsToCustomTableAsync(List<AuthorizationEventsDTO?> dtos, string vbrHostName)
        {
            _logger.LogInformation($"Calling {nameof(SaveAuthorizationEventsToCustomTableAsync)}");

            var credential = new DefaultAzureCredential();
            var ingestionClient = new LogsIngestionClient(new Uri(_dceAuthorizationEventsEndpoint), credential);

            if (dtos.Count > 0)
            {
                _logger.LogInformation($"{dtos.Count} authorization events detected on {vbrHostName}, ingesting them all to {_authorizationEventsStreamName} using {_dcrAuthorizationEventsImmutableId}");
                await ingestionClient.UploadAsync(_dcrAuthorizationEventsImmutableId, _authorizationEventsStreamName, dtos);
            }
            else
                _logger.LogInformation($"No authorization events for {vbrHostName} will be ingested, because they are already present in the {_authorizationEventsStreamName} table.");
        }

        public async Task<List<Guid>> FilterProcessedIdsAsync(List<Guid?> ids, string vbrHostName)
        {
            _logger.LogInformation($"Calling {nameof(FilterProcessedIdsAsync)}");

            var client = new LogsQueryClient(new DefaultAzureCredential());

            var queryParams = BuildQueryInfo(IngestedStreamType.BestPracticeAnalysis);

            var joinedIds = FilteringHelper.FormatIdsToString(ids);

            var kustoQuery = $"""
                              datatable(Id:string)[{joinedIds}]
                              | join kind=anti ({queryParams.TableName} | where VbrHostName == '{vbrHostName}' | project Id) on Id
                              """;

            _logger.LogInformation($"Kusto query: {kustoQuery}");

            var result = await client.QueryWorkspaceAsync(_workspaceId, kustoQuery, LogAnalyticsConstants.DefaultQueryTimeSpan);

            var table = result.Value.Table;

            if (table.Rows.Count == 0 || table.Rows[0].Count == 0 || table.Rows[0][0] is not object cell)
            {
                _logger.LogInformation($"All {IngestedStreamType.BestPracticeAnalysis} are already present in the {queryParams.TableName}, nothing will be ingested.");
                return [];
            }

            var idsNotInTable = table.Rows.Select(me => me.GetString("Id")).Select(Guid.Parse).ToList();

            return idsNotInTable;
        }

        public async Task SaveTriggeredAlarmsToCustomTableAsync(List<TriggeredAlarmDTO> dtos, string voneHostName)
        {
            _logger.LogInformation($"Calling {nameof(SaveTriggeredAlarmsToCustomTableAsync)}");

            var credential = new DefaultAzureCredential();
            var ingestionClient = new LogsIngestionClient(new Uri(_dceTriggeredAlarmEndpoint), credential);

            if (dtos.Count > 0)
            {
                _logger.LogInformation($"{dtos.Count} alarms detected on {voneHostName}, ingesting them all to {_triggeredAlarmStreamName} using {_dcrTriggeredAlarmImmutableId}");
                await ingestionClient.UploadAsync(_dcrTriggeredAlarmImmutableId, _triggeredAlarmStreamName, dtos);
            }
            else
                _logger.LogInformation($"No alarms for {voneHostName} will be ingested, because they are already present in the {_triggeredAlarmStreamName} table.");
        }
    }
}