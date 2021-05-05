using System;
using System.Net;
using System.Net.Http;
using System.Threading.Tasks;
using AzureSentinel_ManagementAPI.Infrastructure.Authentication;
using AzureSentinel_ManagementAPI.Infrastructure.Configuration;
using Microsoft.Extensions.Configuration;
using Newtonsoft.Json;
using Newtonsoft.Json.Linq;

namespace AzureSentinel_ManagementAPI.AlertRuleTemplates
{
    public class AlertRuleTemplatesController
    {       
        private readonly AuthenticationService authenticationService;
        private readonly AzureSentinelApiConfiguration[] azureConfigs;
        private bool cliMode;

        public AlertRuleTemplatesController(
            AuthenticationService authenticationService,
            IConfigurationRoot rawConfig,
            AzureSentinelApiConfiguration[] azureConfig)
        {
            this.authenticationService = authenticationService;
            azureConfigs = azureConfig;
            cliMode = rawConfig.GetValue<bool>("Climode");
        }

        /// <summary>
        /// Get alert rule templates for all instances or for a single instance
        /// </summary>
        /// <returns></returns>
        public async Task GetAlertRuleTemplates(int insId = -1)
        {            
            if (insId != -1)
            {
                await GetAlertRuleTemplatesByInstance(insId);
            }
            else
            {
                for (var i = 0; i < azureConfigs.Length; i++)
                {
                    await GetAlertRuleTemplatesByInstance(i);
                }
            }
        }

        /// <summary>
        /// Get alert rule templates for a single instance
        /// </summary>
        /// <param name="i"></param>
        /// <returns></returns>
        private async Task GetAlertRuleTemplatesByInstance(int i)
        {
            try
            {
                var url = $"{azureConfigs[i].BaseUrl}/alertRuleTemplates?api-version={azureConfigs[i].ApiVersion}";
                var request = new HttpRequestMessage(HttpMethod.Get, url);
                await authenticationService.AuthenticateRequest(request, i);
                var http = new HttpClient();
                var response = await http.SendAsync(request);

                if (response.IsSuccessStatusCode)
                {
                    string res = await response.Content.ReadAsStringAsync();
                    Utils.WriteJsonStringToFile($"GetAlertRuleTemplates_{azureConfigs[i].InstanceName}.json", cliMode, res);
                    Console.WriteLine(JToken.Parse(res).ToString(Formatting.Indented));
                    return;
                }

                var error = await response.Content.ReadAsStringAsync();
                var formatted = JsonConvert.DeserializeObject(error);
                throw new WebException("Error calling the API: \n" +
                                       JsonConvert.SerializeObject(formatted, Formatting.Indented));
            }
            catch (Exception ex)
            {
                throw new Exception($"Something went wrong on {azureConfigs[i].InstanceName}: \n"
                    + ex.Message);
            }

        }

        /// <summary>
        /// Get alert rule template by id
        /// </summary>
        /// <param name="ruleTmplId"></param>
        /// <returns></returns>
        public async Task<string> GetAlertRuleTemplateById(string ruleTmplId, int insId)
        {
            try
            {
                var url = $"{azureConfigs[insId].BaseUrl}/alertRuleTemplates/{ruleTmplId}?api-version={azureConfigs[insId].ApiVersion}";
                var request = new HttpRequestMessage(HttpMethod.Get, url);
                await authenticationService.AuthenticateRequest(request, insId);
                var http = new HttpClient();
                var response = await http.SendAsync(request);

                if (response.IsSuccessStatusCode) return await response.Content.ReadAsStringAsync();

                var error = await response.Content.ReadAsStringAsync();
                var formatted = JsonConvert.DeserializeObject(error);
                throw new WebException("Error calling the API: \n" +
                                       JsonConvert.SerializeObject(formatted, Formatting.Indented));
            }
            catch (Exception ex)
            {
                throw new Exception("Something went wrong: \n" + ex.Message);
            }
        }
    }
}