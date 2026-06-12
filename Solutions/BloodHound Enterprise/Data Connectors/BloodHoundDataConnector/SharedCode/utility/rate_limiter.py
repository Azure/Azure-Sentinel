"""
Global rate limiter for BloodHound API requests.
Uses token bucket algorithm to ensure we never exceed the API rate limit.
Thread-safe and shared across all BloodhoundManager instances.
"""
import threading
import time
import logging
import random
from typing import Optional
from .utils import get_max_requests_per_second


class GlobalRateLimiter:
    """
    Thread-safe global rate limiter using token bucket algorithm.
    Ensures all BloodHound API requests across all functions stay within rate limits.
    
    The rate limiter maintains a bucket of tokens that refill at a fixed rate.
    Each API request consumes one token. If no tokens are available, the request waits.
    """
    
    _instance: Optional['GlobalRateLimiter'] = None
    _lock = threading.Lock()
    
    def __init__(self, max_requests_per_second: float = 50.0, logger: Optional[logging.Logger] = None):
        """
        Initialize the global rate limiter.
        
        Args:
            max_requests_per_second: Maximum requests per second (default: 50, well under 65 limit)
            logger: Logger instance (optional)
        """
        self.original_max_requests_per_second = max_requests_per_second
        self.max_requests_per_second = max_requests_per_second
        self.tokens_per_second = max_requests_per_second
        self.max_tokens = max_requests_per_second  # Bucket capacity equals refill rate
        self.current_tokens = self.max_tokens  # Start with full bucket
        self.last_refill_time = time.time()
        self._lock = threading.Lock()
        self.logger = logger or logging.getLogger(__name__)
        
        # Statistics
        self.total_requests = 0
        self.total_wait_time = 0.0
        
        # Dynamic rate limiting (for handling 429 errors)
        self.consecutive_429s = 0
        self.successful_requests_since_429 = 0
        self.min_requests_per_second = max_requests_per_second * 0.1  # Don't go below 10% of original
        
        # Request rate tracking (for per-second logging)
        self.request_timestamps = []  # Store timestamps of recent requests
        self.last_rate_log_time = time.time()
        self.rate_log_interval = 1.0  # Log rate every 1 second
        
        self.logger.info(
            f"GlobalRateLimiter initialized: {max_requests_per_second} requests/second "
            f"(max tokens: {self.max_tokens})"
        )
    
    @classmethod
    def get_instance(cls, max_requests_per_second: Optional[float] = None, 
                     logger: Optional[logging.Logger] = None) -> 'GlobalRateLimiter':
        """
        Get or create the singleton instance of GlobalRateLimiter.
        
        Args:
            max_requests_per_second: Maximum requests per second (only used on first creation)
            logger: Logger instance (optional)
        
        Returns:
            GlobalRateLimiter: The singleton instance
        """
        if cls._instance is None:
            with cls._lock:
                # Double-check locking pattern
                if cls._instance is None:
                    if max_requests_per_second is None:
                        # Get from environment variable or use default
                        max_requests_per_second = get_max_requests_per_second()
                    cls._instance = cls(max_requests_per_second, logger)
        return cls._instance
    
    def _refill_tokens(self):
        """Refill tokens based on elapsed time since last refill."""
        try:
            now = time.time()
            elapsed = now - self.last_refill_time
            
            if elapsed > 0:
                # Add tokens based on refill rate
                tokens_to_add = elapsed * self.tokens_per_second
                self.current_tokens = min(
                    self.max_tokens,
                    self.current_tokens + tokens_to_add
                )
                self.last_refill_time = now
        except Exception as e:
            self.logger.error(
                f"Rate limiter error in _refill_tokens(): {type(e).__name__}: {str(e)}",
                exc_info=True
            )
            # Reset to safe state on error
            self.last_refill_time = time.time()
            raise
    
    def acquire(self, timeout: Optional[float] = None) -> bool:
        """
        Acquire a token for making an API request.
        Blocks until a token is available or timeout occurs.
        
        Args:
            timeout: Maximum time to wait for a token (None = wait indefinitely)
        
        Returns:
            bool: True if token acquired, False if timeout
        """
        start_time = time.time()
        
        with self._lock:
            while True:
                # Refill tokens
                self._refill_tokens()
                
                # Enforce minimum time between requests to prevent exceeding rate limit
                min_time_between_requests = 1.0 / self.max_requests_per_second
                now = time.time()
                
                # Check if we need to wait based on last request time
                if self.request_timestamps:
                    time_since_last_request = now - self.request_timestamps[-1]
                    if time_since_last_request < min_time_between_requests:
                        # Need to wait to enforce rate limit
                        wait_needed = min_time_between_requests - time_since_last_request
                        self._lock.release()
                        try:
                            time.sleep(wait_needed)
                        except Exception as e:
                            self.logger.error(
                                f"Rate limiter error during sleep: {type(e).__name__}: {str(e)}",
                                exc_info=True
                            )
                            raise
                        finally:
                            try:
                                self._lock.acquire()
                            except Exception as e:
                                self.logger.error(
                                    f"Rate limiter error re-acquiring lock: {type(e).__name__}: {str(e)}",
                                    exc_info=True
                                )
                                raise
                        # Refill tokens again after waiting and update now
                        self._refill_tokens()
                        now = time.time()
                
                # Check if we have a token available
                if self.current_tokens >= 1.0:
                    self.current_tokens -= 1.0
                    self.total_requests += 1
                    wait_time = now - start_time
                    self.total_wait_time += wait_time
                    
                    # Track request timestamp for rate calculation
                    self.request_timestamps.append(now)
                    
                    # Clean old timestamps (keep only last 5 seconds)
                    cutoff_time = now - 5.0
                    self.request_timestamps = [ts for ts in self.request_timestamps if ts > cutoff_time]
                    
                    # Log requests per second periodically (WARNING level = yellow)
                    if now - self.last_rate_log_time >= self.rate_log_interval:
                        requests_in_last_second = len([ts for ts in self.request_timestamps if ts > now - 1.0])
                        self.logger.info(
                            f"Rate Limiter Stats: {requests_in_last_second} request(s)/second "
                            f"(Limit: {self.max_requests_per_second}/sec) | "
                            f"Total requests: {self.total_requests} | "
                            f"Available tokens: {self.current_tokens:.2f}/{self.max_tokens:.2f}"
                        )
                        self.last_rate_log_time = now
                    
                    if wait_time > 0.01:  # Log if we had to wait more than 10ms
                        self.logger.debug(
                            f"Rate limiter: waited {wait_time:.3f}s for token. "
                            f"Remaining tokens: {self.current_tokens:.2f}"
                        )
                    return True
                
                # No token available, calculate wait time
                tokens_needed = 1.0 - self.current_tokens
                wait_time = tokens_needed / self.tokens_per_second
                
                # Check timeout
                if timeout is not None:
                    elapsed = time.time() - start_time
                    if elapsed + wait_time > timeout:
                        self.logger.warning(
                            f"Rate limiter timeout: could not acquire token within {timeout}s"
                        )
                        return False
                
                # Release lock and wait
                self._lock.release()
                try:
                    time.sleep(wait_time)
                except Exception as e:
                    self.logger.error(
                        f"Rate limiter error during sleep: {type(e).__name__}: {str(e)}",
                        exc_info=True
                    )
                    raise
                finally:
                    try:
                        self._lock.acquire()
                    except Exception as e:
                        self.logger.error(
                            f"Rate limiter error re-acquiring lock: {type(e).__name__}: {str(e)}",
                            exc_info=True
                        )
                        raise
    
    def wait(self):
        """
        Wait until a token is available, then consume it.
        This is the main method to call before making an API request.
        
        Raises:
            RuntimeError: If token acquisition fails unexpectedly
        """
        try:
            if not self.acquire():
                raise RuntimeError(
                    "Rate limiter failed to acquire token. This should not happen "
                    "with default timeout=None (infinite wait)."
                )
        except Exception as e:
            self.logger.error(
                f"Rate limiter error in wait(): {type(e).__name__}: {str(e)}",
                exc_info=True
            )
            raise
    
    def get_stats(self, timeout: Optional[float] = 5.0) -> dict:
        """
        Get statistics about rate limiter usage.
        
        Args:
            timeout: Maximum time to wait for lock acquisition (default: 5 seconds)
        
        Returns:
            dict: Statistics including total requests, average wait time, etc.
                  Returns empty dict with error message if lock cannot be acquired.
        """
        # Try to acquire lock with timeout
        if not self._lock.acquire(timeout=timeout):
            self.logger.warning(
                f"Could not acquire lock for get_stats() within {timeout}s. "
                "Returning partial stats without lock."
            )
            # Return stats that don't require lock (immutable values)
            return {
                "error": "Lock acquisition timeout",
                "max_requests_per_second": self.max_requests_per_second,
                "tokens_per_second": self.tokens_per_second,
            }
        
        try:
            avg_wait_time = (
                self.total_wait_time / self.total_requests
                if self.total_requests > 0
                else 0.0
            )
            return {
                "total_requests": self.total_requests,
                "total_wait_time": self.total_wait_time,
                "average_wait_time": avg_wait_time,
                "current_tokens": self.current_tokens,
                "max_requests_per_second": self.max_requests_per_second,
                "tokens_per_second": self.tokens_per_second,
            }
        finally:
            self._lock.release()
    
    def reset_stats(self, timeout: Optional[float] = 5.0):
        """
        Reset statistics counters.
        
        Args:
            timeout: Maximum time to wait for lock acquisition (default: 5 seconds)
        
        Returns:
            bool: True if stats were reset, False if lock acquisition failed
        """
        if not self._lock.acquire(timeout=timeout):
            self.logger.warning(
                f"Could not acquire lock for reset_stats() within {timeout}s."
            )
            return False
        
        try:
            self.total_requests = 0
            self.total_wait_time = 0.0
            return True
        finally:
            self._lock.release()
    
    def handle_rate_limit(self, response=None):
        """
        Handle rate limit error (429) by dynamically reducing the rate limit.
        Uses Retry-After header if available, otherwise uses exponential backoff.
        
        Args:
            response: HTTP response object (may contain Retry-After header)
        
        Returns:
            float: Delay in seconds to wait before retry
        """
        with self._lock:
            self.consecutive_429s += 1
            self.successful_requests_since_429 = 0
            
            # Check for Retry-After header
            retry_after = None
            if response and hasattr(response, 'headers') and 'Retry-After' in response.headers:
                try:
                    retry_after = int(response.headers['Retry-After'])
                    self.logger.info(f"Rate limit detected. Retry-After header: {retry_after} seconds")
                except (ValueError, TypeError):
                    pass
            
            if retry_after:
                # Reduce rate limit based on Retry-After
                # If Retry-After is large, reduce rate more aggressively
                reduction_factor = min(0.5, retry_after / 60.0)  # Max 50% reduction
                new_rate = max(
                    self.min_requests_per_second,
                    self.max_requests_per_second * (1.0 - reduction_factor)
                )
                delay = retry_after + random.uniform(0, 2)  # Add jitter
            else:
                # Exponential backoff: reduce rate by 50% for each consecutive 429
                reduction_factor = 0.5 ** min(self.consecutive_429s, 5)  # Cap at 5 consecutive 429s
                new_rate = max(
                    self.min_requests_per_second,
                    self.original_max_requests_per_second * reduction_factor
                )
                # Calculate delay based on exponential backoff
                base_delay = 1.0 * (2 ** min(self.consecutive_429s - 1, 10))
                delay = base_delay + random.uniform(0, base_delay * 0.2)
            
            # Update rate limit
            old_rate = self.max_requests_per_second
            self.max_requests_per_second = new_rate
            self.tokens_per_second = new_rate
            self.max_tokens = new_rate
            
            # Reduce current tokens to reflect the new rate limit
            if self.current_tokens > new_rate:
                self.current_tokens = new_rate
            
            self.logger.warning(
                f"Rate limit error (429). Reducing rate limit from {old_rate:.2f} to {new_rate:.2f} req/s. "
                f"Consecutive 429s: {self.consecutive_429s}. Waiting {delay:.2f} seconds before retry."
            )
            
            return delay
    
    def handle_success(self):
        """
        Handle successful request by gradually recovering the rate limit.
        """
        with self._lock:
            if self.consecutive_429s > 0:
                self.successful_requests_since_429 += 1
                
                # After 10 successful requests, start recovering rate
                if self.successful_requests_since_429 >= 10:
                    # Gradually increase rate limit back towards original
                    recovery_factor = 1.1  # Increase by 10%
                    new_rate = min(
                        self.original_max_requests_per_second,
                        self.max_requests_per_second * recovery_factor
                    )
                    
                    old_rate = self.max_requests_per_second
                    self.max_requests_per_second = new_rate
                    self.tokens_per_second = new_rate
                    self.max_tokens = new_rate
                    
                    # Reduce consecutive 429s counter
                    self.consecutive_429s = max(0, self.consecutive_429s - 1)
                    self.successful_requests_since_429 = 0
                    
                    if self.consecutive_429s == 0:
                        # Fully recovered
                        self.max_requests_per_second = self.original_max_requests_per_second
                        self.tokens_per_second = self.original_max_requests_per_second
                        self.max_tokens = self.original_max_requests_per_second
                        self.logger.info(
                            f"Rate limit fully recovered. Rate limit restored to {self.original_max_requests_per_second:.2f} req/s."
                        )
                    else:
                        self.logger.info(
                            f"Rate limit recovering. Increased from {old_rate:.2f} to {new_rate:.2f} req/s. "
                            f"Consecutive 429s remaining: {self.consecutive_429s}"
                        )


