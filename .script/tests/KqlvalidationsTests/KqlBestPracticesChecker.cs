using System;
using System.Collections.Generic;

namespace Kqlvalidations.Tests
{
    public class KqlBestPracticesChecker
    {
        public static string CheckBestPractices(string queryStr, string fileName)
        {
            var suggestions = new List<string>();

            // Rule 1: Don't use the long data type for datetime columns.
            CheckDontUseLongForDatetime(queryStr, suggestions);

            // Rule 2: Use the has operator instead of contains for string operators.
            CheckUseHasInsteadOfContains(queryStr, suggestions);

            // Rule 3: Use == instead of =~ for case-insensitive comparisons.
            CheckUseEqualsInsteadOfEqualsTilde(queryStr, suggestions);

            // Rule 4: Use in instead of in~ for case-sensitive comparisons.
            CheckUseInInsteadOfInTilde(queryStr, suggestions);

            // Rule 5: Use contains_cs instead of contains for case-sensitive comparisons.
            CheckUseContainsCSInsteadOfContains(queryStr, suggestions);

            // Rule 6: Don't use * for searching text. Look in a specific column.
            CheckSearchTextInSpecificColumn(queryStr, suggestions);

            // Rule 7: Use materialize() for let statements with reused variables
            CheckLetStatementReuse(queryStr, suggestions);

            // Rule 8: Use Col =~ "lowercasestring".
            CheckCaseInsensitiveComparisons(queryStr, suggestions);

            // Rule 9: Filter on a table column.
            CheckFilteringOnCalculatedColumn(queryStr, suggestions);

            // Rule 10: Usage of the summarize operator.
            CheckSummarizeOperator(queryStr, suggestions);

            // Rule 11: Usage of the join operator.
            CheckJoinOperator(queryStr, suggestions);

            // Rule 12: Usage of the materialize operator.
            CheckMaterializeFunction(queryStr, suggestions);

            // Combine suggestions into a single string
            return FormatSuggestionsWithDisclaimer(suggestions,fileName);
        }

        private static string FormatSuggestionsWithDisclaimer(List<string> suggestions, string fileName)
        {
            var formattedSuggestions = new List<string>
            {
                // Suggestions for the file comment
                $"KQL Best Practices Suggestions for: **{fileName}**"
            };

            // Add numbered suggestions
            for (int i = 0; i < suggestions.Count; i++)
            {
                formattedSuggestions.Add($"{i + 1}. {suggestions[i]}");
            }

            // Add the disclaimer
            formattedSuggestions.Add("\n**Disclaimer:** These suggestions are offered to enhance query efficiency and adherence to best practices. It is recommended to consider applying them for improved code quality, but their application is optional and context-dependent.");

            return string.Join("\n", formattedSuggestions);
        }



        private static void CheckDontUseLongForDatetime(string queryStr, List<string> suggestions)
        {
            var functionsToCheck = new List<string>
    {
        "unixtime_microseconds_todatetime",
        "unixtime_milliseconds_todatetime",
        "unixtime_nanoseconds_todatetime",
        "unixtime_seconds_todatetime"
    };

            foreach (var function in functionsToCheck)
            {
                // Example: Check if queryStr contains the function and suggest not using long
                if (queryStr.Contains($"{function}("))
                {
                    suggestions.Add($"Consider using datetime columns directly instead of the long data type. " +
                                    $"KQL works better with datetime than long. " +
                                    $"You can use update policies to convert unix time to the datetime data type during ingestion. " +
                                    $"Function causing the suggestion: {function}");
                }
            }
        }

        private static void CheckUseHasInsteadOfContains(string queryStr, List<string> suggestions)
        {
            // Check for the use of contains operator and suggest using has operator
            if (queryStr.Contains("contains", StringComparison.OrdinalIgnoreCase))
            {
                suggestions.Add("Use the 'has' operator instead of 'contains' for string operators.");
            }
        }

        private static void CheckUseEqualsInsteadOfEqualsTilde(string queryStr, List<string> suggestions)
        {
            // Check for the use of =~ operator and suggest using == operator for case-sensitive comparisons
            if (queryStr.Contains("=~", StringComparison.OrdinalIgnoreCase))
            {
                suggestions.Add("Use the '==' operator instead of '=~' for case-sensitive comparisons.");
            }
        }

        private static void CheckUseInInsteadOfInTilde(string queryStr, List<string> suggestions)
        {
            // Check for the use of in~ and suggest using in operator for case-sensitive comparisons
            if (queryStr.Contains("in~", StringComparison.OrdinalIgnoreCase))
            {
                suggestions.Add("Use the 'in' operator instead of 'in~' for case-sensitive comparisons.");
            }
        }

        private static void CheckUseContainsCSInsteadOfContains(string queryStr, List<string> suggestions)
        {
            // Check for the use of contains and suggest using contains_cs operator for case-sensitive comparisons
            if (queryStr.Contains("contains", StringComparison.OrdinalIgnoreCase))
            {
                suggestions.Add("Use the 'contains_cs' operator instead of 'contains' for case-sensitive comparisons.");
            }
        }

