import pytest
import tempfile
import os
from pathlib import Path
from datetime import timedelta
from uuid import uuid4
from starlette.testclient import TestClient


# ===================================
# Environment Setup
# ===================================

@pytest.fixture(scope="session", autouse=True)
def setup_test_environment(monkeypatch_session):
    """Set up required environment variables for testing"""
    monkeypatch_session.setenv("SECRET_KEY", "test-secret-key-for-jwt-tokens-in-tests")
    monkeypatch_session.setenv("ALGORITHM", "HS256")
    monkeypatch_session.setenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30")
    monkeypatch_session.setenv("DEFAULT_USER", "test_admin")
    monkeypatch_session.setenv("DEFAULT_EMAIL", "test@example.com")
    monkeypatch_session.setenv("DEFAULT_PASSWORD", "TestPassword123!")


@pytest.fixture(scope="session")
def monkeypatch_session():
    """Session-scoped monkeypatch for environment variables"""
    from _pytest.monkeypatch import MonkeyPatch
    m = MonkeyPatch()
    yield m
    m.undo()


# ===================================
# Database Fixtures
# ===================================

@pytest.fixture(scope="session")
def test_db_file():
    """Create temporary database file for the entire test session"""
    fd, path = tempfile.mkstemp(suffix=".db", prefix="test_bat_")
    yield path
    os.close(fd)
    # Cleanup database files (including WAL and SHM files)
    Path(path).unlink(missing_ok=True)
    Path(f"{path}-wal").unlink(missing_ok=True)
    Path(f"{path}-shm").unlink(missing_ok=True)


@pytest.fixture(scope="function")
def test_db(test_db_file, monkeypatch):
    """
    Initialize isolated test database for each test function.

    This fixture:
    1. Resets the db_initialized flag
    2. Forces re-initialization with test database
    3. Creates all tables
    4. Yields the connection
    5. Truncates all tables for next test
    """
    # Import here to avoid issues with environment variables
    import app.data.init as db_init

    # Reset initialization flag to force fresh connection
    db_init.db_initialized = False

    # Initialize database with test file
    conn, curs = db_init.get_db(name=test_db_file)

    # Import all data modules to ensure tables are created
    import app.data.user
    import app.data.assessment
    import app.data.question
    import app.data.report
    import app.data.note
    import app.data.setting

    yield conn

    # Cleanup: Truncate all tables but keep schema
    curs.execute("PRAGMA foreign_keys = OFF")
    tables_query = """
        SELECT name FROM sqlite_master
        WHERE type='table' AND name NOT LIKE 'sqlite_%'
    """
    tables = curs.execute(tables_query).fetchall()
    for (table_name,) in tables:
        curs.execute(f"DELETE FROM {table_name}")
    conn.commit()
    curs.execute("PRAGMA foreign_keys = ON")


# ===================================
# User Fixtures
# ===================================

@pytest.fixture
def admin_user(test_db):
    """Create an admin user for testing"""
    from app.model.user import User, UserRoleEnum
    from app.service.authentication import get_password_hash
    import app.data.user as user_data

    # Generate unique username/email using UUID to avoid conflicts
    unique_id = str(uuid4())[:8]
    user = User(
        user_id=str(uuid4()),
        username=f"test_admin_{unique_id}",
        email=f"admin_{unique_id}@test.com",
        hash=get_password_hash("AdminPass123!"),
        role=UserRoleEnum.admin
    )
    return user_data.create(user)


@pytest.fixture
def coach_user(test_db):
    """Create a coach user for testing"""
    from app.model.user import User, UserRoleEnum
    from app.service.authentication import get_password_hash
    import app.data.user as user_data

    # Generate unique username/email using UUID to avoid conflicts
    unique_id = str(uuid4())[:8]
    user = User(
        user_id=str(uuid4()),
        username=f"test_coach_{unique_id}",
        email=f"coach_{unique_id}@test.com",
        hash=get_password_hash("CoachPass123!"),
        role=UserRoleEnum.coach
    )
    return user_data.create(user)


