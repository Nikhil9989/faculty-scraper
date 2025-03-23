"""
Rate Limiting module for Faculty API

This module provides the rate limiting implementation using slowapi
with different rate limits for different endpoints.
"""

import os
import redis
from slowapi import Limiter
from slowapi.util import get_remote_address
from fastapi import Depends, Request
from functools import wraps
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Configuration from environment variables
REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", "6379"))
REDIS_DB = int(os.getenv("REDIS_DB", "0"))
REDIS_PASSWORD = os.getenv("REDIS_PASSWORD", None)

# Define rate limits (can be configured from environment variables)
DEFAULT_RATE_LIMIT = os.getenv("DEFAULT_RATE_LIMIT", "60/minute")
FACULTY_SEARCH_LIMIT = os.getenv("FACULTY_SEARCH_LIMIT", "30/minute")
RESUME_UPLOAD_LIMIT = os.getenv("RESUME_UPLOAD_LIMIT", "10/minute")
RESUME_PARSE_LIMIT = os.getenv("RESUME_PARSE_LIMIT", "20/minute")
MATCH_RATE_LIMIT = os.getenv("MATCH_RATE_LIMIT", "15/minute")

# Define endpoint-specific rate limits
ENDPOINT_LIMITS = {
    "/faculty/search": FACULTY_SEARCH_LIMIT,
    "/resume/upload": RESUME_UPLOAD_LIMIT,
    "/resume/parse": RESUME_PARSE_LIMIT,
    "/match": MATCH_RATE_LIMIT
}

# Global limiter instance
limiter = None

async def setup_limiter():
    """
    Setup and initialize the rate limiter with Redis backend.
    """
    global limiter
    
    try:
        # Create Redis connection
        redis_client = redis.Redis(
            host=REDIS_HOST,
            port=REDIS_PORT,
            db=REDIS_DB,
            password=REDIS_PASSWORD,
            decode_responses=True
        )
        
        # Test Redis connection
        redis_client.ping()
        
        # Create limiter with Redis backend
        limiter = Limiter(
            key_func=get_key_func,
            default_limits=[DEFAULT_RATE_LIMIT],
            storage_uri=f"redis://{REDIS_HOST}:{REDIS_PORT}/{REDIS_DB}"
        )
        
        logger.info("Rate limiter initialized with Redis backend")
        return limiter
        
    except redis.exceptions.ConnectionError as e:
        logger.error(f"Failed to connect to Redis: {e}")
        
        # Fallback to memory storage if Redis is not available
        limiter = Limiter(
            key_func=get_key_func,
            default_limits=[DEFAULT_RATE_LIMIT]
        )
        
        logger.warning("Rate limiter initialized with memory storage (fallback)")
        return limiter
    
    except Exception as e:
        logger.error(f"Error initializing rate limiter: {e}")
        return None

def get_key_func(request: Request) -> str:
    """
    Get a unique key for rate limiting based on user identity or IP.
    
    For authenticated requests, uses the user's email.
    For anonymous requests, uses the IP address.
    """
    # If user is authenticated, use their email as the key
    if hasattr(request.state, "user") and request.state.user:
        return f"user:{request.state.user.email}"
    
    # Otherwise use IP address
    return f"ip:{get_remote_address(request)}"

def rate_limit(endpoint_path=None):
    """
    Factory function to create a rate limiter dependency with the appropriate
    limit for a given endpoint.
    
    Args:
        endpoint_path: Optional endpoint path to apply specific rate limit
        
    Returns:
        A dependency function that will apply rate limiting
    """
    from fastapi_limiter.depends import RateLimiter
    
    # Get the appropriate limit for this endpoint
    limit = ENDPOINT_LIMITS.get(endpoint_path, DEFAULT_RATE_LIMIT)
    
    # Parse the limit (format: "number/timeunit")
    parts = limit.split("/")
    if len(parts) != 2:
        # Fallback to default if format is invalid
        times, seconds = 60, 60  # 60 per minute default
    else:
        times = int(parts[0])
        
        # Convert time unit to seconds
        time_unit = parts[1].lower()
        if time_unit == "second":
            seconds = 1
        elif time_unit == "minute":
            seconds = 60
        elif time_unit == "hour":
            seconds = 3600
        elif time_unit == "day":
            seconds = 86400
        else:
            seconds = 60  # Default to minute
    
    # Create and return the limiter dependency
    return RateLimiter(times=times, seconds=seconds)
