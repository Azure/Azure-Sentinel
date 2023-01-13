using System.Collections.Generic;
using System.ComponentModel.DataAnnotations;
using System.Text.RegularExpressions;

namespace Microsoft.Azure.Sentinel.Analytics.Management.AnalyticsManagement.Contracts.Model.ARM.ModelValidation
{
    public class DictionaryValueMatchesRegexAttribute : ValidationAttribute
    {
        private readonly Regex _valueRegex;

        public DictionaryValueMatchesRegexAttribute(string regexToMatch)
        {
            _valueRegex = new Regex(regexToMatch);
        }

        protected override ValidationResult IsValid(object value, ValidationContext validationContext)
        {
            if (value == null)
            {
                return ValidationResult.Success;
            }

            var dictionaryValue = (Dictionary<string, string>)value;
            var fieldName = validationContext.MemberName;

            foreach (string entryValue in dictionaryValue.Values)
            {
                if (!_valueRegex.IsMatch(entryValue))
                {
                    return new ValidationResult($"The value '{entryValue}' in {fieldName} is invalid. The value must start with a letter or underscore, and contain only alphanumeric English characters");
                }
            }

            return ValidationResult.Success;
        }
    }
}
