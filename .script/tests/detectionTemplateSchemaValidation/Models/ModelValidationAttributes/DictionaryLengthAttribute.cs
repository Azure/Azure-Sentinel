using System.Collections.Generic;
using System.ComponentModel.DataAnnotations;

namespace Microsoft.Azure.Sentinel.Analytics.Management.AnalyticsManagement.Contracts.Model.ARM.ModelValidation
{
    public class DictionaryLengthAttribute : ValidationAttribute
    {
        private readonly int _maxLength;

        public DictionaryLengthAttribute(int maxLength)
        {
            _maxLength = maxLength;
        }

        protected override ValidationResult IsValid(object value, ValidationContext validationContext)
        {
            if (value == null)
            {
                return ValidationResult.Success;
            }

            var dictionaryValue = (Dictionary<string, string>)value;
            var fieldName = validationContext.MemberName;

            return dictionaryValue.Count <= _maxLength ? ValidationResult.Success : new ValidationResult($"Maximum length of {fieldName} exceeded. {fieldName} length should be less than or equal to {_maxLength}");
        }
    }
}
