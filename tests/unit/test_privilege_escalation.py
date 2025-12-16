"""
Unit Tests for Privilege Escalation Prevention

These tests verify that users cannot escalate their privileges beyond
what is allowed by the role hierarchy.

Key scenarios tested:
- Coach cannot elevate self to admin
- Coach cannot create admin users
- Coach cannot assign admin role to other users
- User cannot elevate self to coach or admin
- Admins can assign any role (control test)
"""

import pytest
from uuid import uuid4
from app.model.user import User, UserCreate, UserUpdate, UserRoleEnum
from app.service.user import create, update
from app.exception.service import Unauthorized
from unittest.mock import MagicMock


# Generate UUIDs for tests
COACH_UUID_1 = str(uuid4())
COACH_UUID_2 = str(uuid4())
USER_UUID_1 = str(uuid4())
USER_UUID_2 = str(uuid4())
ADMIN_UUID_1 = str(uuid4())


class TestPrivilegeEscalationPrevention:
    """Test that privilege escalation is properly prevented"""

    def test_coach_cannot_elevate_self_to_admin(self):
        """Coach attempting to change their own role to admin should fail"""
        # Setup: Coach user
        coach = User(
            user_id=COACH_UUID_1,
            username="coach_user",
            email="coach@example.com",
            hash="hashed_password",
            role=UserRoleEnum.coach
        )

        # Attempt to update self to admin
        updated_coach = UserUpdate(
            user_id=COACH_UUID_1,
            username="coach_user",
            email="coach@example.com",
            password=None,
            role=UserRoleEnum.admin  # Trying to escalate
        )

        # Mock the data layer
        import app.data.user as user_data
        user_data.get_one = MagicMock(return_value=coach)

        # This should raise Unauthorized
        with pytest.raises(Unauthorized) as exc_info:
            update(user_id=COACH_UUID_1, user=updated_coach, current_user=coach)

        assert "cannot assign the 'admin' role" in str(exc_info.value.msg).lower()

    def test_coach_cannot_elevate_other_coach_to_admin(self):
        """Coach attempting to elevate another coach to admin should fail"""
        # Setup: Current user is coach
        current_coach = User(
            user_id=COACH_UUID_1,
            username="coach_one",
            email="coach1@example.com",
            hash="hashed_password",
            role=UserRoleEnum.coach
        )

        # Target: Another coach being elevated to admin
        target_coach = User(
            user_id=COACH_UUID_2,
            username="coach_two",
            email="coach2@example.com",
            hash="hashed_password",
            role=UserRoleEnum.coach
        )

        updated_target = UserUpdate(
            user_id=COACH_UUID_2,
            username="coach_two",
            email="coach2@example.com",
            password=None,
            role=UserRoleEnum.admin  # Trying to escalate
        )

        # Mock the data layer
        import app.data.user as user_data
        user_data.get_one = MagicMock(return_value=target_coach)

        # This should raise Unauthorized (either for modify permission or role assignment)
        with pytest.raises(Unauthorized) as exc_info:
            update(user_id=COACH_UUID_2, user=updated_target, current_user=current_coach)

        # Either error message is acceptable - the important thing is it's blocked
        error_msg = str(exc_info.value.msg).lower()
        assert "cannot" in error_msg and ("admin" in error_msg or "modify" in error_msg)

    def test_coach_cannot_elevate_user_to_admin(self):
        """Coach attempting to elevate a regular user to admin should fail"""
        # Setup: Current user is coach
        current_coach = User(
            user_id=COACH_UUID_1,
            username="coach_one",
            email="coach1@example.com",
            hash="hashed_password",
            role=UserRoleEnum.coach
        )

        # Target: Regular user being elevated to admin
        target_user = User(
            user_id=USER_UUID_1,
            username="regular_user",
            email="user@example.com",
            hash="hashed_password",
            role=UserRoleEnum.user
        )

        updated_target = UserUpdate(
            user_id=USER_UUID_1,
            username="regular_user",
            email="user@example.com",
            password=None,
            role=UserRoleEnum.admin  # Trying to escalate
        )

        # Mock the data layer
        import app.data.user as user_data
        user_data.get_one = MagicMock(return_value=target_user)

        # This should raise Unauthorized
        with pytest.raises(Unauthorized) as exc_info:
            update(user_id=USER_UUID_1, user=updated_target, current_user=current_coach)

        # Either error message is acceptable - the important thing is it's blocked
        error_msg = str(exc_info.value.msg).lower()
        assert "cannot" in error_msg and ("admin" in error_msg or "modify" in error_msg)

    def test_user_cannot_elevate_self_to_coach(self):
        """Regular user attempting to change their role to coach should fail"""
        # Setup: Regular user
        user = User(
            user_id=USER_UUID_1,
            username="regular_user",
            email="user@example.com",
            hash="hashed_password",
            role=UserRoleEnum.user
        )

        # Attempt to update self to coach
        updated_user = UserUpdate(
            user_id=USER_UUID_1,
            username="regular_user",
            email="user@example.com",
            password=None,
            role=UserRoleEnum.coach  # Trying to escalate
        )

        # Mock the data layer
        import app.data.user as user_data
        user_data.get_one = MagicMock(return_value=user)

        # This should raise Unauthorized
        with pytest.raises(Unauthorized) as exc_info:
            update(user_id=USER_UUID_1, user=updated_user, current_user=user)

        assert "cannot assign the 'coach' role" in str(exc_info.value.msg).lower()

    def test_user_cannot_elevate_self_to_admin(self):
        """Regular user attempting to change their role to admin should fail"""
        # Setup: Regular user
        user = User(
            user_id=USER_UUID_1,
            username="regular_user",
            email="user@example.com",
            hash="hashed_password",
            role=UserRoleEnum.user
        )

        # Attempt to update self to admin
        updated_user = UserUpdate(
            user_id=USER_UUID_1,
            username="regular_user",
            email="user@example.com",
            password=None,
            role=UserRoleEnum.admin  # Trying to escalate
        )

        # Mock the data layer
        import app.data.user as user_data
        user_data.get_one = MagicMock(return_value=user)

        # This should raise Unauthorized
        with pytest.raises(Unauthorized) as exc_info:
            update(user_id=USER_UUID_1, user=updated_user, current_user=user)

        assert "cannot assign the 'admin' role" in str(exc_info.value.msg).lower()

    def test_coach_can_elevate_user_to_coach(self):
        """Coach should be able to elevate a user to coach (allowed)"""
        # Setup: Current user is coach
        current_coach = User(
            user_id=COACH_UUID_1,
            username="coach_one",
            email="coach1@example.com",
            hash="hashed_password",
            role=UserRoleEnum.coach
        )

        # Target: Regular user being elevated to coach
        target_user = User(
            user_id=USER_UUID_1,
            username="regular_user",
            email="user@example.com",
            hash="hashed_password",
            role=UserRoleEnum.user
        )

        updated_target = UserUpdate(
            user_id=USER_UUID_1,
            username="regular_user",
            email="user@example.com",
            password=None,
            role=UserRoleEnum.coach  # Allowed escalation
        )

        promoted_user = User(
            user_id=USER_UUID_1,
            username="regular_user",
            email="user@example.com",
            hash="hashed_password",
            role=UserRoleEnum.coach
        )

        # Mock the data layer
        import app.data.user as user_data
        user_data.get_one = MagicMock(return_value=target_user)
        user_data.modify = MagicMock(return_value=promoted_user)

        # This should succeed
        result = update(user_id=USER_UUID_1, user=updated_target, current_user=current_coach)

        assert result.role == UserRoleEnum.coach

    def test_admin_can_assign_any_role(self):
        """Admin should be able to assign any role including admin (control test)"""
        # Setup: Current user is admin
        admin = User(
            user_id=ADMIN_UUID_1,
            username="admin_user",
            email="admin@example.com",
            hash="hashed_password",
            role=UserRoleEnum.admin
        )

        # Target: Coach being promoted to admin
        target_coach = User(
            user_id=COACH_UUID_1,
            username="coach_user",
            email="coach@example.com",
            hash="hashed_password",
            role=UserRoleEnum.coach
        )

        updated_target = UserUpdate(
            user_id=COACH_UUID_1,
            username="coach_user",
            email="coach@example.com",
            password=None,
            role=UserRoleEnum.admin
        )

        promoted_admin = User(
            user_id=COACH_UUID_1,
            username="coach_user",
            email="coach@example.com",
            hash="hashed_password",
            role=UserRoleEnum.admin
        )

        # Mock the data layer
        import app.data.user as user_data
        user_data.get_one = MagicMock(return_value=target_coach)
        user_data.modify = MagicMock(return_value=promoted_admin)

        # This should succeed
        result = update(user_id=COACH_UUID_1, user=updated_target, current_user=admin)

        assert result.role == UserRoleEnum.admin

    def test_coach_cannot_create_admin_user(self):
        """Coach attempting to create a new admin user should fail"""
        # Setup: Current user is coach
        coach = User(
            user_id=COACH_UUID_1,
            username="coach_user",
            email="coach@example.com",
            hash="hashed_password",
            role=UserRoleEnum.coach
        )

        # Attempt to create admin user
        new_admin = UserCreate(
            user_id=None,
            username="new_admin",
            email="newadmin@example.com",
            password="securepassword123",
            role=UserRoleEnum.admin  # Trying to create admin
        )

        # Mock request object
        request = MagicMock()

        # This should raise Unauthorized
        with pytest.raises(Unauthorized) as exc_info:
            create(user=new_admin, request=request, current_user=coach)

        # Either error message is acceptable - the important thing is it's blocked
        error_msg = str(exc_info.value.msg).lower()
        assert "cannot" in error_msg and ("admin" in error_msg or "create" in error_msg or "assign" in error_msg)

    def test_role_unchanged_no_validation_needed(self):
        """When role is not changed, no role validation should occur"""
        # Setup: Coach updating their own email/username but keeping role
        coach = User(
            user_id=COACH_UUID_1,
            username="coach_user",
            email="coach@example.com",
            hash="hashed_password",
            role=UserRoleEnum.coach
        )

        # Update with same role
        updated_coach = UserUpdate(
            user_id=COACH_UUID_1,
            username="coach_user_updated",
            email="newcoach@example.com",
            password=None,
            role=UserRoleEnum.coach  # Same role
        )

        updated_result = User(
            user_id=COACH_UUID_1,
            username="coach_user_updated",
            email="newcoach@example.com",
            hash="hashed_password",
            role=UserRoleEnum.coach
        )

        # Mock the data layer
        import app.data.user as user_data
        user_data.get_one = MagicMock(return_value=coach)
        user_data.modify = MagicMock(return_value=updated_result)

        # This should succeed (no role change)
        result = update(user_id=COACH_UUID_1, user=updated_coach, current_user=coach)

        assert result.username == "coach_user_updated"
        assert result.role == UserRoleEnum.coach
