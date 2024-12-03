from unittest.mock import patch, MagicMock
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from .models import PlayerGachaCollection


class OwnGachaTest(APITestCase):
    def setUp(self):
        self.player_id = 1

        # Ensure a unique gacha_id for testing
        self.used_gacha_id = 101
        self.gacha_id = 102  # Unique gacha_id for the test to avoid conflicts

        # Create an existing PlayerGachaCollection for the used gacha_id
        self.collection = PlayerGachaCollection.objects.create(
            player_id=self.player_id,
            gacha_id=self.used_gacha_id
        )

        # Mock external services for player and gacha details
        self.mock_get = patch('requests.get').start()
        self.mock_put = patch('requests.put').start()

        # Add cleanup to stop mocks after tests
        self.addCleanup(patch.stopall)

    def tearDown(self):
        result = self.defaultTestResult()
        self._feedErrorsToResult(result, self._outcome.errors)
        if not result.failures and not result.errors:
            print(f"{self._testMethodName}: passed")
        else:
            for _, err in result.failures + result.errors:
                print(f"{self._testMethodName} failed: {err}")

    @patch("requests.get")
    @patch("requests.put")
    def test_roll_to_win_gacha_success(self, mock_put, mock_get):
        mock_get.side_effect = [
            MagicMock(status_code=200, json=lambda: {"current_balance": 200}),
            MagicMock(status_code=200, json=lambda: [
                {"id": 101, "rarity": 50, "status": "active", "inventory": 5},
                {"id": 102, "rarity": 50, "status": "active", "inventory": 3}
            ]),
            MagicMock(status_code=200, json=lambda: {
                "id": 101, "rarity": 50, "status": "active", "inventory": 5})
        ]

        mock_put.side_effect = [
            MagicMock(status_code=200),  # Balance update
            MagicMock(status_code=200),  # Inventory update
        ]

        # Correctly send player_id as a query parameter
        response = self.client.post(
            f"{reverse('create-player-gacha')}?player_id={self.player_id}",
            {"roll_price": 50}
        )
        # Debugging: Print the response status code and data
        # print("Response Status Code:", response.status_code)
        # Include the response body for debugging
        # print("Response Data:", response.data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn("Congratulations! You rolled and won a Gacha!",
                      response.data["detail"])

    @patch("requests.get")
    @patch("requests.put")
    def test_create_player_gacha_by_purchase_success(self, mock_put, mock_get):
        mock_get.side_effect = [
            MagicMock(status_code=200, json=lambda: {"current_balance": 500}),
            MagicMock(status_code=200, json=lambda: {
                      "price": 100, "inventory": 5}),
        ]
        mock_put.side_effect = [
            MagicMock(status_code=200),  # Balance update
            MagicMock(status_code=200),  # Inventory update
        ]
        self.mock_put.return_value = MagicMock(status_code=200)
        response = self.client.post(
            f"{reverse('create-player-gacha-purchase')}?player_id={self.player_id}&gacha_id={self.gacha_id}",
            {}
        )
        # Debugging: Print the response status code and data
        # print("Response Status Code:", response.status_code)
        # Include the response body for debugging
        # print("Response Data:", response.data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn("Gacha purchased successfully.", response.data["detail"])

    def test_player_gacha_collections(self):
        response = self.client.get(
            reverse("player-gacha-collections", args=[self.player_id])
        )
        # Debugging: Print the response status code and data
        # print("Response Status Code:", response.status_code)
        # Include the response body for debugging
        # print("Response Data:", response.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["player_id"], self.player_id)

    @patch("requests.get")
    def test_player_gacha_collection_details_success(self, mock_get):
        mock_get.return_value = MagicMock(
            status_code=200,
            json=lambda: {"id": 101, "name": "Rare Gacha", "status": "active"}
        )
        response = self.client.get(
            reverse("player-gacha-collection-details",
                    args=[self.collection.id])
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("gacha_details", response.data)

    @patch("requests.put")
    def test_player_gacha_collection_details_delete(self, mock_put):
        mock_put.return_value = MagicMock(status_code=200)
        response = self.client.delete(
            reverse("player-gacha-collection-details",
                    args=[self.collection.id])
        )
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(PlayerGachaCollection.objects.count(), 0)
