"""
Rate Limiter Module for Faculty API.

This module provides rate limiting functionality using slowapi.
"""

import os
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from fastapi import Request, Response
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Environment variables for rate limiting configuration
DEFAULT_RATE_LIMIT = os.getenv("DEFAULT_RATE_LIMIT", "60/minute")
SEARCH_RATE_LIMIT = os.getenv("SEARCH_RATE_LIMIT", "30/minute")
UPLOAD_RATE_LIMIT = os.getenv("UPLOAD_RATE_LIMIT", "10/minute")
MATCH_RATE_LIMIT = os.getenv("MATCH_RATE_LIMIT", "20/minute")

def get_key_func(request: Request) -> str:
    """
    Get a unique key for rate limiting.
    
    Uses JWT token user if authenticated, otherwise IP address.
    """
    # Try to get user from request state (set by auth middleware)
    if hasattr(request.state, "user") and request.state.user:
        # Return email as key for authenticated users
        return request.state.user.email
    
    # Fallback to IP address
    return get_remote_address(request)

# Initialize the rate limiter
limiter = Limiter(
    key_func=get_key_func,
    default_limits=[DEFAULT_RATE_LIMIT],
    headers_enabled=True,  # Enable X-RateLimit headers in response
    strategy="fixed-window",  # Use fixed window strategy
)

def get_limiter_response(
    request: Request, response: Response, key: str, limit: str, limited: bool
) -> Response:
    """
    Custom callback to modify response headers for rate-limited responses.
    """
    if limited:
        # Log the rate limit exceeded event
        logger.warning(f"Rate limit exceeded: {key} - {request.url.path}")
        
        # Add custom response header
        response.headers["X-Rate-Limit-Reason"] = f"Rate limit of {limit} exceeded for this endpoint"
    
    return response

# Configure the limiter to use our custom callback
limiter.response_callback = get_limiter_response
