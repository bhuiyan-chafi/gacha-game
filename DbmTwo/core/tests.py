from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from .models import Player, Admin
from unittest.mock import patch
from django.conf import settings
from django.test import override_settings


class PlayerTests(APITestCase):
    def setUp(self):
        # Create a sample player to test retrieval and deletion
        self.player = Player.objects.create(
            user_id=1,
            first_name="John",
            last_name="Doe",
            email_address="john.doe@example.com",
            phone_number="1234567890",
            bank_details="IT234y3294y34",
            current_balance=100.0,
        )

    def tearDown(self):
        # Check if the current test case passed
        result = self.defaultTestResult()
        self._feedErrorsToResult(result, self._outcome.errors)
        if not result.failures and not result.errors:
            print(f"{self._testMethodName}: passed")

    def test_create_player(self):
        """Test creating a new player"""
        data = {
            "user_id": 2,
            "first_name": "Jane",
            "last_name": "Smith",
            "email_address": "jane.smith@example.com",
            "phone_number": "0987654321",
            "bank_details": "IT234y3294y35",
            "current_balance": 50.0,
        }
        response = self.client.post(reverse("create_player"), data)
        # Print the response data if the status code is not as expected
        if response.status_code != status.HTTP_201_CREATED:
            print("Response Data:", response.data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Player.objects.count(), 2)
        self.assertEqual(Player.objects.last().first_name, "Jane")

    def test_list_players(self):
        """Test listing all players"""
        response = self.client.get(reverse("list_players"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_get_player_details(self):
        """Test retrieving player details"""
        response = self.client.get(
            reverse("player_details", args=[self.player.id]))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["first_name"], "John")

    @patch('core.views.requests.delete')  # Mock the external API call
    def test_delete_player(self, mock_delete):
        """Test deleting a player with mocked external API call"""
        # Configure the mock to return a 204 status code
        mock_delete.return_value.status_code = status.HTTP_204_NO_CONTENT

        # Make the DELETE request
        response = self.client.delete(
            reverse("delete_player", args=[self.player.id]))

        # Assert the response
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Player.objects.count(), 0)


class AdminTests(APITestCase):
    def setUp(self):
        # Create a sample admin to test retrieval and deletion
        self.admin = Admin.objects.create(
            user_id=1,
            first_name="Admin",
            last_name="User",
            email_address="admin.user@example.com",
            phone_number="1234509876",
        )

    def test_create_admin(self):
        """Test creating a new admin"""
        data = {
            "user_id": 2,
            "first_name": "Super",
            "last_name": "Admin",
            "email_address": "super.admin@example.com",
            "phone_number": "9876543210",
        }
        response = self.client.post(reverse("create_admin"), data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Admin.objects.count(), 2)
        self.assertEqual(Admin.objects.last().first_name, "Super")

    def test_list_admins(self):
        """Test listing all admins"""
        response = self.client.get(reverse("list_admins"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_get_admin_details(self):
        """Test retrieving admin details"""
        response = self.client.get(
            reverse("admin_details", args=[self.admin.id]))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["first_name"], "Admin")

    @patch('core.views.requests.delete')  # Mock the external API call
    def test_delete_admin(self, mock_delete):
        """Test deleting an admin with mocked external API call"""
        # Configure the mock to return a 204 status code
        mock_delete.return_value.status_code = status.HTTP_204_NO_CONTENT

        # Make the DELETE request
        response = self.client.delete(
            reverse("delete_admin", args=[self.admin.id]))

        # Assert the response
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Admin.objects.count(), 0)
