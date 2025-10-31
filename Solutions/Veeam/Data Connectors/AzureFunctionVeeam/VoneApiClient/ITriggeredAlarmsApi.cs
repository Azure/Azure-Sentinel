using VoneApiClient.Models;

namespace VoneApiClient
{
    public interface ITriggeredAlarmsApi
    {
        Task<List<TriggeredAlarm>> GetTriggeredAlarmsAsync(TriggeredAlarmFilter alarmsFilter);

        Task ResolveTriggeredAlarmAsync(int predefinedAlarmId);
    }
}
