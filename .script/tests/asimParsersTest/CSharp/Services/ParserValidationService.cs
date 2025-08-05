using System;
using System.Collections.Generic;
using System.Globalization;
using System.Linq;
using System.Text.RegularExpressions;
using System.Threading.Tasks;
using Microsoft.Extensions.Logging;
using AsimParserValidation.Configuration;
using AsimParserValidation.Models;
using AsimParserValidation.Services;

namespace AsimParserValidation.Services
{
    /// <summary>
    /// Service for validating ASIM parser configurations
    /// </summary>
    public interface IParserValidationService
    {
        /// <summary>
        /// Validates a parser and returns test results
        /// </summary>
        /// <param name="parser">The parser to validate</param>
        /// <param name="unionParser">The union parser for reference</param>
        /// <param name="fileType">Type of parser file (ASim or vim)</param>
        /// <param name="parserUrl">URL of the parser</param>
        /// <param name="sampleDataUrl">Base URL for sample data</param>
        /// <returns>List of test results</returns>
        Task<List<ParserTestResult>> ValidateParserAsync(
            ParserYaml parser, 
            ParserYaml unionParser, 
            string fileType, 
            string parserUrl, 
            string sampleDataUrl);

        /// <summary>
        /// Extracts schema name from parser path
        /// </summary>
        /// <param name="parserPath">Path to the parser</param>
        /// <returns>Schema name or null if not found</returns>
        string? ExtractSchemaName(string parserPath);

        /// <summary>
        /// Checks if parser should be skipped based on naming conventions
        /// </summary>
        /// <param name="parserPath">Path to the parser</param>
        /// <param name="schemaName">Schema name</param>
        /// <returns>True if should be skipped</returns>
        bool ShouldSkipParser(string parserPath, string schemaName);
    }

    /// <summary>
    /// Implementation of parser validation service
    /// </summary>
    public class ParserValidationService : IParserValidationService
    {
        private readonly IHttpYamlService _httpYamlService;
        private readonly ILogger<ParserValidationService> _logger;
        private readonly List<SchemaInfo> _schemaInfoList;

        public ParserValidationService(
            IHttpYamlService httpYamlService, 
            ILogger<ParserValidationService> logger)
        {
            _httpYamlService = httpYamlService ?? throw new ArgumentNullException(nameof(httpYamlService));
            _logger = logger ?? throw new ArgumentNullException(nameof(logger));
            _schemaInfoList = SchemaInfo.GetSchemaInfoList();
        }

        /// <inheritdoc />
        public async Task<List<ParserTestResult>> ValidateParserAsync(
            ParserYaml parser, 
            ParserYaml unionParser, 
            string fileType, 
            string parserUrl, 
            string sampleDataUrl)
        {
            var results = new List<ParserTestResult>();

            try
            {
                // Validate parser properties
                ValidateParserBasicProperties(parser, results);
                
                // Validate event fields in KQL query
                await ValidateEventFieldsAsync(parser, fileType, results);
                
                // Validate parser presence in union parser
                ValidateParserInUnion(parser, unionParser, results);
                
                // Validate metadata
                ValidateMetadata(parser, results);
                
                // Validate normalization info
                ValidateNormalization(parser, results);
                
                // Validate references
                ValidateReferences(parser, results);
                
                // Validate naming conventions
                ValidateNamingConventions(parser, fileType, results);
                
                // Validate sample data (only for ASim parsers)
                if (fileType.Equals("ASim", StringComparison.OrdinalIgnoreCase))
                {
                    await ValidateSampleDataAsync(parser, sampleDataUrl, results);
                }

                _logger.LogInformation("Validation completed for parser: {ParserName} with {ResultCount} results", 
                    parser.EquivalentBuiltInParser, results.Count);
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Error during parser validation: {ParserName}", parser.EquivalentBuiltInParser);
                results.Add(ParserTestResult.Fail("Validation", "Parser validation failed due to unexpected error", ex.Message));
            }

            return results;
        }

        /// <inheritdoc />
        public string? ExtractSchemaName(string parserPath)
        {
            if (string.IsNullOrWhiteSpace(parserPath))
                return null;

            var match = Regex.Match(parserPath, ValidationConstants.SchemaNamePattern);
            return match.Success ? match.Groups[1].Value : null;
        }

