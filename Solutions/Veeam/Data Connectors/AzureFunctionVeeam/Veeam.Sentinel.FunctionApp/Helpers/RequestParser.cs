using Microsoft.AspNetCore.Http;

namespace Sentinel.Helpers
{
    static internal class RequestParser
    {
        internal static Guid GetBackupObjectId(HttpRequest request)
        {
            var backupObjectId = request.Query["backupObjectId"].FirstOrDefault() ?? throw new ArgumentNullException("backupObjectId");

            if (!Guid.TryParse(backupObjectId, out Guid backupObjectGuid))
                throw new ArgumentException($"Invalid session ID: '{backupObjectId}' is not a valid GUID. {nameof(backupObjectId)}");

            return backupObjectGuid;
        }

        internal static string GetVmHostNameFromQuery(HttpRequest request)
        {
            return request.Query["VmHostName"].FirstOrDefault() ?? throw new ArgumentNullException("VmHostName");
        }

        internal static string GetObjectIdFromQuery(HttpRequest request)
        {
            return request.Query["ObjectId"].FirstOrDefault() ?? throw new ArgumentNullException("ObjectId");
        }

        internal static Guid GetSessionId(HttpRequest request)
        {
            var sessionId = request.Query["sessionId"].FirstOrDefault() ?? throw new ArgumentNullException("sessionId");

            if (!Guid.TryParse(sessionId, out Guid sessionIdGuid))
                throw new ArgumentException($"Invalid session ID: '{sessionId}' is not a valid GUID. {nameof(sessionId)}");

            return sessionIdGuid;
        }

        static internal string GetVbrHostNameFromQuery(HttpRequest request)
        {
            return request.Query["vbrHostName"].FirstOrDefault() ?? throw new ArgumentNullException("vbrHostName");
        }

        static internal string GetCovewareHostNameFromQuery(HttpRequest request)
        {
            return request.Query["CovewareHostName"].FirstOrDefault() ?? "CovewareServer";
        }

        internal static string GetViTypeFromQuery(HttpRequest request)
        {
            return request.Query["ViType"].FirstOrDefault() ?? throw new ArgumentNullException("ViType");
        }

        internal static string GetVmNameFromQuery(HttpRequest request)
        {
            return request.Query["VmName"].FirstOrDefault() ?? throw new ArgumentNullException("VmName");
        }

        internal static DateTime GetDetectionTimeUtc(HttpRequest request)
        {
            var detectionTimeStr = request.Query["DetectionTime"].FirstOrDefault() ?? throw new ArgumentNullException("DetectionTime");

            if (!DateTime.TryParse(detectionTimeStr, out DateTime detectionTime))
                throw new ArgumentException($"Invalid DetectionTime: '{detectionTimeStr}' is not a valid GUID. {nameof(detectionTime)}");

            return detectionTime;
        }

        internal static string? GetMachineFqdn(HttpRequest request)
        {
            return request.Query["MachineFQDN"].FirstOrDefault();
        }

        internal static string? GetMachineIpv6(HttpRequest request)
        {
            return request.Query["MachineIpv6"].FirstOrDefault();
        }

        internal static string? GetMachineIpv4(HttpRequest request)
        {
            return request.Query["MachineIpv4"].FirstOrDefault();
        }

        internal static string? GetMachineUuid(HttpRequest request)
        {
            return request.Query["MachineUuid"].FirstOrDefault();
        }

        internal static string GetDetails(HttpRequest request)
        {
            return request.Query["Details"].FirstOrDefault() ?? throw new ArgumentNullException("Details");
        }
        internal static string GetEngine(HttpRequest request)
        {
            return request.Query["Engine"].FirstOrDefault() ?? throw new ArgumentNullException("Engine");
        }

        internal static string GetVoneHostNameFromQuery(HttpRequest request)
        {
            return request.Query["VoneHostName"].FirstOrDefault() ?? throw new ArgumentNullException("VoneHostName");
        }

        internal static int ParseTriggeredAlarmId(HttpRequest request)
        {
            var triggeredAlarmId = request.Query["TriggeredAlarmId"].FirstOrDefault() ?? throw new ArgumentNullException("TriggeredAlarmId");

            if (!int.TryParse(triggeredAlarmId, out int triggeredAlarmIdInt))
                throw new ArgumentNullException("TriggeredAlarmId cannot be null or empty");

           return triggeredAlarmIdInt;
        }

        public static Guid GetRestorePointId(HttpRequest request)
        {
            var restorePointId = request.Query["restorePointId"].FirstOrDefault() ?? throw new ArgumentNullException("restorePointId");

            if (!Guid.TryParse(restorePointId, out Guid restorePointGuid))
                throw new ArgumentException($"Invalid restore point ID: '{restorePointId}' is not a valid GUID. {nameof(restorePointId)}");

            return restorePointGuid;
        }
    }
}
