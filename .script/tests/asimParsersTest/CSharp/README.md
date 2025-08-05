# ASIM Parser Validation - C# Implementation

This is a C# conversion of the Python ASIM (Advanced Security Information Model) Parser Validation script, designed with modern .NET best practices and suitable for integration into WebAPI or Windows Forms projects. **This version is optimized for user input-based validation rather than Git repository scanning.**

## Features

- **User Input-Based Validation**: Accepts parser file paths or URLs directly from users
- **Comprehensive Parser Validation**: Validates ASIM parser YAML files for correctness and compliance
- **HTTP/YAML Processing**: Downloads and parses YAML files from GitHub repositories or any URL
- **Configurable Validation Rules**: Supports exclusion lists and configurable validation options
- **Structured Logging**: Uses Microsoft.Extensions.Logging for comprehensive logging
- **Dependency Injection**: Fully supports DI container integration
- **API Wrapper**: Includes API wrapper for easy integration into existing applications
- **No Git Dependencies**: Removed Git-related code for simplified deployment and usage

## Architecture

### Core Components

1. **Models**: Data structures representing parser configurations and test results
2. **Services**: Business logic for validation and HTTP/YAML processing
3. **Configuration**: Centralized configuration management
4. **API**: Wrapper for easy integration into applications
5. **Controllers**: WebAPI controller examples
6. **WinForms**: Windows Forms example application

### Key Classes

- `ParserValidationOrchestrator`: Main orchestrator for the validation process
- `ParserValidationService`: Core validation logic for individual parsers
- `HttpYamlService`: HTTP operations and YAML parsing
- `OutputService`: Formatted output for console applications
- `ValidationInput`: Input model for user-provided parser paths and configuration

## Usage

### Console Application

```bash
# Validate single parser
dotnet run Parsers/ASimAuthentication/Parsers/ASimAuthenticationOktaSSO.yaml

# Validate multiple parsers
dotnet run parser1.yaml parser2.yaml --base-url https://raw.githubusercontent.com/Azure/Azure-Sentinel/main

# Validate with URL
dotnet run https://raw.githubusercontent.com/Azure/Azure-Sentinel/main/Parsers/ASimAuthentication/Parsers/ASimAuthenticationOktaSSO.yaml

# Command line options
dotnet run parser.yaml --base-url <url> --sample-data-url <url> --exclusion-list <path> --no-vim --no-sample-data
```

### API Integration

```csharp
// Create API instance
var api = AsimParserValidationApi.CreateInstance();

// Validate single parser
var result = await api.ValidateSingleParserAsync("Parsers/ASimAuthentication/Parsers/ASimAuthenticationOktaSSO.yaml");

// Validate multiple parsers
var parserPaths = new List<string> { "parser1.yaml", "parser2.yaml" };
var result = await api.ValidateMultipleParsersAsync(parserPaths, "https://raw.githubusercontent.com/Azure/Azure-Sentinel/main");

// Using ValidationInput for more control
var input = new ValidationInput
{
    ParserPaths = parserPaths,
    BaseUrl = "https://raw.githubusercontent.com/Azure/Azure-Sentinel/main",
    IncludeVimParsers = true,
    ValidateSampleData = true
};
var result = await api.ValidateParsersAsync(input);
```

### Dependency Injection Setup

```csharp
// In your Startup.cs or Program.cs
services.AddSingleton<ValidationConfiguration>();
services.AddHttpClient<IHttpYamlService, HttpYamlService>();
services.AddSingleton<IFileService, FileService>();
services.AddSingleton<IParserValidationService, ParserValidationService>();
services.AddSingleton<IParserValidationOrchestrator, ParserValidationOrchestrator>();
services.AddSingleton<AsimParserValidationApi>();
```

## Configuration

Configuration can be managed through `appsettings.json`:

```json
{
  "ValidationConfiguration": {
    "FailOnParserNotFound": true,
    "IncludeVimParserTesting": true,
    "MaxConcurrentRequests": 10,
    "HttpTimeoutSeconds": 30,
    "UseExclusionList": true,
    "ValidateSampleDataFiles": true
  }
}
```

## Input Methods

### 1. Direct File Paths
```csharp
var input = ValidationInput.FromSingleParser("Parsers/ASimAuthentication/Parsers/ASimAuthenticationOktaSSO.yaml");
```

### 2. Full URLs
```csharp
var input = ValidationInput.FromSingleParser("https://raw.githubusercontent.com/Azure/Azure-Sentinel/main/Parsers/ASimAuthentication/Parsers/ASimAuthenticationOktaSSO.yaml");
```

