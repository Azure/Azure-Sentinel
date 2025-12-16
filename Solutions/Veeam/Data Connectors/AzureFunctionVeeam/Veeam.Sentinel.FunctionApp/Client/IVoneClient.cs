using VoneApiClient.Models;

namespace Sentinel.Client
{
    public interface IVoneClient
    {
        Task<List<TriggeredAlarm>> GetTriggeredAlarmsAsync(TriggeredAlarmFilter filter);

        Task ResolveTriggeredAlarmAsync(int predefinedAlaramId);
    }
}
