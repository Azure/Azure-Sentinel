using System;
using System.Collections.Generic;
using System.Linq;
using Microsoft.Extensions.Logging;
using AsimParserValidation.Models;

namespace AsimParserValidation.Services
{
    /// <summary>
    /// Service for outputting validation results in various formats
    /// </summary>
    public interface IOutputService
    {
        /// <summary>
        /// Prints test results in a formatted table
        /// </summary>
        /// <param name="results">Test results to display</param>
        void PrintResultsTable(List<ParserTestResult> results);

        /// <summary>
        /// Prints a test header for a parser
        /// </summary>
        /// <param name="parserName">Name of the parser</param>
        void PrintTestHeader(string parserName);

        /// <summary>
        /// Prints validation summary
        /// </summary>
        /// <param name="validationResult">Overall validation result</param>
        void PrintValidationSummary(ValidationResult validationResult);

        /// <summary>
        /// Prints individual parser results
        /// </summary>
        /// <param name="parserResult">Parser validation result</param>
        void PrintParserResult(ParserValidationResult parserResult);

        /// <summary>
        /// Prints modified files list
        /// </summary>
        /// <param name="files">List of modified files</param>
        void PrintModifiedFiles(List<string> files);
    }

    /// <summary>
    /// Implementation of output service for console output
    /// </summary>
    public class ConsoleOutputService : IOutputService
    {
        private readonly ILogger<ConsoleOutputService> _logger;

        // ANSI escape sequences for colors
        private const string Green = "\u001b[92m";
        private const string Yellow = "\u001b[93m";
        private const string Red = "\u001b[91m";
        private const string Reset = "\u001b[0m";

        public ConsoleOutputService(ILogger<ConsoleOutputService> logger)
        {
            _logger = logger ?? throw new ArgumentNullException(nameof(logger));
        }

        /// <inheritdoc />
        public void PrintResultsTable(List<ParserTestResult> results)
        {
            if (results == null || !results.Any())
            {
                Console.WriteLine("No test results to display.");
                return;
            }

            try
            {
                // Create table headers
                var headers = new[] { "S.No", "Test Value", "Test Name", "Result" };
                var columnWidths = CalculateColumnWidths(results, headers);

                // Print header
                PrintTableHeader(headers, columnWidths);
                PrintTableSeparator(columnWidths);

                // Print rows
                for (int i = 0; i < results.Count; i++)
                {
                    PrintTableRow(i + 1, results[i], columnWidths);
                }

                PrintTableSeparator(columnWidths);
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Error printing results table");
                Console.WriteLine("Error displaying results table.");
            }
        }

        /// <inheritdoc />
        public void PrintTestHeader(string parserName)
        {
            Console.WriteLine("***********************************");
            Console.WriteLine($"{Green}Performing tests for Parser: {parserName}{Reset}");
            Console.WriteLine("***********************************");
        }

        /// <inheritdoc />
        public void PrintValidationSummary(ValidationResult validationResult)
        {
            Console.WriteLine("\n" + new string('=', 60));
            Console.WriteLine($"{Green}VALIDATION SUMMARY{Reset}");
            Console.WriteLine(new string('=', 60));

            var statusColor = validationResult.Success ? Green : Red;
            var status = validationResult.Success ? "PASSED" : "FAILED";
            
            Console.WriteLine($"Overall Status: {statusColor}{status}{Reset}");
            Console.WriteLine($"Message: {validationResult.Message}");
            Console.WriteLine($"Executed At: {validationResult.ExecutedAt:yyyy-MM-dd HH:mm:ss} UTC");
            Console.WriteLine($"Total Parsers Processed: {validationResult.ParserResults.Count}");
            
            var successCount = validationResult.ParserResults.Count(p => p.Success);
            var failureCount = validationResult.ParserResults.Count(p => !p.Success);
            
            Console.WriteLine($"Successful Validations: {Green}{successCount}{Reset}");
            Console.WriteLine($"Failed Validations: {Red}{failureCount}{Reset}");

            if (failureCount > 0)
            {
                Console.WriteLine($"\n{Red}Failed Parsers:{Reset}");
                foreach (var failure in validationResult.ParserResults.Where(p => !p.Success))
                {
                    Console.WriteLine($"  - {failure.ParserName ?? failure.ParserPath} ({failure.ParserType}): {failure.ErrorMessage}");
                }
            }

            Console.WriteLine(new string('=', 60));
        }

