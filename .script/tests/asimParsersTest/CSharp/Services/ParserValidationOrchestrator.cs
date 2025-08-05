using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Threading.Tasks;
using Microsoft.Extensions.Logging;
using AsimParserValidation.Configuration;
using AsimParserValidation.Models;
using AsimParserValidation.Services;

namespace AsimParserValidation.Services
{
    /// <summary>
    /// Main orchestrator service for ASIM parser validation
    /// </summary>
    public interface IParserValidationOrchestrator
    {
        /// <summary>
        /// Validates parser files from user-provided input
        /// </summary>
        /// <param name="input">Validation input containing parser paths and configuration</param>
        /// <returns>Overall validation result</returns>
        Task<ValidationResult> RunValidationAsync(ValidationInput input);

        /// <summary>
        /// Validates a specific parser file by URL or path
        /// </summary>
        /// <param name="parserPath">Path or URL to the parser file</param>
        /// <param name="baseUrl">Base URL for constructing parser URLs (optional)</param>
        /// <returns>Validation results for the parser</returns>
        Task<List<ParserTestResult>> ValidateSpecificParserAsync(string parserPath, string? baseUrl = null);
    }

    /// <summary>
    /// Implementation of the parser validation orchestrator
    /// </summary>
    public class ParserValidationOrchestrator : IParserValidationOrchestrator
    {
        private readonly IHttpYamlService _httpYamlService;
        private readonly IParserValidationService _parserValidationService;
        private readonly IFileService _fileService;
        private readonly ILogger<ParserValidationOrchestrator> _logger;
        private readonly ValidationConfiguration _configuration;

        public ParserValidationOrchestrator(
            IHttpYamlService httpYamlService,
            IParserValidationService parserValidationService,
            IFileService fileService,
            ILogger<ParserValidationOrchestrator> logger,
            ValidationConfiguration? configuration = null)
        {
            _httpYamlService = httpYamlService ?? throw new ArgumentNullException(nameof(httpYamlService));
            _parserValidationService = parserValidationService ?? throw new ArgumentNullException(nameof(parserValidationService));
            _fileService = fileService ?? throw new ArgumentNullException(nameof(fileService));
            _logger = logger ?? throw new ArgumentNullException(nameof(logger));
            _configuration = configuration ?? new ValidationConfiguration();
        }

        /// <inheritdoc />
        public async Task<ValidationResult> RunValidationAsync(ValidationInput input)
        {
            var result = new ValidationResult();
            
            try
            {
                _logger.LogInformation("Starting parser validation with {Count} parser paths", input.ParserPaths.Count);

                if (!input.ParserPaths.Any())
                {
                    _logger.LogInformation("No parser paths provided for validation");
                    result.Success = true;
                    result.Message = "No parser paths provided for validation";
                    return result;
                }

                _logger.LogInformation("Validating {Count} parser files", input.ParserPaths.Count);
                foreach (var parserPath in input.ParserPaths)
                {
                    _logger.LogInformation("Parser path to validate: {ParserPath}", parserPath);
                }

                var sampleDataUrl = !string.IsNullOrWhiteSpace(input.SampleDataBaseUrl) 
                    ? input.SampleDataBaseUrl 
                    : $"{ValidationConstants.SentinelRepoRawUrl}/master/{ValidationConstants.SampleDataPath}";

                // Process each parser file
                foreach (var parserPath in input.ParserPaths)
                {
                    try
                    {
                        var parserResults = await ProcessParserFileAsync(parserPath, input.BaseUrl, sampleDataUrl);
                        result.ParserResults.AddRange(parserResults);
                    }
                    catch (Exception ex)
                    {
                        _logger.LogError(ex, "Error processing parser file: {ParserPath}", parserPath);
                        result.ParserResults.Add(new ParserValidationResult
                        {
                            ParserPath = parserPath,
                            Success = false,
                            ErrorMessage = $"Error processing parser: {ex.Message}"
                        });
                    }
                }

                // Check for overall failures
                var hasFailures = result.ParserResults.Any(p => !p.Success);
                var exclusionList = new List<string>();
                
                if (_configuration.UseExclusionList && !string.IsNullOrWhiteSpace(input.ExclusionListPath))
                {
                    exclusionList = await _fileService.ReadExclusionListAsync(input.ExclusionListPath);
                }
                
                if (hasFailures && _configuration.UseExclusionList && exclusionList.Any())
                {
                    // Check if all failures are in exclusion list
                    var failedParsers = result.ParserResults
                        .Where(p => !p.Success)
                        .SelectMany(p => p.TestResults)
                        .Where(t => t.Result == TestStatus.Fail)
                        .ToList();

                    var hasNonExcludedFailures = failedParsers.Any(f => 
                        !exclusionList.Contains(f.TestValue) && 
                        !exclusionList.Any(e => f.TestValue.Contains(e)));

                    result.Success = !hasNonExcludedFailures;
                    if (!result.Success)
                    {
                        result.Message = "Some tests failed for parsers not in exclusion list";
                    }
                    else
                    {
                        result.Message = "All failures are for parsers in exclusion list";
                        _logger.LogWarning("All failing parsers are in the exclusion list");
                    }
                }
                else
                {
                    result.Success = !hasFailures;
                    result.Message = hasFailures ? "Some parser validations failed" : "All parser validations passed";
                }

                _logger.LogInformation("Parser validation completed. Success: {Success}, Message: {Message}", 
                    result.Success, result.Message);
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Unexpected error during parser validation");
                result.Success = false;
                result.Message = $"Unexpected error: {ex.Message}";
            }

            return result;
        }

