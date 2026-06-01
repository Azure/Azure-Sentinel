using BeyondTrustPMCloud.Models;
using BeyondTrustPMCloud.Services;
using Microsoft.Azure.Functions.Worker;
using Microsoft.Extensions.Logging;

namespace BeyondTrustPMCloud.Functions;

public class ActivityAuditsFunction
{
    private readonly IBeyondTrustApiService _apiService;
    private readonly ILogAnalyticsService _logAnalyticsService;
    private readonly IStateService _stateService;
    private readonly BeyondTrustConfiguration _config;
    private readonly ILogger<ActivityAuditsFunction> _logger;

    public ActivityAuditsFunction(
        IBeyondTrustApiService apiService,
        ILogAnalyticsService logAnalyticsService,
        IStateService stateService,
        BeyondTrustConfiguration config,
        ILogger<ActivityAuditsFunction> logger)
    {
        _apiService = apiService;
        _logAnalyticsService = logAnalyticsService;
        _stateService = stateService;
        _config = config;
        _logger = logger;
    }

    [Function("ActivityAuditsTimerTrigger")]
    public async Task Run([TimerTrigger("%ActivityAuditsCron%")] TimerInfo timer)
    {
        _logger.LogDebug("ActivityAudits function started at: {DateTime}", DateTime.Now);

        try
        {
            var state = await _stateService.GetStateAsync(StateKeys.ActivityAudits);
            var fromDate = state.LastProcessedTimestamp;
            var toDate = DateTime.UtcNow;

            _logger.LogInformation("Processing Activity Audits from {FromDate} to {ToDate}", fromDate, toDate);

            var currentPage = 1;
            var maxAuditId = state.LastProcessedId;
            var latestTimestamp = state.LastProcessedTimestamp;
            var processedAny = false;

            while (true)
            {
                var response = await _apiService.GetActivityAuditsAsync(fromDate, toDate, currentPage, 200);

                if (response.Data.Count == 0)
                {
                    _logger.LogDebug("No more Activity Audits to process on page {Page}", currentPage);
                    break;
                }

                // Filter against the live in-memory cursor so pages 2+ don't re-emit
                // records already sent in this invocation.
                var newAudits = response.Data.Where(a => a.Id > maxAuditId).ToList();

                if (newAudits.Any())
                {
                    var currentMaxId = newAudits.Max(a => a.Id);
                    var currentLatestTimestamp = newAudits.Max(a => a.Created);

                    if (currentMaxId > maxAuditId)
                        maxAuditId = currentMaxId;

                    if (currentLatestTimestamp > latestTimestamp)
                        latestTimestamp = currentLatestTimestamp;

                    var transformedAudits = TransformActivityAudits(newAudits);

                    await _logAnalyticsService.SendToLogAnalyticsAsync(transformedAudits, "BeyondTrustPM_ActivityAudits");

                    // Checkpoint after each page so progress survives a host timeout mid-loop.
                    state.LastProcessedTimestamp = DateTime.SpecifyKind(latestTimestamp.AddMilliseconds(1), DateTimeKind.Utc);
                    state.LastProcessedId = maxAuditId;
                    state.RecordsProcessed += newAudits.Count;
                    state.Status = "Success";
                    state.ErrorMessage = null;
                    await _stateService.UpdateStateAsync(state);

                    processedAny = true;
                    _logger.LogInformation("✅ Successfully processed {RecordCount} Activity Audits. Latest ID: {LatestId}, Latest Timestamp: {LatestTimestamp}, Next Query From: {NextFromTime}",
                        newAudits.Count, maxAuditId, latestTimestamp, state.LastProcessedTimestamp);
                }

                if (currentPage >= response.PageCount)
                    break;

                currentPage++;
            }

            if (!processedAny)
            {
                _logger.LogDebug("No new Activity Audits found");
                state.Status = "Success - No Data";
                state.ErrorMessage = null;
                await _stateService.UpdateStateAsync(state);
            }
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "❌ Error processing Activity Audits");

            try
            {
                var state = await _stateService.GetStateAsync(StateKeys.ActivityAudits);
                state.Status = "Error";
                state.ErrorMessage = ex.Message;
                await _stateService.UpdateStateAsync(state);
            }
            catch (Exception stateEx)
            {
                _logger.LogError(stateEx, "❌ Failed to update error state");
            }

            throw;
        }

        _logger.LogDebug("ActivityAudits function completed at: {DateTime}", DateTime.Now);
    }

    private static IEnumerable<object> TransformActivityAudits(IEnumerable<ActivityAudit> audits) =>
        audits.Select(audit => (object)new
        {
            TimeGenerated = audit.Created,
            id = audit.Id,
            details = audit.Details,
            userId = audit.UserId,
            user = audit.User,
            entity = audit.Entity,
            entityName = audit.EntityName,
            auditType = audit.AuditType,
            created = audit.Created,
            changedBy = audit.ChangedBy,
            apiClientDataAuditing = audit.ApiClientDataAuditing,
            computerDataAuditing = audit.ComputerDataAuditing,
            groupDataAuditing = audit.GroupDataAuditing,
            installationKeyDataAuditing = audit.InstallationKeyDataAuditing,
            policyDataAuditing = audit.PolicyDataAuditing,
            policyRevisionDataAuditing = audit.PolicyRevisionDataAuditing,
            settingsDataAuditing = audit.SettingsDataAuditing,
            userDataAuditing = audit.UserDataAuditing,
            mapToIdentityProviderGroupAuditing = audit.MapToIdentityProviderGroupAuditing,
            openIdConfigDataAuditing = audit.OpenIdConfigDataAuditing,
            mmcRemoteClientDataAuditing = audit.MmcRemoteClientDataAuditing,
            computerPolicyDataAuditing = audit.ComputerPolicyDataAuditing,
            azureADIntegrationDataAuditing = audit.AzureADIntegrationDataAuditing,
            authorizationRequestDataAuditing = audit.AuthorizationRequestDataAuditing,
            reputationSettingsDataAuditing = audit.ReputationSettingsDataAuditing,
            securitySettingsDataAuditing = audit.SecuritySettingsDataAuditing,
            siemIntegrationBaseDetailModel = audit.SiemIntegrationBaseDetailModel,
            siemIntegrationQradarAuditing = audit.SiemIntegrationQradarAuditing,
            siemIntegrationS3Auditing = audit.SiemIntegrationS3Auditing,
            siemIntegrationSentinelAuditing = audit.SiemIntegrationSentinelAuditing,
            siemIntegrationSplunkAuditing = audit.SiemIntegrationSplunkAuditing,
            agentDataAuditing = audit.AgentDataAuditing,
            managementRuleDataAuditing = audit.ManagementRuleDataAuditing,
            autoUpdateRateLimitDataAuditing = audit.AutoUpdateRateLimitDataAuditing,
            autoUpdateGroupConfigSettingsDataAuditing = audit.AutoUpdateGroupConfigSettingsDataAuditing,
            autoUpdateGroupClientSettingsDataAuditing = audit.AutoUpdateGroupClientSettingsDataAuditing,
            permissionGroupDataAuditing = audit.PermissionGroupDataAuditing,
            autoUpdateGroupMacClientSettingsDataAuditing = audit.AutoUpdateGroupMacClientSettingsDataAuditing,
            identityProviderGroupDataAuditing = audit.IdentityProviderGroupDataAuditing,
            timeTransmitted = DateTime.UtcNow
        });
}
