using Microsoft.Sentinel.ValidationFramework.ValidationRules.Solution;

namespace Microsoft.Sentinel.ValidationFramework
{
    internal class Program
    {
        static void Main(string[] args)
        {
            // Add the validation rule to the framework
            ValidationFramework.AddValidationRule(new SolutionIDValidationRule());

            // Example usage: Run validations on a pull request
            string prNumber = "123";
            ValidationFramework.RunValidationsOnPR(prNumber);
        }
    }
}