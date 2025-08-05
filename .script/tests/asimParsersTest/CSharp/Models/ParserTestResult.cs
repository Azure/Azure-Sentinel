using System;

namespace AsimParserValidation.Models
{
    /// <summary>
    /// Represents the result of a parser validation test
    /// </summary>
    public class ParserTestResult
    {
        /// <summary>
        /// The test value that was evaluated
        /// </summary>
        public string TestValue { get; set; } = string.Empty;

        /// <summary>
        /// The name or description of the test
        /// </summary>
        public string TestName { get; set; } = string.Empty;

        /// <summary>
        /// The result of the test (Pass/Fail)
        /// </summary>
        public TestStatus Result { get; set; }

        /// <summary>
        /// Additional details or error information
        /// </summary>
        public string? Details { get; set; }

        /// <summary>
        /// Timestamp when the test was executed
        /// </summary>
        public DateTime ExecutedAt { get; set; } = DateTime.UtcNow;

        /// <summary>
        /// Creates a successful test result
        /// </summary>
        public static ParserTestResult Pass(string testValue, string testName, string? details = null)
        {
            return new ParserTestResult
            {
                TestValue = testValue,
                TestName = testName,
                Result = TestStatus.Pass,
                Details = details
            };
        }

        /// <summary>
        /// Creates a failed test result
        /// </summary>
        public static ParserTestResult Fail(string testValue, string testName, string? details = null)
        {
            return new ParserTestResult
            {
                TestValue = testValue,
                TestName = testName,
                Result = TestStatus.Fail,
                Details = details
            };
        }

        /// <summary>
        /// Creates a warning test result
        /// </summary>
        public static ParserTestResult Warning(string testValue, string testName, string? details = null)
        {
            return new ParserTestResult
            {
                TestValue = testValue,
                TestName = testName,
                Result = TestStatus.Warning,
                Details = details
            };
        }
    }

    /// <summary>
    /// Enumeration for test status
    /// </summary>
    public enum TestStatus
    {
        Pass,
        Fail,
        Warning,
        Skipped
    }
}
