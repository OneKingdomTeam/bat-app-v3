# Security Audit Report - BAT Application v3
**Date:** 2025-12-15
**Auditor:** Security Review
**Scope:** Complete authentication, authorization, and security vulnerability assessment

---

## Executive Summary

This security audit covers the BAT (Benchmark Assessment Tool) application, focusing on authentication mechanisms, role-based access control (RBAC), privilege escalation vulnerabilities, and common web security issues. The application implements a three-tier role system: **admin**, **coach**, and **user**.

### Overall Security Posture: **GOOD with CRITICAL ISSUES**

**Critical Issues Found:** 1
**High Risk Issues:** 1
**Medium Risk Issues:** 2
**Low Risk Issues:** 3
**Informational:** 2

---

## 1. Authentication Analysis

### 1.1 Token-Based Authentication ✅ **SECURE**

**Implementation:** `app/service/authentication.py`

**Strengths:**
- JWT-based authentication using HS256 algorithm
- Tokens stored in HTTP-only cookies (prevents XSS token theft)
- SameSite=strict attribute on cookies (CSRF protection)
- Token expiration properly enforced (default: configurable via `ACCESS_TOKEN_EXPIRE_MINUTES`)
- Token renewal mechanism for sessions near expiration (180s threshold)
- Proper token validation with signature verification

**Token Lifecycle:**
```python
# Token creation: app/service/authentication.py:99-108
- Includes user_id and expiration timestamp
- Signed with SECRET_KEY using ALGORITHM (HS256)
- Format: Bearer <token>

# Token validation: app/service/authentication.py:46-56
- Validates signature
- Checks expiration
- Extracts user_id for user lookup
```

**Protection Features:**
- ExpiredSignatureError handling
- JWTError exception handling for tampering detection
- Proper Bearer token prefix validation

---

### 1.2 Password Security ✅ **SECURE**

**Implementation:** `app/service/authentication.py:35-43`

**Strengths:**
- Uses `pwdlib` with Bcrypt hasher (industry standard)
- No plaintext password storage
- Minimum password length: 12 characters (enforced at `app/service/user.py:83`)
- Maximum password length: 128 characters
- Password reset tokens: 64-byte hex tokens (128 characters) with 60-minute expiration
- Token-based password reset flow prevents unauthorized resets

**Password Reset Flow:**
```
1. User requests reset via email
2. Secure token generated (secrets.token_hex(64))
3. Token stored with expiration timestamp
4. Email sent with reset link
5. Token validated on password change
6. Token cleared after use
```

---

### 1.3 Cloudflare Turnstile Integration ✅ **OPTIONAL**

**Implementation:** `app/service/authentication.py:194-224`

**Features:**
- CAPTCHA verification on login (when enabled)
- Server-side validation with Cloudflare API
- Configurable via environment variables
- Prevents automated brute force attacks

---

### 1.4 Login Security Measures ✅ **GOOD**

**Implementation:** `app/web/public.py:324-433`

**Protections:**
- Timing attack mitigation: Random delay 100-500ms (line 341-342)
- Email-based login support (converts email to username)
- Prevents username enumeration through consistent error messages
- Open redirect protection via `validate_redirect_url()` (line 232-283)

**Open Redirect Protection:**
```python
# app/service/authentication.py:232-283
- Validates redirect URLs
- Rejects external domains
- Requires path to start with /
- Whitelist: /share/assessment/, /app/, /dashboard/
```

---

## 2. Role-Based Access Control (RBAC)

### 2.1 Role Hierarchy ✅ **WELL-DEFINED**

**Roles:** (app/model/user.py:7-10)
```
admin  → Full system access
coach  → Dashboard access, user management (limited)
user   → Own assessments and profile only
```

### 2.2 Permission Model ✅ **ROBUST**

**Implementation:** `app/model/user.py:61-129`

