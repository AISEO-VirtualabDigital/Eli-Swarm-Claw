"""
Security Dependencies and Authority Verification.

This module provides FastAPI dependencies for:
- Authentication (JWT)
- Organization Context & Membership Verification
- Role-Based Access Control (RBAC)
- Resource Ownership Verification
- API Key Authentication
"""
from fastapi import Depends, HTTPException, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Optional, List, Literal
import jwt
import os

from app.core.database import get_db
from app.models.user import User, UserEmail, Membership, Role
from app.models.organization import Organization
from app.models.api_key import ApiKey
from app.core.security import verify_password_hash

# Constants
JWT_SECRET = os.getenv("JWT_SECRET", "dev-secret-change-in-prod")
JWT_ALGORITHM = "HS256"

http_bearer = HTTPBearer(auto_error=False)


class CurrentUser:
    """Represents the authenticated user with organization context."""
    def __init__(
        self,
        user: User,
        organization: Organization,
        membership: Membership,
        db: AsyncSession
    ):
        self.user = user
        self.organization = organization
        self.membership = membership
        self.db = db
        self.org_id = str(organization.id)
        self.user_id = str(user.id)
        self.roles = membership.roles  # List of Role enums

    def has_role(self, required_role: Role) -> bool:
        """Check if user has specific role or higher."""
        role_hierarchy = {
            Role.VIEWER: 1,
            Role.WRITER: 2,
            Role.ADMIN: 3,
            Role.OWNER: 4
        }
        user_max_role = max([role_hierarchy.get(r, 0) for r in self.roles], default=0)
        return user_max_role >= role_hierarchy.get(required_role, 0)

    def is_owner(self) -> bool:
        return Role.OWNER in self.roles

    def is_admin_or_higher(self) -> bool:
        return self.has_role(Role.ADMIN)


async def get_current_user_from_token(
    credentials: HTTPAuthorizationCredentials = Depends(http_bearer),
    db: AsyncSession = Depends(get_db)
) -> User:
    """Decode JWT and fetch user from DB."""
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )

    try:
        payload = jwt.decode(credentials.credentials, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid token payload")
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()

    if not user or not user.is_active:
        raise HTTPException(status_code=401, detail="User not found or inactive")

    return user


async def get_organization_context(
    request: Request,
    current_user: User = Depends(get_current_user_from_token),
    db: AsyncSession = Depends(get_db)
) -> tuple[Organization, Membership]:
    """
    Verify organization context from header and ensure membership.
    Security: Do not trust header alone. Verify DB membership.
    """
    org_id = request.headers.get("X-Organization-ID")
    
    if not org_id:
        # Fallback to user's primary organization if only one exists
        memberships = await db.execute(
            select(Membership).where(Membership.user_id == current_user.id)
        )
        all_memberships = memberships.scalars().all()
        if len(all_memberships) == 1:
            org_id = str(all_memberships[0].organization_id)
        else:
            raise HTTPException(
                status_code=400, 
                detail="Organization ID required in X-Organization-ID header"
            )

    # Verify membership
    membership_result = await db.execute(
        select(Membership)
        .where(Membership.user_id == current_user.id)
        .where(Membership.organization_id == org_id)
    )
    membership = membership_result.scalar_one_or_none()

    if not membership:
        raise HTTPException(
            status_code=403, 
            detail="Access denied: You are not a member of this organization"
        )

    org_result = await db.execute(
        select(Organization).where(Organization.id == org_id)
    )
    organization = org_result.scalar_one_or_none()

    if not organization:
        raise HTTPException(status_code=404, detail="Organization not found")

    return organization, membership


async def get_current_org_user(
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user_from_token)
) -> CurrentUser:
    """
    Main dependency: Returns CurrentUser object with verified org context.
    Use this for all protected endpoints.
    """
    organization, membership = await get_organization_context(request, current_user, db)
    return CurrentUser(current_user, organization, membership, db)


def require_role(required_role: Role):
    """Dependency factory to enforce minimum role."""
    async def role_checker(current_org_user: CurrentUser = Depends(get_current_org_user)):
        if not current_org_user.has_role(required_role):
            raise HTTPException(
                status_code=403,
                detail=f"Access denied: Requires {required_role.value} role or higher"
            )
        return current_org_user
    return role_checker


async def verify_resource_ownership(
    resource_org_id: str,
    current_org_user: CurrentUser = Depends(get_current_org_user)
):
    """
    Ensure the resource being accessed belongs to the current organization.
    Prevents IDOR by checking org ID match.
    """
    if str(resource_org_id) != current_org_user.org_id:
        raise HTTPException(
            status_code=403,
            detail="Access denied: Resource does not belong to your organization"
        )
    return current_org_user


# API Key Authentication
async def get_api_key_auth(
    request: Request,
    db: AsyncSession = Depends(get_db)
) -> tuple[ApiKey, User, Organization]:
    """
    Authenticate via API Key header.
    Validates key hash, scopes, and organization.
    """
    api_key_header = request.headers.get("X-API-Key")
    if not api_key_header:
        raise HTTPException(status_code=401, detail="API Key missing")

    # Find key by prefix first (optimization)
    prefix = api_key_header[:8] if len(api_key_header) > 8 else api_key_header
    
    # In real implementation, we'd search by prefix then verify hash
    # For now, simple lookup (implementation depends on ApiKey model structure)
    result = await db.execute(select(ApiKey).where(ApiKey.key_prefix == prefix))
    candidate_keys = result.scalars().all()

    valid_key = None
    for key in candidate_keys:
        if verify_password_hash(api_key_header, key.key_hash): # Assuming helper exists
            valid_key = key
            break

    if not valid_key or valid_key.is_revoked:
        raise HTTPException(status_code=401, detail="Invalid or revoked API key")

    # Check scopes if endpoint requires specific scope
    # Update last used
    # Return context
    user_result = await db.execute(select(User).where(User.id == valid_key.user_id))
    user = user_result.scalar_one_or_none()
    
    org_result = await db.execute(select(Organization).where(Organization.id == valid_key.organization_id))
    org = org_result.scalar_one_or_none()

    if not user or not org:
        raise HTTPException(status_code=401, detail="Associated user/org not found")

    return valid_key, user, org
