using System;
using System.ComponentModel.DataAnnotations;

namespace Microsoft.Azure.Sentinel.Analytics.Management.AnalyticsManagement.Contracts.Model.ARM.ModelValidation
{
    public class PeriodGreaterThanOrEqualFrequencyAttribute : ValidationAttribute
    {
        public PeriodGreaterThanOrEqualFrequencyAttribute()
            : base("Invalid Properties for Scheduled alert rule: 'queryPeriod' should be greater than or equal to 'queryFrequency'")
        { }

        public override bool IsValid(object value)
        {
            var queryPeriod = value.GetType().GetProperty("QueryPeriod")?.GetValue(value, null);
            var queryFrequency = value.GetType().GetProperty("QueryFrequency")?.GetValue(value, null);

            return queryPeriod != null
                && queryFrequency != null
                && (TimeSpan)queryPeriod >= (TimeSpan)queryFrequency;
        }
    }
}
