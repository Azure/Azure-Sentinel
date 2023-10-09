using System;
using System.Threading.Tasks;

namespace Teams.CustomConnector.Common
{

    /// <summary></summary>
    internal struct ExponentialBackoff
    {
        private readonly int maxRetries, delayMilliseconds, maxDelayMilliseconds;
        private int retries, pow;


        /// <summary>Initializes a new instance of the <see cref="ExponentialBackoff"/> struct.</summary>
        /// <param name="maxRetries">The maximum retries.</param>
        /// <param name="delayMilliseconds">The delay milliseconds.</param>
        /// <param name="maxDelayMilliseconds">The maximum delay milliseconds.</param>
        public ExponentialBackoff(int maxRetries, int delayMilliseconds,
            int maxDelayMilliseconds)
        {
            this.maxRetries = maxRetries;
            this.delayMilliseconds = delayMilliseconds;
            this.maxDelayMilliseconds = maxDelayMilliseconds;
            retries = 0;
            pow = 1;
        }


        /// <summary>Delays this instance.</summary>
        /// <returns></returns>
        /// <exception cref="TimeoutException">Max retry attempts exceeded.</exception>
        public Task Delay()
        {
            if (retries == maxRetries)
            {
                throw new TimeoutException("Max retry attempts exceeded.");
            }
            ++retries;
            if (retries < 31)
            {
                pow = pow << 1; //// pow = Pow(2, retries - 1)
            }
            int delay = Math.Min(
                delayMilliseconds * (pow - 1) / 2,
                maxDelayMilliseconds);
            return Task.Delay(delay);
        }
    }
}