@pytest.fixture
def regular_user(test_db):
    """Create a regular user for testing"""
    from app.model.user import User, UserRoleEnum
    from app.service.authentication import get_password_hash
    import app.data.user as user_data

    # Generate unique username/email using UUID to avoid conflicts
    unique_id = str(uuid4())[:8]
    user = User(
        user_id=str(uuid4()),
        username=f"test_user_{unique_id}",
        email=f"user_{unique_id}@test.com",
        hash=get_password_hash("UserPass123!"),
        role=UserRoleEnum.user
    )
    return user_data.create(user)


@pytest.fixture
def another_user(test_db):
    """Create another regular user for testing user-to-user interactions"""
    from app.model.user import User, UserRoleEnum
    from app.service.authentication import get_password_hash
    import app.data.user as user_data

    # Generate unique username/email using UUID to avoid conflicts
    unique_id = str(uuid4())[:8]
    user = User(
        user_id=str(uuid4()),
        username=f"another_user_{unique_id}",
        email=f"another_{unique_id}@test.com",
        hash=get_password_hash("AnotherPass123!"),
        role=UserRoleEnum.user
    )
    return user_data.create(user)


# ===================================
# Client Fixtures
# ===================================

@pytest.fixture
def test_client(test_db):
    """Basic test client for unauthenticated requests"""
    from app.main import app
    with TestClient(app) as client:
        yield client


@pytest.fixture
def authenticated_client(test_client, test_db, admin_user, coach_user, regular_user):
    """
    Factory fixture for creating authenticated test clients.

    Usage:
        def test_something(authenticated_client):
            client = authenticated_client("admin")
            response = client.get("/dashboard")

    Args:
        role (str): One of "admin", "coach", or "user"

    Returns:
        TestClient with authentication cookie set
    """
    def _make_client(role="admin"):
        from app.service.authentication import generate_bearer_token

        # Select user by role
        user_map = {
            "admin": admin_user,
            "coach": coach_user,
            "user": regular_user
        }
        user = user_map.get(role)
        if not user:
            raise ValueError(f"Invalid role: {role}. Must be 'admin', 'coach', or 'user'")

        # Generate token
        token = generate_bearer_token(
            data={"user_id": user.user_id},
            expires_delta=timedelta(minutes=30)
        )

        # Set cookie on test client
        test_client.cookies.set("access_token", token)

        # Attach user object for reference in tests
        test_client.current_user = user

        return test_client

    return _make_client


# ===================================
# Mock Fixtures
# ===================================

@pytest.fixture
def mock_request():
    """Mock FastAPI Request object for testing"""
    class MockRequest:
        base_url = "http://testserver"

        def url_for(self, name, **kwargs):
            return f"http://testserver/{name}"

    return MockRequest()


@pytest.fixture
def mock_smtp(monkeypatch):
    """Mock SMTP for email testing without actually sending emails"""
    class MockSMTP:
        sent_emails = []

        def __init__(self, *args, **kwargs):
            pass

        def __enter__(self):
            return self

        def __exit__(self, *args):
            pass

        def login(self, *args):
            pass

        def sendmail(self, from_addr, to_addr, msg):
            self.sent_emails.append({
                "from": from_addr,
                "to": to_addr,
                "message": msg
            })

    mock = MockSMTP()
    monkeypatch.setattr("smtplib.SMTP_SSL", lambda *args, **kwargs: mock)
    return mock


@pytest.fixture
def mock_turnstile_success(monkeypatch):
    """Mock successful Cloudflare Turnstile verification"""
    def mock_post(*args, **kwargs):
        class MockResponse:
            def json(self):
                return {"success": True}
        return MockResponse()

    monkeypatch.setattr("requests.post", mock_post)


@pytest.fixture
def mock_turnstile_failure(monkeypatch):
    """Mock failed Cloudflare Turnstile verification"""
    def mock_post(*args, **kwargs):
        class MockResponse:
            def json(self):
                return {"success": False}
        return MockResponse()

    monkeypatch.setattr("requests.post", mock_post)
