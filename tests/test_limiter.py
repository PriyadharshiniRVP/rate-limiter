# tests/test_limiter.py

import time
from app.limiter import TokenBucketLimiter


def test_new_client_has_full_bucket():
    """A brand new client starts with capacity tokens."""
    limiter = TokenBucketLimiter(capacity=5, refill_rate=1)
    tokens = limiter.get_tokens("user1")
    assert tokens == 5


def test_first_request_allowed():
    """A new client can make at least one request."""
    limiter = TokenBucketLimiter(capacity=5, refill_rate=1)
    assert limiter.allow_requests("user1") is True


def test_requests_drain_the_bucket():
    """After capacity requests, the bucket is empty."""
    limiter = TokenBucketLimiter(capacity=5, refill_rate=0.0001)  # almost no refill
    for _ in range(5):
        assert limiter.allow_requests("user1") is True
    # 6th request should be blocked
    assert limiter.allow_requests("user1") is False


def test_blocked_when_empty():
    """Once empty, all further requests are blocked until refill."""
    limiter = TokenBucketLimiter(capacity=3, refill_rate=0.0001)
    for _ in range(3):
        limiter.allow_requests("user1")
    # Now empty
    assert limiter.allow_requests("user1") is False
    assert limiter.allow_requests("user1") is False
    assert limiter.allow_requests("user1") is False


def test_refill_adds_tokens_over_time():
    """After waiting, tokens refill."""
    limiter = TokenBucketLimiter(capacity=5, refill_rate=10)  # 10/sec, fast
    # Drain the bucket
    for _ in range(5):
        limiter.allow_requests("user1")
    assert limiter.allow_requests("user1") is False
    # Wait 0.5 seconds -> should add ~5 tokens
    time.sleep(0.5)
    assert limiter.allow_requests("user1") is True


def test_capacity_is_capped():
    """Even after a long idle, tokens don't exceed capacity."""
    limiter = TokenBucketLimiter(capacity=5, refill_rate=100)  # very fast refill
    # Drain
    for _ in range(5):
        limiter.allow_requests("user1")
    # Wait 1 second -> refill would add 100 tokens, but cap is 5
    time.sleep(1)
    assert limiter.get_tokens("user1") <= 5


def test_clients_are_isolated():
    """Two clients have separate buckets."""
    limiter = TokenBucketLimiter(capacity=2, refill_rate=0.0001)
    # Drain user1
    limiter.allow_requests("user1")
    limiter.allow_requests("user1")
    assert limiter.allow_requests("user1") is False
    # user2 should still have full bucket
    assert limiter.allow_requests("user2") is True
    assert limiter.allow_requests("user2") is True
    assert limiter.allow_requests("user2") is False