        /// <inheritdoc />
        public bool ShouldSkipParser(string parserPath, string schemaName)
        {
            if (string.IsNullOrWhiteSpace(parserPath) || string.IsNullOrWhiteSpace(schemaName))
                return false;

            var fileName = System.IO.Path.GetFileName(parserPath);
            
            // Skip union or empty parser files
            return fileName.EndsWith($"ASim{schemaName}.yaml") ||
                   fileName.EndsWith($"im{schemaName}.yaml") ||
                   fileName.EndsWith($"vim{schemaName}Empty.yaml");
        }

        #region Private Validation Methods

        private void ValidateParserBasicProperties(ParserYaml parser, List<ParserTestResult> results)
        {
            // Validate ParserName
            if (!string.IsNullOrWhiteSpace(parser.ParserName))
            {
                results.Add(ParserTestResult.Pass(parser.ParserName, "ParserName exists"));
            }
            else
            {
                results.Add(ParserTestResult.Fail("ParserName", "ParserName not found in parser YAML"));
            }

            // Validate EquivalentBuiltInParser
            if (!string.IsNullOrWhiteSpace(parser.EquivalentBuiltInParser))
            {
                results.Add(ParserTestResult.Pass(parser.EquivalentBuiltInParser, "EquivalentBuiltInParser exists"));
            }
            else
            {
                results.Add(ParserTestResult.Fail("EquivalentBuiltInParser", "EquivalentBuiltInParser not found in parser YAML"));
            }
        }

        private async Task ValidateEventFieldsAsync(ParserYaml parser, string fileType, List<ParserTestResult> results)
        {
            var parserQuery = parser.ParserQuery ?? string.Empty;
            var isNativeParser = parser.EquivalentBuiltInParser?.EndsWith(ValidationConstants.NativeTableSuffix) == true;

            // Validate EventProduct
            await ValidateEventFieldAsync(
                parserQuery, 
                ValidationConstants.EventProductPattern, 
                "EventProduct", 
                isNativeParser, 
                ValidationConstants.DefaultEventProduct, 
                results);

            // Validate EventVendor
            await ValidateEventFieldAsync(
                parserQuery, 
                ValidationConstants.EventVendorPattern, 
                "EventVendor", 
                isNativeParser, 
                ValidationConstants.DefaultEventVendor, 
                results);
        }

        private async Task ValidateEventFieldAsync(
            string parserQuery, 
            string pattern, 
            string fieldName, 
            bool isNativeParser, 
            string defaultValue, 
            List<ParserTestResult> results)
        {
            var match = Regex.Match(parserQuery, pattern);

            if (match.Success)
            {
                var value = match.Groups[1].Value;
                results.Add(ParserTestResult.Pass(value, $'"{fieldName}" field is mapped in parser'));
            }
            else if (isNativeParser)
            {
                results.Add(ParserTestResult.Pass(
                    defaultValue, 
                    $'"{fieldName}" field is not required since this is a native table parser. Static value will be used for "{fieldName}".'));
            }
            else
            {
                results.Add(ParserTestResult.Fail(
                    fieldName, 
                    $'"{fieldName}" field not mapped in parser. Please map it in parser query.'));
            }
        }

        private void ValidateParserInUnion(ParserYaml parser, ParserYaml unionParser, List<ParserTestResult> results)
        {
            var parserName = parser.ParserName;
            var equivalentBuiltInParser = parser.EquivalentBuiltInParser;

            // Check if parser exists in union parser's ParserQuery
            if (!string.IsNullOrWhiteSpace(parserName))
            {
                var unionParserQuery = unionParser.ParserQuery ?? string.Empty;
                if (unionParserQuery.Contains(parserName))
                {
                    results.Add(ParserTestResult.Pass(parserName, "Parser entry exists in union parser under \"ParserQuery\" property"));
                }
                else
                {
                    results.Add(ParserTestResult.Fail(parserName, "Parser entry not found in union parser under \"ParserQuery\" property"));
                }
            }

            // Check if parser exists in union parser's Parsers list
            if (!string.IsNullOrWhiteSpace(equivalentBuiltInParser))
            {
                var unionParsers = unionParser.Parsers ?? new List<string>();
                if (unionParsers.Contains(equivalentBuiltInParser))
                {
                    results.Add(ParserTestResult.Pass(equivalentBuiltInParser, "Parser entry exists in union parser under \"Parsers\" property"));
                }
                else
                {
                    results.Add(ParserTestResult.Fail(equivalentBuiltInParser, "Parser entry not found in union parser under \"Parsers\" property"));
                }
            }
        }

