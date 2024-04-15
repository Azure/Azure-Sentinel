using System;
using System.ComponentModel.DataAnnotations;

namespace Microsoft.Azure.Sentinel.Analytics.Management.AnalyticsManagement.Contracts.Model.ARM.ModelValidation
{
    public class FrequencyLimitationForLongPeriodQuery : ValidationAttribute
    {
        public FrequencyLimitationForLongPeriodQuery()
            : base("Invalid Properties for Scheduled alert rule: When 'queryPeriod' greater than or equal to 2 days, the 'queryFrequency' should be greater than or equal to 1 hour.")
        { }

        public override bool IsValid(object value)
        {
            var queryPeriod = (TimeSpan)value.GetType().GetProperty("QueryPeriod")?.GetValue(value, null);
            var queryFrequency = (TimeSpan)value.GetType().GetProperty("QueryFrequency")?.GetValue(value, null);

            return queryPeriod.TotalDays >= 2 ? queryFrequency.TotalHours >= 1 : true;
        }
    }
}