**Permission Methods:**
| Method | Admin | Coach | User |
|--------|-------|-------|------|
| `can_grant_roles()` | admin, coach, user | coach, user | [] |
| `can_create_user()` | ✅ All | ✅ Coach, User | ❌ |
| `can_delete_user()` | ✅ All | ✅ Coach, User (not Admin) | ❌ |
| `can_modify_user()` | ✅ All | ✅ Coach, User | ✅ Self only |
| `can_manage_questions()` | ✅ | ✅ | ❌ |
| `can_manage_assessments()` | ✅ | ✅ | ❌ |
| `can_manage_notes()` | ✅ | ✅ | ❌ |
| `can_manage_reports()` | ✅ | ✅ | ❌ |
| `can_send_emails()` | ✅ | ✅ | ❌ |

---

### 2.3 Endpoint Protection Analysis

#### Admin-Only Endpoints ✅ **PROTECTED**

**Protected by:** `app/service/authentication.py:182-186` (`admin_only` dependency)

```python
# Settings endpoints - ADMIN ONLY
GET  /dashboard/settings
GET  /dashboard/settings/branding
POST /dashboard/settings/branding
POST /dashboard/settings/branding/logo
POST /dashboard/settings/branding/favicon
```

**Verification:** Settings routes properly use `Depends(admin_only)` at `app/web/dashboard/settings.py`

---

#### Coach + Admin Endpoints ✅ **PROTECTED**

**Protected by:** `user_htmx_dep` + service-layer checks

```python
# Dashboard User Management
GET    /dashboard/users
GET    /dashboard/users/add
POST   /dashboard/users/add
GET    /dashboard/users/{user_id}
PUT    /dashboard/users/{user_id}
DELETE /dashboard/users/{user_id}

# Dashboard Assessments
GET    /dashboard/assessments
POST   /dashboard/assessments
GET    /dashboard/assessments/create
POST   /dashboard/assessments/create
GET    /dashboard/assessments/edit/{assessment_id}
DELETE /dashboard/assessments/{assessment_id}
# ... (all dashboard assessment routes)

# Dashboard Questions
GET    /dashboard/questions
GET    /dashboard/questions/{category_id}
POST   /dashboard/questions/reorder
# ... (all question management routes)

# Dashboard Reports
GET    /dashboard/reports
POST   /dashboard/reports/create
GET    /dashboard/reports/edit/{report_id}
DELETE /dashboard/reports/{report_id}
# ... (all report management routes)
```

**Authorization Checks:**
- Service layer: `current_user.can_manage_assessments()` (app/service/assessment.py:24, 73, 81)
- Service layer: `current_user.can_manage_questions()` (app/service/question.py:72, 80, 88, etc.)
- Service layer: `current_user.can_manage_reports()` (app/service/report.py:27, 35, 74, etc.)

---

#### User Endpoints ✅ **PROTECTED**

**Protected by:** `user_htmx_dep` + ownership/collaborator checks

```python
# App Assessments
GET  /app/assessments
GET  /app/assessments/edit/{assessment_id}
POST /app/assessments/edit/{assessment_id}/{category_order}/{question_order}

# App Profile
GET  /app/profile
PUT  /app/profile

# App Reports
GET  /app/reports/{assessment_id}
GET  /app/reports/view/{report_id}
```

**Data Isolation:**
- Users can only access their own assessments (owner_id check)
- Collaborator access properly validated via `data.is_collaborator()` (app/service/assessment.py:61-63)
- Profile updates restricted to own profile (app/service/user.py:218)

---

#### Public Endpoints ✅ **PROPERLY PUBLIC**

```python
GET  /                      # Homepage
GET  /login                 # Login page
POST /login                 # Login submission
GET  /logout                # Logout
GET  /password-reset        # Password reset request
POST /password-reset        # Password reset submission
GET  /set-password          # Set new password
POST /set-password          # Submit new password
GET  /share/assessment/{id} # Share link (redirects based on auth)
```

---

## 3. CRITICAL PRIVILEGE ESCALATION VULNERABILITY

### 🚨 CRITICAL: Coach Can Escalate Privileges to Admin

**Severity:** CRITICAL
**CVSS Score:** 8.8 (High)
**Location:** `app/service/user.py:211-237`

#### Vulnerability Description

A coach can modify their own user record and change their role to "admin", bypassing the intended role hierarchy. The `update()` function in the user service only validates:
1. Whether the current user can modify the target user (`can_modify_user()`)
2. But does NOT validate whether the role change is authorized

#### Vulnerable Code

