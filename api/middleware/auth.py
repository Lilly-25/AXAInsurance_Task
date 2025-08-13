"""
Global HTTP Basic Authentication middleware for the Titanic API.
Users can enter username/password directly in browser - much more user-friendly!
"""

from fastapi import Request, HTTPException, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
import base64

# User credentials (username, password)
AUTHORIZED_USERS = {
    "admin": "secret",
    "analyst": "password123", 
    "viewer": "view2024"
}

def verify_password(plain_password: str, stored_password: str) -> bool:
    """Verify password (simple comparison for Basic Auth)"""
    return plain_password == stored_password

class GlobalBasicAuthMiddleware(BaseHTTPMiddleware):
    """
    Global HTTP Basic Authentication middleware.
    Users can enter username/password directly in browser prompts.
    """
    
    # Public endpoints that don't require authentication
    PUBLIC_PATHS = {
        "/",
        "/health", 
        "/docs",
        "/redoc",
        "/openapi.json",
        "/favicon.ico"
    }
    
    async def dispatch(self, request: Request, call_next):
        """
        Process each request and check HTTP Basic Authentication.
        """
        path = request.url.path
        
        # Allow public endpoints
        if path in self.PUBLIC_PATHS:
            response = await call_next(request)
            return response
        
        # Check for Authorization header
        authorization = request.headers.get("authorization")
        if not authorization:
            return JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content={"detail": "Authentication required. Please provide username and password."},
                headers={"WWW-Authenticate": "Basic realm=\"Titanic API\""},
            )
        
        # Parse Basic Auth
        try:
            scheme, credentials = authorization.split(' ', 1)
            if scheme.lower() != "basic":
                raise ValueError("Invalid authentication scheme")
            
            # Decode base64 credentials
            decoded = base64.b64decode(credentials).decode('utf-8')
            username, password = decoded.split(':', 1)
            
        except (ValueError, UnicodeDecodeError):
            return JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content={"detail": "Invalid authorization header format"},
                headers={"WWW-Authenticate": "Basic realm=\"Titanic API\""},
            )
        
        # Verify credentials
        if username not in AUTHORIZED_USERS:
            return JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content={"detail": "Invalid username or password"},
                headers={"WWW-Authenticate": "Basic realm=\"Titanic API\""},
            )
        
        stored_password = AUTHORIZED_USERS[username]
        
        if not verify_password(password, stored_password):
            return JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content={"detail": "Invalid username or password"},
                headers={"WWW-Authenticate": "Basic realm=\"Titanic API\""},
            )
        
        # Add user info to request state
        request.state.username = username
        
        # Continue with the request
        response = await call_next(request)
        return response