        /// <inheritdoc />
        public async Task<List<ParserTestResult>> ValidateSpecificParserAsync(string parserPath, string? baseUrl = null)
        {
            var sampleDataUrl = !string.IsNullOrWhiteSpace(baseUrl) 
                ? $"{baseUrl}/{ValidationConstants.SampleDataPath}" 
                : $"{ValidationConstants.SentinelRepoRawUrl}/master/{ValidationConstants.SampleDataPath}";
                
            var parserResults = await ProcessParserFileAsync(parserPath, baseUrl, sampleDataUrl);
            
            return parserResults.SelectMany(p => p.TestResults).ToList();
        }

        #region Private Methods

        private async Task<List<ParserValidationResult>> ProcessParserFileAsync(string parserPath, string? baseUrl, string sampleDataUrl)
        {
            var results = new List<ParserValidationResult>();
            
            var schemaName = _parserValidationService.ExtractSchemaName(parserPath);
            if (string.IsNullOrWhiteSpace(schemaName))
            {
                _logger.LogWarning("Could not extract schema name from parser path: {ParserPath}", parserPath);
                results.Add(new ParserValidationResult
                {
                    ParserPath = parserPath,
                    Success = false,
                    ErrorMessage = "Could not extract schema name from parser path"
                });
                return results;
            }

            // Skip certain parser types
            if (_parserValidationService.ShouldSkipParser(parserPath, schemaName))
            {
                _logger.LogInformation("Skipping parser {ParserPath} as it is a union or empty parser file", parserPath);
                return results;
            }

            // Process vim parser files
            var processedParserPath = ProcessVimParser(parserPath);
            
            // Validate ASim parser
            var asimResult = await ValidateParserTypeAsync(processedParserPath, schemaName, baseUrl, sampleDataUrl, "ASim");
            if (asimResult != null)
            {
                results.Add(asimResult);
            }

            // Validate vim parser if enabled
            if (_configuration.IncludeVimParserTesting)
            {
                var vimResult = await ValidateParserTypeAsync(processedParserPath, schemaName, baseUrl, sampleDataUrl, "vim");
                if (vimResult != null)
                {
                    results.Add(vimResult);
                }
            }

            return results;
        }

        private string ProcessVimParser(string parserPath)
        {
            // If this is a vim parser and corresponding ASim parser is not in the list, use ASim version
            if (Path.GetFileName(parserPath).StartsWith("vim"))
            {
                var asimParserPath = parserPath.Replace("vim", "ASim", StringComparison.OrdinalIgnoreCase);
                _logger.LogInformation("Processing vim parser, will validate ASim version: {AsimParserPath}", asimParserPath);
                return asimParserPath;
            }

            return parserPath;
        }