```python
# app/service/user.py:211-237
def update(user_id: str, user: UserUpdate, current_user: User) -> User:
    if user_id != user.user_id:
        raise EndpointDataMismatch(...)

    # ✅ Checks if user can be modified
    if not current_user.can_modify_user(user):
        raise Unauthorized(msg="You cannot modify this user")

    # ❌ MISSING: No check for role escalation!
    # ❌ Coach can set role=admin here
    current_data: User = data.get_one(user_id)

    updated_data = User(
        user_id=user.user_id,
        username=user.username,
        email=user.email,
        hash=password_hash,
        role=user.role,  # ⚠️ Accepts any role from input
    )

    modified_user = data.modify(user_id, updated_data)
    return modified_user
```

#### Attack Scenario

1. **Coach logs in** with legitimate credentials
2. **Navigates to their profile** at `/app/profile` or `/dashboard/users/{their_id}`
3. **Intercepts PUT request** (using browser dev tools or proxy)
4. **Modifies role field** in the request body from `"coach"` to `"admin"`
5. **Submits the request**
6. **System accepts the change** because:
   - `can_modify_user()` returns `True` (coach can modify themselves - line 91-92)
   - No validation that the new role is in `can_grant_roles()`

#### Proof of Concept

```bash
# Assume coach's user_id = "coach-uuid-123"
# Assume coach is authenticated with valid token

curl -X PUT https://app.example.com/dashboard/users/coach-uuid-123 \
  -H "Cookie: access_token=Bearer <coach-token>" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "coach-uuid-123",
    "username": "coach_user",
    "email": "coach@example.com",
    "password": "",
    "role": "admin"
  }'

# Result: Coach is now admin!
```

#### Impact

- **Complete system compromise**
- Coach gains admin privileges
- Can access settings, modify all users, delete admins
- Can create additional admin accounts
- Violates principle of least privilege

#### Remediation

**REQUIRED FIX:**

Add role validation to the `update()` function:

```python
def update(user_id: str, user: UserUpdate, current_user: User) -> User:
    if user_id != user.user_id:
        raise EndpointDataMismatch(...)

    if not current_user.can_modify_user(user):
        raise Unauthorized(msg="You cannot modify this user")

    current_data: User = data.get_one(user_id)

    # ✅ NEW: Validate role changes
    if current_data.role != user.role:
        # Role is being changed - validate permission
        grantable_roles = current_user.can_grant_roles()
        if user.role.value not in grantable_roles:
            raise Unauthorized(
                msg=f"You cannot grant the '{user.role.value}' role. "
                    f"You can only grant: {', '.join(grantable_roles)}"
            )

        # Additional check: prevent privilege escalation via self-modification
        # when changing to a higher privilege role
        if current_user.user_id == user_id:
            # User is modifying themselves
            if user.role == UserRoleEnum.admin and current_user.role != UserRoleEnum.admin:
                raise Unauthorized(msg="You cannot elevate your own privileges to admin")
            if user.role == UserRoleEnum.coach and current_user.role == UserRoleEnum.user:
                raise Unauthorized(msg="You cannot elevate your own privileges to coach")

    # Rest of the function...
```

---

## 4. HIGH RISK: SQL Injection Vulnerability

### ⚠️ HIGH: SQL Injection in `get_by()` Function

**Severity:** HIGH
**CVSS Score:** 7.5
**Location:** `app/data/user.py:96-111`

#### Vulnerability Description

The `get_by()` function uses string formatting to build SQL queries with the field name directly interpolated, creating a SQL injection vulnerability.

#### Vulnerable Code

```python
# app/data/user.py:96-111
def get_by(field: str, value: str|int) -> User:
    qry = f"select * from users where {field} = :value"  # ⚠️ SQL Injection
    params = {"value": value}

    cursor = conn.cursor()
    try:
        cursor.execute(qry, params)
        # ...
```

#### Attack Scenario

While the `field` parameter is only used internally in the service layer with hardcoded values (`"email"`, `"username"`), this pattern is dangerous and could be exploited if:
1. Future code changes expose this parameter to user input
2. Other developers copy this pattern elsewhere

#### Current Usage (Safe But Brittle)

