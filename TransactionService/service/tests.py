import json
from unittest.mock import patch, Mock
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status


class TransactionServiceTests(APITestCase):

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
    def test_player_game_currency_transactions(self, mock_get, mock_verify_token):
        """Test retrieving all game currency transactions for a specific player."""
        # Mock token validation
        mock_verify_token.return_value = True

        # Mock external GET request
        mock_get.return_value = Mock(
            status_code=200,
            json=Mock(return_value=[
                {"id": 1, "amount": 100},
                {"id": 2, "amount": -50},
            ])
        )

        # Perform the GET request
        response = self.client.get(
            reverse('player-transaction', args=[1]),
            headers=self.auth_headers,
        )

        # Assertions
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), [
            {"id": 1, "amount": 100},
            {"id": 2, "amount": -50},
        ])

    @patch('service.helper.verifyToken')
    @patch('requests.post')
    def test_player_game_currency_purchase(self, mock_post, mock_verify_token):
        """Test handling game currency purchases for a specific player."""
        # Mock token validation
        mock_verify_token.return_value = True

        # Mock external POST request
        mock_post.return_value = Mock(
            status_code=201,
            json=Mock(return_value={"detail": "Purchase successful."})
        )

        # Perform the POST request
        response = self.client.post(
            reverse('player-game-currency-purchase', args=[1]),
            data=json.dumps({"cash_amount": 100}),
            content_type='application/json',
            headers=self.auth_headers,
        )

        # Assertions
        self.assertEqual(response.status_code, 201)
