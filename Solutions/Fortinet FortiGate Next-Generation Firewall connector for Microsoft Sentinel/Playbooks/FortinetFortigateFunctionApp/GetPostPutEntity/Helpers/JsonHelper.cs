//-----------------------------------------------------------------------
// <copyright file="JSONHelper.cs" company="Microsoft">
// Copyright (c) Microsoft. All rights reserved.
// </copyright>
//-----------------------------------------------------------------------

namespace Microsoft.Sentinel.Fortinet.Helpers
{
    using Newtonsoft.Json;
    using System.IO;
    using System.Text;
    using System.Runtime.Serialization.Formatters.Binary;
    using System.Runtime.Serialization.Json;
    using System.Threading.Tasks;

    /// <summary>
    /// This class is used for desinerizing JSON
    /// </summary>
    public static class JSONHelper
    {
        /// <summary>
        /// Jsons the deserialize.
        /// </summary>
        /// <typeparam name="TResult">The type of the result.</typeparam>
        /// <param name="json">The json.</param>
        /// <returns></returns>
        public static async Task<TResult> JsonDeserialize<TResult>(string json)
        {

            byte[] jsonBytes = Encoding.UTF8.GetBytes(json);
            using (MemoryStream stream = new MemoryStream(jsonBytes))
            {
                using (StreamReader sr = new StreamReader(stream))
                {
                    using (JsonTextReader reader = new JsonTextReader(sr))
                    {
                        JsonSerializer serializer = new JsonSerializer
                        {
                            MissingMemberHandling = MissingMemberHandling.Ignore,
                            NullValueHandling = NullValueHandling.Ignore
                        };

                        return serializer.Deserialize<TResult>(reader);
                    }
                }
            }
        }


        /// <summary>
        /// Jsonserializes the specified t.
        /// </summary>
        /// <typeparam name="T"></typeparam>
        /// <param name="t">The t.</param>
        /// <returns></returns>
        public static async Task<string> Jsonserialize<T>(T t)
        {

            DataContractJsonSerializer serialize = new DataContractJsonSerializer(typeof(T));
            MemoryStream ms = new MemoryStream();
            serialize.WriteObject(ms, t);
            string jsonString = Encoding.UTF8.GetString(ms.ToArray());
            ms.Close();
            return jsonString;
        }

    }
}