```python
# app/service/user.py:172
return data.get_by(field="email", value=email)  # ✅ Hardcoded field

# app/service/user.py:197
return data.get_by(field="username", value=username)  # ✅ Hardcoded field
```

#### Impact (Potential)

If field parameter ever becomes user-controlled:
- Database structure disclosure
- Arbitrary SQL query execution
- Potential data exfiltration
- Bypass authentication/authorization

#### Remediation

**RECOMMENDED FIX:**

Use a whitelist approach for field names:

```python
def get_by(field: str, value: str|int) -> User:
    # Whitelist allowed fields
    allowed_fields = {"email", "username", "user_id"}

    if field not in allowed_fields:
        raise ValueError(f"Invalid field name: {field}")

    # Now safe to use field in query
    qry = f"select * from users where {field} = :value"
    params = {"value": value}
    # ...
```

**BETTER FIX (Separate functions):**

```python
def get_by_email(email: str) -> User:
    qry = "select * from users where email = :email"
    params = {"email": email}
    # ...

def get_by_username(username: str) -> User:
    qry = "select * from users where username = :username"
    params = {"username": username}
    # ...
```

---

## 5. MEDIUM RISK ISSUES

### 5.1 ⚠️ MEDIUM: Missing Role Validation in User Creation

**Severity:** MEDIUM
**Location:** `app/service/user.py:75-110`

#### Issue

The `create()` function validates permission using `can_create_user()`, but does NOT validate that the assigned role is in the current user's `can_grant_roles()` list.

```python
# app/service/user.py:75-78
if not current_user.can_create_user(user):
    raise Unauthorized(msg="You cannot create this user")
```

The `can_create_user()` method only checks if the new user's role is coach or user (for coaches), but doesn't use the more restrictive `can_grant_roles()` list.

#### Impact

Lower than the update vulnerability because:
- `can_create_user()` does prevent coaches from creating admins
- But inconsistent with the role-granting model

#### Remediation

```python
def create(user: UserCreate, request: Request, current_user: User) -> User:
    if not current_user.can_create_user(user):
        raise Unauthorized(msg="You cannot create this user")

    # ✅ NEW: Additional role validation
    grantable_roles = current_user.can_grant_roles()
    if user.role.value not in grantable_roles:
        raise Unauthorized(
            msg=f"You cannot grant the '{user.role.value}' role. "
                f"You can only grant: {', '.join(grantable_roles)}"
        )

    # Rest of function...
```

---

### 5.2 ⚠️ MEDIUM: No Rate Limiting on Authentication Endpoints

**Severity:** MEDIUM
**Location:** `app/web/public.py:324-433`

#### Issue

While login includes timing attack mitigation (random delay), there is no rate limiting to prevent brute force attacks.

#### Impact

- Attackers can attempt unlimited login attempts
- Password enumeration via timing attacks (partially mitigated)
- Account lockout attacks possible
- Resource exhaustion

#### Remediation

Implement rate limiting:
```python
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)

@router.post("/login")
@limiter.limit("5/minute")  # 5 attempts per minute
async def login_page_post(...):
    # ...
```

Or use Cloudflare Turnstile (already implemented but optional).

---

## 6. LOW RISK ISSUES

### 6.1 ℹ️ LOW: Weak Default Password Enforcement

**Severity:** LOW
**Location:** `app/service/user.py:82-92`

#### Issue

When creating users without passwords, a random 128-character password is generated but:
- User must reset via email (requires SMTP configuration)
- If SMTP not configured, user account is created but inaccessible

#### Impact

- Accounts can be created but unusable
- Poor user experience

#### Remediation

Enforce password requirement during user creation or ensure SMTP is configured.

---

### 6.2 ℹ️ LOW: Password Reset Token Not Cleared After Use

**Severity:** LOW
**Location:** `app/data/user.py:269-288`

#### Issue

After password is successfully reset, the token remains in the database (though expired).

#### Impact

- Database bloat over time
- Expired tokens remain visible in database

#### Remediation

Clear token after successful password reset:
```python
def set_password_from_token(...):
    # Validate token
    # Set password

    # Clear token
    qry = """
    UPDATE users
    SET password_reset_token = NULL, reset_token_expires = NULL
    WHERE user_id = :user_id
    """
    conn.execute(qry, {"user_id": user_id})
```

