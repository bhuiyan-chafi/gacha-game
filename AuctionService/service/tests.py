import json
from unittest.mock import patch, Mock
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status


class AuctionServiceTests(APITestCase):

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
    def test_list_auctions(self, mock_get, mock_verify_token):
        """Test listing all auctions."""
        # Mock token validation
        mock_verify_token.return_value = True

        # Mock external GET request
        mock_get.return_value = Mock(
            status_code=200,
            json=Mock(return_value=[
                {"id": 1, "name": "Auction1"},
                {"id": 2, "name": "Auction2"},
            ])
        )

        # Perform the GET request
        response = self.client.get(
            reverse('list-auctions'), headers=self.auth_headers)

        # Assertions
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), [
            {"id": 1, "name": "Auction1"},
            {"id": 2, "name": "Auction2"},
        ])

    @patch('service.helper.verifyToken')
    @patch('requests.post')
    def test_create_auction(self, mock_post, mock_verify_token):
        """Test creating an auction."""
        # Mock token validation
        mock_verify_token.return_value = True

        # Mock external POST request
        mock_post.return_value = Mock(
            status_code=201,
            json=Mock(return_value={"detail": "Auction created successfully."})
        )

        # Perform the POST request
        response = self.client.post(
            reverse('create-auction'),
            data=json.dumps(
                {
                    "name": "Easter Sell",
                    "start_date": "2024-11-11T00:00:00Z",
                    "end_date": "2024-11-11T00:00:00Z",
                    "status": "inactive"
                }),
            content_type='application/json',
            headers=self.auth_headers,
        )

        # Assertions
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json(), {
                         "detail": "Auction created successfully."})

    @patch('service.helper.verifyToken')
    @patch('requests.get')
    @patch('requests.post')
    def test_place_gacha_for_auction(self, mock_post, mock_get, mock_verify_token):
        """Test placing a gacha for auction."""
        # Mock token validation
        mock_verify_token.return_value = True

        # Mock auction validation response
        mock_get.side_effect = [
            Mock(
                status_code=200,
                json=Mock(return_value={"id": 1, "status": "active"})
            ),
            Mock(
                status_code=200,
                json=Mock(return_value={"gacha_id": 1, "player_id": 1})
            )
        ]

        # Mock external POST request
        mock_post.return_value = Mock(
            status_code=200,
            json=Mock(return_value={
                      "detail": "Gacha placed for auction successfully."})
        )

        # Perform the POST request
        response = self.client.post(
            reverse('place-gacha-for-auction'),
            data=json.dumps({"auction_id": 1, "collection_id": 1}),
            content_type='application/json',
            headers=self.auth_headers,
        )

        # Assertions
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {
                         "detail": "Gacha placed for auction successfully."})

    @patch('service.helper.verifyToken')
    @patch('requests.get')
    def test_list_all_gachas_on_auction(self, mock_get, mock_verify_token):
        """Test listing all gachas on auction."""
        # Mock token validation
        mock_verify_token.return_value = True

        # Mock external GET request
        mock_get.return_value = Mock(
            status_code=200,
            json=Mock(return_value=[
                {"id": 1, "collection_id": "Gacha1"},
                {"id": 2, "collection_id": "Gacha2"},
            ])
        )

        # Perform the GET request
        response = self.client.get(
            reverse('list-gachas-on-auction', args=[1]),
            headers=self.auth_headers,
        )

        # Assertions
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), [
            {"id": 1, "collection_id": "Gacha1"},
            {"id": 2, "collection_id": "Gacha2"},
        ])

    @patch('service.helper.verifyToken')
    @patch('requests.get')
    def test_gacha_winner(self, mock_get, mock_verify_token):
        """Test determining the winner of an auction gacha."""
        # Mock token validation
        mock_verify_token.return_value = True

        # Mock bids and winner validation response
        mock_get.side_effect = [
            Mock(
                status_code=200,
                json=Mock(return_value=[
                    {"bidder_id": 1, "price": 100},
                    {"bidder_id": 2, "price": 90}
                ])
            ),
            Mock(
                status_code=200,
                json=Mock(return_value={"id": 1, "current_balance": 150})
            )
        ]

        # Mock declare winner response
        # Mock declare winner response
        with patch('requests.post') as mock_post:
            mock_post.return_value = Mock(
                status_code=200,
                json=Mock(return_value={
                    "detail": "Winner declared successfully."
                })
            )

            # Perform the GET request
            response = self.client.get(
                reverse('gacha-winner', args=[1]),
                headers=self.auth_headers,
            )

            # Assertions
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.json(), {
                "detail": "Winner declared successfully.",
                "winner": {
                    "auction_gacha_id": 1,
                    "bidder_id": 1,
                    "price": 100
                }
            })
