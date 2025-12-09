"""
Unit tests for User permission methods (app/model/user.py)

Tests cover all permission methods for the three user roles:
- Admin: Full access to everything
- Coach: Can manage assessments, questions, reports, users (except admins)
- User: Limited to own data only

Permission methods tested:
- can_grant_roles()
- can_create_user()
- can_delete_user()
- can_modify_user()
- can_manage_questions()
- can_manage_assessments()
- can_manage_notes()
- can_manage_reports()
- can_send_emails()
"""

import pytest
from uuid import uuid4

from app.model.user import User, UserRoleEnum, UserCreate
from app.service.authentication import get_password_hash


@pytest.mark.unit
@pytest.mark.authz
class TestCanGrantRoles:
    """Test which roles each user type can grant"""

    def test_admin_can_grant_all_roles(self):
        """Admin should be able to grant admin, coach, and user roles"""
        admin = User(
            user_id=str(uuid4()),
            username="admin",
            email="admin@test.com",
            hash="hash",
            role=UserRoleEnum.admin
        )

        roles = admin.can_grant_roles()

        assert "admin" in roles
        assert "coach" in roles
        assert "user" in roles
        assert len(roles) == 3

    def test_coach_can_grant_coach_and_user_roles(self):
        """Coach should only grant coach and user roles, not admin"""
        coach = User(
            user_id=str(uuid4()),
            username="coach",
            email="coach@test.com",
            hash="hash",
            role=UserRoleEnum.coach
        )

        roles = coach.can_grant_roles()

        assert "coach" in roles
        assert "user" in roles
        assert "admin" not in roles
        assert len(roles) == 2

    def test_user_cannot_grant_any_roles(self):
        """Regular user should not be able to grant any roles"""
        user = User(
            user_id=str(uuid4()),
            username="user",
            email="user@test.com",
            hash="hash",
            role=UserRoleEnum.user
        )

        roles = user.can_grant_roles()

        assert len(roles) == 0


@pytest.mark.unit
@pytest.mark.authz
class TestCanCreateUser:
    """Test user creation permissions"""

    def test_admin_can_create_admin(self):
        """Admin should be able to create another admin"""
        admin = User(
            user_id=str(uuid4()),
            username="admin",
            email="admin@test.com",
            hash="hash",
            role=UserRoleEnum.admin
        )
        new_admin = UserCreate(
            username="new_admin",
            email="new@test.com",
            password="Pass123!",
            role=UserRoleEnum.admin
        )

        assert admin.can_create_user(new_admin) is True

    def test_admin_can_create_coach(self):
        """Admin should be able to create coach"""
        admin = User(
            user_id=str(uuid4()),
            username="admin",
            email="admin@test.com",
            hash="hash",
            role=UserRoleEnum.admin
        )
        new_coach = UserCreate(
            username="new_coach",
            email="coach@test.com",
            password="Pass123!",
            role=UserRoleEnum.coach
        )

        assert admin.can_create_user(new_coach) is True

    def test_admin_can_create_user(self):
        """Admin should be able to create regular user"""
        admin = User(
            user_id=str(uuid4()),
            username="admin",
            email="admin@test.com",
            hash="hash",
            role=UserRoleEnum.admin
        )
        new_user = UserCreate(
            username="new_user",
            email="user@test.com",
            password="Pass123!",
            role=UserRoleEnum.user
        )

        assert admin.can_create_user(new_user) is True

    def test_coach_can_create_coach(self):
        """Coach should be able to create another coach"""
        coach = User(
            user_id=str(uuid4()),
            username="coach",
            email="coach@test.com",
            hash="hash",
            role=UserRoleEnum.coach
        )
        new_coach = UserCreate(
            username="new_coach",
            email="coach2@test.com",
            password="Pass123!",
            role=UserRoleEnum.coach
        )

        assert coach.can_create_user(new_coach) is True

    def test_coach_can_create_user(self):
        """Coach should be able to create regular user"""
        coach = User(
            user_id=str(uuid4()),
            username="coach",
            email="coach@test.com",
            hash="hash",
            role=UserRoleEnum.coach
        )
        new_user = UserCreate(
            username="new_user",
            email="user@test.com",
            password="Pass123!",
            role=UserRoleEnum.user
        )

        assert coach.can_create_user(new_user) is True

    def test_coach_cannot_create_admin(self):
        """Coach should NOT be able to create admin"""
        coach = User(
            user_id=str(uuid4()),
            username="coach",
            email="coach@test.com",
            hash="hash",
            role=UserRoleEnum.coach
        )
        new_admin = UserCreate(
            username="new_admin",
            email="admin@test.com",
            password="Pass123!",
            role=UserRoleEnum.admin
        )

        assert coach.can_create_user(new_admin) is False

    def test_user_cannot_create_any_user(self):
        """Regular user should not be able to create any users"""
        user = User(
            user_id=str(uuid4()),
            username="user",
            email="user@test.com",
            hash="hash",
            role=UserRoleEnum.user
        )
        new_user = UserCreate(
            username="another_user",
            email="another@test.com",
            password="Pass123!",
            role=UserRoleEnum.user
        )

        assert user.can_create_user(new_user) is False


