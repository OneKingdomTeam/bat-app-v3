"""
Authorization Matrix E2E Tests - **MOST CRITICAL TEST FILE**

This file tests the complete authorization matrix for the BAT application.
It verifies that all endpoints enforce proper role-based access control (RBAC):

- Admin: Full access to all endpoints
- Coach: Access to dashboard (except settings), no admin-only features
- User: Access to own data in /app routes only, no dashboard access

The matrix tests:
1. Settings endpoints (admin-only)
2. Dashboard endpoints (admin + coach)
3. App endpoints (all authenticated users, with data isolation)
4. Public endpoints (unauthenticated access)
"""

import pytest


@pytest.mark.e2e
@pytest.mark.authz
class TestSettingsEndpointsAdminOnly:
    """Settings endpoints should be accessible ONLY to admins"""

    @pytest.mark.parametrize("role,expected_status", [
        ("admin", 200),
        ("coach", 403),
        ("user", 403),
    ])
    def test_settings_page_access_by_role(self, authenticated_client, role, expected_status):
        """GET /dashboard/settings - Admin only"""
        client = authenticated_client(role)
        response = client.get("/dashboard/settings")

        assert response.status_code == expected_status

    @pytest.mark.parametrize("role,expected_status", [
        ("admin", 200),
        ("coach", 403),
        ("user", 403),
    ])
    def test_settings_branding_partial_access_by_role(self, authenticated_client, role, expected_status):
        """GET /dashboard/settings/branding - Admin only"""
        client = authenticated_client(role)
        response = client.get("/dashboard/settings/branding")

        assert response.status_code == expected_status

    def test_update_branding_as_admin_succeeds(self, authenticated_client):
        """POST /dashboard/settings/branding - Admin can update"""
        client = authenticated_client("admin")
        response = client.post("/dashboard/settings/branding", data={
            "organization_name": "Test Organization",
            "organization_website": "https://test.com",
            "feedback_url": "https://feedback.test.com",
            "feedback_button_text": "Feedback"
        })

        # Should succeed (200 OK or 303 redirect)
        assert response.status_code in [200, 303]

    def test_update_branding_as_coach_fails(self, authenticated_client):
        """POST /dashboard/settings/branding - Coach cannot update"""
        client = authenticated_client("coach")
        response = client.post("/dashboard/settings/branding", data={
            "organization_name": "Hacked Organization"
        })

        assert response.status_code == 403

    def test_update_branding_as_user_fails(self, authenticated_client):
        """POST /dashboard/settings/branding - User cannot update"""
        client = authenticated_client("user")
        response = client.post("/dashboard/settings/branding", data={
            "organization_name": "Hacked Organization"
        })

        assert response.status_code == 403


@pytest.mark.e2e
@pytest.mark.authz
class TestDashboardUsersEndpoints:
    """Dashboard users endpoints should be accessible to admin and coach"""

    @pytest.mark.parametrize("role,expected_status", [
        ("admin", 200),
        ("coach", 200),
        ("user", 303),  # Redirected to login
    ])
    def test_users_list_access_by_role(self, authenticated_client, role, expected_status):
        """GET /dashboard/users - Admin and Coach only"""
        client = authenticated_client(role)
        response = client.get("/dashboard/users")

        assert response.status_code == expected_status

    @pytest.mark.parametrize("role,expected_status", [
        ("admin", 200),
        ("coach", 200),
        ("user", 303),
    ])
    def test_add_user_page_access_by_role(self, authenticated_client, role, expected_status):
        """GET /dashboard/users/add - Admin and Coach only"""
        client = authenticated_client(role)
        response = client.get("/dashboard/users/add")

        assert response.status_code == expected_status

    def test_admin_can_access_any_user_edit_page(self, authenticated_client, coach_user):
        """Admin should be able to access edit page for any user"""
        client = authenticated_client("admin")
        response = client.get(f"/dashboard/users/{coach_user.user_id}")

        assert response.status_code == 200

    def test_coach_cannot_access_admin_edit_page(self, authenticated_client, admin_user):
        """Coach should NOT be able to access admin edit page"""
        client = authenticated_client("coach")
        response = client.get(f"/dashboard/users/{admin_user.user_id}")

        # Should fail (403 or redirect)
        assert response.status_code in [403, 303]

    def test_user_cannot_access_dashboard_users(self, authenticated_client):
        """Regular user should not access dashboard users page"""
        client = authenticated_client("user")
        response = client.get("/dashboard/users")

        # Redirect to login or access denied
        assert response.status_code == 303


