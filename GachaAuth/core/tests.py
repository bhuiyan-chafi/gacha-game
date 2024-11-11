from django.test import TestCase
from rest_framework.test import APITestCase
from django.urls import reverse
from rest_framework import status
from django.core.exceptions import ValidationError
from .models import User
from auth.constant import Status as appStatus
from .serializers import UserSerializer, UpdateUserSerializer
from django.contrib.auth.hashers import check_password, make_password

# testing the model only


class UserModelTest(TestCase):

    def setUp(self):
        # This user will be used in multiple tests
        self.user = User.objects.create(
            username="testuser",
            password="testpassword123",
            status=appStatus.ACTIVE
        )

    def test_user_creation(self):
        # Check if user is created with the correct fields
        user = User.objects.create(
            username="newuser",
            password="newpassword123",
            status=appStatus.INACTIVE
        )
        self.assertEqual(user.username, "newuser")
        self.assertEqual(user.status, appStatus.INACTIVE)

    def test_username_unique_constraint(self):
        # Attempting to create another user with the same username should raise an IntegrityError
        # Using Exception as a placeholder for IntegrityError in test db
        with self.assertRaises(Exception):
            User.objects.create(
                username="testuser",  # Same username as self.user
                password="anotherpassword"
            )

    def test_status_choices(self):
        # Test that only valid choices can be assigned to status
        self.user.status = "invalid_status"  # Assign invalid choice
        with self.assertRaises(ValidationError):
            self.user.full_clean()  # full_clean() checks field validation

    def test_auto_timestamps(self):
        # Check that created_at and updated_at are automatically set
        user = User.objects.create(
            username="timestampuser", password="password123")
        self.assertIsNotNone(user.created_at)
        self.assertIsNotNone(user.updated_at)

# testing the views


class UserApiTest(APITestCase):

    def setUp(self):
        # Creating a test user for use in tests
        self.user = User.objects.create(
            username="testuser",
            password="password123",
            status=appStatus.INACTIVE
        )

    def test_core_test_endpoint(self):
        url = reverse('core:core-test')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, 'You app is working!')

    def test_create_user(self):
        url = reverse('core:create-user')
        data = {
            'username': 'newuser',
            'password': 'newpassword123',
            'status': appStatus.ACTIVE
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['user']['username'], 'newuser')

    def test_list_users(self):
        url = reverse('core:user-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Initially, only 1 user in the database
        self.assertEqual(len(response.data), 1)

    def test_user_details_get(self):
        url = reverse('core:user-details', args=[self.user.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['username'], self.user.username)

    def test_user_details_update(self):
        url = reverse('core:user-details', args=[self.user.id])
        data = {
            'username': 'updateduser',
            'status': appStatus.ACTIVE
        }
        response = self.client.put(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['user']['username'], 'updateduser')
        self.assertEqual(response.data['user']['status'], appStatus.ACTIVE)

    def test_delete_user_inactive(self):
        # Ensure we can delete the user if they are inactive
        url = reverse('core:user-delete', args=[self.user.id])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(User.objects.filter(id=self.user.id).exists())

    def test_delete_user_active(self):
        # Set user status to active and attempt to delete
        self.user.status = appStatus.ACTIVE
        self.user.save()
        url = reverse('core:user-delete', args=[self.user.id])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.data['detail'], 'Active users cannot be deleted. Please deactivate the user first.')

# test the serializer


class UserSerializerTest(TestCase):

    def setUp(self):
        # Create a test user for use in serializer tests
        self.user = User.objects.create(
            username="existinguser",
            password=make_password("existingpassword123"),
            status=appStatus.INACTIVE
        )

    def test_create_user_serializer_valid_data(self):
        data = {
            'username': 'newuser',
            'password': 'newpassword123',
            'status': appStatus.ACTIVE
        }
        serializer = UserSerializer(data=data)
        self.assertTrue(serializer.is_valid())

        # Save and retrieve the created user
        user = serializer.save()
        self.assertEqual(user.username, data['username'])
        # Check hashed password
        self.assertTrue(check_password(data['password'], user.password))
        self.assertEqual(user.status, data['status'])

    def test_create_user_serializer_duplicate_username(self):
        # Attempt to create a user with a duplicate username
        data = {
            'username': 'existinguser',  # Duplicate username
            'password': 'newpassword123',
            'status': appStatus.ACTIVE
        }
        serializer = UserSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('username', serializer.errors)
        self.assertEqual(
            serializer.errors['username'][0], 'This field must be unique.')

    def test_create_user_serializer_password_hashed(self):
        data = {
            'username': 'passwordhashuser',
            'password': 'plaintextpassword',
            'status': appStatus.INACTIVE
        }
        serializer = UserSerializer(data=data)
        self.assertTrue(serializer.is_valid())
        user = serializer.save()

        # Ensure the password is hashed
        # Password should not be plain text
        self.assertNotEqual(user.password, data['password'])
        # Check if hashed correctly
        self.assertTrue(check_password(data['password'], user.password))

    def test_update_user_serializer(self):
        # Prepare update data
        data = {
            'username': 'updateduser',
            'status': appStatus.ACTIVE
        }
        serializer = UpdateUserSerializer(self.user, data=data, partial=True)
        self.assertTrue(serializer.is_valid())

        # Save and retrieve the updated user
        updated_user = serializer.save()
        self.assertEqual(updated_user.username, data['username'])
        self.assertEqual(updated_user.status, data['status'])

        # Check that password remains unchanged
        self.assertTrue(check_password('existingpassword123',
                        updated_user.password))  # Verify old password

    def test_update_user_serializer_read_only_updated_at(self):
        # Attempt to update `updated_at` field manually
        data = {
            'username': 'user_attempt_update',
            'status': appStatus.INACTIVE,
            'updated_at': '2025-01-01T00:00:00Z'
        }
        serializer = UpdateUserSerializer(self.user, data=data, partial=True)
        self.assertTrue(serializer.is_valid())

        # Save and verify that `updated_at` was not manually modified
        updated_user = serializer.save()
        # Should not match manually set date
        self.assertNotEqual(str(updated_user.updated_at), data['updated_at'])