@pytest.mark.unit
@pytest.mark.authz
class TestCanDeleteUser:
    """Test user deletion permissions"""

    def test_admin_can_delete_admin(self):
        """Admin should be able to delete another admin"""
        admin = User(
            user_id=str(uuid4()),
            username="admin",
            email="admin@test.com",
            hash="hash",
            role=UserRoleEnum.admin
        )
        target_admin = User(
            user_id=str(uuid4()),
            username="target_admin",
            email="target@test.com",
            hash="hash",
            role=UserRoleEnum.admin
        )

        assert admin.can_delete_user(target_admin) is True

    def test_admin_can_delete_coach(self):
        """Admin should be able to delete coach"""
        admin = User(
            user_id=str(uuid4()),
            username="admin",
            email="admin@test.com",
            hash="hash",
            role=UserRoleEnum.admin
        )
        coach = User(
            user_id=str(uuid4()),
            username="coach",
            email="coach@test.com",
            hash="hash",
            role=UserRoleEnum.coach
        )

        assert admin.can_delete_user(coach) is True

    def test_admin_can_delete_user(self):
        """Admin should be able to delete regular user"""
        admin = User(
            user_id=str(uuid4()),
            username="admin",
            email="admin@test.com",
            hash="hash",
            role=UserRoleEnum.admin
        )
        user = User(
            user_id=str(uuid4()),
            username="user",
            email="user@test.com",
            hash="hash",
            role=UserRoleEnum.user
        )

        assert admin.can_delete_user(user) is True

    def test_coach_cannot_delete_admin(self):
        """Coach should NOT be able to delete admin"""
        coach = User(
            user_id=str(uuid4()),
            username="coach",
            email="coach@test.com",
            hash="hash",
            role=UserRoleEnum.coach
        )
        admin = User(
            user_id=str(uuid4()),
            username="admin",
            email="admin@test.com",
            hash="hash",
            role=UserRoleEnum.admin
        )

        assert coach.can_delete_user(admin) is False

    def test_coach_can_delete_coach(self):
        """Coach should be able to delete another coach"""
        coach = User(
            user_id=str(uuid4()),
            username="coach",
            email="coach@test.com",
            hash="hash",
            role=UserRoleEnum.coach
        )
        target_coach = User(
            user_id=str(uuid4()),
            username="target_coach",
            email="target@test.com",
            hash="hash",
            role=UserRoleEnum.coach
        )

        assert coach.can_delete_user(target_coach) is True

    def test_coach_can_delete_user(self):
        """Coach should be able to delete regular user"""
        coach = User(
            user_id=str(uuid4()),
            username="coach",
            email="coach@test.com",
            hash="hash",
            role=UserRoleEnum.coach
        )
        user = User(
            user_id=str(uuid4()),
            username="user",
            email="user@test.com",
            hash="hash",
            role=UserRoleEnum.user
        )

        assert coach.can_delete_user(user) is True

    def test_user_cannot_delete_any_user(self):
        """Regular user should not be able to delete any users"""
        user1 = User(
            user_id=str(uuid4()),
            username="user1",
            email="user1@test.com",
            hash="hash",
            role=UserRoleEnum.user
        )
        user2 = User(
            user_id=str(uuid4()),
            username="user2",
            email="user2@test.com",
            hash="hash",
            role=UserRoleEnum.user
        )

        assert user1.can_delete_user(user2) is False


