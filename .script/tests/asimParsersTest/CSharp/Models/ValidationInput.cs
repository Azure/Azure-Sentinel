using System.Collections.Generic;

namespace AsimParserValidation.Models
{
    /// <summary>
    /// Input model for parser validation containing user-provided parameters
    /// </summary>
    public class ValidationInput
    {
        /// <summary>
        /// List of parser file paths or URLs to validate
        /// </summary>
        public List<string> ParserPaths { get; set; } = new();

        /// <summary>
        /// Base URL for constructing parser URLs (optional)
        /// If not provided, will use the default GitHub repository URL
        /// </summary>
        public string? BaseUrl { get; set; }

        /// <summary>
        /// Base URL for sample data files (optional)
        /// If not provided, will use the default sample data path
        /// </summary>
        public string? SampleDataBaseUrl { get; set; }

        /// <summary>
        /// Path to exclusion list file (optional)
        /// </summary>
        public string? ExclusionListPath { get; set; }

        /// <summary>
        /// Whether to validate vim parsers in addition to ASim parsers
        /// </summary>
        public bool IncludeVimParsers { get; set; } = true;

        /// <summary>
        /// Whether to validate sample data files existence
        /// </summary>
        public bool ValidateSampleData { get; set; } = true;

        /// <summary>
        /// Creates a validation input with a single parser path
        /// </summary>
        /// <param name="parserPath">Path or URL to the parser file</param>
        /// <param name="baseUrl">Optional base URL</param>
        /// <returns>Validation input instance</returns>
        public static ValidationInput FromSingleParser(string parserPath, string? baseUrl = null)
        {
            return new ValidationInput
            {
                ParserPaths = new List<string> { parserPath },
                BaseUrl = baseUrl
            };
        }

        /// <summary>
        /// Creates a validation input with multiple parser paths
        /// </summary>
        /// <param name="parserPaths">List of parser paths or URLs</param>
        /// <param name="baseUrl">Optional base URL</param>
        /// <returns>Validation input instance</returns>
        public static ValidationInput FromMultipleParsers(List<string> parserPaths, string? baseUrl = null)
        {
            return new ValidationInput
            {
                ParserPaths = parserPaths ?? new List<string>(),
                BaseUrl = baseUrl
            };
        }
    }

    /// <summary>
    /// Request model for API endpoints
    /// </summary>
    public class ValidationRequest
    {
        /// <summary>
        /// List of parser file paths or URLs to validate
        /// </summary>
        public List<string> ParserPaths { get; set; } = new();

        /// <summary>
        /// Base URL for constructing parser URLs (optional)
        /// Example: "https://raw.githubusercontent.com/Azure/Azure-Sentinel/main"
        /// </summary>
        public string? BaseUrl { get; set; }

        /// <summary>
        /// Base URL for sample data files (optional)
        /// </summary>
        public string? SampleDataBaseUrl { get; set; }

        /// <summary>
        /// Path to exclusion list file (optional)
        /// </summary>
        public string? ExclusionListPath { get; set; }

        /// <summary>
        /// Whether to validate vim parsers in addition to ASim parsers
        /// </summary>
        public bool IncludeVimParsers { get; set; } = true;

        /// <summary>
        /// Whether to validate sample data files existence
        /// </summary>
        public bool ValidateSampleData { get; set; } = true;

        /// <summary>
        /// Converts the request to a validation input
        /// </summary>
        /// <returns>Validation input instance</returns>
        public ValidationInput ToValidationInput()
        {
            return new ValidationInput
            {
                ParserPaths = ParserPaths,
                BaseUrl = BaseUrl,
                SampleDataBaseUrl = SampleDataBaseUrl,
                ExclusionListPath = ExclusionListPath,
                IncludeVimParsers = IncludeVimParsers,
                ValidateSampleData = ValidateSampleData
            };
        }
    }
}
