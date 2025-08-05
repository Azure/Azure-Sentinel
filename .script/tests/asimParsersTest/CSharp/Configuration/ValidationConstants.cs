namespace AsimParserValidation.Configuration
{
    /// <summary>
    /// Configuration constants for the ASIM Parser Validation system
    /// </summary>
    public static class ValidationConstants
    {
        /// <summary>
        /// Base URL for the Sentinel repository raw files
        /// </summary>
        public const string SentinelRepoRawUrl = "https://raw.githubusercontent.com/Azure/Azure-Sentinel";

        /// <summary>
        /// Path to sample data in the repository
        /// </summary>
        public const string SampleDataPath = "Sample%20Data/ASIM/";

        /// <summary>
        /// Path to the parser exclusion file
        /// </summary>
        public const string ParserExclusionFilePath = ".script/tests/asimParsersTest/ExclusionListForASimTests.csv";

        /// <summary>
        /// Sentinel repository URL for git operations
        /// </summary>
        public const string SentinelRepoUrl = "https://github.com/Azure/Azure-Sentinel.git";

        /// <summary>
        /// Expected format for parser versions (X.X.X)
        /// </summary>
        public const string VersionPattern = @"^\d+\.\d+\.\d+$";

        /// <summary>
        /// Expected format for LastUpdated field (MMM DD, YYYY)
        /// </summary>
        public const string DateFormat = "MMM d, yyyy";

        /// <summary>
        /// Pattern for extracting EventProduct from KQL queries
        /// </summary>
        public const string EventProductPattern = @"EventProduct\s*=\s*['""]([^'""]+)['""]";

        /// <summary>
        /// Pattern for extracting EventVendor from KQL queries
        /// </summary>
        public const string EventVendorPattern = @"EventVendor\s*=\s*['""]([^'""]+)['""]";

        /// <summary>
        /// Pattern for extracting schema name from parser path
        /// </summary>
        public const string SchemaNamePattern = @"ASim(\w+)/";

        /// <summary>
        /// Pattern for validating ParserName format
        /// </summary>
        public const string ParserNamePattern = @"^{0}{1}";

        /// <summary>
        /// Pattern for validating EquivalentBuiltInParser format
        /// </summary>
        public const string EquivalentBuiltInParserPattern = @"^_{0}_{1}_";

        /// <summary>
        /// Default event vendor for native table parsers
        /// </summary>
        public const string DefaultEventVendor = "Microsoft";

        /// <summary>
        /// Default event product for native table parsers
        /// </summary>
        public const string DefaultEventProduct = "NativeTable";

        /// <summary>
        /// Suffix for native table parsers
        /// </summary>
        public const string NativeTableSuffix = "_Native";

        /// <summary>
        /// ASIM documentation link
        /// </summary>
        public const string AsimDocumentationLink = "https://aka.ms/AboutASIM";

        /// <summary>
        /// ASIM documentation title
        /// </summary>
        public const string AsimDocumentationTitle = "ASIM";
    }

    /// <summary>
    /// Configuration settings for the validation process
    /// </summary>
    public class ValidationConfiguration
    {
        /// <summary>
        /// Whether to fail the validation on parser file not found
        /// </summary>
        public bool FailOnParserNotFound { get; set; } = true;

        /// <summary>
        /// Whether to include vim parser testing
        /// </summary>
        public bool IncludeVimParserTesting { get; set; } = true;

        /// <summary>
        /// Maximum number of concurrent HTTP requests
        /// </summary>
        public int MaxConcurrentRequests { get; set; } = 10;

        /// <summary>
        /// HTTP client timeout in seconds
        /// </summary>
        public int HttpTimeoutSeconds { get; set; } = 30;

        /// <summary>
        /// Whether to use exclusion list for parser failures
        /// </summary>
        public bool UseExclusionList { get; set; } = true;

        /// <summary>
        /// Whether to validate sample data files
        /// </summary>
        public bool ValidateSampleDataFiles { get; set; } = true;
    }
}