# Azure Monitor rate limiter instance (separate from BloodHound API)
_azure_monitor_rate_limiter: Optional[GlobalRateLimiter] = None
_azure_monitor_lock = threading.Lock()

def get_azure_monitor_rate_limiter(max_requests_per_second: Optional[float] = None,
                                   logger: Optional[logging.Logger] = None) -> GlobalRateLimiter:
    """
    Get the Azure Monitor rate limiter instance.
    Uses a separate instance from the BloodHound API rate limiter.
    Rate limit is read from MAX_REQUESTS_PER_SECOND_LIMIT environment variable.
    
    Args:
        max_requests_per_second: Maximum requests per second (default: from env var MAX_REQUESTS_PER_SECOND_LIMIT)
        logger: Logger instance (optional)
    
    Returns:
        GlobalRateLimiter: The Azure Monitor rate limiter instance
    """
    global _azure_monitor_rate_limiter
    
    if _azure_monitor_rate_limiter is None:
        with _azure_monitor_lock:
            if _azure_monitor_rate_limiter is None:
                if max_requests_per_second is None:
                    # Get from environment variable MAX_REQUESTS_PER_SECOND_LIMIT (capped at 50)
                    max_requests_per_second = get_max_requests_per_second()
                _azure_monitor_rate_limiter = GlobalRateLimiter(max_requests_per_second, logger)
    
    return _azure_monitor_rate_limiter


# Convenience function to get the global rate limiter instance
def get_global_rate_limiter(logger: Optional[logging.Logger] = None) -> GlobalRateLimiter:
    """
    Get the global rate limiter instance for BloodHound API.
    
    Args:
        logger: Logger instance (optional)
    
    Returns:
        GlobalRateLimiter: The singleton rate limiter instance
    """
    return GlobalRateLimiter.get_instance(logger=logger)

