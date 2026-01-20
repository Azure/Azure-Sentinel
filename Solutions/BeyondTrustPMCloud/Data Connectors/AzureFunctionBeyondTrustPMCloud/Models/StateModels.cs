using Azure;
using Azure.Data.Tables;

namespace BeyondTrustPMCloud.Models;

public class StateEntity : ITableEntity
{
    public string PartitionKey { get; set; } = "BeyondTrustPMCloud";
    public string RowKey { get; set; } = string.Empty;
    public DateTimeOffset? Timestamp { get; set; }
    public ETag ETag { get; set; }

    public DateTime LastProcessedTimestamp { get; set; }
    public int LastProcessedId { get; set; }
    public string LastProcessedEventId { get; set; } = string.Empty;
    public int RecordsProcessed { get; set; }
    public DateTime LastRunTimestamp { get; set; }
    public string Status { get; set; } = string.Empty;
    public string? ErrorMessage { get; set; }
}

public static class StateKeys
{
    public const string ActivityAudits = "ActivityAudits";
    public const string ClientEvents = "ClientEvents";
}