@pytest.mark.e2e
@pytest.mark.authz
class TestDashboardQuestionsEndpoints:
    """Dashboard questions endpoints should be accessible to admin and coach"""

    @pytest.mark.parametrize("role,expected_status", [
        ("admin", 200),
        ("coach", 200),
        ("user", 303),
    ])
    def test_questions_list_access_by_role(self, authenticated_client, role, expected_status):
        """GET /dashboard/questions - Admin and Coach only"""
        client = authenticated_client(role)
        response = client.get("/dashboard/questions")

        assert response.status_code == expected_status

    @pytest.mark.parametrize("role,expected_status", [
        ("admin", 200),
        ("coach", 200),
        ("user", 303),
    ])
    def test_questions_reorder_page_access_by_role(self, authenticated_client, role, expected_status):
        """GET /dashboard/questions/reorder - Admin and Coach only"""
        client = authenticated_client(role)
        response = client.get("/dashboard/questions/reorder")

        assert response.status_code == expected_status


@pytest.mark.e2e
@pytest.mark.authz
class TestDashboardAssessmentsEndpoints:
    """Dashboard assessments endpoints should be accessible to admin and coach"""

    @pytest.mark.parametrize("role,expected_status", [
        ("admin", 200),
        ("coach", 200),
        ("user", 303),
    ])
    def test_assessments_list_access_by_role(self, authenticated_client, role, expected_status):
        """GET /dashboard/assessments - Admin and Coach only"""
        client = authenticated_client(role)
        response = client.get("/dashboard/assessments")

        assert response.status_code == expected_status

    @pytest.mark.parametrize("role,expected_status", [
        ("admin", 200),
        ("coach", 200),
        ("user", 303),
    ])
    def test_create_assessment_page_access_by_role(self, authenticated_client, role, expected_status):
        """GET /dashboard/assessments/create - Admin and Coach only"""
        client = authenticated_client(role)
        response = client.get("/dashboard/assessments/create")

        assert response.status_code == expected_status


@pytest.mark.e2e
@pytest.mark.authz
class TestDashboardReportsEndpoints:
    """Dashboard reports endpoints should be accessible to admin and coach"""

    @pytest.mark.parametrize("role,expected_status", [
        ("admin", 200),
        ("coach", 200),
        ("user", 303),
    ])
    def test_reports_list_access_by_role(self, authenticated_client, role, expected_status):
        """GET /dashboard/reports - Admin and Coach only"""
        client = authenticated_client(role)
        response = client.get("/dashboard/reports")

        assert response.status_code == expected_status

    @pytest.mark.parametrize("role,expected_status", [
        ("admin", 200),
        ("coach", 200),
        ("user", 303),
    ])
    def test_create_report_page_access_by_role(self, authenticated_client, role, expected_status):
        """GET /dashboard/reports/create - Admin and Coach only"""
        client = authenticated_client(role)
        response = client.get("/dashboard/reports/create")

        assert response.status_code == expected_status


@pytest.mark.e2e
@pytest.mark.authz
class TestDashboardGeneralEndpoints:
    """General dashboard endpoint access"""

    @pytest.mark.parametrize("role,expected_status", [
        ("admin", 200),
        ("coach", 200),
        ("user", 303),
    ])
    def test_dashboard_home_access_by_role(self, authenticated_client, role, expected_status):
        """GET /dashboard - Admin and Coach only"""
        client = authenticated_client(role)
        response = client.get("/dashboard")

        assert response.status_code == expected_status


@pytest.mark.e2e
@pytest.mark.authz
class TestAppEndpointsAllRoles:
    """App endpoints should be accessible to all authenticated users (with data isolation)"""

    @pytest.mark.parametrize("role", ["admin", "coach", "user"])
    def test_app_profile_access_by_role(self, authenticated_client, role):
        """GET /app/profile - All roles can access their profile"""
        client = authenticated_client(role)
        response = client.get("/app/profile")

        # All authenticated users should be able to access their profile
        assert response.status_code == 200

    @pytest.mark.parametrize("role", ["admin", "coach", "user"])
    def test_app_assessments_access_by_role(self, authenticated_client, role):
        """GET /app/assessments - All roles can access their assessments"""
        client = authenticated_client(role)
        response = client.get("/app/assessments")

        # All authenticated users should see their assessments
        assert response.status_code == 200


@pytest.mark.e2e
@pytest.mark.authz
class TestPublicEndpointsUnauthenticated:
    """Public endpoints should be accessible without authentication"""

    def test_homepage_accessible(self, test_client):
        """GET / - Homepage should be accessible"""
        response = test_client.get("/")

        assert response.status_code == 200

    def test_login_page_accessible(self, test_client):
        """GET /login - Login page should be accessible"""
        response = test_client.get("/login")

        assert response.status_code == 200

    def test_password_reset_page_accessible(self, test_client):
        """GET /password-reset - Password reset page should be accessible"""
        response = test_client.get("/password-reset")

        assert response.status_code == 200


