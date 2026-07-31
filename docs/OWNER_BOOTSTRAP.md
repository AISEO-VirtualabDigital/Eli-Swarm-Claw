# Eli Claw Initial Owner Bootstrap — Two Email Setup

## Overview

This document describes the secure bootstrap system for creating the initial owner account and organization for Eli Claw SaaS.

## Security Requirements

✅ **Password comes from environment variable only**  
✅ **Never hardcoded in source code, migrations, fixtures, or README**  
✅ **Never committed to version control**  
✅ **Never printed in logs or API responses**  

## Environment Variables

Add these to your `.env` file (not committed):

```env
# Owner Bootstrap Configuration
BOOTSTRAP_OWNER_EMAIL=jrainer.seo@gmail.com
BOOTSTRAP_OWNER_SECONDARY_EMAIL=aiseo.virtualabdigital@gmail.com
BOOTSTRAP_OWNER_NAME=Joseph Rainer Miro
BOOTSTRAP_ORG_NAME=Virtualab Digital
BOOTSTRAP_ORG_SLUG=virtualab-digital
BOOTSTRAP_PRIMARY_DOMAIN=virtualabdigital.com
BOOTSTRAP_OWNER_PASSWORD=<set-secure-password-locally>
```

### Variable Descriptions

| Variable | Required | Description |
|----------|----------|-------------|
| `BOOTSTRAP_OWNER_EMAIL` | ✅ Yes | Primary owner login email |
| `BOOTSTRAP_OWNER_SECONDARY_EMAIL` | ⚠️ Recommended | Secondary/alias email for notifications |
| `BOOTSTRAP_OWNER_NAME` | ✅ Yes | Full name of the owner |
| `BOOTSTRAP_ORG_NAME` | ✅ Yes | Organization display name |
| `BOOTSTRAP_ORG_SLUG` | ✅ Yes | URL-friendly organization identifier |
| `BOOTSTRAP_PRIMARY_DOMAIN` | ❌ Optional | Primary domain for the organization |
| `BOOTSTRAP_OWNER_PASSWORD` | ✅ Yes | Secure password (min 8 characters) |

## Database Models

### User Model Enhancements

Added fields:
- `must_change_password`: Boolean flag requiring password change on first login
- Relationship to `UserEmail` for multiple email addresses

### UserEmail Model (New)

Scalable email identity table supporting:
- Primary email
- Secondary emails
- Alias emails
- Notification emails

```python
class UserEmail(Base):
    id: int
    user_id: int
    email: str
    email_type: str  # primary, secondary, alias, notification
    is_primary: bool
    is_verified: bool
    created_at: datetime
    updated_at: datetime
```

## Bootstrap Script

### Location
```bash
/scripts/bootstrap_owner.py
```

### Usage

```bash
# Make executable (if not already)
chmod +x scripts/bootstrap_owner.py

# Run bootstrap
python scripts/bootstrap_owner.py
```

### What It Does

1. ✅ Reads owner details from environment variables
2. ✅ Validates primary email format
3. ✅ Validates secondary email format (if provided)
4. ✅ Creates owner user with primary email (if not exists)
5. ✅ Stores secondary email as verified alias
6. ✅ Hashes password securely with bcrypt
7. ✅ Creates organization (if not exists)
8. ✅ Creates owner membership
9. ✅ Assigns `owner` role with enterprise limits
10. ✅ Marks owner as active and verified
11. ✅ Sets `must_change_password = true`
12. ✅ Never prints raw password
13. ✅ Prints safe success message only

### Expected Output

```
✅ Created owner account: jrainer.seo@gmail.com
✅ Added secondary email: aiseo.virtualabdigital@gmail.com
✅ Created organization: Virtualab Digital (virtualab-digital)

============================================================
🎉 Bootstrap completed successfully!
============================================================
Organization: Virtualab Digital (virtualab-digital)
Owner: Joseph Rainer Miro <jrainer.seo@gmail.com>
Secondary Email: aiseo.virtualabdigital@gmail.com
Primary Domain: virtualabdigital.com

⚠️  Security Notice:
   - Password must be changed on first login
   - Never share your credentials
   - Store passwords in a secure password manager
============================================================
```

## First Login Flow

### Backend Behavior

When owner logs in for the first time:

