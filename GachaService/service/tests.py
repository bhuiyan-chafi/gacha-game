import json
from unittest.mock import patch, Mock
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status


class GachaServiceTests(APITestCase):

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
    def test_list_of_gacha(self, mock_get, mock_verify_token):
        """Test listing all Gachas."""
        # Mock verifyToken to always return True
        mock_verify_token.return_value = True

        # Mock requests.get to simulate a successful response
        mock_get.return_value = Mock(status_code=200, json=lambda: [
            {"id": 1, "name": "Gacha1"},
            {"id": 2, "name": "Gacha2"},
        ])

        # Perform the GET request
        response = self.client.get(
            reverse('gacha-list'), headers=self.auth_headers)

        # Assertions
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), [
            {"id": 1, "name": "Gacha1"},
            {"id": 2, "name": "Gacha2"},
        ])

    @patch('service.helper.verifyToken')
    @patch('requests.post')
    def test_create_gacha(self, mock_post, mock_verify_token):
        """Test creating a Gacha."""
        # Mock verifyToken to always return True
        mock_verify_token.return_value = True

        # Mock requests.post to simulate a successful response
        mock_post.return_value = Mock(
            status_code=201,
            json=Mock(return_value={"detail": "Gacha created successfully."}),
        )

        # Perform the POST request
        response = self.client.post(
            reverse('create-gacha'),
            data=json.dumps({
                "name": "Teemu",
                "rarity": 95,
                "inventory": 12,
                "price": 150,
                "status": "active",
                "description": "teemu is .....",
                "image": "teemu.png"
            }),
            content_type='application/json',
            headers=self.auth_headers,
        )

        # Assertions
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json(), {
                         "detail": "Gacha created successfully."})

    @patch('service.helper.verifyToken')
    @patch('requests.get')
    def test_gacha_details(self, mock_get, mock_verify_token):
        """Test fetching Gacha details."""
        # Mock verifyToken to always return True
        mock_verify_token.return_value = True

        # Mock requests.get to simulate a successful response
        mock_get.return_value = Mock(
            status_code=200,
            json=Mock(return_value={"id": 1, "name": "Gacha1", "rarity": 5}),
        )

        # Perform the GET request
        response = self.client.get(
            reverse('gacha-details', args=[1]), headers=self.auth_headers
        )

        # Assertions
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {
                         "id": 1, "name": "Gacha1", "rarity": 5})

    @patch('service.helper.verifyToken')
    @patch('requests.put')
    def test_update_gacha_details(self, mock_put, mock_verify_token):
        """Test updating Gacha details."""
        # Mock verifyToken to always return True
        mock_verify_token.return_value = True

        # Mock requests.put to simulate a successful response
        mock_put.return_value = Mock(
            status_code=200,
            json=Mock(return_value={"detail": "Gacha updated successfully."}),
        )

        # Perform the PUT request
        response = self.client.put(
            reverse('gacha-details', args=[1]),
            data=json.dumps({"name": "UpdatedGacha"}),
            content_type='application/json',
            headers=self.auth_headers,
        )

        # Assertions
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {
                         "detail": "Gacha updated successfully."})

    @patch('service.helper.verifyToken')
    @patch('requests.delete')
    def test_delete_gacha(self, mock_delete, mock_verify_token):
        """Test deleting a Gacha."""
        # Mock verifyToken to always return True
        mock_verify_token.return_value = True

        # Mock requests.delete to simulate a successful response
        mock_delete.return_value = Mock(
            status_code=204,
            json=Mock(return_value={"detail": "Operation successful."}),
        )

        # Perform the DELETE request
        response = self.client.delete(
            reverse('gacha-delete', args=[1]), headers=self.auth_headers
        )

        # Assertions
        self.assertEqual(response.status_code, 204)