@pytest.mark.e2e
@pytest.mark.authz
class TestUnauthenticatedAccessToProtectedEndpoints:
    """Unauthenticated users should be redirected from protected endpoints"""

    def test_unauthenticated_dashboard_access_redirects(self, test_client):
        """Unauthenticated access to dashboard should redirect to login"""
        response = test_client.get("/dashboard", follow_redirects=False)

        # Should redirect to login (303 or 302)
        assert response.status_code in [303, 302]

    def test_unauthenticated_settings_access_redirects(self, test_client):
        """Unauthenticated access to settings should redirect to login"""
        response = test_client.get("/dashboard/settings", follow_redirects=False)

        assert response.status_code in [303, 302]

    def test_unauthenticated_app_profile_access_redirects(self, test_client):
        """Unauthenticated access to profile should redirect to login"""
        response = test_client.get("/app/profile", follow_redirects=False)

        assert response.status_code in [303, 302]


@pytest.mark.e2e
@pytest.mark.authz
class TestCrossRoleDataIsolation:
    """Users should only be able to access their own data"""

    def test_user_cannot_access_another_users_profile(self, authenticated_client, regular_user, another_user):
        """User should not be able to modify another user's profile"""
        client = authenticated_client("user")

        # Try to update another user's profile (regular_user trying to update another_user)
        response = client.put(f"/dashboard/users/{another_user.user_id}", data={
            "username": "hacked_username",
            "email": another_user.email,
            "role": "user"
        })

        # Should fail - user doesn't have access to dashboard users endpoint
        assert response.status_code == 303  # Redirect to login

    def test_admin_can_access_all_user_profiles(self, authenticated_client, coach_user, regular_user):
        """Admin should be able to access any user's profile"""
        client = authenticated_client("admin")

        # Admin accessing coach profile
        response = client.get(f"/dashboard/users/{coach_user.user_id}")
        assert response.status_code == 200

        # Admin accessing regular user profile
        response = client.get(f"/dashboard/users/{regular_user.user_id}")
        assert response.status_code == 200

    def test_coach_can_access_user_profiles_not_admin(self, authenticated_client, admin_user, regular_user):
        """Coach should access user profiles but not admin profiles"""
        client = authenticated_client("coach")

        # Coach accessing regular user - should succeed
        response = client.get(f"/dashboard/users/{regular_user.user_id}")
        assert response.status_code == 200

        # Coach accessing admin - should fail
        response = client.get(f"/dashboard/users/{admin_user.user_id}")
        assert response.status_code in [403, 303]


@pytest.mark.e2e
@pytest.mark.authz
class TestAuthorizationMatrixSummary:
    """
    Summary verification of the complete authorization matrix.

    This test provides a comprehensive overview of the access control model.
    """

    def test_authorization_matrix_admin_full_access(self, authenticated_client):
        """Verify admin has full access to all endpoints"""
        client = authenticated_client("admin")

        endpoints_admin_should_access = [
            "/dashboard",
            "/dashboard/settings",
            "/dashboard/users",
            "/dashboard/questions",
            "/dashboard/assessments",
            "/dashboard/reports",
            "/app/profile",
            "/app/assessments",
        ]

        for endpoint in endpoints_admin_should_access:
            response = client.get(endpoint)
            assert response.status_code == 200, \
                f"Admin should have access to {endpoint}, got {response.status_code}"

    def test_authorization_matrix_coach_dashboard_no_settings(self, authenticated_client):
        """Verify coach has dashboard access except settings"""
        client = authenticated_client("coach")

        # Coach should access these
        coach_accessible = [
            "/dashboard",
            "/dashboard/users",
            "/dashboard/questions",
            "/dashboard/assessments",
            "/dashboard/reports",
            "/app/profile",
            "/app/assessments",
        ]

        for endpoint in coach_accessible:
            response = client.get(endpoint)
            assert response.status_code == 200, \
                f"Coach should have access to {endpoint}, got {response.status_code}"

        # Coach should NOT access settings
        response = client.get("/dashboard/settings")
        assert response.status_code == 403, \
            f"Coach should NOT have access to settings, got {response.status_code}"

    def test_authorization_matrix_user_app_only(self, authenticated_client):
        """Verify user has access only to /app endpoints, not dashboard"""
        client = authenticated_client("user")

        # User should access these
        user_accessible = [
            "/app/profile",
            "/app/assessments",
        ]

        for endpoint in user_accessible:
            response = client.get(endpoint)
            assert response.status_code == 200, \
                f"User should have access to {endpoint}, got {response.status_code}"

        # User should NOT access any dashboard endpoints
        dashboard_endpoints = [
            "/dashboard",
            "/dashboard/settings",
            "/dashboard/users",
            "/dashboard/questions",
            "/dashboard/assessments",
            "/dashboard/reports",
        ]

        for endpoint in dashboard_endpoints:
            response = client.get(endpoint)
            assert response.status_code == 303, \
                f"User should NOT have access to {endpoint}, got {response.status_code}"
