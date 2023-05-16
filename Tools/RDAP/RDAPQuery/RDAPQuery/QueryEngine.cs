// ***********************************************************************
// Assembly         : RDAPQuery
// Author           : Matt Egen @FlyingBlueMonkey
// Created          : 04-13-2021
//
// Last Modified By : Matt Egen @FlyingBlueMonkey
// Last Modified On : 05-30-2021

using System;
using System.Collections.Generic;
using System.IO;
using System.Net.Http;
using System.Net.Http.Headers;
using System.Security.Cryptography;
using System.Text;
using System.Text.Json.Serialization;
using System.Threading.Tasks;
using Microsoft.AspNetCore.Http;
using Microsoft.AspNetCore.Mvc;
using Microsoft.Azure.WebJobs;
using Microsoft.Azure.WebJobs.Extensions.Http;
using Microsoft.Azure.WebJobs.Host;
using Microsoft.Extensions.Logging;
using Newtonsoft.Json;

namespace RDAPQuery
{
    /// <summary>
    /// Class QueryEngine.
    /// </summary>
    public static class QueryEngine
    {
        /// <summary>
        /// The bootstrap URL at IANA.  Hardcoded as this value shall never change.
        /// </summary>
        private const string bootstrapURL = "https://data.iana.org/rdap/dns.json";
        /// <summary>
        /// URL Paramaters in case we need them TODO: Eliminate this if unneeded.
        /// </summary>
        private const string urlParameters = "";

        /// <summary>
        /// Runs on the specified timer to launch the query process
        /// </summary>
        /// <param name="myTimer">My timer.</param>
        /// <param name="log">The log.</param>
        [FunctionName("CheckDomains")]
        public static void Run([TimerTrigger("0 */30 * * * *")]TimerInfo myTimer, ILogger log)
        {
            //Log the initiation of the function
            log.LogInformation($"CheckDomains Timer trigger function executed at: {DateTime.Now}");
            //Query LogAnalytics by calling the "GetDomains" function in the LA workspace
            try
            {
                string queryBody = GetEnvironmentVariable("query_string");
                log.LogInformation(string.Format("Calling QueryData with query '{0}'", queryBody));
                Task<QueryResults> task = LogAnalytics.QueryData(queryBody);
                QueryResults results = task.Result;
                //Ok, now that we have our domains, for each domain returned, call the bootstrap service and get the responsible server
                log.LogInformation(string.Format("Retrieved: {0} rows.  Beginning resolution with Bootstrap lookups", results.tables[0].rows.Count));

                foreach (List<string> rowData in results.tables[0].rows)
                {
                    RDAPResponseRoot responseRoot = null;
                    rowData.ForEach(delegate (string value)
                    {
                        string TLD = value.Split(".")[1];
                        string uri = BootStrapTLD(TLD, log);
                        Console.WriteLine(string.Format("Results of BootStrap call: {0} serviced by {1}", value, uri));
                        if (uri != string.Empty)
                        {
                            //Call the responsible RDAP server
                            responseRoot = QueryRDAP(string.Format("{0}domain/{1}", uri, value), log);
                        }
                        else
                        {
                            Console.WriteLine(string.Format("Unable to process URI :'{0}' for value {1}", uri, value));
                        }
                        if (responseRoot != null)
                        {
                            // Store the results in LogAnalytics.
                            // Build the JSON body from the results
                            RDAPUpdate rdapUpdate = new RDAPUpdate();
                            // there are at least three "events" in the RDAP server response.  Only one of them is "interesting" to use here:  registration.
                            foreach (Event rdapEvent in responseRoot.events)
                            {
                                if (rdapEvent.eventAction == "registration")
                                {
                                    // update the update object with our update
                                    rdapUpdate.domainName = value;
                                    rdapUpdate.registrationDate = rdapEvent.eventDate;
                                    // Call the WriteData function to store the data in our LA workspace.
                                    LogAnalytics.WriteData(JsonConvert.SerializeObject(rdapUpdate));
                                }
                            }
                        }
                    });
                }
            }
            catch (Exception ex)
            {
                Console.WriteLine(string.Format("Exception: {0}", ex.Message));
            }


            //Log the completion of the function
            log.LogInformation($"CheckDomains Timer trigger function completed at: {DateTime.Now}");
        }

