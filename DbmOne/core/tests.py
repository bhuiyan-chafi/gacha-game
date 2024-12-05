from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from .models import User
from django.contrib.auth.hashers import make_password


class UserTests(APITestCase):

    def setUp(self):
        # Create a sample user for testing
        self.user = User.objects.create(
            username="testuser",
            password=make_password("Test@1234"),
            status="active",
            role="player"
        )

    def tearDown(self):
        # Check if the current test case passed
        result = self.defaultTestResult()
        self._feedErrorsToResult(result, self._outcome.errors)
        if not result.failures and not result.errors:
            print(f"{self._testMethodName}: passed")

    def test_create_user(self):
        """Test creating a new user"""
        data = {
            "username": "newuser",
            "password": "New@1234",
            "status": "active",
            "role": "player"
        }
        response = self.client.post(reverse('core:create-user'), data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(User.objects.count(), 2)
        self.assertEqual(User.objects.last().username, "newuser")

    def test_list_users(self):
        """Test listing all users"""
        response = self.client.get(reverse('core:user-list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)  # Initially, only one user

    def test_user_details(self):
        """Test retrieving user details"""
        response = self.client.get(
            reverse('core:user-details', args=[self.user.id]))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['username'], "testuser")

    def test_update_user(self):
        """Test updating a user"""
        data = {
            "username": "updateduser",
            "status": "inactive"
        }
        response = self.client.put(
            reverse('core:user-details', args=[self.user.id]), data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.user.refresh_from_db()
        self.assertEqual(self.user.username, "updateduser")
        self.assertEqual(self.user.status, "inactive")

    def test_delete_user(self):
        """Test deleting a user"""
        # Make the user inactive to allow deletion
        self.user.status = "inactive"
        self.user.save()

        response = self.client.delete(
            reverse('core:user-delete', args=[self.user.id]))
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(User.objects.count(), 0)

    def test_delete_active_user(self):
        """Test trying to delete an active user"""
        # Ensure the user is active before attempting deletion
        self.user.status = 'active'
        self.user.save()

        response = self.client.delete(
            reverse('core:user-delete', args=[self.user.id])
        )

        # Assert the response status code and error message
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.data['detail'],
            'Active users cannot be deleted. Please deactivate the user first.'
        )

        # Ensure the user still exists in the database
        self.assertTrue(User.objects.filter(pk=self.user.id).exists())
