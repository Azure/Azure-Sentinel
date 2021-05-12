using Nancy.Json;
using Newtonsoft.Json;
using Newtonsoft.Json.Linq;
using System;
using System.Collections;
using System.Collections.Generic;
using System.Dynamic;
using System.IO;
using System.Net.Http;
using System.Net.Http.Headers;
using System.Security.Cryptography;
using System.Text;
using System.Threading.Tasks;

namespace SampleDataIngestTool
{
    public static class ApiExample
    {
        static string customerId = "";
        static string sharedKey = "";
        static string logName = "";
        // You can use an optional field to specify the timestamp from the data. If the time field is not specified, Azure Monitor assumes the time is the message ingestion time
        static string timeStampField = "";
        static void Main()
        {
            // Get a list of Custom Log file names with their paths
            var files = GetFiles();

            if (files.Length > 0)
            {
                // Get credentials
                var appConfig = new AppConfig();
                var creds = appConfig.GetCredentials();
                customerId = creds["workspaceId"];
                sharedKey = creds["sharedKey"];

                var laCheck = new LogAnalyticsCheck();
                var path = new SampleDataPath();
                var dirPath = path.GetDirPath();

                // Loop through files 
                foreach (var file in files)
                {
                    var fileName = file.Replace(dirPath, "");

                    // Check if the file has been pushed to the Log Analytics
                    bool result = laCheck.RunLAQuery(file);
                    if (result == true)
                    {
                        // Prompt user to choose to repush data
                        Console.WriteLine("{0} has been posted. Would you like to post it again?", fileName);
                        var res = Console.ReadLine();
                        if (res.ToLower() == "y" || res.ToLower() == "yes")
                        {
                            PushDataToLog(file);
                        }
                        else
                        {
                            Console.WriteLine("Check Log Analytics for existing data");
                        }
                    }
                    else
                    {
                        PushDataToLog(file);
                    }
                }
            }
            else
            {
                Console.WriteLine("No Custom files in Sample Data");
            }
        }

        //Get Custom Log files from Sample Data
        private static string[] GetFiles()
        {
            try
            {
                var path = new SampleDataPath();
                var filePath = path.GetDirPath();
                string[] files = System.IO.Directory.GetFiles(filePath, "*.json*", SearchOption.AllDirectories);

                return files;
            }
            catch (Exception excep)
            {
                Console.WriteLine("Get Files Error: " + excep.Message);
                throw new Exception("Get Files Error: " + excep.Message);
            }
        }

        //Build the API signature
        public static string BuildSignature(string message, string secret)
        {
            try
            {
                var encoding = new System.Text.ASCIIEncoding();
                byte[] keyByte = Convert.FromBase64String(secret);
                byte[] messageBytes = encoding.GetBytes(message);
                using (var hmacsha256 = new HMACSHA256(keyByte))
                {
                    byte[] hash = hmacsha256.ComputeHash(messageBytes);
                    return Convert.ToBase64String(hash);
                }
            }
            catch (Exception excep)
            {
                Console.WriteLine("Authenticaton Error: " + excep.Message);
                return "Authentication Error" + excep.Message;
            }

        }

        //Read each file in Sample Data repo
        public static string ReadFile(string filePath)
        {
            try
            {
                using (StreamReader streamReader = new StreamReader(filePath))
                {
                    var json = streamReader.ReadToEnd();

                    return json;
                }
            }
            catch (Exception excep)
            {
                Console.WriteLine("Read File exception: " + excep.Message);
                return "Read File error";
            }

        }

        //Send posted data to Log Analytics custom logs
        private static void PushDataToLog(string filePath)
        {
            try
            {
                //Create a hash for the API signature
                var datestring = DateTime.UtcNow.ToString("r");
                string json = ReadFile(filePath);

                //Updated Code to remove _s,_t,_d,_s if already there in sample data before ingest to LA.
                var strippedData = JsonConvert.DeserializeObject(JsonConvert.SerializeObject(StripSuffix(json, filePath)));
                string updatedjson = JsonConvert.SerializeObject(strippedData);
                var jsonBytes = Encoding.UTF8.GetBytes(updatedjson);

                ////var jsonBytes = Encoding.UTF8.GetBytes(json);
                string stringToHash = "POST\n" + jsonBytes.Length + "\napplication/json\n" + "x-ms-date:" + datestring + "\n/api/logs";
                string hashedString = BuildSignature(stringToHash, sharedKey);
                string signature = "SharedKey " + customerId + ":" + hashedString;
                PostData(signature, datestring, updatedjson, filePath);
            }
            catch (Exception excep)
            {
                Console.WriteLine("Error to push data: " + excep.Message);
            }
        }

