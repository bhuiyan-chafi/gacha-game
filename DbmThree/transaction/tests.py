from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from unittest.mock import patch, MagicMock
from transaction.models import InGameCurrencyTransaction


class PlayerGameCurrencyTests(APITestCase):

    def setUp(self):
        self.player_id = 1
        self.transaction = InGameCurrencyTransaction.objects.create(
            player_id=self.player_id,
            amount=100.0
        )

    def tearDown(self):
        result = self.defaultTestResult()
        self._feedErrorsToResult(result, self._outcome.errors)
        if not result.failures and not result.errors:
            print(f"{self._testMethodName}: passed")
        else:
            for _, err in result.failures + result.errors:
                print(f"{self._testMethodName} failed: {err}")

    def test_player_game_currency_transactions_success(self):
        """Test retrieving transactions for a player with existing records."""
        url = reverse('player-transaction', args=[self.player_id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['amount'], self.transaction.amount)

    def test_player_game_currency_transactions_no_records(self):
        """Test retrieving transactions for a player with no records."""
        url = reverse('player-transaction', args=[999])  # Nonexistent player
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data['detail'],
                         "No transactions found for player 999.")

    @patch('requests.get')
    @patch('requests.put')
    def test_player_game_currency_purchase_success(self, mock_put, mock_get):
        """Test purchasing game currency successfully."""
        mock_get.return_value = MagicMock(
            status_code=200, json=lambda: {"current_balance": 50.0}
        )
        mock_put.return_value = MagicMock(status_code=200)

        url = reverse('player-game-currency-purchase', args=[self.player_id])
        data = {'cash_amount': 10.0}  # Expecting 100 game currency to be added
        response = self.client.post(url, data)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["detail"],
                         "Game currency purchased successfully.")
        self.assertEqual(response.data["transaction"]["amount"], 100.0)
        self.assertEqual(response.data["new_balance"], "150.00")  # 50 + 100
