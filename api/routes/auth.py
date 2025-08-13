"""
Web-based authentication system for the Titanic API.
Provides a beautiful login page instead of browser popups.
"""

from fastapi import APIRouter, Request, Form, HTTPException, Depends
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
import os
from typing import Optional

# User credentials (username, password, role)
AUTHORIZED_USERS = {
    "admin": {"password": "secret", "role": "Administrator"},
    "analyst": {"password": "password123", "role": "Datenanalyst"}, 
    "viewer": {"password": "view2024", "role": "Betrachter"}
}

router = APIRouter()
templates = Jinja2Templates(directory="api/templates")

# Simple session storage (in production, use Redis or database)
active_sessions = {}

def verify_credentials(username: str, password: str) -> Optional[dict]:
    """Verify user credentials and return user info if valid"""
    if username in AUTHORIZED_USERS:
        user_data = AUTHORIZED_USERS[username]
        if user_data["password"] == password:
            return {
                "username": username,
                "role": user_data["role"]
            }
    return None

def get_session_user(request: Request) -> Optional[dict]:
    """Get current user from session"""
    session_id = request.cookies.get("session_id")
    if session_id and session_id in active_sessions:
        return active_sessions[session_id]
    return None

def require_auth(request: Request):
    """Dependency to require authentication"""
    user = get_session_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Authentication required")
    return user

@router.get("/", response_class=HTMLResponse)
async def login_page(request: Request, error: Optional[str] = None):
    """Show the login page"""
    # If user is already logged in, redirect to dashboard
    user = get_session_user(request)
    if user:
        return RedirectResponse(url="/auth/dashboard", status_code=302)
    
    return templates.TemplateResponse("login.html", {
        "request": request,
        "error": error
    })

@router.post("/login")
async def login(
    request: Request,
    username: str = Form(...),
    password: str = Form(...)
):
    """Process login form"""
    user_info = verify_credentials(username, password)
    
    if not user_info:
        return templates.TemplateResponse("login.html", {
            "request": request,
            "error": "Ungültiger Benutzername oder Passwort. Bitte versuchen Sie es erneut."
        })
    
    # Create session
    import uuid
    session_id = str(uuid.uuid4())
    active_sessions[session_id] = user_info
    
    # Redirect to dashboard with session cookie
    response = RedirectResponse(url="/auth/dashboard", status_code=302)
    response.set_cookie(
        key="session_id",
        value=session_id,
        max_age=86400,  # 24 hours
        httponly=True,
        secure=False  # Set to True in production with HTTPS
    )
    
    return response

@router.get("/dashboard", response_class=HTMLResponse)
async def dashboard(request: Request, user: dict = Depends(require_auth)):
    """Show the authenticated user dashboard"""
    return templates.TemplateResponse("dashboard.html", {
        "request": request,
        "username": user["username"],
        "user_role": user["role"],
        "role": user["username"]  # For role-based restrictions in template
    })

@router.get("/logout")
async def logout(request: Request):
    """Logout user and clear session"""
    session_id = request.cookies.get("session_id")
    if session_id and session_id in active_sessions:
        del active_sessions[session_id]
    
    response = RedirectResponse(url="/auth/", status_code=302)
    response.delete_cookie("session_id")
    return response

@router.get("/check")
async def check_auth(request: Request):
    """Check if user is authenticated (for API calls)"""
    user = get_session_user(request)
    if user:
        return {"authenticated": True, "user": user}
    else:
        return {"authenticated": False}
