using Azure.Data.Tables;
using BeyondTrustPMCloud.Models;
using BeyondTrustPMCloud.Services;
using Microsoft.Azure.Functions.Worker;
using Microsoft.Extensions.Configuration;
using Microsoft.Extensions.DependencyInjection;
using Microsoft.Extensions.Hosting;
using Microsoft.Extensions.Logging;

var host = new HostBuilder()
    .ConfigureAppConfiguration((context, config) =>
    {
        // Build temporary configuration to read polling intervals
        var tempConfig = config.Build();
        
        // Try reading with both naming conventions (colon and double underscore)
        // This handles both Y1/EP plans (colon) and FC1 plans (double underscore)
        var activityInterval = 15;
        var clientInterval = 5;
        
        // Try reading Activity Audits interval
        if (int.TryParse(tempConfig["BeyondTrust:ActivityAuditsPollingIntervalMinutes"], out var parsedActivity))
            activityInterval = parsedActivity;
        else if (int.TryParse(tempConfig["BeyondTrust__ActivityAuditsPollingIntervalMinutes"], out parsedActivity))
            activityInterval = parsedActivity;
            
        // Try reading Client Events interval
        if (int.TryParse(tempConfig["BeyondTrust:ClientEventsPollingIntervalMinutes"], out var parsedClient))
            clientInterval = parsedClient;
        else if (int.TryParse(tempConfig["BeyondTrust__ClientEventsPollingIntervalMinutes"], out parsedClient))
            clientInterval = parsedClient;
        
        // Generate CRON expressions from polling intervals
        // Format: "0 */N * * * *" means "every N minutes"
        var activityCron = $"0 */{activityInterval} * * * *";
        var clientCron = $"0 */{clientInterval} * * * *";
        
        // Check if cron expressions already exist in config (set by ARM template)
        var existingActivityCron = tempConfig["ActivityAuditsCron"];
        var existingClientCron = tempConfig["ClientEventsCron"];
        
        // Use existing cron if available, otherwise use generated
        activityCron = existingActivityCron ?? activityCron;
        clientCron = existingClientCron ?? clientCron;
        
        // Set environment variables BEFORE function initialization
        // This ensures timer triggers can resolve %ActivityAuditsCron% at startup
        Environment.SetEnvironmentVariable("ActivityAuditsCron", activityCron);
        Environment.SetEnvironmentVariable("ClientEventsCron", clientCron);
    })
    .ConfigureLogging(logging =>
    {
        // Read log level from environment variable (Logging__LogLevel__Default or Logging:LogLevel:Default)
        var logLevelString = Environment.GetEnvironmentVariable("Logging__LogLevel__Default") 
                          ?? Environment.GetEnvironmentVariable("Logging:LogLevel:Default") 
                          ?? "Information";
        
        if (Enum.TryParse<LogLevel>(logLevelString, true, out var logLevel))
        {
            logging.SetMinimumLevel(logLevel);
        }
        else
        {
            logging.SetMinimumLevel(LogLevel.Information);
        }
        
        logging.AddConsole();
        logging.AddDebug();
    })
    .ConfigureFunctionsWorkerDefaults()
    .ConfigureServices((context, services) =>
    {
        // Register configuration
        var beyondTrustConfig = new BeyondTrustConfiguration();
        context.Configuration.GetSection("BeyondTrust").Bind(beyondTrustConfig);
        
        // Override with environment variables if present
        beyondTrustConfig.PMCloudBaseUrl = context.Configuration["BeyondTrust:PMCloudBaseUrl"] ?? beyondTrustConfig.PMCloudBaseUrl;
        beyondTrustConfig.ClientId = context.Configuration["BeyondTrust:ClientId"] ?? beyondTrustConfig.ClientId;
        beyondTrustConfig.ClientSecret = context.Configuration["BeyondTrust:ClientSecret"] ?? beyondTrustConfig.ClientSecret;
        
        if (int.TryParse(context.Configuration["BeyondTrust:ActivityAuditsPollingIntervalMinutes"], out var activityInterval))
            beyondTrustConfig.ActivityAuditsPollingIntervalMinutes = activityInterval;
            
        if (int.TryParse(context.Configuration["BeyondTrust:ClientEventsPollingIntervalMinutes"], out var clientInterval))
            beyondTrustConfig.ClientEventsPollingIntervalMinutes = clientInterval;

        // Read the CRON expressions from environment (already set in ConfigureAppConfiguration)
        beyondTrustConfig.ActivityAuditsCron = Environment.GetEnvironmentVariable("ActivityAuditsCron") ?? $"0 */{beyondTrustConfig.ActivityAuditsPollingIntervalMinutes} * * * *";
        beyondTrustConfig.ClientEventsCron = Environment.GetEnvironmentVariable("ClientEventsCron") ?? $"0 */{beyondTrustConfig.ClientEventsPollingIntervalMinutes} * * * *";

        services.AddSingleton(beyondTrustConfig);

        var logAnalyticsConfig = new LogAnalyticsConfiguration
        {
            DataCollectionEndpoint = context.Configuration["DataCollectionEndpoint"] ?? throw new InvalidOperationException("DataCollectionEndpoint is required"),
            ActivityAuditsDcrImmutableId = context.Configuration["ActivityAuditsDcrImmutableId"] ?? throw new InvalidOperationException("ActivityAuditsDcrImmutableId is required"),
            ClientEventsDcrImmutableId = context.Configuration["ClientEventsDcrImmutableId"] ?? throw new InvalidOperationException("ClientEventsDcrImmutableId is required"),
            ActivityAuditsStreamName = context.Configuration["ActivityAuditsStreamName"] ?? "Custom-BeyondTrustPM_ActivityAudits",
            ClientEventsStreamName = context.Configuration["ClientEventsStreamName"] ?? "Custom-BeyondTrustPM_ClientEvents"
        };
        services.AddSingleton(logAnalyticsConfig);

        // Register HTTP clients (for BeyondTrust API communication)
        services.AddHttpClient<IBeyondTrustAuthService, BeyondTrustAuthService>();
        services.AddHttpClient<IBeyondTrustApiService, BeyondTrustApiService>();
        
        // Register Log Analytics service (uses Managed Identity - no HttpClient needed)
        services.AddSingleton<ILogAnalyticsService, LogAnalyticsService>();

        // Register Table Storage
        var storageConnectionString = context.Configuration.GetConnectionString("AzureWebJobsStorage") ?? 
                                    context.Configuration["AzureWebJobsStorage"];
        if (!string.IsNullOrEmpty(storageConnectionString))
        {
            services.AddSingleton(new TableServiceClient(storageConnectionString));
        }
        else
        {
            throw new InvalidOperationException("AzureWebJobsStorage connection string is required");
        }

        // Register services        
        services.AddScoped<IBeyondTrustAuthService, BeyondTrustAuthService>();
        services.AddScoped<IBeyondTrustApiService, BeyondTrustApiService>();
        services.AddScoped<ILogAnalyticsService, LogAnalyticsService>();
        services.AddScoped<IStateService, StateService>();
        services.AddSingleton<IRateLimitService, RateLimitService>();

        // Configure Application Insights
        services.AddApplicationInsightsTelemetryWorkerService();
        services.ConfigureFunctionsApplicationInsights();
        services.Configure<LoggerFilterOptions>(options =>
        {
            // The Application Insights SDK adds a default logging filter that instructs ILogger to capture only Warning and more severe logs. Application Insights requires an explicit override.
            // Log levels can also be configured using appsettings.json. For more information, see https://learn.microsoft.com/en-us/azure/azure-monitor/app/worker-service#ilogger-logs
            LoggerFilterRule? toRemove = options.Rules.FirstOrDefault(rule => rule.ProviderName
                == "Microsoft.Extensions.Logging.ApplicationInsights.ApplicationInsightsLoggerProvider");
            if (toRemove is not null)
            {
                options.Rules.Remove(toRemove);
            }
        });
    })
    .Build();

host.Run();
