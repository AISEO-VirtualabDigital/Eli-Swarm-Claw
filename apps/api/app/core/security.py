"""
Security utilities for authentication, authorization, and SSRF protection.
"""

from datetime import datetime, timedelta
from typing import Optional, Any
from jose import jwt, JWTError
from passlib.context import CryptContext
from fastapi import HTTPException, status, Depends
from fastapi.security import OAuth2PasswordBearer
import ipaddress
import socket
from urllib.parse import urlparse

from .config import settings


# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# OAuth2 scheme
oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.API_V1_PREFIX}/auth/login")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash."""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Hash a password."""
    return pwd_context.hash(password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create a JWT access token."""
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(
        to_encode, 
        settings.SECRET_KEY, 
        algorithm=settings.ALGORITHM
    )
    return encoded_jwt


def decode_access_token(token: str) -> Optional[dict]:
    """Decode a JWT access token."""
    try:
        payload = jwt.decode(
            token, 
            settings.SECRET_KEY, 
            algorithms=[settings.ALGORITHM]
        )
        return payload
    except JWTError:
        return None


async def get_current_user(token: str = Depends(oauth2_scheme)) -> Any:
    """Get current user from JWT token."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    payload = decode_access_token(token)
    if payload is None:
        raise credentials_exception
    
    user_id: int = payload.get("sub")
    if user_id is None:
        raise credentials_exception
    
    # User lookup will be done in the service layer
    return {"id": user_id}


def is_private_ip(host: str) -> bool:
    """Check if an IP address or hostname resolves to a private/internal IP."""
    try:
        # Check if it's already an IP address
        ip = ipaddress.ip_address(host)
        return ip.is_private or ip.is_loopback or ip.is_link_local or ip.is_reserved
    except ValueError:
        # It's a hostname, resolve it
        try:
            resolved_ips = socket.gethostbyname_ex(host)[2]
            for ip_str in resolved_ips:
                ip = ipaddress.ip_address(ip_str)
                if ip.is_private or ip.is_loopback or ip.is_link_local or ip.is_reserved:
                    return True
            return False
        except socket.gaierror:
            # Cannot resolve, treat as potentially dangerous
            return True


def validate_url(url: str) -> bool:
    """
    Validate a URL for safe crawling.
    Prevents SSRF attacks by blocking private/internal IPs.
    """
    try:
        parsed = urlparse(url)
        
        # Must have http or https scheme
        if parsed.scheme not in ["http", "https"]:
            return False
        
        # Must have a valid host
        if not parsed.hostname:
            return False
        
        # Block private IPs if configured
        if settings.BLOCK_PRIVATE_IPS:
            if is_private_ip(parsed.hostname):
                return False
        
        # Block localhost variations
        blocked_hosts = [
            "localhost", 
            "127.0.0.1", 
            "::1", 
            "0.0.0.0",
            "internal",
            "metadata.google.internal",
            "169.254.169.254"  # AWS metadata
        ]
        
        if parsed.hostname.lower() in blocked_hosts:
            return False
        
        # Block .local and .internal domains
        if parsed.hostname.endswith((".local", ".internal", ".lan")):
            return False
        
        return True
        
    except Exception:
        return False


def check_url_safety(url: str) -> None:
    """
    Check URL safety and raise HTTPException if unsafe.
    Use this in API endpoints before processing URLs.
    """
    if not validate_url(url):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or unsafe URL. Private/internal URLs are not allowed."
        )