        /// <summary>
        /// Calls the bootstrap server endpoint to find the discrete target for the requested TLD
        /// </summary>
        /// <param name="requestedTLD">The requested TLD.</param>
        /// <param name="log">The log.</param>
        /// <returns>System.String.</returns>
        public static string BootStrapTLD(string requestedTLD, ILogger log)
        {
            string queryTLD = requestedTLD;
            string responseMessage = string.Empty;
           

            //Log the request
            log.LogInformation(string.Format("BootStrapDNS function processed a request for TLD '{0}'", queryTLD));

            HttpClient client = new HttpClient();
            client.BaseAddress = new Uri(bootstrapURL);
            Root rootNode = null;
            // Add an Accept header for JSON format.
            client.DefaultRequestHeaders.Accept.Add(
            new MediaTypeWithQualityHeaderValue("application/json"));

            // Get the response from IANA
            HttpResponseMessage response = client.GetAsync(urlParameters).Result;  // Blocking call!
            if (response.IsSuccessStatusCode)
            {

                var jsonString = response.Content.ReadAsStringAsync();
                jsonString.Wait();
                rootNode = JsonConvert.DeserializeObject<Root>(jsonString.Result);
                foreach (var Service in rootNode.Services)
                {
                    // Each "Service" has two nodes with multiple elements under each
                    // The first node is the TLDs
                    // The second node is the RDAP server responsible for servicing the TLDs
                    // TODO:  Really need to clean this up.
                    foreach (string TLD in Service[0])
                    {
                        if (TLD == queryTLD)
                        { // return the full server URL( server URI plus the TLD and some formatting)
                            responseMessage = string.Format("{0}",Service[1][0]);
                            break;  //break out of the foreach()
                        }
                    }
                }
            }
            else
            {
                Console.WriteLine("{0} ({1})", (int)response.StatusCode, response.ReasonPhrase);
            }
            // Dispose of the client since all HttpClient calls are complete.
            client.Dispose();
            // return the URI
            return responseMessage;
        }

        /// <summary>
        /// Queries the rdap.
        /// </summary>
        /// <param name="uri">The URI.</param>
        /// <param name="log">The log.</param>
        /// <returns>RDAPResponseRoot.</returns>
        public static RDAPResponseRoot QueryRDAP(string uri, ILogger log)
        {
            string responseMessage = string.Empty;


            //Log the request
            log.LogInformation(string.Format("QueryRDAP function processed a request for URI '{0}'", uri));

            HttpClient client = new HttpClient();
            client.BaseAddress = new Uri(uri);
            RDAPResponseRoot rootNode = null;
            // Add an Accept header for JSON format.
            client.DefaultRequestHeaders.Accept.Add(
            new MediaTypeWithQualityHeaderValue("application/json"));

            // Get the response from IANA
            HttpResponseMessage response = client.GetAsync(urlParameters).Result;  // Blocking call!
            if (response.IsSuccessStatusCode)
            {

                var jsonString = response.Content.ReadAsStringAsync();
                jsonString.Wait();
                rootNode = JsonConvert.DeserializeObject<RDAPResponseRoot>(jsonString.Result);
            }
            else
            {
                Console.WriteLine("{0} ({1})", (int)response.StatusCode, response.ReasonPhrase);
            }
            // Dispose of the client since all HttpClient calls are complete.
            client.Dispose();
            // return the URI
            return rootNode;

        }

        /// <summary>
        /// Gets the environment variable from the Azure Function hosting service.
        /// </summary>
        /// <param name="name">The name.</param>
        /// <returns>System.String.</returns>
        public static string GetEnvironmentVariable(string name)
        {
            return System.Environment.GetEnvironmentVariable(name, EnvironmentVariableTarget.Process);
        }
    }

    // Root myDeserializedClass = JsonSerializer.Deserialize<Root>(myJsonResponse);
    /// <summary>
    /// Deserialization target for json response from calling RDAP bootstrap server
    /// </summary>
    public class Root
    {
        /// <summary>
        /// Gets or sets the description.
        /// </summary>
        /// <value>The description.</value>
        [JsonPropertyName("description")]
        public string Description { get; set; }

        /// <summary>
        /// Gets or sets the publication.
        /// </summary>
        /// <value>The publication.</value>
        [JsonPropertyName("publication")]
        public DateTime Publication { get; set; }

        /// <summary>
        /// Gets or sets the services.
        /// </summary>
        /// <value>The services.</value>
        [JsonPropertyName("services")]
        public List<List<List<string>>> Services { get; set; }

        /// <summary>
        /// Gets or sets the version.
        /// </summary>
        /// <value>The version.</value>
        [JsonPropertyName("version")]
        public string Version { get; set; }
    }
    // Root myDeserializedClass = JsonConvert.DeserializeObject<Root>(myJsonResponse); 
    /// <summary>
    /// Class Link.
    /// </summary>
    public class Link
    {
        /// <summary>
        /// Gets or sets the value.
        /// </summary>
        /// <value>The value.</value>
        public string value { get; set; }
        /// <summary>
        /// Gets or sets the relative.
        /// </summary>
        /// <value>The relative.</value>
        public string rel { get; set; }
        /// <summary>
        /// Gets or sets the href.
        /// </summary>
        /// <value>The href.</value>
        public string href { get; set; }
        /// <summary>
        /// Gets or sets the type.
        /// </summary>
        /// <value>The type.</value>
        public string type { get; set; }
    }

    /// <summary>
    /// Class PublicId.
    /// </summary>
    public class PublicId
    {
        /// <summary>
        /// Gets or sets the type.
        /// </summary>
        /// <value>The type.</value>
        public string type { get; set; }
        /// <summary>
        /// Gets or sets the identifier.
        /// </summary>
        /// <value>The identifier.</value>
        public string identifier { get; set; }
    }

