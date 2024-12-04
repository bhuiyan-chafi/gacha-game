import json
from unittest.mock import patch, Mock
from django.urls import reverse
from rest_framework.test import APITestCase


class UserServiceTests(APITestCase):

    def setUp(self):
        # Mock headers for authorization
        self.auth_headers = {
            "Authorization": "Bearer test_token",
        }

    def tearDown(self):
        # Check if the current test case passed
        result = self.defaultTestResult()
        self._feedErrorsToResult(result, self._outcome.errors)
        if not result.failures and not result.errors:
            print(f"{self._testMethodName}: passed")

    @patch('service.helper.verifyToken')
    @patch('requests.get')
    def test_list_players(self, mock_get, mock_verify_token):
        """Test listing players."""
        # Mock verifyToken to always return True
        mock_verify_token.return_value = True
        # Mock requests.get to simulate a successful response
        mock_get.return_value = Mock(status_code=200, json=lambda: [
                                     {"id": 1, "username": "Player1", "status": "active", "role": "player"}])

        response = self.client.get(
            reverse('list-players'), headers=self.auth_headers)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), [
                         {"id": 1, "username": "Player1", "status": "active", "role": "player"}])

    @patch('service.helper.verifyToken')
    @patch('requests.post')
    def test_create_player(self, mock_post, mock_verify_token):
        """Test creating a player."""
        mock_verify_token.return_value = True
        mock_post.return_value = Mock(
            status_code=201,
            json=Mock(return_value={"detail": "Player created successfully."})
        )

        response = self.client.post(
            reverse('create-player'),
            data=json.dumps({
                "user_id": 2,
                "first_name": "Jane",
                "last_name": "Smith",
                "email_address": "jane.smith@example.com",
                "phone_number": "0987654321",
                "bank_details": "IT234y3294y35",
                "current_balance": 50.0,
            }),
            content_type='application/json'
        )
        # Debugging: Print response details
        # print("Response Status Code:", response.status_code)
        # print("Response Data:", response.data)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json(), {
                         "detail": "Player created successfully."})

    @patch('service.helper.verifyToken')
    @patch('requests.get')
    def test_player_details(self, mock_get, mock_verify_token):
        """Test fetching player details."""
        mock_verify_token.return_value = True
        mock_get.return_value = Mock(status_code=200, json=lambda: {
                                     "id": 1, "username": "Player1", "status": "active", "role": "player"})

        response = self.client.get(
            reverse('player-details', args=[1]), headers=self.auth_headers)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {
                         "id": 1, "username": "Player1", "status": "active", "role": "player"})

    @patch('service.helper.verifyToken')
    @patch('requests.delete')
    def test_delete_player(self, mock_delete, mock_verify_token):
        """Test deleting a player."""
        # Mock token verification to return True
        mock_verify_token.return_value = True

        # Configure the mock delete request to return 204 No Content
        mock_delete.return_value = Mock(
            status_code=204,
            # This won't be returned for 204
            json=lambda: {"detail": "Operation successful."}
        )

        # Perform the DELETE request
        response = self.client.delete(
            reverse('delete-player', args=[1]), headers=self.auth_headers
        )

        # Debugging: Print response details
        print("Response Status Code:", response.status_code)
        print("Response Data:", getattr(response, 'data', None))

        # Assertions
        self.assertEqual(response.status_code, 204)

        # Only attempt to parse JSON if the response has content
        if response.status_code != 204:
            self.assertEqual(response.json(), {
                             "detail": "Operation successful."})

    @patch('service.helper.verifyToken')
    @patch('requests.get')
    def test_list_admins(self, mock_get, mock_verify_token):
        """Test listing admins."""
        mock_verify_token.return_value = True
        mock_get.return_value = Mock(status_code=200, json=lambda: [
                                     {"id": 1, "username": "Admin1", "status": "active", "role": "admin"}])

        response = self.client.get(
            reverse('list-admins'), headers=self.auth_headers)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), [
                         {"id": 1, "username": "Admin1", "status": "active", "role": "admin"}])

    @patch('service.helper.verifyToken')
    @patch('requests.post')
    def test_create_admin(self, mock_post, mock_verify_token):
        """Test creating an admin."""
        mock_verify_token.return_value = True
        # Configure the mock post request to simulate a successful response
        mock_post.return_value = Mock(
            status_code=201,
            json=Mock(return_value={"detail": "Admin created successfully."})
        )

        # Perform the POST request with properly serialized data
        response = self.client.post(
            reverse('create-admin'),
            data=json.dumps({
                "user_id": 2,
                "first_name": "Super",
                "last_name": "Admin",
                "email_address": "super.admin@example.com",
                "phone_number": "9876543210",
            }),
            content_type='application/json'
        )
        # Debugging: Print response details
        # print("Response Status Code:", response.status_code)
        # print("Response Data:", response.data)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json(), {
                         "detail": "Admin created successfully."})

    @patch('service.helper.verifyToken')
    @patch('requests.get')
    def test_admin_details(self, mock_get, mock_verify_token):
        """Test fetching admin details."""
        mock_verify_token.return_value = True
        mock_get.return_value = Mock(status_code=200, json=lambda: {
                                     "id": 1, "username": "Admin1", "status": "active", "role": "admin"})

        response = self.client.get(
            reverse('admin-details', args=[1]), headers=self.auth_headers)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {
                         "id": 1, "username": "Admin1", "status": "active", "role": "admin"})

    @patch('service.helper.verifyToken')
    @patch('requests.delete')
    def test_delete_admin(self, mock_delete, mock_verify_token):
        """Test deleting an admin."""
        # Mock token verification to return True
        mock_verify_token.return_value = True

        # Configure the mock delete request to return 204 No Content
        mock_delete.return_value = Mock(
            status_code=204,
            # This body won't be present for 204
            json=lambda: {"detail": "Operation successful."}
        )

        # Perform the DELETE request
        response = self.client.delete(
            reverse('delete-admin', args=[1]), headers=self.auth_headers
        )

        # Debugging: Print response details
        print("Response Status Code:", response.status_code)
        print("Response Data:", response.data)

        # Assertions
        self.assertEqual(response.status_code, 204)

        # Only attempt to parse JSON if the response has content
        if response.status_code != 204:
            self.assertEqual(response.json(), {
                             "detail": "Operation successful."})
