using System.ComponentModel.DataAnnotations;
using System.Text.RegularExpressions;

namespace Microsoft.Azure.Sentinel.Analytics.Management.AnalyticsManagement.Contracts.Model.ARM.ModelValidation
{
    public class QueryBasedTemplateVersionValidator : ValidationAttribute
    {
        private static readonly Regex versionRegex = new Regex(@"^(\d+\.)(\d+\.)(\d+)$");

        public QueryBasedTemplateVersionValidator()
           : base("Invalid Properties for Scheduled analytics rule: 'templateVersion' should be in format X.Y.Z (all numbers).")
        { }

        public override bool IsValid(object value)
        {
            if (value == null)
            {
                return true;
            }

            string version = (string)value;
            return versionRegex.IsMatch(version);
        }
    }
}
