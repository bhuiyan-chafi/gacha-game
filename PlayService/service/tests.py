import json
from unittest.mock import patch, Mock
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status


class PlayServiceTests(APITestCase):

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
    def test_player_gacha_collections(self, mock_get, mock_verify_token):
        """Test fetching a player's gacha collection."""
        # Mock token validation
        mock_verify_token.return_value = True

        # Mock external GET request
        mock_get.return_value = Mock(
            status_code=200,
            json=Mock(return_value=[
                {"gacha_id": 1, "gacha_name": "RareGacha"},
                {"gacha_id": 2, "gacha_name": "UltraGacha"},
            ])
        )

        # Perform the GET request
        response = self.client.get(
            reverse('player-collection', args=[1]),
            headers=self.auth_headers
        )

        # Assertions
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), [
            {"gacha_id": 1, "gacha_name": "RareGacha"},
            {"gacha_id": 2, "gacha_name": "UltraGacha"},
        ])

    @patch('service.helper.verifyToken')
    @patch('requests.get')
    def test_player_gacha_collection_details(self, mock_get, mock_verify_token):
        """Test fetching a specific player's gacha collection."""
        # Mock token validation
        mock_verify_token.return_value = True

        # Mock external GET request
        mock_get.return_value = Mock(
            status_code=200,
            json=Mock(return_value={"gacha_id": 1, "gacha_name": "RareGacha"})
        )

        # Perform the GET request
        response = self.client.get(
            reverse('player-collection-details', args=[1]),
            headers=self.auth_headers
        )

        # Assertions
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {
                         "gacha_id": 1, "gacha_name": "RareGacha"})

    @patch('service.helper.verifyToken')
    @patch('requests.delete')
    def test_delete_player_gacha_collection(self, mock_delete, mock_verify_token):
        """Test deleting a player's gacha collection."""
        # Mock token validation
        mock_verify_token.return_value = True

        # Mock external DELETE request
        mock_delete.return_value = Mock(
            status_code=204,
            json=Mock(return_value={"detail": "Operation successful."})
        )

        # Perform the DELETE request
        response = self.client.delete(
            reverse('player-collection-details', args=[1]),
            headers=self.auth_headers
        )

        # Assertions
        self.assertEqual(response.status_code, 204)

    @patch('service.helper.verifyToken')
    @patch('requests.get')
    @patch('requests.post')
    def test_roll_to_win_gacha(self, mock_post, mock_get, mock_verify_token):
        """Test rolling to win a gacha."""
        # Mock token validation
        mock_verify_token.return_value = True

        # Mock user-service validation response
        mock_get.return_value = Mock(
            status_code=200,
            json=Mock(return_value={
                "id": 1,
                "current_balance": 500
            })
        )

        # Mock external POST request
        mock_post.return_value = Mock(
            status_code=200,
            json=Mock(return_value={"gacha_id": 1, "gacha_name": "RareGacha"})
        )

        # Perform the POST request
        response = self.client.post(
            reverse('roll-to-win') + "?player_id=1",
            data=json.dumps({"roll_price": 100}),
            content_type='application/json',
            headers=self.auth_headers,
        )
        # Debugging: Print response details
        # print("Response Status Code:", response.status_code)
        # print("Response Data:", response.data)

        # Assertions
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {
            "gacha_id": 1,
            "gacha_name": "RareGacha"
        })

    @patch('service.helper.verifyToken')
    @patch('requests.get')
    @patch('requests.post')
    def test_create_player_gacha_by_purchase(self, mock_post, mock_get, mock_verify_token):
        """Test purchasing a gacha directly."""
        # Mock token validation
        mock_verify_token.return_value = True

        # Mock player gacha collection response
        mock_get.side_effect = [
            Mock(
                status_code=200,
                json=Mock(return_value=[
                    {"gacha_id": 1, "gacha_name": "RareGacha"},
                    {"gacha_id": 2, "gacha_name": "UltraGacha"},
                ])
            ),
            Mock(
                status_code=200,
                json=Mock(return_value={"id": 1, "current_balance": 500})
            ),
            Mock(
                status_code=200,
                json=Mock(return_value={"id": 1, "price": 100,
                                        "inventory": 10, "status": "active"})
            ),
        ]

        # Mock purchase response
        mock_post.return_value = Mock(
            status_code=200,
            json=Mock(return_value={"detail": "Gacha purchased successfully."})
        )

        # Perform the POST request
        response = self.client.post(
            reverse('direct-purchase') + "?player_id=1&gacha_id=3",
            headers=self.auth_headers
        )
        # # Debugging: Print response details
        # print("Response Status Code:", response.status_code)
        # print("Response Data:", response.data)
        # Assertions
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {
            "detail": "Gacha purchased successfully."})
