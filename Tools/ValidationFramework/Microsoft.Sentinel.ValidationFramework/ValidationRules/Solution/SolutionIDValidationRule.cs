using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Text.RegularExpressions;
using System.Threading.Tasks;

namespace Microsoft.Sentinel.ValidationFramework.ValidationRules.Solution
{
    public class SolutionIDValidationRule : ValidationRule
    {
        public SolutionIDValidationRule()
        {
            // Set the content path regex pattern for SolutionMetadata.json files
            ContentPathRegex = new Regex(@".*\/Solutions\/([^\/]*)\/SolutionMetadata\.json$");
        }

        public override bool Validate(string contentPath)
        {
            // Validation logic to check properties in SolutionMetadata.json
            // Replace this with your actual validation implementation
            string solutionMetadataContent = GetSolutionMetadataContent(contentPath);

            // Example validation: Check publisherId and offerId properties
            return ValidatePublisherId(solutionMetadataContent) && ValidateOfferId(solutionMetadataContent);
        }

        private string GetSolutionMetadataContent(string contentPath)
        {
            // Replace this with your logic to fetch the content of the SolutionMetadata.json file
            // For example, you can use the GitHub API or a file reader to read the content from the provided URL
            string solutionMetadataContent = ""; // Placeholder

            return solutionMetadataContent;
        }

        private bool ValidatePublisherId(string solutionMetadataContent)
        {
            // Example validation: PublisherId should be in lowercase
            // Replace this with your actual validation implementation
            return solutionMetadataContent.Contains("\"publisherId\":") && solutionMetadataContent.Contains("\"publisherId\": \"lowercase\"");
        }

        private bool ValidateOfferId(string solutionMetadataContent)
        {
            // Example validation: OfferId should be in lowercase and contain the word "sentinel"
            // Replace this with your actual validation implementation
            return solutionMetadataContent.Contains("\"offerId\":") && solutionMetadataContent.Contains("\"offerId\": \"lowercase\"") && solutionMetadataContent.Contains("\"offerId\": \"sentinel\"");
        }
    }
}
