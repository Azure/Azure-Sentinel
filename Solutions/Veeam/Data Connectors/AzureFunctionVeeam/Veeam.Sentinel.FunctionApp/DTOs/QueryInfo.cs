namespace Sentinel.DTOs
{
    public class QueryInfo
    {
        public required string TableName { get; set; }
        public required string TimeColumn { get; set; }
    }

    public enum IngestedStreamType
    {
        MalwareEvents,
        BestPracticeAnalysis,
        AuthorizationEvents,
        TriggeredAlarms,
        CovewareFindings
    }

    public static class QueryConstants
    {
        public static readonly string DetectionTimeUtc = "DetectionTimeUtc";
        public static readonly string EndTime = "EndTime";
        public static readonly string CreationTime = "CreationTime";
        public static readonly string TriggeredTime = "TriggeredTime";
        public static readonly string EventTime = "EventTime";
    }
}
