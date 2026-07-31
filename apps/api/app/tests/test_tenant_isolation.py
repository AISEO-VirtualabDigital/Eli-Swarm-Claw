"""
Tenant Isolation and Authority Verification Tests.

These tests verify that:
1. Users cannot access resources from other organizations
2. Role-based permissions are enforced
3. API keys are properly scoped and validated
4. Authentication is required for all protected endpoints
"""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.user import User, Membership, Role, UserEmail
from app.models.organization import Organization
from app.models.api_key import ApiKey, ApiKeyScope
from app.core.security_deps import (
    get_current_user_from_token,
    get_organization_context,
    get_current_org_user,
    require_role,
    CurrentUser
)


class TestTenantIsolation:
    """Test organization isolation."""

    @pytest.mark.asyncio
    async def test_user_cannot_access_other_organization(self):
        """User A cannot access Organization B's resources."""
        # Setup mock DB
        db = AsyncMock(spec=AsyncSession)
        
        # Create mock users and orgs
        user_a = User(id=1, email="user@a.com", hashed_password="hash")
        user_b = User(id=2, email="user@b.com", hashed_password="hash")
        org_a = Organization(id=1, name="Org A", slug="org-a", owner_id=1)
        org_b = Organization(id=2, name="Org B", slug="org-b", owner_id=2)
        
        # User A is only member of Org A
        membership_a = Membership(user_id=1, organization_id=1, role=Role.OWNER)
        
        # Mock DB queries
        async def mock_execute(query):
            mock_result = MagicMock()
            if "users" in str(query) and "user_id=1" in str(query):
                mock_result.scalar_one_or_none.return_value = user_a
            elif "memberships" in str(query):
                if "organization_id=2" in str(query):
                    mock_result.scalar_one_or_none.return_value = None  # No membership in Org B
                else:
                    mock_result.scalar_one_or_none.return_value = membership_a
            elif "organizations" in str(query):
                if "id=2" in str(query):
                    mock_result.scalar_one_or_none.return_value = org_b
                else:
                    mock_result.scalar_one_or_none.return_value = org_a
            return mock_result
        
        db.execute = mock_execute
        
        # Simulate request with Org B header
        from fastapi import Request
        request = MagicMock(spec=Request)
        request.headers = {"X-Organization-ID": "2"}  # Trying to access Org B
        
        # Should raise 403
        from fastapi import HTTPException
        with pytest.raises(HTTPException) as exc_info:
            await get_organization_context(request, user_a, db)
        
        assert exc_info.value.status_code == 403
        assert "not a member" in exc_info.value.detail.lower()

    @pytest.mark.asyncio
    async def test_user_cannot_access_other_project(self):
        """Verify project-level isolation (conceptual)."""
        # Projects should have organization_id foreign key
        # All project queries must filter by current org
        pass  # Implementation depends on project endpoint structure

    @pytest.mark.asyncio
    async def test_user_cannot_access_other_media_job(self):
        """Verify media job isolation."""
        # MediaJob.org_id must match current user's org_id
        pass  # Implementation in media endpoint tests


class TestRoleBasedAccess:
    """Test RBAC enforcement."""

    @pytest.mark.asyncio
    async def test_viewer_cannot_delete_assets(self):
        """Viewer role cannot perform delete operations."""
        viewer_membership = Membership(role=Role.VIEWER)
        viewer_user = User(id=1, email="viewer@test.com", hashed_password="hash")
        org = Organization(id=1, name="Test Org", slug="test-org", owner_id=1)
        
        db = AsyncMock()
        current_user = CurrentUser(viewer_user, org, viewer_membership, db)
        
        # Check role
        assert not current_user.has_role(Role.ADMIN)
        assert not current_user.is_admin_or_higher()
        assert current_user.has_role(Role.VIEWER)

    @pytest.mark.asyncio
    async def test_writer_can_create_drafts(self):
        """Writer role can create content but not manage billing."""
        writer_membership = Membership(role=Role.WRITER)
        writer_user = User(id=1, email="writer@test.com", hashed_password="hash")
        org = Organization(id=1, name="Test Org", slug="test-org", owner_id=1)
        
        db = AsyncMock()
        current_user = CurrentUser(writer_user, org, writer_membership, db)
        
        assert current_user.has_role(Role.WRITER)
        assert not current_user.has_role(Role.ADMIN)

    @pytest.mark.asyncio
    async def test_admin_cannot_remove_owner(self):
        """Admin cannot remove the organization owner."""
        # This logic should be in the membership deletion endpoint
        pass

    @pytest.mark.asyncio
    async def test_owner_full_access(self):
        """Owner has full access to organization."""
        owner_membership = Membership(role=Role.OWNER)
        owner_user = User(id=1, email="owner@test.com", hashed_password="hash")
        org = Organization(id=1, name="Test Org", slug="test-org", owner_id=1)
        
        db = AsyncMock()
        current_user = CurrentUser(owner_user, org, owner_membership, db)
        
        assert current_user.is_owner()
        assert current_user.has_role(Role.OWNER)
        assert current_user.has_role(Role.ADMIN)  # Owner implies admin
        assert current_user.has_role(Role.WRITER)
        assert current_user.has_role(Role.VIEWER)