### 3. Multiple Files with Base URL
```csharp
var parserPaths = new List<string> 
{
    "Parsers/ASimAuthentication/Parsers/ASimAuthenticationOktaSSO.yaml",
    "Parsers/ASimAuthentication/Parsers/ASimAuthenticationSigninLogs.yaml"
};
var input = ValidationInput.FromMultipleParsers(parserPaths, "https://raw.githubusercontent.com/Azure/Azure-Sentinel/main");
```

## Integration Examples

### WebAPI Controller

```csharp
[ApiController]
[Route("api/[controller]")]
public class ParserValidationController : ControllerBase
{
    private readonly AsimParserValidationApi _validationApi;

    public ParserValidationController(AsimParserValidationApi validationApi)
    {
        _validationApi = validationApi;
    }

    [HttpPost("validate")]
    public async Task<ActionResult<ValidationResult>> ValidateAsync([FromBody] ValidationRequest request)
    {
        var input = request.ToValidationInput();
        var result = await _validationApi.ValidateParsersAsync(input);
        return Ok(result);
    }

    [HttpGet("validate-single")]
    public async Task<ActionResult<ValidationResult>> ValidateSingleAsync(
        [FromQuery] string parserPath, 
        [FromQuery] string? baseUrl = null)
    {
        var result = await _validationApi.ValidateSingleParserAsync(parserPath, baseUrl);
        return Ok(result);
    }
}
```

### Windows Forms Integration

```csharp
public partial class ValidationForm : Form
{
    private readonly AsimParserValidationApi _validationApi;

    public ValidationForm()
    {
        InitializeComponent();
        _validationApi = AsimParserValidationApi.CreateInstance();
    }

    private async void ValidateButton_Click(object sender, EventArgs e)
    {
        var parserPaths = parserPathsListBox.Items.Cast<string>().ToList();
        var input = new ValidationInput
        {
            ParserPaths = parserPaths,
            BaseUrl = baseUrlTextBox.Text,
            IncludeVimParsers = includeVimCheckBox.Checked
        };
        
        var result = await _validationApi.ValidateParsersAsync(input);
        DisplayResults(result);
    }
}
```

## Validation Rules

The system validates the following aspects of ASIM parsers:

1. **Basic Properties**: ParserName, EquivalentBuiltInParser existence
2. **Event Fields**: EventProduct and EventVendor mapping in KQL queries
3. **Union Parser Integration**: Presence in union parser configurations
4. **Metadata**: Title, Version, LastUpdated format validation
5. **Schema Compliance**: ASIM schema name and version validation
6. **References**: Documentation links validation
7. **Naming Conventions**: Parser naming format compliance
8. **Sample Data**: Sample data file existence validation

## Error Handling

- Comprehensive exception handling with structured logging
- Graceful degradation for network failures
- Configurable timeout mechanisms
- Detailed error reporting with context
- User-friendly error messages for UI applications

## Security Considerations

- No hardcoded credentials or sensitive information
- HTTP timeout configuration to prevent hanging requests
- Input validation for file paths and URLs
- Secure HTTP client configuration
- No file system access for Git operations (removed security concern)

## Performance Features

- Asynchronous operations throughout
- Configurable concurrent request limits
- Efficient memory usage for large files
- HTTP connection pooling

## API Endpoints

### POST /api/parservalidation/validate
Validates multiple parser files with full configuration options.

### GET /api/parservalidation/validate-single
Validates a single parser file with minimal parameters.

### GET /api/parservalidation/test-results
Gets detailed test results for a specific parser.

### GET /api/parservalidation/configuration
Gets the current validation configuration.

### GET /api/parservalidation/health
Health check endpoint.

## Dependencies

- .NET 8.0
- Microsoft.Extensions.Hosting
- Microsoft.Extensions.DependencyInjection
- Microsoft.Extensions.Logging
- Microsoft.Extensions.Http
- YamlDotNet
- System.Text.Json

## Building and Running

```bash
# Restore dependencies
dotnet restore

# Build the project
dotnet build

# Run the console application
dotnet run parser1.yaml parser2.yaml

# Run with custom base URL
dotnet run parser.yaml --base-url https://raw.githubusercontent.com/Azure/Azure-Sentinel/main
```

## Key Improvements Over Git-Based Version

1. **Simplified Deployment**: No Git dependencies required
2. **User-Friendly**: Users can specify exact parsers to validate
3. **Flexible Input**: Supports both file paths and direct URLs
4. **Better Integration**: Easier to integrate into existing applications
5. **Reduced Complexity**: Removed Git operations and repository management
6. **Direct Control**: Users have full control over what gets validated
7. **Cloud-Friendly**: Works well in containerized environments without Git setup

This C# implementation provides a robust, user-input-driven solution for ASIM parser validation that can be easily integrated into various .NET applications without the complexity of Git repository management.
