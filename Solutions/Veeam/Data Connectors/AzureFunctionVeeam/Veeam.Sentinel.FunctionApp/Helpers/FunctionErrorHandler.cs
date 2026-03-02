using System.Net;
using Microsoft.AspNetCore.Http;
using Microsoft.AspNetCore.Mvc;
using Microsoft.Extensions.Logging;
using Veeam.AC.VBR.ApiClient.Api.v1_2_rev1.Client;

namespace Sentinel.Helpers
{
    public static class FunctionErrorHandler
    {
        public static async Task<IActionResult> ExecuteAsync<T>(
            ILogger logger,
            string functionName,
            string queryString,
            string vbrHostName,
            Func<Task<T>> action,
            Func<T, Task<IActionResult>> onSuccess)
        {
            logger.LogInformation($"Calling {functionName} Azure Function was triggered with query parameters {queryString}");

            try
            {
                var result = await action();
                return await onSuccess(result);
            }
            catch (ApiException ex)
            {
                if (ex.ErrorCode == (int)HttpStatusCode.Unauthorized)
                    return new BadRequestObjectResult($"Invalid username or password for {vbrHostName}, check settings.");

                logger.LogError(ex, $"Error {ex.ErrorCode} in {functionName} for \"{vbrHostName}\". Details: {ex.Message} - {ex.ErrorContent} - {ex.StackTrace} ");

                return new ObjectResult("An unexpected error occurred. See server logs for details.") { StatusCode = StatusCodes.Status500InternalServerError };
            }
            catch (UnauthorizedAccessException ex)
            {
                logger.LogError(ex, $"Unauthorized access in {functionName} for \"{vbrHostName}\". Details: {ex.Message}");
                return new BadRequestObjectResult($"Invalid username or password for {vbrHostName}, check settings.");
            }
            catch (Exception ex)
            {
                logger.LogError(ex, $"Unexpected error in {functionName} for \"{vbrHostName}\". Details: {ex.Message}");

                return new ObjectResult($"An unexpected error occurred. See server logs for details. ERROR MESSAGE: {ex.Message}") { StatusCode = StatusCodes.Status500InternalServerError };
            }
        }
    }
}

