using System.Collections.Generic;
using System.ComponentModel.DataAnnotations;

namespace Microsoft.Azure.Sentinel.Analytics.Management.AnalyticsManagement.Contracts.Model.ARM.ModelValidation
{
    public class DictionaryMaxKeyAndValueLengthsAttribute : ValidationAttribute
    {
        private readonly int _maxKeyLength;
        private readonly int _maxValueLength;

        public DictionaryMaxKeyAndValueLengthsAttribute(int maxKeyLength, int maxValueLength)
        {
            _maxKeyLength = maxKeyLength;
            _maxValueLength = maxValueLength;
        }

        protected override ValidationResult IsValid(object value, ValidationContext validationContext)
        {
            if (value == null)
            {
                return ValidationResult.Success;
            }

            var dictionaryValue = (Dictionary<string, string>)value;
            var fieldName = validationContext.MemberName;

            foreach (KeyValuePair<string, string> keyValuePair in dictionaryValue)
            {
                if (keyValuePair.Key.Length > _maxKeyLength)
                {
                    return new ValidationResult($"Maximum length of key '{keyValuePair.Key}' in {fieldName} exceeded. Max key length should be less than or equal to {_maxKeyLength}");
                }
                else if (keyValuePair.Value.Length > _maxValueLength)
                {
                    return new ValidationResult($"Maximum length of value '{keyValuePair.Value}' in {fieldName} exceeded. Max value length should be less than or equal to {_maxValueLength}");
                }
            }

            return ValidationResult.Success;
        }
    }
}