        private static void CheckSearchTextInSpecificColumn(string queryStr, List<string> suggestions)
        {
            // Check for the presence of '*' in the query.
            if (queryStr.Contains('*'))
            {
                suggestions.Add("Don't use '*' for searching text. Look in a specific column.");
            }
        }

        public static void CheckLetStatementReuse(string queryStr, List<string> suggestions)
        {
            string[] lines = queryStr.Split('\n');

            for (int i = 0; i < lines.Length; i++)
            {
                string line = lines[i].Trim();

                if (line.StartsWith("let ") && line.Contains('='))
                {
                    string variableName = line.Substring(4, line.IndexOf('=') - 4).Trim();

                    // Check if the variable is used more than once after its declaration
                    int variableUsageCount = CountVariableUsage(lines, variableName, i);

                    if (variableUsageCount > 1)
                    {
                        suggestions.Add($"Consider using the materialize() function for the '{variableName}' variable if its assignment involves computation or calculation. This can improve performance.");
                    }
                }
            }
        }

        private static int CountVariableUsage(string[] lines, string variableName, int startIndex)
        {
            int count = 0;

            for (int i = startIndex + 1; i < lines.Length; i++)
            {
                string line = lines[i].Trim();

                if (line.Contains(variableName))
                {
                    count++;
                }
            }

            return count;
        }

        public static void CheckCaseInsensitiveComparisons(string queryStr, List<string> suggestions)
        {
            string[] lines = queryStr.Split('\n');

            foreach (string line in lines)
            {
                string trimmedLine = line.Trim();

                // Check for tolower() or toupper() in the query
                if (trimmedLine.Contains("tolower(") || trimmedLine.Contains("toupper("))
                {
                    // Suggest using Col =~ "lowercasestring" instead of tolower(Col) == "lowercasestring"
                    suggestions.Add("Consider using Col =~ \"lowercasestring\" instead of tolower(Col) == \"lowercasestring\" for case-insensitive comparisons.");
                    break;  // We only need one suggestion if the pattern is found
                }
            }
        }

        public static void CheckFilteringOnCalculatedColumn(string queryStr, List<string> suggestions)
        {
            string[] lines = queryStr.Split('\n');
            string extendedColumn = "";

            for (int i = 0; i < lines.Length; i++)
            {
                string line = lines[i].Trim();

                if (line.StartsWith("| extend"))
                {
                    // Extract the extended column name
                    int equalIndex = line.IndexOf('=');

                    if (equalIndex != -1)
                    {
                        extendedColumn = line.Substring("| extend".Length, equalIndex - "| extend".Length).Trim();
                    }
                }

                if (line.Contains("| where") && line.Contains("=="))
                {
                    // Check if filtering on a calculated column is used
                    int whereIndex = line.IndexOf("| where");

                    if (whereIndex != -1 && !string.IsNullOrEmpty(extendedColumn) && line.Contains(extendedColumn))
                    {
                        suggestions.Add($"Avoid filtering on calculated columns like '{extendedColumn}'. Use in the format of 'T | where predicate(columnName == *value*)' instead of 'T | extend _value = *Expression* | where predicate(_value)'.");
                    }
                }
            }
        }

        public static void CheckSummarizeOperator(string queryStr, List<string> suggestions)
        {
            string[] lines = queryStr.Split('\n');

            for (int i = 0; i < lines.Length; i++)
            {
                string line = lines[i].Trim();

                // Check if the line is a comment
                if (!line.StartsWith("//"))
                {
                    // Check if the line contains the "summarize" keyword
                    if (line.Contains("summarize"))
                    {
                        suggestions.Add("Consider using hint.shufflekey=key with the summarize operator when group by keys have high cardinality.");
                        break;  // No need to continue checking, as we've found a summarize operator
                    }
                }
            }
        }

        public static void CheckJoinOperator(string queryStr, List<string> suggestions)
        {
            string[] lines = queryStr.Split('\n');

            for (int i = 0; i < lines.Length; i++)
            {
                string line = lines[i].Trim();

                // Check for single-line comments
                if (line.StartsWith("//"))
                {
                    continue;
                }

                // Check for join operator
                if (line.Contains("join "))
                {
                    suggestions.Add("Consider using hint.strategy=broadcast when the left side is small and the right side is large.");
                    suggestions.Add("Consider using the lookup operator instead of join when the right side is small and the left side is large.");
                    suggestions.Add("Consider using hint.shufflekey=<key> when both sides are too large.");
                    break;  // No need to continue checking, as we've found a join operator
                }
            }
        }

        public static void CheckMaterializeFunction(string queryStr, List<string> suggestions)
        {
            string[] lines = queryStr.Split('\n');

            foreach (string line in lines)
            {
                string trimmedLine = line.Trim();

                // Ignore commented lines
                if (trimmedLine.StartsWith("//"))
                {
                    continue;
                }

                // Check if materialize() is present in the line
                if (trimmedLine.Contains("materialize("))
                {
                    // Suggest using more specific operators before materialize
                    suggestions.Add("Consider using more specific operators before materialize() to reduce the materialized data set while preserving query semantics.");
                    break;  // No need to continue checking once a materialize is found
                }
            }
        }



    }
}
