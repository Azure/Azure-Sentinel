using VoneApiClient.Models;

namespace VoneApiClient
{
    public interface ITriggeredAlarmsApi
    {
        Task<List<TriggeredAlarm>> GetTriggeredAlarmsAsync(int offset = 0, int limit = 100);

        Task ResolveTriggeredAlarmAsync(int predefinedAlarmId);
    }
}
