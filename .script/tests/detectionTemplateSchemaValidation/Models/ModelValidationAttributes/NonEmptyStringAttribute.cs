using System.ComponentModel.DataAnnotations;

namespace Microsoft.Azure.Sentinel.Analytics.Management.AnalyticsManagement.Contracts.Model.ARM.ModelValidation
{
    /// <summary>
    /// Validate a string is not null or empty
    /// </summary>
    public class NonEmptyStringAttribute : ValidationAttribute
    {
        protected override ValidationResult IsValid(object value, ValidationContext validationContext)
        {
            if (value == null)
            {
                return ValidationResult.Success;
            }

            var format = (string)value;
            var fieldName = validationContext.MemberName;

            if (string.IsNullOrWhiteSpace(format))
            {
                return new ValidationResult($"'{fieldName}' must have a non-empty value");
            }

            return ValidationResult.Success;
        }
    }
}
