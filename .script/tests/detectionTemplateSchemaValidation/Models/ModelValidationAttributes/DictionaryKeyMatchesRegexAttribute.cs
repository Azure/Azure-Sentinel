using System.Collections.Generic;
using System.ComponentModel.DataAnnotations;
using System.Text.RegularExpressions;

namespace Microsoft.Azure.Sentinel.Analytics.Management.AnalyticsManagement.Contracts.Model.ARM.ModelValidation
{
    public class DictionaryKeyMatchesRegexAttribute : ValidationAttribute
    {
        private readonly Regex _keyRegex;

        public DictionaryKeyMatchesRegexAttribute(string regexToMatch)
        {
            _keyRegex = new Regex(regexToMatch);
        }

        protected override ValidationResult IsValid(object value, ValidationContext validationContext)
        {
            if (value == null)
            {
                return ValidationResult.Success;
            }

            var dictionaryValue = (Dictionary<string, string>)value;
            var fieldName = validationContext.MemberName;

            foreach (string key in dictionaryValue.Keys)
            {
                if (!_keyRegex.IsMatch(key))
                {
                    return new ValidationResult($"The key '{key}' in {fieldName} is invalid. The key must start with a letter and contain only alphanumeric English characters");
                }
            }

            return ValidationResult.Success;
        }
    }
}
