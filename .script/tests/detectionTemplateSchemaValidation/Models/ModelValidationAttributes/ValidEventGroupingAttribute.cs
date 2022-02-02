using System;
using System.ComponentModel.DataAnnotations;
using Microsoft.Azure.Sentinel.Analytics.Management.AnalyticsTemplatesService.Interface.Model;



namespace Microsoft.Azure.Sentinel.Analytics.Management.AnalyticsManagement.Contracts.Model.ARM.ModelValidation
{
    public class ValidEventGroupingAttribute : ValidationAttribute
    {

        protected override ValidationResult IsValid(object value, ValidationContext validationContext)
        {
            if (value == null)
            {
                return ValidationResult.Success;
            }

            var eventGroupingSettings = (EventGroupingSettings)value;
            var aggregatonKindStr = eventGroupingSettings.AggregationKind;
            return Enum.IsDefined(typeof(EventGroupingAggregationKind), eventGroupingSettings.AggregationKind) ? ValidationResult.Success : new ValidationResult($"Invalid aggregation kind '{eventGroupingSettings.AggregationKind}' for property '{eventGroupingSettings}'");
        }
    }
}
