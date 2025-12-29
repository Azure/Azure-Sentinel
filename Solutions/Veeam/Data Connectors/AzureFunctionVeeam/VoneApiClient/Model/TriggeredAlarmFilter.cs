namespace VoneApiClient.Models;

public class TriggeredAlarmFilter
{
    public DateTime DetectedAfterTimeUtcFilter { get; set; }
    public int Limit { get; set; } 
    public int Offset { get; set; }
    public int [] PredefinedAlarmIdsFilter { get; set; } = [314, 315, 331, 332, 342, 344, 364, 365, 370, 391, 403, 316, 378, 369, 376, 377, 381, 395];
}