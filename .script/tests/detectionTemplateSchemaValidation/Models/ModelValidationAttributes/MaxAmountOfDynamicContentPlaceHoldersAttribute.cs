using System.ComponentModel.DataAnnotations;
using System.Text.RegularExpressions;
using System.Collections.Generic;
using System.Linq;

namespace Microsoft.Azure.Sentinel.Analytics.Management.AnalyticsManagement.Contracts.Model.ARM.ModelValidation
{
    public class MaxAmountOfDynamicContentPlaceHoldersAttribute : ValidationAttribute
    {
        private const string FORMAT_PREFIX_CHARACTER = "{{";
        private const string FORMAT_SUFFFIX_CHARACTER = "}}";
        private static readonly Regex _placeholderRegExp = new Regex($"{FORMAT_PREFIX_CHARACTER}([^{{}}]*){FORMAT_SUFFFIX_CHARACTER}", RegexOptions.Compiled);
        private readonly int _maxAmount;

        public MaxAmountOfDynamicContentPlaceHoldersAttribute(int maxAmount)
        {
            _maxAmount = maxAmount;
        }

        protected override ValidationResult IsValid(object value, ValidationContext validationContext)
        {
            if (value == null)
            {
                return ValidationResult.Success;
            }

            var format = (string)value;
            var fieldName = validationContext.MemberName;

            var placeHoldersAmount = ExtractPlaceHolders(format).Count;

            if (placeHoldersAmount > _maxAmount)
            {
                return new ValidationResult($"You have defined {placeHoldersAmount} parameters in '{fieldName}'. The maximum allowed is {_maxAmount}.");
            }

            return ValidationResult.Success;
        }

        private List<string> ExtractPlaceHolders(string format)
        {
            MatchCollection placeholderMatchCollection = _placeholderRegExp.Matches(format ?? string.Empty);

            List<string> placeholders = placeholderMatchCollection.OfType<Match>().Select(placeholderMatch => placeholderMatch.Groups[1].Value).ToList();

            return placeholders;
        }
    }
}
