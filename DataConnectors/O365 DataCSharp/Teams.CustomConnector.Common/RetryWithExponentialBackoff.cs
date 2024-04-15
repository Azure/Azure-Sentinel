using System;
using System.Globalization;
using System.Threading.Tasks;

namespace Teams.CustomConnector.Common
{

    /// <summary></summary>
    internal sealed class RetryWithExponentialBackoff
    {
        private readonly int maxRetries, delayMilliseconds, maxDelayMilliseconds;


        /// <summary>Initializes a new instance of the <see cref="RetryWithExponentialBackoff"/> class.</summary>
        /// <param name="maxRetries">The maximum retries.</param>
        /// <param name="delayMilliseconds">The delay milliseconds.</param>
        /// <param name="maxDelayMilliseconds">The maximum delay milliseconds.</param>
        /// <exception cref="ArgumentException"></exception>
        public RetryWithExponentialBackoff(int maxRetries = 5, int delayMilliseconds = 200, int maxDelayMilliseconds = 2000)
        {
            if (maxRetries > 15 || maxRetries < 0)
            {
                throw new ArgumentException(string.Format(CultureInfo.InvariantCulture, "{0} should be greater than 0 and less than 15", nameof(maxRetries)));
            }

            this.maxRetries = maxRetries;
            this.delayMilliseconds = delayMilliseconds;
            this.maxDelayMilliseconds = maxDelayMilliseconds;
        }


        /// <summary>Runs the asynchronous.</summary>
        /// <param name="func">The function.</param>
        public async Task RunAsync(Func<Task> func)
        {
            ExponentialBackoff backoff = new ExponentialBackoff(this.maxRetries, this.delayMilliseconds, this.maxDelayMilliseconds);
            await RunInternalAsync(func, backoff);
        }


        /// <summary>Runs the internal asynchronous.</summary>
        /// <param name="func">The function.</param>
        /// <param name="backoff">The backoff.</param>
        private async Task RunInternalAsync(Func<Task> func, ExponentialBackoff backoff)
        {
            try
            {
                await func().ConfigureAwait(false);
            }
            catch (Exception error) when (error is TimeoutException ||
                error is System.Net.Http.HttpRequestException)
            {
                await backoff.Delay();
                await RunInternalAsync(func, backoff);
            }
        }
    }
}
