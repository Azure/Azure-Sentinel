namespace CovewareApiClient.Models;

public class CovewareFindingFilter
{
    public DateTime DetectedAfterTimeUtcFilter { get; set; }
    public string PageSize { get; set; } = "250";
    public string Offset { get; set; } = "0";
}