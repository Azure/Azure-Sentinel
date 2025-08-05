using System;
using System.Collections.Generic;
using System.Threading.Tasks;
using AsimParserValidation.Configuration;
using AsimParserValidation.Models;
using AsimParserValidation.Services;

namespace AsimParserValidation.Api
{
    /// <summary>
    /// API wrapper for ASIM Parser Validation functionality
    /// Suitable for integration into Web API or Windows Forms applications
    /// </summary>
    public class AsimParserValidationApi
    {
        private readonly IParserValidationOrchestrator _orchestrator;
        private readonly ValidationConfiguration _configuration;

        /// <summary>
        /// Initializes a new instance of the AsimParserValidationApi
        /// </summary>
        /// <param name="orchestrator">The parser validation orchestrator</param>
        /// <param name="configuration">Validation configuration</param>
        public AsimParserValidationApi(
            IParserValidationOrchestrator orchestrator,
            ValidationConfiguration? configuration = null)
        {
            _orchestrator = orchestrator ?? throw new ArgumentNullException(nameof(orchestrator));
            _configuration = configuration ?? new ValidationConfiguration();
        }

        /// <summary>
        /// Validates parsers based on user input
        /// </summary>
        /// <param name="input">Validation input containing parser paths and configuration</param>
        /// <returns>Validation result</returns>
        public async Task<ValidationResult> ValidateParsersAsync(ValidationInput input)
        {
            return await _orchestrator.RunValidationAsync(input);
        }

        /// <summary>
        /// Validates a single parser file
        /// </summary>
        /// <param name="parserPath">Path or URL to the parser file</param>
        /// <param name="baseUrl">Optional base URL for constructing parser URLs</param>
        /// <returns>Validation result</returns>
        public async Task<ValidationResult> ValidateSingleParserAsync(string parserPath, string? baseUrl = null)
        {
            var input = ValidationInput.FromSingleParser(parserPath, baseUrl);
            return await _orchestrator.RunValidationAsync(input);
        }

        /// <summary>
        /// Validates multiple parser files
        /// </summary>
        /// <param name="parserPaths">List of parser paths or URLs</param>
        /// <param name="baseUrl">Optional base URL for constructing parser URLs</param>
        /// <returns>Validation result</returns>
        public async Task<ValidationResult> ValidateMultipleParsersAsync(List<string> parserPaths, string? baseUrl = null)
        {
            var input = ValidationInput.FromMultipleParsers(parserPaths, baseUrl);
            return await _orchestrator.RunValidationAsync(input);
        }

        /// <summary>
        /// Validates a specific parser and returns detailed test results
        /// </summary>
        /// <param name="parserPath">Path or URL to the parser file</param>
        /// <param name="baseUrl">Optional base URL for constructing parser URLs</param>
        /// <returns>Detailed validation results for the specific parser</returns>
        public async Task<List<ParserTestResult>> ValidateSpecificParserAsync(string parserPath, string? baseUrl = null)
        {
            return await _orchestrator.ValidateSpecificParserAsync(parserPath, baseUrl);
        }

        /// <summary>
        /// Gets the current validation configuration
        /// </summary>
        /// <returns>Current validation configuration</returns>
        public ValidationConfiguration GetConfiguration()
        {
            return _configuration;
        }

        /// <summary>
        /// Creates a new API instance with dependency injection setup
        /// This method is useful for integration into existing applications
        /// </summary>
        /// <param name="configuration">Optional validation configuration</param>
        /// <returns>Configured API instance</returns>
        public static AsimParserValidationApi CreateInstance(ValidationConfiguration? configuration = null)
        {
            // This would typically use your application's DI container
            // For demonstration, we'll create a simplified version
            
            var httpClient = new System.Net.Http.HttpClient();
            
            // Create services manually (in real app, use DI container)
            var fileService = new FileService(Microsoft.Extensions.Logging.Abstractions.NullLogger<FileService>.Instance);
            var httpYamlService = new HttpYamlService(httpClient, Microsoft.Extensions.Logging.Abstractions.NullLogger<HttpYamlService>.Instance);
            var parserValidationService = new ParserValidationService(httpYamlService, Microsoft.Extensions.Logging.Abstractions.NullLogger<ParserValidationService>.Instance);
            var orchestrator = new ParserValidationOrchestrator(
                httpYamlService,
                parserValidationService,
                fileService,
                Microsoft.Extensions.Logging.Abstractions.NullLogger<ParserValidationOrchestrator>.Instance,
                configuration
            );

            return new AsimParserValidationApi(orchestrator, configuration);
        }
    }
}
