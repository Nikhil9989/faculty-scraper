"""
Rate limiting module for Faculty API.

This module provides customized rate limiting functionality based on user roles.
"""

import time
from typing import Callable, Dict, Optional, Tuple, Union
from fastapi import Depends, HTTPException, Request, status
from auth import User, get_current_active_user, get_current_admin_user, is_admin
import redis.asyncio
from fastapi_limiter import FastAPILimiter
from fastapi_limiter.depends import RateLimiter
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Rate limiting configuration
DEFAULT_RATE_LIMIT_ANONYMOUS = (20, 60)  # 20 requests per minute for anonymous endpoints
DEFAULT_RATE_LIMIT_USER = (100, 60)  # 100 requests per minute for authenticated users
DEFAULT_RATE_LIMIT_ADMIN = (300, 60)  # 300 requests per minute for admin users

# Endpoint-specific rate limits
ENDPOINT_LIMITS = {
    "/match": (30, 60),  # Resource-intensive endpoint
    "/faculty/search": (50, 60),  # Search endpoint
    "/resume/upload": (10, 60),  # File upload endpoint
    "/resume/parse": (20, 60),  # File processing endpoint
}

# Redis connection string (in production, get from environment variables)
REDIS_URL = "redis://localhost:6379/0"

async def setup_limiter():
    """Setup Redis connection for rate limiting."""
    try:
        redis_connection = redis.asyncio.from_url(REDIS_URL, encoding="utf-8", decode_responses=True)
        await FastAPILimiter.init(redis_connection)
        logger.info("Rate limiter initialized with Redis")
        return True
    except Exception as e:
        logger.warning(f"Failed to initialize rate limiter: {e}")
        logger.warning("Rate limiting will not be active!")
        return False

class RoleLimiter:
    """
    Rate limiter that applies different limits based on user role.
    """
    
    def __init__(
        self,
        anonymous_limit: Tuple[int, int] = DEFAULT_RATE_LIMIT_ANONYMOUS,
        user_limit: Tuple[int, int] = DEFAULT_RATE_LIMIT_USER,
        admin_limit: Tuple[int, int] = DEFAULT_RATE_LIMIT_ADMIN,
        endpoint: Optional[str] = None
    ):
        """
        Initialize role-based rate limiter.
        
        Args:
            anonymous_limit: Tuple of (requests, seconds) for anonymous access
            user_limit: Tuple of (requests, seconds) for normal users
            admin_limit: Tuple of (requests, seconds) for admin users
            endpoint: If provided, use endpoint-specific limits instead of defaults
        """
        # Use endpoint-specific limits if available
        if endpoint and endpoint in ENDPOINT_LIMITS:
            self.endpoint_limit = ENDPOINT_LIMITS[endpoint]
        else:
            self.endpoint_limit = None
            
        self.anonymous_limit = anonymous_limit
        self.user_limit = user_limit
        self.admin_limit = admin_limit
    
    def get_limit_for_endpoint(self, is_admin_user: bool) -> Tuple[int, int]:
        """Get appropriate limit for an endpoint based on user role."""
        # Use endpoint-specific limit if available
        if self.endpoint_limit:
            times, seconds = self.endpoint_limit
            
            # Scale up limits for admin users by 50%
            if is_admin_user:
                times = int(times * 1.5)
                
            return times, seconds
            
        # Otherwise use role-based default limits
        if is_admin_user:
            return self.admin_limit
        else:
            return self.user_limit
    
    async def __call__(self, request: Request, user: User = Depends(get_current_active_user)) -> None:
        """
        Apply rate limiting based on user role.
        
        Args:
            request: FastAPI request object
            user: Current authenticated user
        
        Raises:
            HTTPException: If rate limit is exceeded
        """
        if not hasattr(request.app, "limiter") or not request.app.limiter:
            # Rate limiting not initialized, skip check
            return
            
        # Get appropriate limit based on user role
        admin_user = is_admin(user)
        times, seconds = self.get_limit_for_endpoint(admin_user)
        
        # Create a rate limiter with the appropriate limits
        limiter = RateLimiter(times=times, seconds=seconds)
        
        # Use the user's ID as part of the Redis key for rate limiting
        # This ensures each user has their own rate limit
        request.state.user_id = user.id
        
        # Apply the rate limit
        await limiter(request)

# Helper function for applying rate limits to authenticated endpoints
def rate_limit(endpoint: Optional[str] = None):
    """
    Apply role-based rate limiting to an endpoint.
    
    Args:
        endpoint: Optional endpoint path for endpoint-specific limits
    
    Returns:
        Dependency callable for FastAPI
    """
    return RoleLimiter(endpoint=endpoint)
