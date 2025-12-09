"""
Unit tests for authentication module (app/service/authentication.py)

Tests cover:
- Password hashing and verification
- JWT token generation and validation
- Token expiry status checking
- User authentication
- Token creation and renewal
"""

import pytest
from datetime import timedelta, datetime, timezone
from jose import jwt

from app.service.authentication import (
    verify_password,
    get_password_hash,
    jwt_to_user_id,
    jwt_to_expiry_status,
    jwt_extract_object,
    generate_bearer_token,
    auth_user,
    handle_token_creation,
    handle_token_renewal,
)
from app.exception.service import IncorectCredentials, InvalidBearerToken
from app.config import SECRET_KEY, ALGORITHM


@pytest.mark.unit
@pytest.mark.auth
class TestPasswordHashing:
    """Test password hashing and verification"""

    def test_password_hash_generates_different_hashes_for_same_password(self):
        """Same password should generate different hashes due to salt"""
        password = "TestPassword123!"
        hash1 = get_password_hash(password)
        hash2 = get_password_hash(password)

        assert hash1 != hash2
        assert len(hash1) > 0
        assert len(hash2) > 0

    def test_verify_password_returns_true_for_correct_password(self):
        """Correct password should verify against its hash"""
        password = "TestPassword123!"
        password_hash = get_password_hash(password)

        assert verify_password(password, password_hash) is True

    def test_verify_password_returns_false_for_incorrect_password(self):
        """Incorrect password should not verify"""
        password = "TestPassword123!"
        wrong_password = "WrongPassword456!"
        password_hash = get_password_hash(password)

        assert verify_password(wrong_password, password_hash) is False

    def test_verify_password_returns_false_for_empty_password(self):
        """Empty password should not verify"""
        password = "TestPassword123!"
        password_hash = get_password_hash(password)

        assert verify_password("", password_hash) is False


@pytest.mark.unit
@pytest.mark.auth
class TestJWTTokenGeneration:
    """Test JWT token generation"""

    def test_generate_bearer_token_includes_bearer_prefix(self):
        """Generated token should start with 'Bearer '"""
        token = generate_bearer_token(data={"user_id": "test-user-id"})

        assert token.startswith("Bearer ")

    def test_generate_bearer_token_contains_user_id(self):
        """Token should contain the user_id in payload"""
        user_id = "test-user-12345"
        token = generate_bearer_token(data={"user_id": user_id})

        # Extract token value (remove "Bearer " prefix)
        token_value = token.split("Bearer ")[1]
        payload = jwt.decode(token_value, SECRET_KEY, algorithms=[ALGORITHM])

        assert payload["user_id"] == user_id

    def test_generate_bearer_token_contains_expiration(self):
        """Token should contain expiration timestamp"""
        token = generate_bearer_token(data={"user_id": "test-user-id"})

        token_value = token.split("Bearer ")[1]
        payload = jwt.decode(token_value, SECRET_KEY, algorithms=[ALGORITHM])

        assert "exp" in payload
        assert payload["exp"] > datetime.now(timezone.utc).timestamp()

    def test_generate_bearer_token_with_custom_expiration(self):
        """Token with custom expiration delta should expire at correct time"""
        user_id = "test-user-id"
        expires_delta = timedelta(minutes=60)
        token = generate_bearer_token(
            data={"user_id": user_id},
            expires_delta=expires_delta
        )

        token_value = token.split("Bearer ")[1]
        payload = jwt.decode(token_value, SECRET_KEY, algorithms=[ALGORITHM])

        exp_time = datetime.fromtimestamp(payload["exp"], tz=timezone.utc)
        expected_exp = datetime.now(timezone.utc) + expires_delta

        # Allow 5 second tolerance for test execution time
        assert abs((exp_time - expected_exp).total_seconds()) < 5

    def test_generate_bearer_token_default_expiration_is_15_minutes(self):
        """Token without expiration delta should default to 15 minutes"""
        token = generate_bearer_token(data={"user_id": "test-user-id"})

        token_value = token.split("Bearer ")[1]
        payload = jwt.decode(token_value, SECRET_KEY, algorithms=[ALGORITHM])

        exp_time = datetime.fromtimestamp(payload["exp"], tz=timezone.utc)
        expected_exp = datetime.now(timezone.utc) + timedelta(minutes=15)

        # Allow 5 second tolerance
        assert abs((exp_time - expected_exp).total_seconds()) < 5


