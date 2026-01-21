using Microsoft.Extensions.Logging;
using Sentinel.Constants;
using Sentinel.Managers;
using Veeam.AC.VBR.ApiClient.Api.v1_2_rev1;
using Veeam.AC.VBR.ApiClient.Api.v1_2_rev1.Models;

namespace Sentinel.Client
{
    public class VbrClientImpl : AuthenticatedVbrClientHandler, IVbrClient
    {
        private readonly IMalwareDetectionApi _malwareDetectionApi;
        private readonly IConfigurationBackupApi _configurationBackupApi;
        private readonly IBackupObjectsApi _backupObjectsApi;
        private readonly ISessionsApi _sessionsApi;
        private readonly ISecurityApi _securityApi;
        private readonly IJobsApi _jobsApi;
        private readonly IRestorePointsApi _restorePointsApi;
        private readonly IRestoreApi _restoreApi;
        private readonly string _vbrId;

        public VbrClientImpl(string baseUrl, string vbrId, ISecretsManager secretsManager, ILogger<AuthenticatedVbrClientHandler> logger) : base(baseUrl, vbrId, secretsManager, logger)
        {
            _vbrId = vbrId;

            _malwareDetectionApi = new MalwareDetectionApi(_apiConfig);

            _configurationBackupApi = new ConfigurationBackupApi(_apiConfig);

            _backupObjectsApi = new BackupObjectsApi(_apiConfig);

            _sessionsApi = new SessionsApi(_apiConfig);

            _securityApi = new SecurityApi(_apiConfig);

            _jobsApi = new JobsApi(_apiConfig);

            _restorePointsApi = new RestorePointsApi(_apiConfig);
            
            _restoreApi = new RestoreApi(_apiConfig);
        }

        public async Task<SuspiciousActivityEventsResult> GetAllMalwareEventsAsync(SuspiciousActivityEventsFilters suspiciousActivityEventsFilters)
        {
            _logger.LogInformation($"{nameof(GetAllMalwareEventsAsync)} called for \"{_vbrId}\" with request {suspiciousActivityEventsFilters.ToJson()}");
            _apiConfig.DateTimeFormat = LogAnalyticsConstants.TimeFormatMalwareEvents;
            var response = await SendAsync((_) => _malwareDetectionApi.ViewSuspiciousActivityEventsAsync(suspiciousActivityEventsFilters), default);
            _apiConfig.DateTimeFormat = LogAnalyticsConstants.DefaultTimeFormat;
            _logger.LogInformation($"{nameof(GetAllMalwareEventsAsync)} response fetched {response.Data.Count} events for \"{_vbrId}\"");
            return response;
        }

        public async Task<SessionModel> StartConfigurationBackupAsync()
        {
            _logger.LogInformation($"{nameof(StartConfigurationBackupAsync)} called for \"{_vbrId}\"");
            var response = await SendAsync((_) => _configurationBackupApi.StartConfigBackupAsync(), default);
            _logger.LogInformation($"{nameof(StartConfigurationBackupAsync)} response for \"{_vbrId}\": {response.ToJson()}");
            return response;
        }

        public async Task<ObjectRestorePointsResult> GetBackupObjectRestorePointsAsync(Guid backupObjectId)
        {
            _logger.LogInformation($"{nameof(GetBackupObjectRestorePointsAsync)} called for \"{_vbrId}\" for backupObjectId: {backupObjectId}");
            var response = await SendAsync((_) => _backupObjectsApi.GetBackupObjectRestorePointsAsync(backupObjectId), default);
            _logger.LogInformation($"{nameof(GetBackupObjectRestorePointsAsync)} response for \"{_vbrId}\": {response.ToJson()}");
            return response;
        }

        public async Task<SessionModel> StartScanBackupAsync(Guid backupObjectId, Guid backupId)
        {
            _logger.LogInformation($"{nameof(StartScanBackupAsync)} called for \"{_vbrId}\" for backupObjectId: {backupObjectId}, backupId: {backupId}");

            var backupObjectIdPair = new BackupObjectPair(backupId, backupObjectId);
            var backupObjectIdPairList = new List<BackupObjectPair>() { backupObjectIdPair };

            var scanEngine = new MalwareBackupScanSpecEngine(useAntivirusEngine: true, useYaraRule: false, yaraRule: null);

            var malwareBackupScanSpec = new MalwareBackupScanSpec(
                backupObjectIdPairList,
                EMalwareBackupScanMode.MostRecent, // TODO: extract from request 
                scanEngine, // TODO: extract from request 
                null,
                continueScan: false);

            _logger.LogInformation($"Starting malware scan with spec: {malwareBackupScanSpec.ToJson()}");

            var response = await SendAsync((_) => _malwareDetectionApi.StartMalwareBackupScanAsync(malwareBackupScanSpec), default);
            _logger.LogInformation($"{nameof(StartScanBackupAsync)} response for \"{_vbrId}\": {response.ToJson()}");
            return response;
        }

