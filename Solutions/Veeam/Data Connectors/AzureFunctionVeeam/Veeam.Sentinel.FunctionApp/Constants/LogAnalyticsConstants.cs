namespace Sentinel.Constants
{
    public class LogAnalyticsConstants
    {
        public const int DefaultQueryWindowDays = 30;
        public static readonly TimeSpan DefaultQueryTimeSpan = TimeSpan.FromDays(DefaultQueryWindowDays);
        public const string DefaultTimeFormat = "yyyy-MM-dd HH:mm:ss.ffffff";
        public const string TimeFormatMalwareEvents = "yyyy-MM-ddTHH:mm:ss.fffZ";
    }
}
