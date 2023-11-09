using Azure;
using Azure.AI.OpenAI;
using System.Threading.Tasks;
using System;
using System.Text;

namespace Kqlvalidations.Tests
{
    public class OpenAIServiceClient
    {
        private readonly OpenAIClient _client;

        public OpenAIServiceClient(string baseUrl, string apiKey)
        {
            _client = new OpenAIClient(new Uri(baseUrl), new AzureKeyCredential(apiKey));
        }

        public async Task<string> GetChatCompletionsAsync(string query)
        {
            Response<ChatCompletions> responseWithoutStream = await _client.GetChatCompletionsAsync(
    "ContentValidator",
    new ChatCompletionsOptions()
    {
        Messages =
        {
            new ChatMessage(ChatRole.System, @"You will be provided with KQL query, and you have to provide best practices/improvements that can be done on the given query. Number of suggestions provided can be from 0 to 5."),
        },
        Temperature = (float)0.7,
        MaxTokens = 800,
        NucleusSamplingFactor = (float)0.95,
        FrequencyPenalty = 0,
        PresencePenalty = 0,
        //ChoicesPerPrompt = 1,
        User= query
    });
            StringBuilder stbSuggestions = new StringBuilder();

            ChatCompletions completions = responseWithoutStream.Value;

            foreach (ChatChoice chatChoice in completions.Choices)
            {
                stbSuggestions.Append(chatChoice.Message.Content);
            }

            return stbSuggestions.ToString();
        }
    }
}