        private void ValidateMetadata(ParserYaml parser, List<ParserTestResult> results)
        {
            var metadata = parser.Parser;

            if (metadata == null)
            {
                results.Add(ParserTestResult.Fail("Parser", "Parser metadata section not found"));
                return;
            }

            // Validate Title
            if (!string.IsNullOrWhiteSpace(metadata.Title))
            {
                results.Add(ParserTestResult.Pass(metadata.Title, "This value exists in Title property"));
            }
            else
            {
                results.Add(ParserTestResult.Fail("Title", "Title not found in parser YAML"));
            }

            // Validate Version
            if (!string.IsNullOrWhiteSpace(metadata.Version))
            {
                if (Regex.IsMatch(metadata.Version, ValidationConstants.VersionPattern))
                {
                    results.Add(ParserTestResult.Pass(metadata.Version, "This value exist in the parser version property"));
                }
                else
                {
                    results.Add(ParserTestResult.Fail(metadata.Version, "The parser version should be in a three-digit format, e.g., 0.1.0"));
                }
            }
            else
            {
                results.Add(ParserTestResult.Fail("Version", "Parser version not found in parser YAML"));
            }

            // Validate LastUpdated
            if (!string.IsNullOrWhiteSpace(metadata.LastUpdated))
            {
                if (DateTime.TryParseExact(metadata.LastUpdated, ValidationConstants.DateFormat, 
                    CultureInfo.InvariantCulture, DateTimeStyles.None, out _))
                {
                    results.Add(ParserTestResult.Pass(metadata.LastUpdated, "This value exist in LastUpdated property"));
                }
                else
                {
                    results.Add(ParserTestResult.Fail(metadata.LastUpdated, 
                        "\"LastUpdated\" property exists but is not correct format. The expected format is, for example, \"Jun 29, 2024\""));
                }
            }
            else
            {
                results.Add(ParserTestResult.Fail("LastUpdated", "LastUpdated not found in parser YAML"));
            }
        }

        private void ValidateNormalization(ParserYaml parser, List<ParserTestResult> results)
        {
            var normalization = parser.Normalization;

            if (normalization == null)
            {
                results.Add(ParserTestResult.Fail("Normalization", "Normalization section not found"));
                return;
            }

            // Validate Schema
            var schema = normalization.Schema;
            if (!string.IsNullOrWhiteSpace(schema))
            {
                var schemaInfo = _schemaInfoList.FirstOrDefault(s => s.SchemaName == schema);
                if (schemaInfo != null)
                {
                    results.Add(ParserTestResult.Pass(schema, $"ASIM schema name \"{schema}\" is correct"));
                }
                else
                {
                    results.Add(ParserTestResult.Fail(schema, $"ASIM schema name \"{schema}\" is incorrect. Please re-check Schema name"));
                }
            }
            else
            {
                results.Add(ParserTestResult.Fail("Schema", "ASIM schema name not found in parser YAML"));
            }

            // Validate Schema Version
            var schemaVersion = normalization.Version;
            if (!string.IsNullOrWhiteSpace(schemaVersion) && !string.IsNullOrWhiteSpace(schema))
            {
                var schemaInfo = _schemaInfoList.FirstOrDefault(s => s.SchemaName == schema);
                if (schemaInfo != null && schemaInfo.SchemaVersion == schemaVersion)
                {
                    results.Add(ParserTestResult.Pass(schemaVersion, $"ASIM schema {schema} version is correct"));
                }
                else if (schemaInfo != null)
                {
                    results.Add(ParserTestResult.Fail(schemaVersion, 
                        $"ASIM schema \"{schema}\" version \"{schemaVersion}\" is incorrect. The correct version for ASIM schema \"{schema}\" is \"{schemaInfo.SchemaVersion}\""));
                }
                else
                {
                    results.Add(ParserTestResult.Fail(schemaVersion, "Schema not found for version validation"));
                }
            }
            else
            {
                results.Add(ParserTestResult.Fail("Version", $"ASIM schema {schema} version not found in parser YAML"));
            }
        }

