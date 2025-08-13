"""
Session-based authentication middleware for the Titanic API.
Redirects unauthenticated users to the beautiful login page.
"""

from fastapi import Request
from fastapi.responses import RedirectResponse
from starlette.middleware.base import BaseHTTPMiddleware

class SessionAuthMiddleware(BaseHTTPMiddleware):
    """
    Session-based authentication middleware.
    Redirects unauthenticated users to login page instead of showing browser popup.
    """
    
    # Public endpoints that don't require authentication
    PUBLIC_PATHS = {
        "/",
        "/health", 
        "/auth/",
        "/auth/login",
        "/auth/logout",
        "/auth/check",
        "/docs",
        "/redoc",
        "/openapi.json",
        "/favicon.ico"
    }
    
    # Static file patterns
    STATIC_PATTERNS = [
        "/static/",
        ".css",
        ".js",
        ".png",
        ".jpg",
        ".ico"
    ]
    
    def __init__(self, app):
        super().__init__(app)
        # Import here to avoid circular imports
        from api.routes.auth import active_sessions
        self.active_sessions = active_sessions
    
    async def dispatch(self, request: Request, call_next):
        """
        Process each request and check session authentication.
        """
        path = request.url.path
        
        # Allow public endpoints
        if path in self.PUBLIC_PATHS:
            response = await call_next(request)
            return response
            
        # Allow static files
        if any(pattern in path for pattern in self.STATIC_PATTERNS):
            response = await call_next(request)
            return response
        
        # Check for valid session
        session_id = request.cookies.get("session_id")
        if session_id and session_id in self.active_sessions:
            # Valid session - proceed
            response = await call_next(request)
            return response
        
        # No valid session - redirect to login
        # If it's an API call (JSON request), return 401
        if (request.headers.get("accept", "").startswith("application/json") or 
            path.startswith("/api/")):
            from fastapi.responses import JSONResponse
            return JSONResponse(
                status_code=401,
                content={"detail": "Authentication required. Please login at /auth/"}
            )
        
        # For browser requests, redirect to login page
        return RedirectResponse(url="/auth/", status_code=302)
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