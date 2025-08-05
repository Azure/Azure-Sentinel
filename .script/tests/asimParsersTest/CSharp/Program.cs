using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Net.Http;
using System.Threading.Tasks;
using Microsoft.Extensions.DependencyInjection;
using Microsoft.Extensions.Hosting;
using Microsoft.Extensions.Logging;
using AsimParserValidation.Configuration;
using AsimParserValidation.Models;
using AsimParserValidation.Services;

namespace AsimParserValidation
{
    /// <summary>
    /// Main entry point for the ASIM Parser Validation application
    /// </summary>
    public class Program
    {
        /// <summary>
        /// Main entry point
        /// </summary>
        /// <param name="args">Command line arguments: parser file paths or URLs</param>
        /// <returns>Exit code (0 for success, 1 for failure)</returns>
        public static async Task<int> Main(string[] args)
        {
            try
            {
                var host = CreateHostBuilder(args).Build();
                
                using var scope = host.Services.CreateScope();
                var orchestrator = scope.ServiceProvider.GetRequiredService<IParserValidationOrchestrator>();
                var outputService = scope.ServiceProvider.GetRequiredService<IOutputService>();
                var logger = scope.ServiceProvider.GetRequiredService<ILogger<Program>>();

                logger.LogInformation("Starting ASIM Parser Validation");

                // Parse command line arguments
                var validationInput = ParseCommandLineArguments(args);
                
                if (!validationInput.ParserPaths.Any())
                {
                    logger.LogWarning("No parser paths provided. Usage: AsimParserValidation <parser-path-1> [parser-path-2] ... [--base-url <url>]");
                    Console.WriteLine("Usage: AsimParserValidation <parser-path-1> [parser-path-2] ... [--base-url <url>]");
                    Console.WriteLine("Example: AsimParserValidation Parsers/ASimAuthentication/Parsers/ASimAuthenticationOktaSSO.yaml");
                    Console.WriteLine("Example: AsimParserValidation https://raw.githubusercontent.com/Azure/Azure-Sentinel/main/Parsers/ASimAuthentication/Parsers/ASimAuthenticationOktaSSO.yaml");
                    return 1;
                }

                var result = await orchestrator.RunValidationAsync(validationInput);

                // Output results
                outputService.PrintValidationSummary(result);

                // Print individual parser results if there are failures or detailed output is requested
                foreach (var parserResult in result.ParserResults)
                {
                    outputService.PrintParserResult(parserResult);
                }

                logger.LogInformation("ASIM Parser Validation completed. Success: {Success}", result.Success);
                
                return result.Success ? 0 : 1;
            }
            catch (Exception ex)
            {
                Console.WriteLine($"Fatal error: {ex.Message}");
                return 1;
            }
        }

        /// <summary>
        /// Parses command line arguments into validation input
        /// </summary>
        /// <param name="args">Command line arguments</param>
        /// <returns>Validation input</returns>
        private static ValidationInput ParseCommandLineArguments(string[] args)
        {
            var input = new ValidationInput();
            
            for (int i = 0; i < args.Length; i++)
            {
                switch (args[i].ToLowerInvariant())
                {
                    case "--base-url":
                        if (i + 1 < args.Length)
                        {
                            input.BaseUrl = args[++i];
                        }
                        break;
                    case "--sample-data-url":
                        if (i + 1 < args.Length)
                        {
                            input.SampleDataBaseUrl = args[++i];
                        }
                        break;
                    case "--exclusion-list":
                        if (i + 1 < args.Length)
                        {
                            input.ExclusionListPath = args[++i];
                        }
                        break;
                    case "--no-vim":
                        input.IncludeVimParsers = false;
                        break;
                    case "--no-sample-data":
                        input.ValidateSampleData = false;
                        break;
                    default:
                        // If it doesn't start with --, treat it as a parser path
                        if (!args[i].StartsWith("--"))
                        {
                            input.ParserPaths.Add(args[i]);
                        }
                        break;
                }
            }

            return input;
        }

        /// <summary>
        /// Creates the host builder with dependency injection configuration
        /// </summary>
        /// <param name="args">Command line arguments</param>
        /// <returns>Configured host builder</returns>
        private static IHostBuilder CreateHostBuilder(string[] args) =>
            Host.CreateDefaultBuilder(args)
                .ConfigureServices((context, services) =>
                {
                    // Configuration
                    services.AddSingleton<ValidationConfiguration>();

                    // HTTP Client
                    services.AddHttpClient<IHttpYamlService, HttpYamlService>(client =>
                    {
                        client.Timeout = TimeSpan.FromSeconds(30);
                        client.DefaultRequestHeaders.Add("User-Agent", "ASIM-Parser-Validator/1.0");
                    });

                    // Services (removed GitService)
                    services.AddSingleton<IFileService, FileService>();
                    services.AddSingleton<IParserValidationService, ParserValidationService>();
                    services.AddSingleton<IParserValidationOrchestrator, ParserValidationOrchestrator>();
                    services.AddSingleton<IOutputService, ConsoleOutputService>();

                    // Logging
                    services.AddLogging(builder =>
                    {
                        builder.AddConsole();
                        builder.SetMinimumLevel(LogLevel.Information);
                    });
                });
    }
}