@pytest.mark.unit
@pytest.mark.auth
class TestJWTTokenValidation:
    """Test JWT token validation and extraction"""

    def test_jwt_to_user_id_extracts_correct_user_id(self):
        """Valid token should extract correct user_id"""
        user_id = "test-user-12345"
        token = generate_bearer_token(data={"user_id": user_id})
        token_value = token.split("Bearer ")[1]

        extracted_id = jwt_to_user_id(token_value)

        assert extracted_id == user_id

    def test_jwt_to_user_id_raises_on_expired_token(self):
        """Expired token should raise InvalidBearerToken"""
        user_id = "test-user-id"
        # Create token that expired 1 hour ago
        token = generate_bearer_token(
            data={"user_id": user_id},
            expires_delta=timedelta(hours=-1)
        )
        token_value = token.split("Bearer ")[1]

        with pytest.raises(InvalidBearerToken) as exc_info:
            jwt_to_user_id(token_value)

        assert "expired" in exc_info.value.msg.lower()

    def test_jwt_to_user_id_raises_on_tampered_token(self):
        """Tampered token should raise InvalidBearerToken"""
        user_id = "test-user-id"
        token = generate_bearer_token(data={"user_id": user_id})
        token_value = token.split("Bearer ")[1]

        # Tamper with token by modifying a character
        tampered_token = token_value[:-10] + "TAMPERED"

        with pytest.raises(InvalidBearerToken) as exc_info:
            jwt_to_user_id(tampered_token)

        assert "invalid" in exc_info.value.msg.lower() or "tempered" in exc_info.value.msg.lower()

    def test_jwt_to_user_id_returns_none_on_missing_user_id(self):
        """Token without user_id should return None"""
        # Create token without user_id
        token = generate_bearer_token(data={"some_other_field": "value"})
        token_value = token.split("Bearer ")[1]

        result = jwt_to_user_id(token_value)

        assert result is None

    def test_jwt_extract_object_returns_payload(self):
        """jwt_extract_object should return full payload"""
        user_id = "test-user-id"
        token = generate_bearer_token(data={"user_id": user_id})
        token_value = token.split("Bearer ")[1]

        payload = jwt_extract_object(token_value)

        assert payload["user_id"] == user_id
        assert "exp" in payload

    def test_jwt_extract_object_returns_empty_dict_on_invalid_token(self):
        """Invalid token should return empty dict"""
        invalid_token = "completely.invalid.token"

        payload = jwt_extract_object(invalid_token)

        assert payload == {}


@pytest.mark.unit
@pytest.mark.auth
class TestJWTExpiryStatus:
    """Test JWT token expiry status checking"""

    def test_jwt_expiry_status_returns_0_for_expired_token(self):
        """Expired token should return 0"""
        token = generate_bearer_token(
            data={"user_id": "test-user-id"},
            expires_delta=timedelta(seconds=-10)
        )
        token_value = token.split("Bearer ")[1]

        status = jwt_to_expiry_status(token_value)

        assert status == 0

    def test_jwt_expiry_status_returns_1_for_valid_token(self):
        """Token with plenty of time remaining should return 1"""
        token = generate_bearer_token(
            data={"user_id": "test-user-id"},
            expires_delta=timedelta(minutes=10)
        )
        token_value = token.split("Bearer ")[1]

        status = jwt_to_expiry_status(token_value)

        assert status == 1

    def test_jwt_expiry_status_returns_2_for_renewal_window(self):
        """Token expiring soon (< 180 seconds) should return 2"""
        token = generate_bearer_token(
            data={"user_id": "test-user-id"},
            expires_delta=timedelta(seconds=120)  # 2 minutes
        )
        token_value = token.split("Bearer ")[1]

        status = jwt_to_expiry_status(token_value)

        assert status == 2

    def test_jwt_expiry_status_returns_0_for_invalid_token(self):
        """Invalid token should return 0"""
        invalid_token = "invalid.token.value"

        status = jwt_to_expiry_status(invalid_token)

        assert status == 0

    def test_jwt_expiry_status_returns_0_for_token_without_exp(self):
        """Token without exp field should return 0"""
        # Create token manually without exp
        token_value = jwt.encode({"user_id": "test"}, SECRET_KEY, algorithm=ALGORITHM)

        status = jwt_to_expiry_status(token_value)

        assert status == 0