@pytest.mark.unit
@pytest.mark.authz
class TestCanModifyUser:
    """Test user modification permissions"""

    def test_user_can_modify_own_profile(self):
        """User should be able to modify their own profile"""
        user = User(
            user_id=str(uuid4()),
            username="user",
            email="user@test.com",
            hash="hash",
            role=UserRoleEnum.user
        )

        assert user.can_modify_user(user) is True

    def test_user_cannot_modify_other_users(self):
        """User should not be able to modify other users"""
        user1 = User(
            user_id=str(uuid4()),
            username="user1",
            email="user1@test.com",
            hash="hash",
            role=UserRoleEnum.user
        )
        user2 = User(
            user_id=str(uuid4()),
            username="user2",
            email="user2@test.com",
            hash="hash",
            role=UserRoleEnum.user
        )

        assert user1.can_modify_user(user2) is False

    def test_admin_can_modify_any_user(self):
        """Admin should be able to modify any user"""
        admin = User(
            user_id=str(uuid4()),
            username="admin",
            email="admin@test.com",
            hash="hash",
            role=UserRoleEnum.admin
        )
        user = User(
            user_id=str(uuid4()),
            username="user",
            email="user@test.com",
            hash="hash",
            role=UserRoleEnum.user
        )

        assert admin.can_modify_user(user) is True

    def test_admin_can_modify_own_profile(self):
        """Admin should be able to modify their own profile"""
        admin = User(
            user_id=str(uuid4()),
            username="admin",
            email="admin@test.com",
            hash="hash",
            role=UserRoleEnum.admin
        )

        assert admin.can_modify_user(admin) is True

    def test_coach_cannot_modify_admin(self):
        """Coach should NOT be able to modify admin"""
        coach = User(
            user_id=str(uuid4()),
            username="coach",
            email="coach@test.com",
            hash="hash",
            role=UserRoleEnum.coach
        )
        admin = User(
            user_id=str(uuid4()),
            username="admin",
            email="admin@test.com",
            hash="hash",
            role=UserRoleEnum.admin
        )

        assert coach.can_modify_user(admin) is False

    def test_coach_can_modify_coach(self):
        """Coach should be able to modify another coach"""
        coach1 = User(
            user_id=str(uuid4()),
            username="coach1",
            email="coach1@test.com",
            hash="hash",
            role=UserRoleEnum.coach
        )
        coach2 = User(
            user_id=str(uuid4()),
            username="coach2",
            email="coach2@test.com",
            hash="hash",
            role=UserRoleEnum.coach
        )

        assert coach1.can_modify_user(coach2) is True

    def test_coach_can_modify_user(self):
        """Coach should be able to modify regular user"""
        coach = User(
            user_id=str(uuid4()),
            username="coach",
            email="coach@test.com",
            hash="hash",
            role=UserRoleEnum.coach
        )
        user = User(
            user_id=str(uuid4()),
            username="user",
            email="user@test.com",
            hash="hash",
            role=UserRoleEnum.user
        )

        assert coach.can_modify_user(user) is True

    def test_coach_can_modify_own_profile(self):
        """Coach should be able to modify their own profile"""
        coach = User(
            user_id=str(uuid4()),
            username="coach",
            email="coach@test.com",
            hash="hash",
            role=UserRoleEnum.coach
        )

        assert coach.can_modify_user(coach) is True


