using System;
using System.Net.Http;
using System.Net.Http.Headers;
using System.Security.Cryptography;
using System.Text;
using System.Threading.Tasks;

namespace HttpDataCollectorAPI
{
	class ApiExample
	{
		// An example JSON object, with key/value pairs. You can comment this out and create your own json file with custom log data in the solution
		static string json = @"[{""DemoField1"":""DemoValue1"",""DemoField2"":""DemoValue2""},{""DemoField3"":""DemoValue3"",""DemoField4"":""DemoValue4""}]";

		// Update customerId to your Log Analytics workspace ID
		static string customerId = "enter_your_workspaceId";

		// For sharedKey, use either the primary or the secondary Connected Sources client authentication key   
		static string sharedKey = "enter_your_workspace_key";

		// LogName is name of the event type that is being submitted to Azure Monitor
		static string LogName = "enter_your_log_name";

		// You can use an optional field to specify the timestamp from the data. If the time field is not specified, Azure Monitor assumes the time is the message ingestion time
		static string TimeStampField = "";

		static void Main()
		{
			// Create a hash for the API signature
			var datestring = DateTime.UtcNow.ToString("r");
			var jsonBytes = Encoding.UTF8.GetBytes(json);
			string stringToHash = "POST\n" + jsonBytes.Length + "\napplication/json\n" + "x-ms-date:" + datestring + "\n/api/logs";
			string hashedString = BuildSignature(stringToHash, sharedKey);
			string signature = "SharedKey " + customerId + ":" + hashedString;

			PostData(signature, datestring, json);
		}

		// Build the API signature
		public static string BuildSignature(string message, string secret)
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

		// Send a request to the POST API endpoint
		public static void PostData(string signature, string date, string json)
		{
			try
			{
				string url = "https://" + customerId + ".ods.opinsights.azure.com/api/logs?api-version=2016-04-01";

				System.Net.Http.HttpClient client = new System.Net.Http.HttpClient();
				client.DefaultRequestHeaders.Add("Accept", "application/json");
				client.DefaultRequestHeaders.Add("Log-Type", LogName);
				client.DefaultRequestHeaders.Add("Authorization", signature);
				client.DefaultRequestHeaders.Add("x-ms-date", date);
				client.DefaultRequestHeaders.Add("time-generated-field", TimeStampField);

				System.Net.Http.HttpContent httpContent = new StringContent(json, Encoding.UTF8);
				httpContent.Headers.ContentType = new MediaTypeHeaderValue("application/json");
				Task<System.Net.Http.HttpResponseMessage> response = client.PostAsync(new Uri(url), httpContent);

				System.Net.Http.HttpContent responseContent = response.Result.Content;
				string result = responseContent.ReadAsStringAsync().Result;

				if (response.Result.StatusCode.ToString().Contains("OK"))
				{
					Console.WriteLine("Data is successfully pushed");
				}
				else
				{
					Console.WriteLine("Failed to post data");
				}
			}
			catch (Exception excep)
			{
				Console.WriteLine("API Post Exception: " + excep.Message);
			}
		}
	}
}