from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from unittest.mock import patch, MagicMock
from .models import Auction, AuctionGachas, AuctionGachaBid
from own_gacha.models import PlayerGachaCollection


class AuctionTestCase(APITestCase):

    def setUp(self):
        # Create mock data
        self.auction = Auction.objects.create(
            name="Test Auction",
            start_date="2024-01-01T00:00:00Z",
            end_date="2024-01-10T00:00:00Z",
            status="inactive"
        )
        self.auction_gacha = AuctionGachas.objects.create(
            auction_id=self.auction.id,
            collection_id=1,
            price=100.0,
            status="active"
        )
        self.bid = AuctionGachaBid.objects.create(
            auction_gacha_id=self.auction_gacha.id,
            bidder_id=2,
            price=120.0
        )
        self.player_gacha_collection = PlayerGachaCollection.objects.create(
            id=self.auction_gacha.collection_id,
            gacha_id=999,  # Arbitrary value, not relevant for this test
            player_id=1  # Seller's player ID
        )

    def tearDown(self):
        result = self.defaultTestResult()
        self._feedErrorsToResult(result, self._outcome.errors)
        if not result.failures and not result.errors:
            print(f"{self._testMethodName}: passed")
        else:
            for _, err in result.failures + result.errors:
                print(f"{self._testMethodName} failed: {err}")

    @patch('requests.get')
    def test_list_auctions(self, mock_get):
        """Test listing all auctions"""
        response = self.client.get(reverse('list-auctions'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['name'], self.auction.name)

    def test_create_auction(self):
        """Test creating a new auction"""
        payload = {
            "name": "New Auction",
            "start_date": "2024-02-01T00:00:00Z",
            "end_date": "2024-02-10T00:00:00Z",
            "status": "inactive"
        }
        response = self.client.post(reverse('create-auction'), payload)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Auction.objects.count(), 2)
        self.assertEqual(response.data['auction']['name'], payload['name'])

    @patch('requests.get')
    def test_auction_details(self, mock_get):
        """Test retrieving auction details"""
        response = self.client.get(
            reverse('auction-details', args=[self.auction.id]))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], self.auction.name)

    def test_delete_auction(self):
        """Test deleting an inactive auction"""
        response = self.client.delete(
            reverse('auction-details', args=[self.auction.id]))
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Auction.objects.count(), 0)

    @patch('requests.get')
    def test_place_gacha_for_auction(self, mock_get):
        """Test placing a gacha for auction"""
        payload = {
            "auction_id": self.auction.id,
            "collection_id": 2,
            "price": 150.0,
            "status": "active"
        }
        response = self.client.post(
            reverse('place-gacha-for-auction'), payload)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(AuctionGachas.objects.count(), 2)

    @patch('requests.get')
    def test_list_gachas_on_auction(self, mock_get):
        """Test listing all gachas on an auction"""
        response = self.client.get(
            reverse('list-auction-gachas', args=[self.auction.id]))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['auction_id'], self.auction.id)

    def test_get_auction_gacha_details(self):
        """Test retrieving auction gacha details."""
        response = self.client.get(
            reverse("auction-gacha-details", args=[self.auction_gacha.id]))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["auction_id"],
                         self.auction_gacha.auction_id)

    def test_delete_unsold_auction_gacha(self):
        """Test deleting an unsold auction gacha."""
        response = self.client.delete(
            reverse("auction-gacha-details", args=[self.auction_gacha.id]))
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(AuctionGachas.objects.count(), 0)

    def test_delete_sold_auction_gacha(self):
        """Test deleting a sold auction gacha."""
        self.auction_gacha.status = "sold"
        self.auction_gacha.save()
        response = self.client.delete(
            reverse("auction-gacha-details", args=[self.auction_gacha.id]))
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("Cannot remove a sold gacha", response.data["detail"])

    @patch('requests.get')
    @patch('requests.put')
    def test_gacha_winner_transfer_success(self, mock_put, mock_get):
        """Test transferring gacha ownership and updating balances"""
        # Mock seller and bidder GET responses
        mock_get.side_effect = [
            MagicMock(status_code=200, json=lambda: {"current_balance": 500}),
            MagicMock(status_code=200, json=lambda: {"current_balance": 300}),
        ]
        # Mock successful balance updates with PUT
        mock_put.side_effect = [
            MagicMock(status_code=200, json=lambda: {"current_balance": 600}),
            MagicMock(status_code=200, json=lambda: {"current_balance": 200}),
        ]

        payload = {
            "auction_gacha_id": self.auction_gacha.id,
            "bidder_id": 2,
            "price": 120,
        }

        response = self.client.post(reverse('auction-gacha-winner'), payload)
        # Debugging: Print the response status code and data
        print("Response Status Code:", response.status_code)
        # Include the response body for debugging
        print("Response Data:", response.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.data["detail"], "Gacha ownership transferred and balances updated successfully."
        )