@pytest.mark.unit
@pytest.mark.authz
class TestResourceManagementPermissions:
    """Test permissions for managing questions, assessments, notes, reports"""

    def test_admin_can_manage_questions(self):
        """Admin should be able to manage questions"""
        admin = User(
            user_id=str(uuid4()),
            username="admin",
            email="admin@test.com",
            hash="hash",
            role=UserRoleEnum.admin
        )

        assert admin.can_manage_questions() is True

    def test_coach_can_manage_questions(self):
        """Coach should be able to manage questions"""
        coach = User(
            user_id=str(uuid4()),
            username="coach",
            email="coach@test.com",
            hash="hash",
            role=UserRoleEnum.coach
        )

        assert coach.can_manage_questions() is True

    def test_user_cannot_manage_questions(self):
        """Regular user should NOT be able to manage questions"""
        user = User(
            user_id=str(uuid4()),
            username="user",
            email="user@test.com",
            hash="hash",
            role=UserRoleEnum.user
        )

        assert user.can_manage_questions() is False

    def test_admin_can_manage_assessments(self):
        """Admin should be able to manage assessments"""
        admin = User(
            user_id=str(uuid4()),
            username="admin",
            email="admin@test.com",
            hash="hash",
            role=UserRoleEnum.admin
        )

        assert admin.can_manage_assessments() is True

    def test_coach_can_manage_assessments(self):
        """Coach should be able to manage assessments"""
        coach = User(
            user_id=str(uuid4()),
            username="coach",
            email="coach@test.com",
            hash="hash",
            role=UserRoleEnum.coach
        )

        assert coach.can_manage_assessments() is True

    def test_user_cannot_manage_assessments(self):
        """Regular user should NOT be able to manage assessments"""
        user = User(
            user_id=str(uuid4()),
            username="user",
            email="user@test.com",
            hash="hash",
            role=UserRoleEnum.user
        )

        assert user.can_manage_assessments() is False

    def test_admin_can_manage_notes(self):
        """Admin should be able to manage notes"""
        admin = User(
            user_id=str(uuid4()),
            username="admin",
            email="admin@test.com",
            hash="hash",
            role=UserRoleEnum.admin
        )

        assert admin.can_manage_notes() is True

    def test_coach_can_manage_notes(self):
        """Coach should be able to manage notes"""
        coach = User(
            user_id=str(uuid4()),
            username="coach",
            email="coach@test.com",
            hash="hash",
            role=UserRoleEnum.coach
        )

        assert coach.can_manage_notes() is True

    def test_user_cannot_manage_notes(self):
        """Regular user should NOT be able to manage notes"""
        user = User(
            user_id=str(uuid4()),
            username="user",
            email="user@test.com",
            hash="hash",
            role=UserRoleEnum.user
        )

        assert user.can_manage_notes() is False

    def test_admin_can_manage_reports(self):
        """Admin should be able to manage reports"""
        admin = User(
            user_id=str(uuid4()),
            username="admin",
            email="admin@test.com",
            hash="hash",
            role=UserRoleEnum.admin
        )

        assert admin.can_manage_reports() is True

    def test_coach_can_manage_reports(self):
        """Coach should be able to manage reports"""
        coach = User(
            user_id=str(uuid4()),
            username="coach",
            email="coach@test.com",
            hash="hash",
            role=UserRoleEnum.coach
        )

        assert coach.can_manage_reports() is True

    def test_user_cannot_manage_reports(self):
        """Regular user should NOT be able to manage reports"""
        user = User(
            user_id=str(uuid4()),
            username="user",
            email="user@test.com",
            hash="hash",
            role=UserRoleEnum.user
        )

        assert user.can_manage_reports() is False

    def test_admin_can_send_emails(self):
        """Admin should be able to send emails"""
        admin = User(
            user_id=str(uuid4()),
            username="admin",
            email="admin@test.com",
            hash="hash",
            role=UserRoleEnum.admin
        )

        assert admin.can_send_emails() is True

    def test_coach_can_send_emails(self):
        """Coach should be able to send emails"""
        coach = User(
            user_id=str(uuid4()),
            username="coach",
            email="coach@test.com",
            hash="hash",
            role=UserRoleEnum.coach
        )

        assert coach.can_send_emails() is True

    def test_user_cannot_send_emails(self):
        """Regular user should NOT be able to send emails"""
        user = User(
            user_id=str(uuid4()),
            username="user",
            email="user@test.com",
            hash="hash",
            role=UserRoleEnum.user
        )

        assert user.can_send_emails() is False