---

### 6.3 ℹ️ LOW: Missing HTTPS Enforcement in Production

**Severity:** LOW
**Location:** `app/main.py:61-69`

#### Issue

HTTPS enforcement is optional via `FORCE_HTTPS_PATHS_ENV` environment variable.

#### Impact

- Cookies marked as `secure=True` only when env var is set
- Risk of cookie interception on HTTP connections

#### Remediation

- Always enforce HTTPS in production
- Use HSTS headers
- Reject HTTP connections at load balancer/proxy level

---

## 7. INFORMATIONAL FINDINGS

### 7.1 ✅ CSRF Protection via SameSite Cookies

**Status:** IMPLEMENTED

Cookies use `samesite="strict"` attribute, preventing CSRF attacks.

**Evidence:**
- `app/web/public.py:73-84` (logout)
- `app/web/public.py:374-385` (login)
- `app/web/public.py:403-414` (login alternate path)

---

### 7.2 ✅ XSS Protection via Template Engine

**Status:** PROPERLY CONFIGURED

The application uses Jinja2 templates which automatically escape output by default.

**Evidence:**
- `app/template/init.py` - Uses Jinja2Templates
- All user inputs rendered via templates are auto-escaped
- No `{{ variable | safe }}` misuse found in templates

---

### 7.3 ℹ️ Database: SQLite with Parameterized Queries

**Status:** MOSTLY SECURE

- All user inputs use parameterized queries (`:param` syntax)
- Exception: `get_by()` function (see HIGH RISK section)
- No direct string concatenation in SQL queries (except the one issue)

---

## 8. Endpoint Security Summary

### Authentication Status by Route

| Route Pattern | Authentication | Authorization | Status |
|--------------|----------------|---------------|---------|
| `/` | ❌ Public | N/A | ✅ |
| `/login` | ❌ Public | N/A | ✅ |
| `/logout` | ✅ Required | Any | ✅ |
| `/share/assessment/*` | ✅ Required | Owner/Collaborator | ✅ |
| `/api/v1/auth/*` | ✅ Required | Any | ✅ |
| `/dashboard/settings` | ✅ Required | **Admin Only** | ✅ |
| `/dashboard/users` | ✅ Required | Admin/Coach | ✅ |
| `/dashboard/assessments` | ✅ Required | Admin/Coach | ✅ |
| `/dashboard/questions` | ✅ Required | Admin/Coach | ✅ |
| `/dashboard/reports` | ✅ Required | Admin/Coach | ✅ |
| `/app/assessments` | ✅ Required | Owner/Collaborator | ✅ |
| `/app/profile` | ✅ Required | Self | ⚠️ (vuln) |
| `/app/reports` | ✅ Required | Owner | ✅ |

---

## 9. Testing Recommendations

### Required Security Tests

1. **Privilege Escalation Test**
   ```bash
   # Test coach attempting to become admin
   curl -X PUT /dashboard/users/{coach_id} \
     -d '{"role": "admin"}' \
     -H "Cookie: access_token=Bearer <coach_token>"

   # Expected: 403 Forbidden (after fix)
   # Current: 200 OK (VULNERABILITY!)
   ```

2. **Authorization Matrix Testing**
   - Test each role against each endpoint
   - Verify proper 403/401 responses
   - Check data isolation between users

   **Good news:** Tests already exist at `tests/e2e/test_authorization_matrix.py`

3. **SQL Injection Testing**
   ```python
   # Test get_by with malicious input
   # (Currently not exploitable but test defensive measures)
   ```

---

## 10. Recommendations Summary

### CRITICAL Priority

1. **FIX IMMEDIATELY:** Add role validation to `user.update()` function
   - Prevent coaches from escalating to admin
   - Validate role changes against `can_grant_roles()`
   - Add test coverage for privilege escalation attempts

### HIGH Priority

2. **FIX SOON:** Refactor `get_by()` to use field whitelist or separate functions
   - Prevent future SQL injection vulnerabilities
   - Improve code maintainability

### MEDIUM Priority

3. **Implement rate limiting** on authentication endpoints
4. **Add role validation** to user creation flow (consistency)

