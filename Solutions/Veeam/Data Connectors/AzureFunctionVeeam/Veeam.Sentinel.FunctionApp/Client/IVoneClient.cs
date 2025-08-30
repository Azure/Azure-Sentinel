using VoneApiClient.Models;

namespace Sentinel.Client
{
    public interface IVoneClient
    {
        Task<List<TriggeredAlarm>> GetTriggeredAlarmsAsync();

        Task ResolveTriggeredAlarmAsync(int predefinedAlaramId);
    }
}
