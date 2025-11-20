using Veeam.AC.VBR.ApiClient.Api.v1_2_rev1.Models;

namespace Sentinel.Client
{
    public interface IVbrClient
    {
        Task<SuspiciousActivityEventsResult> GetAllMalwareEventsAsync(SuspiciousActivityEventsFilters suspiciousActivityEventsFilters);

        Task<SessionModel> StartConfigurationBackupAsync();

        Task<ObjectRestorePointsResult> GetBackupObjectRestorePointsAsync(Guid backupObjectId);

        Task<SessionModel> StartScanBackupAsync(Guid backupObjectId, Guid backupId);

        Task<SessionModel> GetSessionAsync(Guid sessionId);

        Task<BestPracticesComplianceResult> GetSecurityComplianceAnalyzerResultsAsync();

        Task<SessionModel> StartSecurityComplianceAnalyzerAsync();

        Task<BackupObjectModel> GetBackupObjectByIdAsync(Guid machineBackupObjectId);

        Task<SessionModel> StartQuickBackupAsync(VmwareObjectModel vmwareObjectModel);

        Task<AuthorizationEventsResult> GetAllAuthorizationEventsAsync(AuthorizationEventsFilters authorizationEventsFilters);

        Task<ObjectRestorePointsResult> GetAllRestorePointsAsync(ObjectRestorePointsFilters objectRestorePointsFilters);

        Task<SuspiciousActivityEventsResult> CreateSuspiciousActivityEventAsync(SuspiciousActivityEventSpec suspiciousActivityEventSpec);

        Task<SessionModel> StartInstantVmRecovery(InstantViVMRecoverySpec instantViVMRecoverySpec);
    }
}