        private async Task<ParserValidationResult?> ValidateParserTypeAsync(
            string parserPath, 
            string schemaName, 
            string? baseUrl, 
            string sampleDataUrl, 
            string fileType)
        {
            try
            {
                var parserUrl = ConstructParserUrl(parserPath, baseUrl, fileType);
                var unionParserUrl = ConstructUnionParserUrl(schemaName, baseUrl, fileType);

                _logger.LogDebug("Parser URL: {ParserUrl}", parserUrl);
                _logger.LogDebug("Union Parser URL: {UnionParserUrl}", unionParserUrl);

                // Download and parse YAML files
                var parser = await _httpYamlService.ReadYamlFromUrlAsync(parserUrl);
                var unionParser = await _httpYamlService.ReadYamlFromUrlAsync(unionParserUrl);

                if (parser == null)
                {
                    var errorMessage = $"Parser file not found: {parserUrl}";
                    _logger.LogError(errorMessage);
                    
                    if (_configuration.FailOnParserNotFound)
                    {
                        return new ParserValidationResult
                        {
                            ParserPath = parserPath,
                            ParserType = fileType,
                            Success = false,
                            ErrorMessage = errorMessage
                        };
                    }
                    return null;
                }

                if (unionParser == null)
                {
                    var errorMessage = $"Union parser file not found: {unionParserUrl}";
                    _logger.LogError(errorMessage);
                    return new ParserValidationResult
                    {
                        ParserPath = parserPath,
                        ParserType = fileType,
                        Success = false,
                        ErrorMessage = errorMessage
                    };
                }

                // Perform validation
                _logger.LogInformation("Performing tests for Parser: {ParserName} (Type: {FileType})", 
                    parser.EquivalentBuiltInParser, fileType);

                var testResults = await _parserValidationService.ValidateParserAsync(
                    parser, unionParser, fileType, parserUrl, sampleDataUrl);

                var hasFailures = testResults.Any(r => r.Result == TestStatus.Fail);

                return new ParserValidationResult
                {
                    ParserPath = parserPath,
                    ParserType = fileType,
                    ParserName = parser.EquivalentBuiltInParser,
                    Success = !hasFailures,
                    TestResults = testResults,
                    ErrorMessage = hasFailures ? "Some tests failed" : null
                };
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Error validating parser type {FileType} for path {ParserPath}", fileType, parserPath);
                return new ParserValidationResult
                {
                    ParserPath = parserPath,
                    ParserType = fileType,
                    Success = false,
                    ErrorMessage = $"Error during validation: {ex.Message}"
                };
            }
        }

        private string ConstructParserUrl(string parserPath, string? baseUrl, string fileType)
        {
            var adjustedPath = parserPath;
            
            if (fileType.Equals("vim", StringComparison.OrdinalIgnoreCase))
            {
                adjustedPath = parserPath.Replace("ASim", "vim", StringComparison.OrdinalIgnoreCase);
            }

            // If the path is already a full URL, return it as-is
            if (Uri.IsWellFormedUriString(adjustedPath, UriKind.Absolute))
            {
                return adjustedPath;
            }

            // If baseUrl is provided, use it; otherwise use default
            var urlBase = !string.IsNullOrWhiteSpace(baseUrl) 
                ? baseUrl 
                : $"{ValidationConstants.SentinelRepoRawUrl}/master";

            return $"{urlBase.TrimEnd('/')}/{adjustedPath.TrimStart('/')}";
        }

        private string ConstructUnionParserUrl(string schemaName, string? baseUrl, string fileType)
        {
            var unionFileType = fileType.Equals("vim", StringComparison.OrdinalIgnoreCase) ? "im" : "ASim";
            var unionPath = $"Parsers/ASim{schemaName}/Parsers/{unionFileType}{schemaName}.yaml";
            
            var urlBase = !string.IsNullOrWhiteSpace(baseUrl) 
                ? baseUrl 
                : $"{ValidationConstants.SentinelRepoRawUrl}/master";

            return $"{urlBase.TrimEnd('/')}/{unionPath}";
        }

        #endregion
    }
}