        //Send a request to the POST API endpoint for Custom Log
        public static void PostData(string signature, string date, string json, string filePath)
        {
            try
            {
                string url = "https://" + customerId + ".ods.opinsights.azure.com/api/logs?api-version=2016-04-01";

                HttpClient client = new HttpClient();
                client.DefaultRequestHeaders.Add("Accept", "application/json");

                var path = new SampleDataPath();
                var dirPath = path.GetDirPath();

                logName = filePath.Replace(dirPath, "").Replace("_CL.json", "").Replace(".json", "");
                client.DefaultRequestHeaders.Add("Log-Type", logName);
                client.DefaultRequestHeaders.Add("Authorization", signature);
                client.DefaultRequestHeaders.Add("x-ms-date", date);
                client.DefaultRequestHeaders.Add("time-generated-field", timeStampField);

                HttpContent httpContent = new StringContent(json, Encoding.UTF8);
                httpContent.Headers.ContentType = new MediaTypeHeaderValue("application/json");
                Task<HttpResponseMessage> response = client.PostAsync(new Uri(url), httpContent);
                HttpContent responseContent = response.Result.Content;
                string result = responseContent.ReadAsStringAsync().Result;

                var fileName = logName + "_CL.json";

                if (response.Result.StatusCode.ToString().Contains("OK"))
                {
                    Console.WriteLine("{0} is successfully pushed", fileName);
                }
                else
                {
                    Console.WriteLine("Failed to push {0}", fileName);
                }
            }
            catch (Exception excep)
            {
                Console.WriteLine("API Post Exception: " + excep.Message);
            }
        }

        // Stripsuffix _s,_t,_d,_g,_b if any for key
        //private static List<JObject> StripSuffix(string json)
        //{
        //    JToken a = JToken.Parse(json);
        //    //var a = new JArray();
        //    //if (json.StartsWith("["))
        //    //    a = JArray.Parse(json);
        //    //else
        //    //    a = a.Add(JObject.Parse(json));
        //   // var a = JObject.Parse(json);

        //    var obj = new List<JObject>();
        //    foreach (JObject o in a)
        //    {
        //        JObject addob = new JObject();
        //        foreach (JProperty p in o.Properties())
        //        {

        //            try
        //            {

        //                string name = p.Name;
        //                if (name.EndsWith("_s") || name.EndsWith("_t") || name.EndsWith("_d") || name.EndsWith("_g") || name.EndsWith("_b"))
        //                {
        //                    name = name.Substring(0, name.Length - 2);
        //                }
        //                if ((p.Value.Type.ToString() == "Object") && p.Value.HasValues)
        //                {
        //                    StripSuffix(Convert.ToString(p.Value));
        //                }

        //                if (p.Value.Type.Equals("Array") && p.Value.HasValues)
        //                {
        //                    foreach (var val in p.Value)
        //                    {
        //                        StripSuffix(Convert.ToString(val));
        //                    }
        //                }
        //                addob.Add(new JProperty(name, p.Value));

        //            }

        //            catch (Exception ex)
        //            {
        //                Console.WriteLine("Issue while stripping data: ", ex);
        //            }
        //        }

        //        obj.Add(addob);
        //    }
        //    return obj;
        //}

        private static List<JObject> StripSuffix(string json, string filePath)
        {
            var obj = new List<JObject>();
            var deserializedJson = JsonConvert.DeserializeObject<dynamic>(json) as dynamic;
            foreach (var value in deserializedJson)
            {
                var data = recursiveJson(value, new JObject(), filePath);

                obj.Add(data);
            }
            
            return obj;

        }

        public static JObject recursiveJson(JObject j, JObject pa, string filePath)
        {
            JObject addob = new JObject();
            foreach (var p in j.Properties())
            {
                try
                {
                    string oldName = p.Name;
                    string name = p.Name;
                    var val = p.Value;

                    if (name.EndsWith("_s") || name.EndsWith("_t") || name.EndsWith("_d") || name.EndsWith("_g") || name.EndsWith("_b"))
                    {
                        name = name.Substring(0, name.Length - 2);
                        addob.Add(name, val);
                        //j.Replace(name);

                    }
                    else if (val.Type.ToString().Equals("Object"))
                    {
                        var v = recursiveJson((JObject)val, addob, filePath);
                        // j[name] = recursiveJson((JObject)val, pa);
                        addob.Add(name, v);
                    }

                    else if (val.Type.ToString().Equals("Array"))
                    {
                        var arrayobj = new JArray();
                        int count = 0;
                        foreach (var v in val)
                        {
                            if (v.Type.ToString().Equals("String"))
                            {
                                arrayobj.Add(v);
                            }
                            else
                            {
                                var index = count;
                                arrayobj.Add(recursiveJson((JObject)val[index], addob, filePath));
                                //j[name][index] = recursiveJson((JObject)val[index], pa);
                                count++;
                            }

                        }
                        //for (int i=0;i< arrayobj.Count;i++)
                        //{
                        addob.Add(name, arrayobj);
                        //j.Property(oldName).Remove();
                        //}

                        // j[name] = (dynamic)arrayobj;
                    }
                    else
                    {
                        addob.Add(name, val);
                    }

                }

                catch (Exception ex)
                {
                    Console.WriteLine("Issue while stripping data in file: " + filePath + ex.Message);
                }
            }
            return addob;
        }
        
    }
}


