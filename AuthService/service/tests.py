from unittest.mock import patch, Mock
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from service.jwt_utils import generate_jwt


class AuthAppTests(APITestCase):

    def setUp(self):
        # Mock JWT token generation for admin and player roles
        self.admin_token = generate_jwt({
            "user_id": 1,
            "username": "adminuser",
            "role": "admin",
            "status": "active"
        })

        self.player_token = generate_jwt({
            "user_id": 2,
            "username": "playeruser",
            "role": "player",
            "status": "active"
        })

    def tearDown(self):
        # Check if the current test case passed
        result = self.defaultTestResult()
        self._feedErrorsToResult(result, self._outcome.errors)
        if not result.failures and not result.errors:
            print(f"{self._testMethodName}: passed")

    @patch('requests.get')
    def test_auth_app_test(self, mock_get):
        """Test the health-check endpoint."""
        mock_get.return_value = Mock(status_code=200, json=lambda: {
                                     "detail": "Core service is running"})
        response = self.client.get(reverse('test-auth-service'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {
                         "detail": "Core service is running"})

    @patch('requests.post')
    @patch('service.decorators.decode_jwt')
    def test_verify_token_valid(self, mock_decode_jwt, mock_post):
        """Test token verification with valid role."""
        mock_decode_jwt.return_value = {
            "user_id": 1, "role": "admin", "username": "adminuser"}
        mock_post.return_value = Mock(
            status_code=200, json=lambda: {"token": "valid"})

        response = self.client.post(
            reverse('verify-token'),
            HTTP_AUTHORIZATION=f"Bearer {self.admin_token}",
            headers={"Role": "admin"}
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"token": "valid"})

    @patch('requests.post')
    def test_create_user(self, mock_post):
        """Test user creation."""
        mock_post.return_value = Mock(status_code=201, json=lambda: {
                                      "detail": "User created"})
        response = self.client.post(reverse('create-user'), data={
            "username": "newuser",
            "password": "Secure@123",
            "role": "player"
        })
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json(), {"detail": "User created"})

    @patch('requests.get')
    @patch('service.decorators.decode_jwt')
    def test_list_users(self, mock_decode_jwt, mock_get):
        """Test listing users."""
        mock_decode_jwt.return_value = {
            "user_id": 1, "role": "admin", "username": "adminuser"}
        mock_get.return_value = Mock(status_code=200, json=lambda: [
                                     {"id": 1, "username": "adminuser"}])

        response = self.client.get(
            reverse('list-user'), HTTP_AUTHORIZATION=f"Bearer {self.admin_token}")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), [{"id": 1, "username": "adminuser"}])

    @patch('requests.get')
    @patch('service.decorators.decode_jwt')
    def test_user_details_get(self, mock_decode_jwt, mock_get):
        """Test fetching user details."""
        mock_decode_jwt.return_value = {
            "user_id": 2, "role": "player", "username": "playeruser"}
        mock_get.return_value = Mock(status_code=200, json=lambda: {
                                     "id": 2, "username": "playeruser"})

        response = self.client.get(
            reverse('user-details', args=[2]),
            HTTP_AUTHORIZATION=f"Bearer {self.player_token}"
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"id": 2, "username": "playeruser"})

    @patch('requests.delete')
    @patch('service.decorators.decode_jwt')
    def test_delete_user(self, mock_decode_jwt, mock_delete):
        """Test deleting a user."""
        mock_decode_jwt.return_value = {
            "user_id": 1, "role": "admin", "username": "adminuser"}
        mock_delete.return_value = Mock(status_code=204)

        response = self.client.delete(
            reverse('delete-user', args=[2]),
            HTTP_AUTHORIZATION=f"Bearer {self.admin_token}"
        )
        self.assertEqual(response.status_code, 204)

    @patch('requests.post')
    def test_login_user(self, mock_post):
        """Test user login."""
        mock_post.return_value = Mock(status_code=200, json=lambda: {
            "user": {"id": 1, "username": "adminuser", "role": "admin", "status": "active"}
        })

        response = self.client.post(reverse('user-login'), data={
            "username": "adminuser",
            "password": "Admin@123"
        })
        self.assertEqual(response.status_code, 200)
        self.assertIn("access_token", response.json())
        self.assertEqual(response.json()["user"]["username"], "adminuser")

    @patch('requests.post')
    @patch('service.decorators.decode_jwt')
    def test_logout_user(self, mock_decode_jwt, mock_post):
        """Test user logout."""
        mock_decode_jwt.return_value = {
            "user_id": 1, "role": "admin", "username": "adminuser"}
        mock_post.return_value = Mock(status_code=200, json=lambda: {
                                      "detail": "Logged out successfully"})

        response = self.client.post(
            reverse('user-logout', args=[1]),
            HTTP_AUTHORIZATION=f"Bearer {self.admin_token}"
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {
                         "detail": "Logged out successfully"})