1. Authenticate with email/password
2. Check `must_change_password` flag
3. If `true`, return response indicating password change required
4. Frontend redirects to password change page
5. After successful change, set `must_change_password = false`
6. Allow access to dashboard

### Frontend Implementation (Future)

```javascript
// After login
if (user.must_change_password) {
  router.push('/auth/change-password');
} else {
  router.push('/dashboard');
}
```

## Local Development Setup

### Step 1: Create .env file

```bash
cp .env.example .env
```

### Step 2: Add bootstrap configuration

Edit `.env` and add:

```env
BOOTSTRAP_OWNER_EMAIL=jrainer.seo@gmail.com
BOOTSTRAP_OWNER_SECONDARY_EMAIL=aiseo.virtualabdigital@gmail.com
BOOTSTRAP_OWNER_NAME=Joseph Rainer Miro
BOOTSTRAP_ORG_NAME=Virtualab Digital
BOOTSTRAP_ORG_SLUG=virtualab-digital
BOOTSTRAP_PRIMARY_DOMAIN=virtualabdigital.com
BOOTSTRAP_OWNER_PASSWORD=YourSecurePassword123!
```

### Step 3: Start database

```bash
docker-compose up -d postgres
```

### Step 4: Run migrations

```bash
cd backend
alembic upgrade head
```

### Step 5: Run bootstrap

```bash
python scripts/bootstrap_owner.py
```

### Step 6: Start application

```bash
docker-compose up -d
```

## Production Deployment

### VPS Deployment

For production VPS deployment:

1. **Do NOT use bootstrap script in production**
2. Create owner through secure admin panel
3. Use environment variables from secrets manager
4. Set strong password via secure channel

### Environment Variables on VPS

Use your VPS environment or secrets manager:

```bash
# /etc/eliclaw/.env or Docker secrets
export BOOTSTRAP_OWNER_PASSWORD="<generated-secure-password>"
```

### Password Generation

Generate secure password:

```bash
# Using openssl
openssl rand -base64 32

# Using Python
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

## Idempotency

The bootstrap script is **idempotent**:

- Running multiple times is safe
- Existing accounts are not modified (except linking)
- Existing organizations are preserved
- Secondary emails are not duplicated

### Re-running Bootstrap

If you need to update owner details:

```bash
# Delete existing owner (careful!)
# Then run bootstrap again
python scripts/bootstrap_owner.py
```

Or manually update through database:

```sql
-- Update organization owner
UPDATE organizations SET owner_id = <new_user_id> WHERE slug = 'virtualab-digital';
```

## Troubleshooting

### Error: BOOTSTRAP_OWNER_EMAIL is required

**Solution:** Set the environment variable in `.env` or export it:

```bash
export BOOTSTRAP_OWNER_EMAIL=jrainer.seo@gmail.com
```

### Error: Invalid email format

**Solution:** Ensure email follows standard format:

```bash
# Valid
BOOTSTRAP_OWNER_EMAIL=user@example.com

# Invalid
BOOTSTRAP_OWNER_EMAIL=user@
BOOTSTRAP_OWNER_EMAIL=example.com
```

### Error: Password must be at least 8 characters

**Solution:** Use stronger password:

```bash
# Too short
BOOTSTRAP_OWNER_PASSWORD=short

# Good
BOOTSTRAP_OWNER_PASSWORD=SecurePass123!
```

### Error: Database connection failed

**Solution:** Ensure PostgreSQL is running:

```bash
docker-compose up -d postgres
docker-compose ps
```

### Error: Table doesn't exist

**Solution:** Run migrations first:

```bash
cd backend
alembic upgrade head
```

## Audit Logging (Future)

Future enhancement will add audit log entry:

```python
audit_log = AuditLog(
    event_type="organization.bootstrap_owner_created",
    organization_id=org.id,
    user_id=user.id,
    metadata={
        "primary_email": owner_email,
        "secondary_email": owner_secondary_email,
        "organization_name": org_name,
        "created_at": datetime.utcnow()
    }
)
```

## Related Documentation

- [Environment Setup](./ENVIRONMENT_SETUP.md)
- [Database Models](./DATABASE_MODELS.md)
- [Authentication](./AUTHENTICATION.md)
- [Multi-Tenancy](./MULTITENANCY.md)
- [VPS Deployment](./VPS_DEPLOYMENT.md)