        public async Task<SessionModel> GetSessionAsync(Guid sessionId)
        {
            _logger.LogInformation($"{nameof(GetSessionAsync)} called for \"{_vbrId}\" for sessionId: {sessionId}");
            var response = await SendAsync((_) => _sessionsApi.GetSessionAsync(sessionId), default);
            _logger.LogInformation($"{nameof(GetSessionAsync)} response for \"{_vbrId}\": {response.ToJson()}");
            return response;
        }

        public async Task<BestPracticesComplianceResult> GetSecurityComplianceAnalyzerResultsAsync()
        {
            _logger.LogInformation($"{nameof(GetSecurityComplianceAnalyzerResultsAsync)} called for \"{_vbrId}\"");
            var response = await SendAsync((_) => _securityApi.GetBestPracticesComplianceResultAsync(), default);
            _logger.LogInformation($"{nameof(GetSecurityComplianceAnalyzerResultsAsync)} response fetched {response.Items.Count} events for \"{_vbrId}\"");
            return response;
        }

        public async Task<SessionModel> StartSecurityComplianceAnalyzerAsync()
        {
            _logger.LogInformation($"{nameof(StartSecurityComplianceAnalyzerAsync)} called for \"{_vbrId}\"");
            var response = await SendAsync((_) => _securityApi.StartSecurityAnalyzerAsync(), default);
            _logger.LogInformation($"{nameof(StartSecurityComplianceAnalyzerAsync)} response for \"{_vbrId}\": {response.ToJson()}");
            return response;
        }

        public async Task<BackupObjectModel> GetBackupObjectByIdAsync(Guid machineBackupObjectId)
        {
            _logger.LogInformation($"{nameof(GetBackupObjectByIdAsync)} called for \"{_vbrId}\" for machineBackupObjectId: {machineBackupObjectId}");
            var response = await SendAsync((_) => _backupObjectsApi.GetBackupObjectAsync(machineBackupObjectId), default);
            _logger.LogInformation($"{nameof(GetBackupObjectByIdAsync)} response for \"{_vbrId}\": {response.ToJson()}");
            return response;
        }

        public async Task<SessionModel> StartQuickBackupAsync(VmwareObjectModel vmwareObjectModel)
        {
            _logger.LogInformation($"{nameof(StartQuickBackupAsync)} called for \"{_vbrId}\" with request {vmwareObjectModel.ToJson()}");
            var response = await SendAsync((_) => _jobsApi.StartVSphereQuickBackupJobAsync(vmwareObjectModel), default);
            _logger.LogInformation($"{nameof(StartQuickBackupAsync)} response for \"{_vbrId}\": {response.ToJson()}");
            return response;
        }

        public async Task<AuthorizationEventsResult> GetAllAuthorizationEventsAsync(AuthorizationEventsFilters authorizationEventsFilters)
        {
            _logger.LogInformation($"{nameof(GetAllAuthorizationEventsAsync)} called for \"{_vbrId}\" with request {authorizationEventsFilters.ToJson()}");
            var response = await SendAsync((_) => _securityApi.GetAllAuthorizationEventsAsync(authorizationEventsFilters), default);
            _logger.LogInformation($"{nameof(GetAllAuthorizationEventsAsync)} response fetched {response.Data.Count} events for \"{_vbrId}\"");
            return response;
        }

        public async Task<ObjectRestorePointsResult> GetAllRestorePointsAsync(ObjectRestorePointsFilters objectRestorePointsFilters)
        {
            _logger.LogInformation($"{nameof(GetAllRestorePointsAsync)} called for \"{_vbrId}\" with request {objectRestorePointsFilters.ToJson()}");
            var response = await SendAsync((_) => _restorePointsApi.GetAllObjectRestorePointsAsync(objectRestorePointsFilters), default);
            _logger.LogInformation($"{nameof(GetAllRestorePointsAsync)} response for fetched {response.Data.Count} events for {_vbrId}");
            return response;
        }

        public async Task<SuspiciousActivityEventsResult> CreateSuspiciousActivityEventAsync(SuspiciousActivityEventSpec suspiciousActivityEventSpec)
        {
            _logger.LogInformation($"{nameof(CreateSuspiciousActivityEventAsync)} called for \"{_vbrId}\" with request {suspiciousActivityEventSpec.ToJson()}");
            var response = await SendAsync((_) => _malwareDetectionApi.CreateSuspiciousActivityEventAsync(suspiciousActivityEventSpec), default);
            _logger.LogInformation($"{nameof(CreateSuspiciousActivityEventAsync)} response for \"{_vbrId}\": {response.ToJson()}");
            return response;
        }

        public Task<SessionModel> StartInstantVmRecovery(InstantViVMRecoverySpec instantViVMRecoverySpec)
        {
            _logger.LogInformation($"{nameof(StartInstantVmRecovery)} called for \"{_vbrId}\" with request {instantViVMRecoverySpec.ToJson()}");
            var response = SendAsync((_) => _restoreApi.InstantViVMRecoveryMountAsync(instantViVMRecoverySpec), default);
            response.ContinueWith(task =>
            {
                if (task.IsCompletedSuccessfully)
                {
                    _logger.LogInformation($"{nameof(StartInstantVmRecovery)} response for \"{_vbrId}\": {task.Result.ToJson()}");
                }
            });
            return response;
        }
    }
}