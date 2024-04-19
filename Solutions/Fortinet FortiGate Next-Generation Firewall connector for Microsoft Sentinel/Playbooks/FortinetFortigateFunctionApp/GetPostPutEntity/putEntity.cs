
//-----------------------------------------------------------------------
// <copyright file="putEntity.cs" company="Microsoft">
// Copyright (c) Microsoft. All rights reserved.
// </copyright>
//-----------------------------------------------------------------------

namespace postEntity
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
    /// This class is used for put service
    /// </summary>
    public static class putEntity
    {   
      /// <summary>
      /// This used for put service
      /// </summary>
      /// <param name="req"></param>
      /// <param name="log"></param>
      /// <returns></returns>
        [FunctionName("putEntity")]
        public static async Task<IActionResult> Run(
            [HttpTrigger(AuthorizationLevel.Function, "put", Route = null)] HttpRequest req,
            ILogger log)
        {
            log.LogInformation("Started the request.");
            var content = await new StreamReader(req.Body).ReadToEndAsync();
            dynamic results=null;
            var key = Environment.GetEnvironmentVariable("Authorization", EnvironmentVariableTarget.Process);
            var endpointURL = Environment.GetEnvironmentVariable("EndpointURL", EnvironmentVariableTarget.Process);
            var baseURL = Environment.GetEnvironmentVariable("PUTBaseURL", EnvironmentVariableTarget.Process);  
            if(key!=null && endpointURL !=null && baseURL !=null)
            { 
              try
              {
               results= await Service.HTTPPutService(endpointURL+baseURL,content,key);
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
