# BAT App v3 Test Suite

## Overview

This directory contains a comprehensive test suite for the BAT (Benchmark Assessment Tool) application with a focus on authentication, authorization, and security testing.

## Test Structure

```
tests/
├── conftest.py                    # Global fixtures (DB, users, clients, mocks)
├── pytest.ini                     # Pytest configuration (in project root)
├── README.md                      # This file
├── unit/                          # Unit tests (fast, isolated)
│   ├── test_authentication.py    # JWT, password hashing (COMPLETE)
│   ├── test_user_permissions.py  # RBAC permission methods (COMPLETE)
│   └── test_models.py            # Pydantic validation (TODO)
├── integration/                   # Integration tests (database-dependent)
│   ├── data/                     # Data layer CRUD tests (TODO)
│   └── service/                  # Service layer business logic tests (TODO)
├── e2e/                          # End-to-end tests (full stack)
│   ├── test_authorization_matrix.py  # **CRITICAL** - Role-based access (COMPLETE)
│   ├── test_authentication_flow.py   # Login/logout workflows (TODO)
│   ├── test_user_management.py       # User CRUD endpoints (TODO)
│   ├── test_assessment_workflow.py   # Assessment workflows (TODO)
│   └── test_settings_routes.py       # Settings endpoints (TODO)
├── security/                     # Security tests
│   ├── test_sql_injection.py     # SQL injection prevention (TODO)
│   ├── test_xss_prevention.py    # XSS prevention (TODO)
│   ├── test_token_security.py    # JWT tampering tests (TODO)
│   └── test_authorization_bypass.py  # Permission bypass attempts (TODO)
├── fixtures/                     # Reusable test data
└── mocks/                        # External dependency mocks
```

## Phase 1 Implementation (COMPLETED)

Phase 1 focuses on the **critical path** - authentication and authorization:

### ✅ Completed

1. **Test Infrastructure**
   - Directory structure created
   - `pytest.ini` configured with coverage settings
   - `conftest.py` with comprehensive fixtures

2. **Authentication Unit Tests** (`tests/unit/test_authentication.py`)
   - 34 tests covering:
     - Password hashing and verification
     - JWT token generation and validation
     - Token expiry status checking
     - User authentication
     - Token creation and renewal

3. **Permission Unit Tests** (`tests/unit/test_user_permissions.py`)
   - 47 tests covering all permission methods:
     - `can_grant_roles()` - 3 tests
     - `can_create_user()` - 8 tests
     - `can_delete_user()` - 7 tests
     - `can_modify_user()` - 9 tests
     - Resource management permissions - 20 tests

4. **Authorization Matrix E2E Tests** (`tests/e2e/test_authorization_matrix.py`)
   - 30+ tests verifying:
     - Settings (admin-only)
     - Dashboard endpoints (admin + coach)
     - App endpoints (all authenticated users)
     - Public endpoints (unauthenticated)
     - Cross-role data isolation
     - Complete authorization matrix summary

### 📊 Test Statistics (Phase 1)

- **Total Tests Written**: ~111 tests
- **Coverage Target**: 90%+ on critical modules
- **Critical Modules Tested**:
  - `app/service/authentication.py`
  - `app/model/user.py`
  - All endpoint routes for authorization

## Running Tests

### Prerequisites

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Ensure environment variables are set (handled automatically in tests):
   - `SECRET_KEY`
   - `ALGORITHM`
   - `ACCESS_TOKEN_EXPIRE_MINUTES`
   - `DEFAULT_USER`, `DEFAULT_PASSWORD`, `DEFAULT_EMAIL`

### Running All Tests

```bash
# Run all tests
pytest

# Run with coverage report
pytest --cov=app --cov-report=html

# Run with verbose output
pytest -v
```

### Running Specific Test Categories

```bash
# Unit tests only (fast)
pytest -m unit

# Integration tests only
pytest -m integration

# E2E tests only
pytest -m e2e

# Security tests only
pytest -m security

# Authentication-related tests
pytest -m auth

# Authorization-related tests
pytest -m authz
```

### Running Specific Test Files

```bash
# Authentication tests
pytest tests/unit/test_authentication.py -v

# Permission tests
pytest tests/unit/test_user_permissions.py -v

# Authorization matrix (MOST CRITICAL)
pytest tests/e2e/test_authorization_matrix.py -v
```

### Coverage Reports

