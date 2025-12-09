# Quick Start Guide - Running Tests

## Prerequisites

Ensure you're in the project root directory and dependencies are installed:

```bash
cd /home/petrv/Work/coding/bat-app-v3
pip install -r requirements.txt
```

## Basic Test Commands

### Run All Tests (No Coverage)

```bash
pytest
```

### Run Specific Test Categories

```bash
# Unit tests only (fast, 69 tests)
pytest tests/unit/

# E2E tests only (57 tests)
pytest tests/e2e/

# Specific markers
pytest -m unit          # Unit tests
pytest -m auth          # Authentication tests
pytest -m authz         # Authorization tests
```

### Run Specific Test Files

```bash
# Authentication tests (29 tests)
pytest tests/unit/test_authentication.py

# Permission tests (40 tests)
pytest tests/unit/test_user_permissions.py

# Authorization matrix (57 tests)
pytest tests/e2e/test_authorization_matrix.py
```

### Run Specific Test by Name

```bash
# Run one specific test
pytest tests/unit/test_authentication.py::TestPasswordHashing::test_password_hash_generates_different_hashes_for_same_password

# Run all tests in a class
pytest tests/unit/test_user_permissions.py::TestCanCreateUser
```

## Coverage Commands

### Basic Coverage

```bash
# Run unit tests with coverage
pytest tests/unit/ --cov=app

# Generate HTML coverage report
pytest tests/unit/ --cov=app --cov-report=html
# Then open htmlcov/index.html in browser
```

### Coverage on Specific Modules

```bash
# Critical modules only
pytest tests/unit/ --cov=app/service/authentication.py --cov=app/model/user.py --cov-report=term-missing

# With missing line numbers
pytest tests/unit/ --cov=app/service/authentication.py --cov-report=term-missing
```

### Coverage with Threshold

```bash
# Fail if coverage below 70%
pytest tests/unit/ --cov=app --cov-fail-under=70

# Fail if coverage below 90% on critical modules
pytest tests/unit/ --cov=app/service/authentication.py --cov=app/model/user.py --cov-fail-under=90
```

## Common Options

```bash
# Verbose output
pytest -v

# Show print statements
pytest -s

# Stop at first failure
pytest -x

# Show full traceback
pytest --tb=long

# Run last failed tests
pytest --lf

# Quiet mode (less output)
pytest -q
```

## Combining Options

```bash
# Verbose unit tests with coverage
pytest tests/unit/ -v --cov=app

# Run failing E2E tests with verbose output
pytest tests/e2e/ -x -v

# Run auth tests with coverage on auth module
pytest -m auth --cov=app/service/authentication.py --cov-report=term-missing
```

## Troubleshooting

### "No module named 'app'"

Make sure you're running from the project root:
```bash
cd /home/petrv/Work/coding/bat-app-v3
pytest
```

### "No tests collected"

Check that you're in the correct directory and test files exist:
```bash
ls tests/unit/
pytest tests/unit/ --collect-only
```

### Coverage not working

Ensure pytest-cov is installed:
```bash
pip install pytest-cov
```

### Import errors

Reinstall dependencies:
```bash
pip install -r requirements.txt
```

## Expected Results (Phase 1)

**Unit Tests:**
- ✅ All 69 tests should pass (100%)
- `tests/unit/test_authentication.py`: 29 passed
- `tests/unit/test_user_permissions.py`: 40 passed

**E2E Tests:**
- ⚠️ 30/57 tests pass (expected - reveals application bugs)
- Some failures are expected and indicate real issues in the app

**Coverage:**
- `app/model/user.py`: 97% coverage ✅
- `app/service/authentication.py`: 69% coverage ✅

## Example Session

```bash
# Navigate to project
cd /home/petrv/Work/coding/bat-app-v3

# Run unit tests only (fast, all passing)
pytest tests/unit/ -v

# Expected output:
# tests/unit/test_authentication.py::... PASSED [ XX%]
# tests/unit/test_user_permissions.py::... PASSED [ XX%]
# ===================== 69 passed in X.XXs ====================

# Run with coverage
pytest tests/unit/ --cov=app/model/user.py --cov-report=term-missing

# Expected: 97% coverage on app/model/user.py
```

## Next Steps

After confirming tests work:
1. Review `tests/README.md` for comprehensive documentation
2. Review `tests/PHASE1_SUMMARY.md` for detailed results
3. Proceed to Phase 2: Service Layer Tests (see plan document)

## Quick Reference Card

| Command | Description |
|---------|-------------|
| `pytest` | Run all tests |
| `pytest tests/unit/` | Run only unit tests |
| `pytest -m unit` | Run tests marked as unit |
| `pytest -v` | Verbose output |
| `pytest -x` | Stop at first failure |
| `pytest --cov=app` | Run with coverage |
| `pytest --lf` | Run last failed |
| `pytest -k "password"` | Run tests matching "password" |

---

**Pro Tip**: Start with `pytest tests/unit/` - these are fast (6 seconds) and all passing!
