"""
Unit Tests for Coach Cannot Edit Admin Protection

These tests verify that coaches cannot access or modify admin user profiles.

Key scenarios tested:
- Coach cannot view admin profile (GET request)
- Coach cannot update admin profile (PUT request)
- Coach cannot delete admin users
- Admin can still access all users (control test)
- Coach can still access coach and user profiles
"""

import pytest
from uuid import uuid4
from app.model.user import User, UserUpdate, UserRoleEnum
from app.service.user import get, update, delete
from app.exception.service import Unauthorized
from unittest.mock import MagicMock


# Generate UUIDs for tests
COACH_UUID = str(uuid4())
ADMIN_UUID = str(uuid4())
USER_UUID = str(uuid4())


class TestCoachCannotAccessAdmin:
    """Test that coaches cannot access or modify admin users"""

    def test_coach_cannot_view_admin_profile(self):
        """Coach attempting to view admin profile should fail"""
        # Setup: Coach user
        coach = User(
            user_id=COACH_UUID,
            username="coach_user",
            email="coach@example.com",
            hash="hashed_password",
            role=UserRoleEnum.coach
        )

        # Target: Admin user
        admin = User(
            user_id=ADMIN_UUID,
            username="admin_user",
            email="admin@example.com",
            hash="hashed_password",
            role=UserRoleEnum.admin
        )

        # Mock the data layer
        import app.data.user as user_data
        user_data.get_one = MagicMock(return_value=admin)

        # This should raise Unauthorized
        with pytest.raises(Unauthorized) as exc_info:
            get(user_id=ADMIN_UUID, current_user=coach)

        assert "cannot access this user" in str(exc_info.value.msg).lower()

    def test_coach_cannot_update_admin_profile(self):
        """Coach attempting to update admin profile should fail"""
        # Setup: Coach user
        coach = User(
            user_id=COACH_UUID,
            username="coach_user",
            email="coach@example.com",
            hash="hashed_password",
            role=UserRoleEnum.coach
        )

        # Target: Admin user
        admin = User(
            user_id=ADMIN_UUID,
            username="admin_user",
            email="admin@example.com",
            hash="hashed_password",
            role=UserRoleEnum.admin
        )

        # Update data
        updated_admin = UserUpdate(
            user_id=ADMIN_UUID,
            username="admin_user_modified",
            email="admin@example.com",
            password=None,
            role=UserRoleEnum.admin
        )

        # Mock the data layer
        import app.data.user as user_data
        user_data.get_one = MagicMock(return_value=admin)

        # This should raise Unauthorized
        with pytest.raises(Unauthorized) as exc_info:
            update(user_id=ADMIN_UUID, user=updated_admin, current_user=coach)

        assert "cannot" in str(exc_info.value.msg).lower()

    def test_coach_cannot_delete_admin(self):
        """Coach attempting to delete admin should fail"""
        # Setup: Coach user
        coach = User(
            user_id=COACH_UUID,
            username="coach_user",
            email="coach@example.com",
            hash="hashed_password",
            role=UserRoleEnum.coach
        )

        # Target: Admin user
        admin = User(
            user_id=ADMIN_UUID,
            username="admin_user",
            email="admin@example.com",
            hash="hashed_password",
            role=UserRoleEnum.admin
        )

        # Mock the data layer
        import app.data.user as user_data
        user_data.get_one = MagicMock(return_value=admin)

        # This should raise Unauthorized
        with pytest.raises(Unauthorized) as exc_info:
            delete(user_id=ADMIN_UUID, current_user=coach)

        assert "cannot" in str(exc_info.value.msg).lower()

    def test_coach_can_view_other_coach_profile(self):
        """Coach should be able to view another coach's profile"""
        # Setup: Coach user
        coach1 = User(
            user_id=COACH_UUID,
            username="coach_one",
            email="coach1@example.com",
            hash="hashed_password",
            role=UserRoleEnum.coach
        )

        # Target: Another coach
        coach2_uuid = str(uuid4())
        coach2 = User(
            user_id=coach2_uuid,
            username="coach_two",
            email="coach2@example.com",
            hash="hashed_password",
            role=UserRoleEnum.coach
        )

        # Mock the data layer
        import app.data.user as user_data
        user_data.get_one = MagicMock(return_value=coach2)

        # This should succeed
        result = get(user_id=coach2_uuid, current_user=coach1)

        assert result.username == "coach_two"
        assert result.role == UserRoleEnum.coach

    def test_coach_can_view_user_profile(self):
        """Coach should be able to view regular user's profile"""
        # Setup: Coach user
        coach = User(
            user_id=COACH_UUID,
            username="coach_user",
            email="coach@example.com",
            hash="hashed_password",
            role=UserRoleEnum.coach
        )

        # Target: Regular user
        user = User(
            user_id=USER_UUID,
            username="regular_user",
            email="user@example.com",
            hash="hashed_password",
            role=UserRoleEnum.user
        )

        # Mock the data layer
        import app.data.user as user_data
        user_data.get_one = MagicMock(return_value=user)

        # This should succeed
        result = get(user_id=USER_UUID, current_user=coach)

        assert result.username == "regular_user"
        assert result.role == UserRoleEnum.user

    def test_admin_can_view_all_users(self):
        """Admin should be able to view any user including other admins (control test)"""
        # Setup: Admin user
        admin1 = User(
            user_id=ADMIN_UUID,
            username="admin_one",
            email="admin1@example.com",
            hash="hashed_password",
            role=UserRoleEnum.admin
        )

        # Target: Another admin
        admin2_uuid = str(uuid4())
        admin2 = User(
            user_id=admin2_uuid,
            username="admin_two",
            email="admin2@example.com",
            hash="hashed_password",
            role=UserRoleEnum.admin
        )

        # Mock the data layer
        import app.data.user as user_data
        user_data.get_one = MagicMock(return_value=admin2)

        # This should succeed
        result = get(user_id=admin2_uuid, current_user=admin1)

        assert result.username == "admin_two"
        assert result.role == UserRoleEnum.admin

    def test_coach_can_view_own_profile(self):
        """Coach should be able to view their own profile (even as coach role)"""
        # Setup: Coach user
        coach = User(
            user_id=COACH_UUID,
            username="coach_user",
            email="coach@example.com",
            hash="hashed_password",
            role=UserRoleEnum.coach
        )

        # Mock the data layer
        import app.data.user as user_data
        user_data.get_one = MagicMock(return_value=coach)

        # This should succeed (viewing own profile)
        result = get(user_id=COACH_UUID, current_user=coach)

        assert result.username == "coach_user"
        assert result.role == UserRoleEnum.coach
