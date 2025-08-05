using System.Collections.Generic;
using System.Threading.Tasks;
using Microsoft.AspNetCore.Mvc;
using Microsoft.Extensions.Logging;
using AsimParserValidation.Api;
using AsimParserValidation.Models;

namespace AsimParserValidation.Controllers
{
    /// <summary>
    /// WebAPI controller for ASIM parser validation
    /// </summary>
    [ApiController]
    [Route("api/[controller]")]
    [Produces("application/json")]
    public class ParserValidationController : ControllerBase
    {
        private readonly AsimParserValidationApi _validationApi;
        private readonly ILogger<ParserValidationController> _logger;

        /// <summary>
        /// Initializes a new instance of the ParserValidationController
        /// </summary>
        /// <param name="validationApi">The validation API instance</param>
        /// <param name="logger">Logger instance</param>
        public ParserValidationController(
            AsimParserValidationApi validationApi, 
            ILogger<ParserValidationController> logger)
        {
            _validationApi = validationApi;
            _logger = logger;
        }

        /// <summary>
        /// Validates multiple parser files
        /// </summary>
        /// <param name="request">Validation request containing parser paths and configuration</param>
        /// <returns>Validation result</returns>
        /// <response code="200">Validation completed successfully</response>
        /// <response code="400">Invalid request data</response>
        /// <response code="500">Internal server error</response>
        [HttpPost("validate")]
        [ProducesResponseType(typeof(ValidationResult), 200)]
        [ProducesResponseType(400)]
        [ProducesResponseType(500)]
        public async Task<ActionResult<ValidationResult>> ValidateAsync([FromBody] ValidationRequest request)
        {
            if (request == null)
            {
                return BadRequest("Request cannot be null");
            }

            if (request.ParserPaths == null || request.ParserPaths.Count == 0)
            {
                return BadRequest("At least one parser path must be provided");
            }

            try
            {
                _logger.LogInformation("Validating {Count} parser files", request.ParserPaths.Count);
                
                var validationInput = request.ToValidationInput();
                var result = await _validationApi.ValidateParsersAsync(validationInput);
                
                _logger.LogInformation("Validation completed. Success: {Success}", result.Success);
                return Ok(result);
            }
            catch (System.Exception ex)
            {
                _logger.LogError(ex, "Error during parser validation");
                return StatusCode(500, $"Validation failed: {ex.Message}");
            }
        }

        /// <summary>
        /// Validates a single parser file
        /// </summary>
        /// <param name="parserPath">Path or URL to the parser file</param>
        /// <param name="baseUrl">Optional base URL for constructing parser URLs</param>
        /// <returns>Validation result</returns>
        /// <response code="200">Validation completed successfully</response>
        /// <response code="400">Invalid request data</response>
        /// <response code="500">Internal server error</response>
        [HttpGet("validate-single")]
        [ProducesResponseType(typeof(ValidationResult), 200)]
        [ProducesResponseType(400)]
        [ProducesResponseType(500)]
        public async Task<ActionResult<ValidationResult>> ValidateSingleAsync(
            [FromQuery] string parserPath, 
            [FromQuery] string? baseUrl = null)
        {
            if (string.IsNullOrWhiteSpace(parserPath))
            {
                return BadRequest("Parser path cannot be empty");
            }

            try
            {
                _logger.LogInformation("Validating single parser: {ParserPath}", parserPath);
                
                var result = await _validationApi.ValidateSingleParserAsync(parserPath, baseUrl);
                
                _logger.LogInformation("Single parser validation completed. Success: {Success}", result.Success);
                return Ok(result);
            }
            catch (System.Exception ex)
            {
                _logger.LogError(ex, "Error during single parser validation");
                return StatusCode(500, $"Validation failed: {ex.Message}");
            }
        }

        /// <summary>
        /// Gets detailed test results for a specific parser
        /// </summary>
        /// <param name="parserPath">Path or URL to the parser file</param>
        /// <param name="baseUrl">Optional base URL for constructing parser URLs</param>
        /// <returns>List of detailed test results</returns>
        /// <response code="200">Test results retrieved successfully</response>
        /// <response code="400">Invalid request data</response>
        /// <response code="500">Internal server error</response>
        [HttpGet("test-results")]
        [ProducesResponseType(typeof(List<ParserTestResult>), 200)]
        [ProducesResponseType(400)]
        [ProducesResponseType(500)]
        public async Task<ActionResult<List<ParserTestResult>>> GetTestResultsAsync(
            [FromQuery] string parserPath, 
            [FromQuery] string? baseUrl = null)
        {
            if (string.IsNullOrWhiteSpace(parserPath))
            {
                return BadRequest("Parser path cannot be empty");
            }

            try
            {
                _logger.LogInformation("Getting test results for parser: {ParserPath}", parserPath);
                
                var results = await _validationApi.ValidateSpecificParserAsync(parserPath, baseUrl);
                
                _logger.LogInformation("Retrieved {Count} test results", results.Count);
                return Ok(results);
            }
            catch (System.Exception ex)
            {
                _logger.LogError(ex, "Error getting test results");
                return StatusCode(500, $"Failed to get test results: {ex.Message}");
            }
        }

        /// <summary>
        /// Gets the current validation configuration
        /// </summary>
        /// <returns>Current validation configuration</returns>
        /// <response code="200">Configuration retrieved successfully</response>
        [HttpGet("configuration")]
        [ProducesResponseType(typeof(object), 200)]
        public ActionResult GetConfiguration()
        {
            var config = _validationApi.GetConfiguration();
            return Ok(new
            {
                config.FailOnParserNotFound,
                config.IncludeVimParserTesting,
                config.MaxConcurrentRequests,
                config.HttpTimeoutSeconds,
                config.UseExclusionList,
                config.ValidateSampleDataFiles
            });
        }

        /// <summary>
        /// Health check endpoint
        /// </summary>
        /// <returns>Health status</returns>
        /// <response code="200">Service is healthy</response>
        [HttpGet("health")]
        [ProducesResponseType(200)]
        public ActionResult HealthCheck()
        {
            return Ok(new { Status = "Healthy", Timestamp = System.DateTime.UtcNow });
        }
    }
}