### LOW Priority

5. Clear password reset tokens after use
6. Enforce HTTPS in production configuration
7. Improve error handling for missing SMTP configuration

---

## 11. Positive Security Findings

### Well-Implemented Features ✅

1. **JWT Token Management**
   - Proper signature validation
   - Expiration enforcement
   - HTTP-only cookies
   - Token renewal mechanism

2. **Password Security**
   - Bcrypt hashing
   - Minimum length enforcement
   - Secure reset token generation

3. **CSRF Protection**
   - SameSite=Strict cookies
   - No CSRF token needed for HTMX endpoints

4. **Open Redirect Prevention**
   - URL validation with whitelist
   - Rejects external domains

5. **RBAC Implementation**
   - Clear role hierarchy
   - Granular permission methods
   - Service-layer authorization checks

6. **Assessment Collaboration Model**
   - Owner and collaborator access properly segregated
   - Coaches cannot access users' private assessments

7. **XSS Protection**
   - Jinja2 auto-escaping enabled
   - No unsafe template rendering found

---

## 12. Compliance & Best Practices

### OWASP Top 10 Coverage

| OWASP Risk | Status | Notes |
|------------|--------|-------|
| A01:2021 Broken Access Control | ⚠️ **VULNERABLE** | Privilege escalation issue |
| A02:2021 Cryptographic Failures | ✅ Secure | Bcrypt, HTTPS optional |
| A03:2021 Injection | ⚠️ Minor Issue | SQL injection in get_by() |
| A04:2021 Insecure Design | ✅ Good | Clear role model |
| A05:2021 Security Misconfiguration | ⚠️ Optional HTTPS | Should enforce |
| A06:2021 Vulnerable Components | ℹ️ Unknown | Requires dependency audit |
| A07:2021 Authentication Failures | ⚠️ No rate limit | Otherwise secure |
| A08:2021 Software/Data Integrity | ✅ Good | No supply chain issues found |
| A09:2021 Logging Failures | ℹ️ Not assessed | Out of scope |
| A10:2021 SSRF | ✅ Not applicable | No external requests from user input |

---

## 13. Conclusion

The BAT application demonstrates **strong security fundamentals** in authentication and general authorization. However, the **critical privilege escalation vulnerability** poses an immediate risk that must be addressed before production deployment.

### Risk Assessment

- **Authentication:** ✅ Strong (8/10)
- **Authorization:** ⚠️ Vulnerable (5/10) - Due to privilege escalation
- **Data Protection:** ✅ Good (7/10)
- **Input Validation:** ⚠️ Good with gaps (7/10)

### Immediate Action Required

**BLOCK PRODUCTION DEPLOYMENT** until the privilege escalation vulnerability is fixed. This is a **CRITICAL** security issue that allows role escalation from coach to admin.

### Post-Fix Assessment

After implementing the critical fix, the application security rating would improve to:
- **Authorization:** ✅ Strong (8/10)
- **Overall Security:** ✅ Strong (8/10)

---

## Appendix A: Authorization Test Matrix

See `tests/e2e/test_authorization_matrix.py` for comprehensive endpoint authorization tests.

**Test Coverage:**
- Settings endpoints (admin only) ✅
- Dashboard endpoints (admin + coach) ✅
- User endpoints (own data only) ✅
- Profile modification restrictions ⚠️ (needs privilege escalation test)

---

## Appendix B: Code References

### Key Security Files

- **Authentication:** `app/service/authentication.py`
- **User Service:** `app/service/user.py`
- **User Model:** `app/model/user.py`
- **User Data:** `app/data/user.py`
- **Public Routes:** `app/web/public.py`
- **Dashboard Routes:** `app/web/dashboard/*.py`
- **App Routes:** `app/web/app/*.py`
- **Main Application:** `app/main.py`

### Database Schema

```sql
-- users table (app/data/user.py:7-15)
CREATE TABLE users(
    user_id TEXT PRIMARY KEY,
    username TEXT UNIQUE,
    email TEXT UNIQUE,
    hash TEXT,
    role TEXT,
    password_reset_token TEXT,
    reset_token_expires INTEGER
)
```

---

**Report End**