        /// <inheritdoc />
        public void PrintParserResult(ParserValidationResult parserResult)
        {
            var statusColor = parserResult.Success ? Green : Red;
            var status = parserResult.Success ? "PASSED" : "FAILED";

            Console.WriteLine($"\nParser: {parserResult.ParserName ?? parserResult.ParserPath}");
            Console.WriteLine($"Type: {parserResult.ParserType}");
            Console.WriteLine($"Status: {statusColor}{status}{Reset}");

            if (!string.IsNullOrWhiteSpace(parserResult.ErrorMessage))
            {
                Console.WriteLine($"Error: {Red}{parserResult.ErrorMessage}{Reset}");
            }

            if (parserResult.TestResults.Any())
            {
                Console.WriteLine($"Test Results ({parserResult.TestResults.Count} tests):");
                PrintResultsTable(parserResult.TestResults);
            }

            // Print summary for this parser
            var passCount = parserResult.TestResults.Count(t => t.Result == TestStatus.Pass);
            var failCount = parserResult.TestResults.Count(t => t.Result == TestStatus.Fail);
            var warnCount = parserResult.TestResults.Count(t => t.Result == TestStatus.Warning);

            Console.WriteLine($"Summary: {Green}{passCount} passed{Reset}, {Red}{failCount} failed{Reset}, {Yellow}{warnCount} warnings{Reset}");

            if (parserResult.Success)
            {
                Console.WriteLine($"{Green}All tests successfully passed for this parser.{Reset}");
            }
            else
            {
                Console.WriteLine($"{Red}Some tests failed for this parser. Please check the results above.{Reset}");
            }
        }

        /// <inheritdoc />
        public void PrintModifiedFiles(List<string> files)
        {
            if (files == null || !files.Any())
            {
                Console.WriteLine("No modified files found.");
                return;
            }

            Console.WriteLine($"{Green}Following files were found to be modified:{Reset}");
            foreach (var file in files)
            {
                Console.WriteLine($"{Yellow}{file}{Reset}");
            }
        }

        #region Private Helper Methods

        private int[] CalculateColumnWidths(List<ParserTestResult> results, string[] headers)
        {
            var widths = new int[headers.Length];

            // Initialize with header widths
            for (int i = 0; i < headers.Length; i++)
            {
                widths[i] = headers[i].Length;
            }

            // Check each result row
            for (int i = 0; i < results.Count; i++)
            {
                var result = results[i];
                var row = new[]
                {
                    (i + 1).ToString(),
                    CleanAnsiCodes(result.TestValue ?? ""),
                    CleanAnsiCodes(result.TestName ?? ""),
                    CleanAnsiCodes(result.Result.ToString())
                };

                for (int j = 0; j < row.Length && j < widths.Length; j++)
                {
                    widths[j] = Math.Max(widths[j], row[j].Length);
                }
            }

            // Add some padding
            for (int i = 0; i < widths.Length; i++)
            {
                widths[i] += 2;
            }

            return widths;
        }

        private void PrintTableHeader(string[] headers, int[] widths)
        {
            Console.Write("|");
            for (int i = 0; i < headers.Length; i++)
            {
                Console.Write($" {headers[i].PadRight(widths[i] - 1)}|");
            }
            Console.WriteLine();
        }

        private void PrintTableSeparator(int[] widths)
        {
            Console.Write("|");
            for (int i = 0; i < widths.Length; i++)
            {
                Console.Write(new string('-', widths[i]) + "|");
            }
            Console.WriteLine();
        }

        private void PrintTableRow(int index, ParserTestResult result, int[] widths)
        {
            var row = new[]
            {
                index.ToString(),
                result.TestValue ?? "",
                result.TestName ?? "",
                GetColoredResult(result.Result)
            };

            Console.Write("|");
            for (int i = 0; i < row.Length && i < widths.Length; i++)
            {
                var content = row[i];
                var cleanContent = CleanAnsiCodes(content);
                var padding = widths[i] - cleanContent.Length - 1;
                Console.Write($" {content}{new string(' ', Math.Max(0, padding))}|");
            }
            Console.WriteLine();
        }

        private string GetColoredResult(TestStatus status)
        {
            return status switch
            {
                TestStatus.Pass => $"{Green}Pass{Reset}",
                TestStatus.Fail => $"{Red}Fail{Reset}",
                TestStatus.Warning => $"{Yellow}Warning{Reset}",
                TestStatus.Skipped => $"{Yellow}Skipped{Reset}",
                _ => status.ToString()
            };
        }

        private string CleanAnsiCodes(string text)
        {
            if (string.IsNullOrEmpty(text))
                return string.Empty;

            // Remove ANSI escape codes for width calculation
            return System.Text.RegularExpressions.Regex.Replace(text, @"\u001b\[[0-9;]*m", "");
        }

        #endregion
    }
}
