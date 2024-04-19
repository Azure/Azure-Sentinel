//-----------------------------------------------------------------------
// <copyright file="Service.cs" company="Microsoft">
// Copyright (c) Microsoft. All rights reserved.
// </copyright>
//-----------------------------------------------------------------------


namespace Microsoft.Sentinel.Fortinet.Service
{
using System;
using System.Linq;
using System.Net;
using System.Net.Http;
using System.Net.Http.Json;
using System.Net.Security;
using System.Reflection.Emit;
using System.Security.Cryptography.X509Certificates;
using System.Text;
using System.Threading.Tasks;
using Microsoft.AspNetCore.Http.Features.Authentication;
using Microsoft.AspNetCore.Mvc.ApplicationModels;
using Microsoft.Azure.WebJobs;
using Microsoft.Extensions.DependencyInjection;
using Microsoft.Extensions.Logging;
using Microsoft.Sentinel.Fortinet.Helpers;
using Newtonsoft.Json.Linq;

 /// <summary>
    /// This class is used for service the fortunet end pint
    /// </summary>
 public static class Service
{
  /// <summary>
  /// This used for put service
  /// </summary>
  /// <param name="endpointURL"></param>
  /// <param name="json"></param>
  /// <param name="key"></param>
  /// <returns></returns>
   public static async Task <dynamic> HTTPPutService(string endpointURL,string json,string key)
   {
     dynamic obj=null;
     var clientHandler = new HttpClientHandler();
     clientHandler.ServerCertificateCustomValidationCallback = (sender, cert, chain, sslPolicyErrors) => { return true; };
     using (var httpClient = new HttpClient(clientHandler))
     {
            ServicePointManager.SecurityProtocol = SecurityProtocolType.Tls13;
            ServicePointManager.ServerCertificateValidationCallback = delegate { return true; };
            httpClient.DefaultRequestHeaders.Add("Authorization", "Bearer "+ key);
            var content=new StringContent(json, UnicodeEncoding.UTF8, "application/json");
            using(var response =  await httpClient.PutAsync(endpointURL,content).ConfigureAwait(false))
            {
             var responseJson = await response.Content.ReadAsStringAsync();
             if (responseJson != null)
             {
              obj = await JSONHelper.JsonDeserialize<dynamic>(responseJson);
     
             }
             else
             {
               //Response null
             } 
          }
          
     }
     
    return obj;
   }  


/// <summary>
/// This used for get service
/// </summary>
/// <param name="endpointURL"></param>
/// <param name="baseURL"></param>
/// <param name="key"></param>
/// <param name="entity"></param>
/// <param name="filter"></param>
/// <returns></returns>
public static async Task <dynamic> HTTPGetService(string endpointURL,string baseURL,string key,string entity, string filter)
   {
     dynamic obj=null;
     var clientHandler = new HttpClientHandler();
     clientHandler.ServerCertificateCustomValidationCallback = (sender, cert, chain, sslPolicyErrors) => { return true; };
     using (var httpClient = new HttpClient(clientHandler))
     {
            ServicePointManager.SecurityProtocol = SecurityProtocolType.Tls13;
            ServicePointManager.ServerCertificateValidationCallback = delegate { return true; };
            var httpRequest = new HttpRequestMessage(HttpMethod.Get,  new Uri(endpointURL + baseURL + entity + "?" + filter));
            httpRequest.Headers.Add("Authorization", "Bearer "+ key);
            using(var response =  await httpClient.SendAsync(httpRequest).ConfigureAwait(false))
            {
             var responseJson = await response.Content.ReadAsStringAsync();
             if (responseJson != null)
             {
              obj = await JSONHelper.JsonDeserialize<dynamic>(responseJson);
     
             }
             else
             {
               //Response null
             } 
          }
          
     }
     if(obj!=null)
     {
       return obj.results;
     }
    return obj;
   }

   /// <summary>
   /// This used to post service
   /// </summary>
   /// <param name="endpointURL"></param>
   /// <param name="json"></param>
   /// <param name="key"></param>
   /// <param name="logger"></param>
   /// <returns></returns>
   public static async Task <dynamic> HTTPPostService(string endpointURL,string json,string key,ILogger logger)
   {
    
  
    dynamic obj=null;
     logger.LogInformation("INput JSON"+ json);
     if(json!=null)
     {
     var endpoint= await ReturnEndpoint(json).ConfigureAwait(false);
     logger.LogInformation("Endpoint"+endpoint);
     if(endpoint !=null)
     {
     var json2 =await ReturnJsonstring(json).ConfigureAwait(false);
     logger.LogInformation("JSON2"+json2);
     if(json2 !=null)
     {
     
     var clientHandler = new HttpClientHandler();
     clientHandler.ServerCertificateCustomValidationCallback = (sender, cert, chain, sslPolicyErrors) => { return true; };
     using (var httpClient = new HttpClient(clientHandler))
     {
            ServicePointManager.SecurityProtocol = SecurityProtocolType.Tls13;
            ServicePointManager.ServerCertificateValidationCallback = delegate { return true; };
            httpClient.DefaultRequestHeaders.Add("Authorization", "Bearer "+ key);
            var content=new StringContent(json2, UnicodeEncoding.UTF8, "application/json");
            using(var response =  await httpClient.PostAsync(endpointURL+endpoint,content).ConfigureAwait(false))
            {
             var responseJson = await response.Content.ReadAsStringAsync().ConfigureAwait(false);
             if (responseJson != null)
             {
              obj = await JSONHelper.JsonDeserialize<dynamic>(responseJson).ConfigureAwait(false);
     
             }
             else
             {
               //Response null
             } 
          }
     }
          
     }
     }
     }
     
    return obj;
   }
        /// <summary>
        /// This is used to return end point removed attribute from json
        /// </summary>
        /// <param name="json"></param>
        /// <returns></returns>
        public async static Task<string> ReturnJsonstring(string json)
        {
          var jsonpar=await JSONHelper.JsonDeserialize<JObject>(json).ConfigureAwait(false);
              jsonpar.Properties()
             .Where(attr => attr.Name == "endpoint")
             .First()
             .Remove();
            return jsonpar.ToString();
        }
        /// <summary>
        /// This is used to select end point
        /// </summary>
        /// <param name="json"></param>
        /// <returns></returns>
        public async static Task<string> ReturnEndpoint(string json)
        {
           JObject result =await JSONHelper.JsonDeserialize<JObject>(json).ConfigureAwait(false);
          return (string)result.SelectToken("endpoint");

        }
      
   
}


}