@pytest.mark.unit
@pytest.mark.auth
class TestUserAuthentication:
    """Test user authentication logic"""

    def test_auth_user_succeeds_with_correct_credentials(self, test_db, admin_user):
        """Correct username and password should authenticate successfully"""
        user = auth_user(username=admin_user.username, password="AdminPass123!")

        assert user.user_id == admin_user.user_id
        assert user.username == admin_user.username
        assert user.role.value == "admin"

    def test_auth_user_fails_with_incorrect_password(self, test_db, admin_user):
        """Incorrect password should raise IncorectCredentials"""
        with pytest.raises(IncorectCredentials):
            auth_user(username=admin_user.username, password="WrongPassword!")

    def test_auth_user_fails_with_nonexistent_username(self, test_db):
        """Nonexistent username should raise exception"""
        from app.exception.database import RecordNotFound

        with pytest.raises(RecordNotFound):
            auth_user(username="nonexistent_user", password="SomePassword123!")


@pytest.mark.unit
@pytest.mark.auth
class TestTokenCreation:
    """Test token creation workflow"""

    def test_handle_token_creation_returns_bearer_token(self, test_db, admin_user):
        """Valid credentials should return bearer token"""
        token = handle_token_creation(username=admin_user.username, password="AdminPass123!")

        assert token.startswith("Bearer ")

    def test_handle_token_creation_token_contains_user_id(self, test_db, admin_user):
        """Created token should contain correct user_id"""
        token = handle_token_creation(username=admin_user.username, password="AdminPass123!")
        token_value = token.split("Bearer ")[1]

        payload = jwt.decode(token_value, SECRET_KEY, algorithms=[ALGORITHM])

        assert payload["user_id"] == admin_user.user_id

    def test_handle_token_creation_fails_with_wrong_password(self, test_db, admin_user):
        """Wrong password should raise IncorectCredentials"""
        with pytest.raises(IncorectCredentials):
            handle_token_creation(username=admin_user.username, password="WrongPassword!")


@pytest.mark.unit
@pytest.mark.auth
class TestTokenRenewal:
    """Test token renewal workflow"""

    def test_handle_token_renewal_returns_new_token(self, test_db, admin_user):
        """Token renewal should return new bearer token"""
        new_token = handle_token_renewal(current_user=admin_user)

        assert new_token.startswith("Bearer ")

    def test_handle_token_renewal_contains_same_user_id(self, test_db, admin_user):
        """Renewed token should contain same user_id"""
        new_token = handle_token_renewal(current_user=admin_user)
        token_value = new_token.split("Bearer ")[1]

        payload = jwt.decode(token_value, SECRET_KEY, algorithms=[ALGORITHM])

        assert payload["user_id"] == admin_user.user_id

    def test_handle_token_renewal_extends_expiration(self, test_db, admin_user):
        """Renewed token should have fresh expiration time"""
        new_token = handle_token_renewal(current_user=admin_user)
        token_value = new_token.split("Bearer ")[1]

        payload = jwt.decode(token_value, SECRET_KEY, algorithms=[ALGORITHM])
        exp_time = datetime.fromtimestamp(payload["exp"], tz=timezone.utc)
        now = datetime.now(timezone.utc)

        # Should have approximately 30 minutes (or configured time) remaining
        time_remaining = (exp_time - now).total_seconds()
        assert time_remaining > 25 * 60  # At least 25 minutes
        assert time_remaining < 35 * 60  # At most 35 minutes