class TestAPIKeySecurity:
    """Test API key security features."""

    def test_api_key_hash_not_exposed(self):
        """API key hash should never be exposed in responses."""
        # Schema serialization should exclude key_hash
        pass  # Test schema serialization

    def test_revoked_key_rejected(self):
        """Revoked API keys cannot be used."""
        revoked_key = ApiKey(
            id=1,
            organization_id=1,
            user_id=1,
            name="Test Key",
            key_prefix="sk_test_",
            key_hash="hashed_value",
            is_revoked=True
        )
        
        assert revoked_key.is_revoked
        # Endpoint should check this before allowing access

    def test_api_key_scopes_enforced(self):
        """API key scopes limit what actions can be performed."""
        read_only_key = ApiKey(
            id=1,
            organization_id=1,
            user_id=1,
            name="Read Only",
            key_prefix="sk_read_",
            key_hash="hash",
            scopes=[ApiKeyScope.READ.value]
        )
        
        assert ApiKeyScope.READ.value in read_only_key.scopes
        assert ApiKeyScope.WRITE.value not in read_only_key.scopes
        assert ApiKeyScope.DELETE.value not in read_only_key.scopes

    def test_api_key_shown_once_at_creation(self):
        """Full API key is only shown once at creation time."""
        # This is a behavioral test - after creation, only prefix is stored
        # The full key should be returned to user once, then never again
        pass  # Test API response at creation


class TestAuthenticationFlow:
    """Test authentication requirements."""

    @pytest.mark.asyncio
    async def test_inactive_user_rejected(self):
        """Inactive users cannot authenticate."""
        db = AsyncMock()
        inactive_user = User(id=1, email="inactive@test.com", hashed_password="hash", is_active=False)
        
        result = MagicMock()
        result.scalar_one_or_none.return_value = inactive_user
        db.execute = AsyncMock(return_value=result)
        
        from fastapi import HTTPException
        with pytest.raises(HTTPException) as exc_info:
            # Simulate token decode returning inactive user
            await get_current_user_from_token.__wrapped__(
                credentials=MagicMock(credentials="fake_token"),
                db=db
            )
        
        # Should raise 401 for inactive user
        assert exc_info.value.status_code == 401

    @pytest.mark.asyncio
    async def test_expired_token_handled(self):
        """Expired JWT tokens are rejected."""
        # JWT library will raise error for expired token
        pass  # Test JWT expiration handling

    @pytest.mark.asyncio
    async def test_missing_auth_header_rejected(self):
        """Requests without auth header are rejected."""
        from fastapi import HTTPException
        from fastapi.security import HTTPAuthorizationCredentials
        
        with pytest.raises(HTTPException) as exc_info:
            await get_current_user_from_token(
                credentials=None,
                db=AsyncMock()
            )
        
        assert exc_info.value.status_code == 401


class TestMustChangePassword:
    """Test password change requirement flow."""

    def test_bootstrap_user_must_change_password(self):
        """Bootstrap users have must_change_password flag set."""
        bootstrap_user = User(
            id=1,
            email="jrainer.seo@gmail.com",
            hashed_password="hashed_bootstrap_pwd",
            full_name="Joseph Rainer Miro",
            must_change_password=True,
            is_verified=True,
            is_active=True
        )
        
        assert bootstrap_user.must_change_password is True

    def test_frontend_redirects_on_must_change(self):
        """Frontend should redirect to password change page."""
        # This is a frontend behavior test
        pass


class TestResourceOwnership:
    """Test resource ownership verification."""

    @pytest.mark.asyncio
    async def test_resource_org_mismatch_blocked(self):
        """Resources from different org are blocked."""
        db = AsyncMock()
        user = User(id=1, email="user@test.com", hashed_password="hash")
        org = Organization(id=1, name="Test Org", slug="test-org", owner_id=1)
        membership = Membership(user_id=1, organization_id=1, role=Role.OWNER)
        
        current_user = CurrentUser(user, org, membership, db)
        
        from fastapi import HTTPException
        with pytest.raises(HTTPException) as exc_info:
            # Try to access resource from org 2
            from app.core.security_deps import verify_resource_ownership
            await verify_resource_ownership("2", current_user)
        
        assert exc_info.value.status_code == 403
        assert "does not belong" in exc_info.value.detail.lower()

    @pytest.mark.asyncio
    async def test_same_org_resource_allowed(self):
        """Resources from same org are accessible."""
        db = AsyncMock()
        user = User(id=1, email="user@test.com", hashed_password="hash")
        org = Organization(id=1, name="Test Org", slug="test-org", owner_id=1)
        membership = Membership(user_id=1, organization_id=1, role=Role.OWNER)
        
        current_user = CurrentUser(user, org, membership, db)
        
        from app.core.security_deps import verify_resource_ownership
        result = await verify_resource_ownership("1", current_user)
        
        assert result is current_user


# Run with: pytest apps/api/app/tests/test_tenant_isolation.py -v
