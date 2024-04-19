//-----------------------------------------------------------------------
// <copyright file="postEntity.cs" company="Microsoft">
// Copyright (c) Microsoft. All rights reserved.
// </copyright>
//-----------------------------------------------------------------------

namespace Microsoft.Sentinel.Fortinet.PostEntity
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
 /// <summary>
    /// This class is used for post service
    /// </summary>
    public static class postEntity
    {
      /// <summary>
      /// This is used for post entity
      /// </summary>
      /// <param name="req"></param>
      /// <param name="log"></param>
      /// <returns></returns>
        [FunctionName("postEntity")]
        public static async Task<IActionResult> Run(
            [HttpTrigger(AuthorizationLevel.Function,"post", Route = null)] HttpRequest req,
            ILogger log)
        {
            log.LogInformation("Started the request.");
            var entity = req.Query["entity"];
            var filter = req.Query["filter"];
            var content = await new StreamReader(req.Body).ReadToEndAsync().ConfigureAwait(false);
            dynamic results=null;
            var key = Environment.GetEnvironmentVariable("Authorization", EnvironmentVariableTarget.Process);
            var endpointURL = Environment.GetEnvironmentVariable("EndpointURL", EnvironmentVariableTarget.Process);
            var baseURL = Environment.GetEnvironmentVariable("POSTBaseURL", EnvironmentVariableTarget.Process);  
            if(key!=null && endpointURL !=null && baseURL !=null)
            { 
              try
              {
               results= await Service.Service.HTTPPostService(endpointURL+baseURL,content,key,log).ConfigureAwait(false);
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
