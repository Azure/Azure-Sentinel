//-----------------------------------------------------------------------
// <copyright file="getEntity.cs" company="Microsoft">
// Copyright (c) Microsoft. All rights reserved.
// </copyright>
//-----------------------------------------------------------------------
namespace Microsoft.Sentinel.Fortinet.GetEntity
{
using System;
using System.IO;
using System.Threading.Tasks;
using Microsoft.AspNetCore.Mvc;
using Microsoft.Azure.WebJobs;
using Microsoft.Azure.WebJobs.Extensions.Http;
using Microsoft.AspNetCore.Http;
using Microsoft.Extensions.Logging;
using Newtonsoft.Json;
using Microsoft.Sentinel.Fortinet.Service;

 /// <summary>
    /// This class is used for get service
    /// </summary>
    public static class getEntity
    {
        /// <summary>
        /// This is used for get entity
        /// </summary>
        /// <param name="req"></param>
        /// <param name="log"></param>
        /// <returns></returns>
        [FunctionName("getEntity")]
        public static async Task<IActionResult> Run(
            [HttpTrigger(AuthorizationLevel.Function, "get", Route = null)] HttpRequest req,
            ILogger log)
        {
            log.LogInformation("C# HTTP trigger function processed a request.");
            var entity = req.Query["entity"];
            var filter = req.Query["filter"];
            dynamic results=null;
            var key = Environment.GetEnvironmentVariable("Authorization", EnvironmentVariableTarget.Process);
            var endpointURL = Environment.GetEnvironmentVariable("EndpointURL", EnvironmentVariableTarget.Process);
            var baseURL = Environment.GetEnvironmentVariable("GetBaseURL", EnvironmentVariableTarget.Process);  
            if(key!=null && endpointURL !=null && baseURL !=null)
            { 
              try
              {
                results= await Service.Service.HTTPGetService(endpointURL,baseURL,key,entity,filter);
               
              }
              catch(Exception ex)
              {
                log.LogError(ex.StackTrace);
              }
            }
            log.LogInformation("Processed the request.");
            return new OkObjectResult(results);
        }
    }
}