        private void ValidateReferences(ParserYaml parser, List<ParserTestResult> results)
        {
            var references = parser.References;
            var schema = parser.Normalization?.Schema;

            if (references == null || !references.Any())
            {
                results.Add(ParserTestResult.Fail("References", "References section not found or empty"));
                return;
            }

            var schemaInfo = _schemaInfoList.FirstOrDefault(s => s.SchemaName == schema);

            foreach (var reference in references)
            {
                var title = reference.Title;
                var link = reference.Link;

                if (schemaInfo != null && 
                    title == schemaInfo.SchemaTitle && 
                    link == schemaInfo.SchemaLink)
                {
                    results.Add(ParserTestResult.Pass(title ?? "Unknown", "Schema specific reference link matching"));
                }
                else if (title == ValidationConstants.AsimDocumentationTitle && 
                         link == ValidationConstants.AsimDocumentationLink)
                {
                    results.Add(ParserTestResult.Pass(title, "ASim doc reference link matching"));
                }
                else if (!string.IsNullOrWhiteSpace(title) && 
                         title != ValidationConstants.AsimDocumentationTitle && 
                         title != schemaInfo?.SchemaTitle)
                {
                    results.Add(ParserTestResult.Pass(title, "Product specific reference title exist. Please access URL manually to confirm it is a valid link"));
                }
                else
                {
                    var expectedTitle = schemaInfo?.SchemaTitle ?? "Unknown";
                    var expectedLink = schemaInfo?.SchemaLink ?? "Unknown";
                    results.Add(ParserTestResult.Fail(title ?? "Unknown", 
                        $"Reference title or link not matching. Please use title as \"{expectedTitle}\" and link as \"{expectedLink}\""));
                }
            }
        }

        private void ValidateNamingConventions(ParserYaml parser, string fileType, List<ParserTestResult> results)
        {
            var parserName = parser.ParserName;
            var equivalentBuiltInParser = parser.EquivalentBuiltInParser;
            var schema = parser.Normalization?.Schema;

            // Adjust file type for validation
            var validationFileType = fileType.Equals("vim", StringComparison.OrdinalIgnoreCase) ? "Im" : fileType;

            // Validate ParserName format
            if (!string.IsNullOrWhiteSpace(parserName) && !string.IsNullOrWhiteSpace(schema))
            {
                var expectedPattern = string.Format(ValidationConstants.ParserNamePattern, fileType, schema);
                if (Regex.IsMatch(parserName, expectedPattern))
                {
                    results.Add(ParserTestResult.Pass(parserName, "ParserName is in correct format"));
                }
                else
                {
                    results.Add(ParserTestResult.Fail(parserName, "ParserName is not in correct format"));
                }
            }

            // Validate EquivalentBuiltInParser format
            if (!string.IsNullOrWhiteSpace(equivalentBuiltInParser) && !string.IsNullOrWhiteSpace(schema))
            {
                var expectedPattern = string.Format(ValidationConstants.EquivalentBuiltInParserPattern, validationFileType, schema);
                if (Regex.IsMatch(equivalentBuiltInParser, expectedPattern))
                {
                    results.Add(ParserTestResult.Pass(equivalentBuiltInParser, "EquivalentBuiltInParser is in correct format"));
                }
                else
                {
                    results.Add(ParserTestResult.Fail(equivalentBuiltInParser, 
                        $"EquivalentBuiltInParser is not in correct format. The correct format is \"_{validationFileType}_{schema}_ProductName\""));
                }
            }
        }

        private async Task ValidateSampleDataAsync(ParserYaml parser, string sampleDataUrl, List<ParserTestResult> results)
        {
            try
            {
                // Extract event vendor and product from parser query
                var parserQuery = parser.ParserQuery ?? string.Empty;
                var schema = parser.Normalization?.Schema;

                var eventVendorMatch = Regex.Match(parserQuery, ValidationConstants.EventVendorPattern);
                var eventProductMatch = Regex.Match(parserQuery, ValidationConstants.EventProductPattern);

                if (!eventVendorMatch.Success || !eventProductMatch.Success || string.IsNullOrWhiteSpace(schema))
                {
                    results.Add(ParserTestResult.Warning("Sample Data", "Cannot validate sample data - missing event vendor, product, or schema information"));
                    return;
                }

                var eventVendor = eventVendorMatch.Groups[1].Value;
                var eventProduct = eventProductMatch.Groups[1].Value;
                var sampleDataFile = $"{eventVendor}_{eventProduct}_{schema}_IngestedLogs.csv";
                var sampleDataFileUrl = $"{sampleDataUrl}{sampleDataFile}";

                var isAccessible = await _httpYamlService.IsUrlAccessibleAsync(sampleDataFileUrl);
                if (isAccessible)
                {
                    results.Add(ParserTestResult.Pass(sampleDataFile, "Sample data file exists"));
                }
                else
                {
                    results.Add(ParserTestResult.Fail("Expected sample file not found", 
                        $"Sample data file does not exist or may not be named correctly. Please include sample data file \"{eventVendor}_{eventProduct}_{schema}_IngestedLogs.csv\""));
                }
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Error validating sample data");
                results.Add(ParserTestResult.Fail("Sample Data", "Error occurred while validating sample data"));
            }
        }

        #endregion
    }
}
