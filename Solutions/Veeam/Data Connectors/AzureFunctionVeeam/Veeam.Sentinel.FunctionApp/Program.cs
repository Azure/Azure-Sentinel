using Microsoft.Azure.Functions.Worker;
using Microsoft.Extensions.DependencyInjection;
using Microsoft.Extensions.Hosting;
using Sentinel.Client;
using Sentinel.Managers;

var host = new HostBuilder()
    .ConfigureFunctionsWebApplication()
    .ConfigureServices(services =>
    {
        services.AddApplicationInsightsTelemetryWorkerService();
        services.ConfigureFunctionsApplicationInsights();
        services.AddSingleton<IVbrConnectionsManager, VbrConnectionsManagerImpl>();
        services.AddSingleton<ISecretsManager, SecretsManagerImpl>();
        services.AddSingleton<ILogAnalyticsManager, LogAnalyticsManagerImpl>();
        services.AddSingleton<IVoneConnectionsManager, VoneConnectionsManagerImpl>();
        services.AddSingleton<ICovewareConnectionsManager, CovewareConnectionsManagerImpl>();
    })
    .Build();

host.Run();