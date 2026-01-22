using System.Globalization;
using Sentinel.Constants;

namespace Sentinel.Helpers
{
    public class DateTimeParser
    {
        public static DateTime ParseExactUniversal(string dateString)
        {
            if (!DateTime.TryParseExact(
                dateString,
                LogAnalyticsConstants.DefaultTimeFormat,
                CultureInfo.InvariantCulture,
                DateTimeStyles.None,
                out DateTime dt))
            {
                throw new FormatException(
                    $"Could not parse '{dateString}' as DateTime with format '{LogAnalyticsConstants.DefaultTimeFormat}'.");
            }

            return dt;
        }
    }
}
