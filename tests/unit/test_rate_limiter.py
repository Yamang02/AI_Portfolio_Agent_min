"""Tests for rate limiter middleware"""

import pytest
import time
from app.middleware.rate_limiter import SlidingWindowRateLimiter


class TestSlidingWindowRateLimiter:
    """Test sliding window rate limiting algorithm"""
    
    @pytest.fixture
    def limiter(self):
        """Create rate limiter with 3 RPM for testing"""
        return SlidingWindowRateLimiter(rpm=3)
    
    def test_allow_within_limit(self, limiter):
        """Test requests within limit are allowed"""
        allowed, retry_after = limiter.is_allowed("192.168.1.1")
        assert allowed is True
        assert retry_after == 0
    
    def test_multiple_within_limit(self, limiter):
        """Test multiple requests within limit are allowed"""
        for _ in range(3):
            allowed, retry_after = limiter.is_allowed("192.168.1.1")
            assert allowed is True
            assert retry_after == 0
    
    def test_exceed_limit(self, limiter):
        """Test requests exceeding limit are blocked"""
        # Fill up the quota
        for _ in range(3):
            limiter.is_allowed("192.168.1.1")
        
        # Next request should be blocked
        allowed, retry_after = limiter.is_allowed("192.168.1.1")
        assert allowed is False
        assert retry_after > 0
    
    def test_different_ips_independent(self, limiter):
        """Test rate limiting is per-IP"""
        # Fill quota for IP 1
        for _ in range(3):
            limiter.is_allowed("192.168.1.1")
        
        # IP 1 should be blocked
        allowed, _ = limiter.is_allowed("192.168.1.1")
        assert allowed is False
        
        # IP 2 should still be allowed
        allowed, retry_after = limiter.is_allowed("192.168.1.2")
        assert allowed is True
        assert retry_after == 0
    
    def test_window_resets(self, limiter):
        """Test window resets after 60 seconds"""
        # Use shorter window for testing
        limiter.window_size = 1  # 1 second window
        
        # Fill quota
        for _ in range(3):
            limiter.is_allowed("192.168.1.1")
        
        # Should be blocked
        allowed, _ = limiter.is_allowed("192.168.1.1")
        assert allowed is False
        
        # Wait for window to pass
        time.sleep(1.5)
        
        # Should be allowed again
        allowed, retry_after = limiter.is_allowed("192.168.1.1")
        assert allowed is True
        assert retry_after == 0
    
    def test_retry_after_value(self, limiter):
        """Test retry_after header value is reasonable"""
        # Fill quota
        for _ in range(3):
            limiter.is_allowed("192.168.1.1")
        
        # Check retry_after
        allowed, retry_after = limiter.is_allowed("192.168.1.1")
        assert allowed is False
        assert 1 <= retry_after <= 61  # Should be 1-61 seconds for 60-second window
    
    def test_cleanup_old_requests(self, limiter):
        """Test old requests are cleaned from memory"""
        limiter.window_size = 1  # 1 second window
        
        # Add request
        limiter.is_allowed("192.168.1.1")
        assert len(limiter.requests["192.168.1.1"]) == 1
        
        # Wait for window to pass
        time.sleep(1.5)
        
        # Check requests again (should trigger cleanup)
        limiter.is_allowed("192.168.1.1")
        
        # Old requests should be cleaned
        start_time = time.time()
        for req_time in limiter.requests["192.168.1.1"]:
            assert start_time - req_time < limiter.window_size
