using Microsoft.Extensions.Logging;

namespace BeyondTrustPMCloud.Services;

public interface IRateLimitService
{
    Task WaitForRateLimitAsync();
}

public class RateLimitService : IRateLimitService
{
    private readonly ILogger<RateLimitService> _logger;
    private readonly Queue<DateTime> _requestTimes = new();
    private readonly SemaphoreSlim _semaphore = new(1, 1);
    
    // BeyondTrust API limit: 1000 requests per 100 seconds
    private const int MaxRequests = 1000;
    private const int TimeWindowSeconds = 100;

    public RateLimitService(ILogger<RateLimitService> logger)
    {
        _logger = logger;
    }

    public async Task WaitForRateLimitAsync()
    {
        await _semaphore.WaitAsync();
        try
        {
            var now = DateTime.UtcNow;
            
            // Remove requests older than the time window
            while (_requestTimes.Count > 0 && (now - _requestTimes.Peek()).TotalSeconds > TimeWindowSeconds)
            {
                _requestTimes.Dequeue();
            }

            // If we're at the limit, calculate wait time
            if (_requestTimes.Count >= MaxRequests)
            {
                var oldestRequest = _requestTimes.Peek();
                var waitTime = TimeSpan.FromSeconds(TimeWindowSeconds) - (now - oldestRequest);
                
                if (waitTime > TimeSpan.Zero)
                {
                    _logger.LogInformation("Rate limit reached. Waiting {WaitTime} seconds before next request", 
                        waitTime.TotalSeconds);
                    
                    // Release the semaphore, wait, then re-acquire
                    _semaphore.Release();
                    try
                    {
                        await Task.Delay(waitTime);
                    }
                    finally
                    {
                        await _semaphore.WaitAsync();
                    }
                    
                    // Clean up again after waiting
                    now = DateTime.UtcNow;
                    while (_requestTimes.Count > 0 && (now - _requestTimes.Peek()).TotalSeconds > TimeWindowSeconds)
                    {
                        _requestTimes.Dequeue();
                    }
                }
            }

            // Record this request
            _requestTimes.Enqueue(now);
            
            _logger.LogDebug("Rate limit check complete. Current request count: {RequestCount}/{MaxRequests}", 
                _requestTimes.Count, MaxRequests);
        }
        finally
        {
            _semaphore.Release();
        }
    }
}