    /// <summary>
    /// Class Entity.
    /// </summary>
    public class Entity
    {
        /// <summary>
        /// Gets or sets the name of the object class.
        /// </summary>
        /// <value>The name of the object class.</value>
        public string objectClassName { get; set; }
        /// <summary>
        /// Gets or sets the roles.
        /// </summary>
        /// <value>The roles.</value>
        public List<string> roles { get; set; }
        /// <summary>
        /// Gets or sets the vcard array.
        /// </summary>
        /// <value>The vcard array.</value>
        public List<object> vcardArray { get; set; }
        /// <summary>
        /// Gets or sets the handle.
        /// </summary>
        /// <value>The handle.</value>
        public string handle { get; set; }
        /// <summary>
        /// Gets or sets the public ids.
        /// </summary>
        /// <value>The public ids.</value>
        public List<PublicId> publicIds { get; set; }
        /// <summary>
        /// Gets or sets the entities.
        /// </summary>
        /// <value>The entities.</value>
        public List<Entity> entities { get; set; }
    }

    /// <summary>
    /// Class Event.
    /// </summary>
    public class Event
    {
        /// <summary>
        /// Gets or sets the event action.
        /// </summary>
        /// <value>The event action.</value>
        public string eventAction { get; set; }
        /// <summary>
        /// Gets or sets the event date.
        /// </summary>
        /// <value>The event date.</value>
        public DateTime eventDate { get; set; }
    }

    /// <summary>
    /// Class SecureDNS.
    /// </summary>
    public class SecureDNS
    {
        /// <summary>
        /// Gets or sets a value indicating whether [delegation signed].
        /// </summary>
        /// <value><c>true</c> if [delegation signed]; otherwise, <c>false</c>.</value>
        public bool delegationSigned { get; set; }
    }

    /// <summary>
    /// Class Nameserver.
    /// </summary>
    public class Nameserver
    {
        /// <summary>
        /// Gets or sets the name of the object class.
        /// </summary>
        /// <value>The name of the object class.</value>
        public string objectClassName { get; set; }
        /// <summary>
        /// Gets or sets the name of the LDH.
        /// </summary>
        /// <value>The name of the LDH.</value>
        public string ldhName { get; set; }
    }

    /// <summary>
    /// Class Notice.
    /// </summary>
    public class Notice
    {
        /// <summary>
        /// Gets or sets the title.
        /// </summary>
        /// <value>The title.</value>
        public string title { get; set; }
        /// <summary>
        /// Gets or sets the description.
        /// </summary>
        /// <value>The description.</value>
        public List<string> description { get; set; }
        /// <summary>
        /// Gets or sets the links.
        /// </summary>
        /// <value>The links.</value>
        public List<Link> links { get; set; }
    }

    /// <summary>
    /// Class RDAPResponseRoot.
    /// </summary>
    /// Encompases the response from the RDAP query server
    public class RDAPResponseRoot
    {
        /// <summary>
        /// Gets or sets the name of the object class.
        /// </summary>
        /// <value>The name of the object class.</value>
        public string objectClassName { get; set; }
        /// <summary>
        /// Gets or sets the handle.
        /// </summary>
        /// <value>The handle.</value>
        public string handle { get; set; }
        /// <summary>
        /// Gets or sets the name of the LDH.
        /// </summary>
        /// <value>The name of the LDH.</value>
        public string ldhName { get; set; }
        /// <summary>
        /// Gets or sets the links.
        /// </summary>
        /// <value>The links.</value>
        public List<Link> links { get; set; }
        /// <summary>
        /// Gets or sets the status.
        /// </summary>
        /// <value>The status.</value>
        public List<string> status { get; set; }
        /// <summary>
        /// Gets or sets the entities.
        /// </summary>
        /// <value>The entities.</value>
        public List<Entity> entities { get; set; }
        /// <summary>
        /// Gets or sets the events.
        /// </summary>
        /// <value>The events.</value>
        public List<Event> events { get; set; }
        /// <summary>
        /// Gets or sets the secure DNS.
        /// </summary>
        /// <value>The secure DNS.</value>
        public SecureDNS secureDNS { get; set; }
        /// <summary>
        /// Gets or sets the nameservers.
        /// </summary>
        /// <value>The nameservers.</value>
        public List<Nameserver> nameservers { get; set; }
        /// <summary>
        /// Gets or sets the rdap conformance.
        /// </summary>
        /// <value>The rdap conformance.</value>
        public List<string> rdapConformance { get; set; }
        /// <summary>
        /// Gets or sets the notices.
        /// </summary>
        /// <value>The notices.</value>
        public List<Notice> notices { get; set; }
    }

    /// <summary>
    /// Class RDAPUpdate.
    /// </summary>
    public class RDAPUpdate
    {
        /// <summary>
        /// Gets or sets the name of the domain.
        /// </summary>
        /// <value>The name of the domain.</value>
        public string domainName { get; set; }
        /// <summary>
        /// Gets or sets the registration date.
        /// </summary>
        /// <value>The registration date.</value>
        public DateTime registrationDate { get; set; }
    }
}

