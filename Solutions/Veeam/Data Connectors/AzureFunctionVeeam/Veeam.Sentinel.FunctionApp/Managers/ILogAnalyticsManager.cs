using Sentinel.DTOs;
using Veeam.AC.VBR.ApiClient.Api.v1_2_rev1.Models;

namespace Sentinel.Managers
{
    public interface ILogAnalyticsManager
    {
        Task SaveMalwareEventsToCustomTableAsync(SuspiciousActivityEventsResult malwareEvents, string vbrHostName);

        Task SaveBestPracticeAnalysisToCustomTableAsync(List<BestPracticeAnalysisDTO> analysis, string vbrHostName);

        Task<DateTime> GetLatestDateTimeIngested(string vbrHostName, IngestedStreamType ingestedStreamType);

        Task SaveAuthorizationEventsToCustomTableAsync(List<AuthorizationEventsDTO?> dtos, string vbrHostName);

        Task<List<Guid>> FilterProcessedIdsAsync(List<Guid?> ids, string vbrHostName);

        Task SaveTriggeredAlarmsToCustomTableAsync(List<TriggeredAlarmDTO> dtos, string voneHostName);

        Task SaveCovewareFindingsToCustomTableAsync(List<CovewareFindingDTO> dtos, string covewareHostName);
        
        Task SaveSessionDataAsync(SessionModelDTO sessionModelDTO, string vbrHostName);
    }
}
