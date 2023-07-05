using Octokit;
using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace Microsoft.Sentinel.ValidationFramework
{
    public class ValidationFramework
    {
        private static List<ValidationRule> _validationRules = new List<ValidationRule>();

        public static void AddValidationRule(ValidationRule validationRule)
        {
            _validationRules.Add(validationRule);
        }
              

        //public static void StoreValidationResults(List<Validation> validationResults)
        //{
        //    // Store the validation results in a database
        //}

        public static void RunValidationsOnPR(string prNumber)
        {
            // Get the list of files committed as part of the PR
            List<string> prFiles = GetPRFiles(prNumber);

            // Iterate through the list of files and run the validations
            foreach (string prFile in prFiles)
            {
                // Run validations on files that match the content path regex of validation rules
                foreach (ValidationRule validationRule in _validationRules)
                {
                    if (validationRule.ContentPathRegex.IsMatch(prFile))
                    {
                        if (!validationRule.Validate(prFile))
                        {
                            // Add a review comment to the PR with the validation error message
                        }
                    }
                }
            }
        }

        private static List<string> GetPRFiles(string prNumber)
        {
            //// Get the pull request from GitHub
            //PullRequest pr = GitHubClient.GetPullRequest(prNumber);

            //// Get the list of files committed as part of the PR
            //List<string> prFiles = pr.Files.Select(file => file.Path).ToList();

            //return prFiles;

            return new List<string>();
        }
    }
}
