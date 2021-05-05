using System;
using System.Threading.Tasks;
using AzureSentinel_ManagementAPI.Actions;
using AzureSentinel_ManagementAPI.AlertRules;
using AzureSentinel_ManagementAPI.AlertRuleTemplates;
using AzureSentinel_ManagementAPI.Bookmarks;
using AzureSentinel_ManagementAPI.DataConnectors;
using AzureSentinel_ManagementAPI.Incidents;
using AzureSentinel_ManagementAPI.IncidentRelation;
using AzureSentinel_ManagementAPI.Infrastructure.Authentication;
using AzureSentinel_ManagementAPI.Infrastructure.Configuration;
using Microsoft.Extensions.Configuration;
using Microsoft.Extensions.DependencyInjection;
using AzureSentinel_ManagementAPI.Hunting;

namespace AzureSentinel_ManagementAPI
{
    class Program
    {
        public static async Task Main(string[] args)
        {
            var rawConfig = new ConfigurationBuilder().AddJsonFile("appsettings.json").Build();
            var configurations = rawConfig.GetSection("Instances").Get<AzureSentinelApiConfiguration[]>();

            var serviceProvider = new ServiceCollection()
                .AddSingleton<AppHost>()
                .AddSingleton<IConfigurationRoot>(rawConfig)
                .AddSingleton<AzureSentinelApiConfiguration[]>(configurations)
                .AddTransient<AlertRulesController>()
                .AddTransient<AuthenticationService>()
                .AddTransient<AlertRuleTemplatesController>()
                .AddTransient<IncidentsController>()
                .AddTransient<ActionsController>()
                .AddTransient<BookmarksController>()
                .AddTransient<DataConnectorsController>()
                .AddTransient<IncidentRelationController>()
                .AddTransient<SavedSearchController>()
                .BuildServiceProvider();

            await serviceProvider.GetService<AppHost>().Run(args);
        }
    }

}