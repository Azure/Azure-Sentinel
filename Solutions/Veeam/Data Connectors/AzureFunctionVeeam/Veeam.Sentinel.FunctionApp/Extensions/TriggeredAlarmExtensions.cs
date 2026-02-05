using Sentinel.DTOs;
using VoneApiClient.Models;

namespace Sentinel.Extensions
{
    public static class TriggeredAlarmExtensions
    {
        public static TriggeredAlarmDTO ToDTO(this TriggeredAlarm alarm, string voneHostName)
        {
            return new TriggeredAlarmDTO
            {
                VoneHostName = voneHostName,
                TriggeredAlarmId = alarm.TriggeredAlarmId ?? 0,
                Name = alarm.Name,
                AlarmTemplateId = alarm.AlarmTemplateId ?? 0,
                PredefinedAlarmId = alarm.PredefinedAlarmId ?? 0,
                TriggeredTime = alarm.TriggeredTime,
                Status = alarm.Status,
                Description = alarm.Description,
                Comment = alarm.Comment,
                RepeatCount = alarm.RepeatCount ?? 0,
                ObjectId = alarm.AlarmAssignment?.ObjectId ?? 0,
                ObjectName = alarm.AlarmAssignment?.ObjectName,
                ObjectType = alarm.AlarmAssignment?.ObjectType,
                ChildAlarmsCount = alarm.ChildAlarmsCount ?? 0,
                RemediationDescription = alarm.Remediation?.FirstOrDefault()?.Description,
                RemediationMode = alarm.Remediation?.FirstOrDefault()?.Mode.ToString()
            };
        }
    }
}