```bash
# Generate HTML coverage report
pytest --cov=app --cov-report=html
# Open htmlcov/index.html in browser

# Terminal coverage report with missing lines
pytest --cov=app --cov-report=term-missing

# Coverage for specific modules
pytest --cov=app/service/authentication.py --cov-report=term-missing
```

## Fixtures Available

### Database Fixtures

- `test_db` - Isolated test database (function-scoped)
- Automatically truncates tables between tests
- Handles SQLite WAL mode cleanup

### User Fixtures

- `admin_user` - Admin with full access
- `coach_user` - Coach with limited access
- `regular_user` - Regular user
- `another_user` - Additional user for testing user-to-user interactions

### Client Fixtures

- `test_client` - Basic unauthenticated TestClient
- `authenticated_client(role)` - Factory for authenticated clients
  - Usage: `client = authenticated_client("admin")`
  - Roles: "admin", "coach", "user"

### Mock Fixtures

- `mock_request` - Mock FastAPI Request object
- `mock_smtp` - Mock SMTP for email testing
- `mock_turnstile_success` - Mock successful CAPTCHA
- `mock_turnstile_failure` - Mock failed CAPTCHA

## Test Writing Guidelines

### 1. Test Naming

Use descriptive names that explain what is tested and the expected outcome:

```python
✅ def test_coach_cannot_delete_admin_user():
❌ def test_user_delete():
```

### 2. AAA Pattern

Follow Arrange-Act-Assert structure:

```python
def test_create_user_as_admin():
    # Arrange
    admin = admin_user
    user_data = UserCreate(...)

    # Act
    result = create_user(user_data, admin)

    # Assert
    assert result.username == user_data.username
```

### 3. Test Independence

Each test should:
- Create its own test data
- Not depend on other tests
- Work in any order

### 4. Parametrization

Use `@pytest.mark.parametrize` for testing multiple similar cases:

```python
@pytest.mark.parametrize("role,expected", [
    ("admin", True),
    ("coach", True),
    ("user", False),
])
def test_can_manage_questions(role, expected):
    ...
```

### 5. Both Success and Failure Paths

Always test both:
- Success cases (valid inputs)
- Failure cases (invalid inputs, unauthorized access)

## Next Steps (Phases 2-4)

### Phase 2: Service Layer Tests (Week 2)
- [ ] User service integration tests
- [ ] Assessment service tests
- [ ] Question service tests
- [ ] Report service tests
- [ ] Settings service tests

### Phase 3: Data Layer & Routes (Week 3)
- [ ] User data CRUD tests
- [ ] Assessment data tests
- [ ] Question data tests
- [ ] Report data tests
- [ ] Public routes tests (login, password reset)
- [ ] Dashboard route tests
- [ ] App route tests

### Phase 4: Security & Coverage (Week 4)
- [ ] SQL injection prevention tests
- [ ] XSS prevention tests
- [ ] JWT token tampering tests
- [ ] Authorization bypass attempts
- [ ] Edge case testing
- [ ] Achieve 70%+ overall coverage
- [ ] 90%+ coverage on critical modules

## Success Criteria

- [ ] 70%+ overall code coverage
- [ ] 90%+ coverage on critical authentication/authorization code
- [ ] All 3 user roles tested across all endpoints
- [ ] Complete authorization matrix verified
- [ ] Security tests verify SQL injection and XSS prevention
- [ ] Security tests verify JWT token tampering detection
- [ ] Security tests verify authorization bypass prevention
- [ ] Database isolation working (tests don't interfere)
- [ ] All tests pass consistently
- [ ] Test suite runs in < 5 minutes

## Troubleshooting

### Import Errors

If you see import errors, ensure:
1. You're running from the project root directory
2. Dependencies are installed: `pip install -r requirements.txt`
3. Python path includes the project root

### Database Errors

If tests fail with database errors:
1. Check that temp directory is writable
2. Ensure no other process is using the test database
3. Check that WAL files are being cleaned up

### Coverage Too Low

If coverage fails to meet 70%:
1. Run coverage report to see missing lines
2. Focus on critical modules first (auth, permissions)
3. Add tests for uncovered edge cases

## Additional Resources

- **Plan Document**: `/home/claude/.claude/plans/bright-wibbling-noodle.md`
- **Application Code**: `/home/claude/coding/bat-app-v3/app/`
- **Coverage Reports**: `htmlcov/index.html` (after running with --cov)

## Contact

For questions about the test suite, refer to:
- The comprehensive testing plan in `.claude/plans/`
- Individual test file docstrings
- FastAPI testing documentation: https://fastapi.tiangolo.com/tutorial/testing/
