from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from .models import Gacha


class GachaTests(APITestCase):

    def setUp(self):
        # Create a sample Gacha for testing
        self.gacha = Gacha.objects.create(
            name="Ahri",
            rarity=5,
            inventory=10,
            price=100,
            description="A rare Gacha item.",
            image="ahri.jpg",
            status="active"
        )

    def tearDown(self):
        result = self.defaultTestResult()
        self._feedErrorsToResult(result, self._outcome.errors)
        if not result.failures and not result.errors:
            print(f"{self._testMethodName}: passed")
        else:
            for _, err in result.failures + result.errors:
                print(f"{self._testMethodName} failed: {err}")

    def test_create_gacha(self):
        """Test creating a new Gacha"""
        data = {
            "name": "Jinx",
            "rarity": 7,
            "inventory": 20,
            "price": 200,
            "description": "An ultra-rare Gacha item.",
            "image": "jinx.jpg",
            "status": "active"
        }
        response = self.client.post(reverse('create-gacha'), data)
        if response.status_code != status.HTTP_201_CREATED:
            print("Response Data:", response.data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Gacha.objects.count(), 2)
        self.assertEqual(Gacha.objects.last().name, "Jinx")

    def test_list_gacha(self):
        """Test listing all Gachas"""
        response = self.client.get(reverse('list-gacha'))
        if response.status_code != status.HTTP_200_OK:
            print("Response Data:", response.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Initially, one Gacha is created
        self.assertEqual(len(response.data), 1)

    def test_gacha_details(self):
        """Test retrieving Gacha details"""
        response = self.client.get(
            reverse('gacha-details', args=[self.gacha.id]))
        if response.status_code != status.HTTP_200_OK:
            print("Response Data:", response.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], "Ahri")

    def test_update_gacha(self):
        """Test updating a Gacha"""
        data = {
            "name": "UpdatedGacha",
            "price": 150
        }
        response = self.client.put(
            reverse('gacha-details', args=[self.gacha.id]), data)
        if response.status_code != status.HTTP_200_OK:
            print("Response Data:", response.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.gacha.refresh_from_db()
        self.assertEqual(self.gacha.name, "UpdatedGacha")
        self.assertEqual(self.gacha.price, 150)

    def test_delete_gacha(self):
        """Test deleting an inactive Gacha"""
        # Make the Gacha inactive to allow deletion
        self.gacha.status = "inactive"
        self.gacha.save()

        response = self.client.delete(
            reverse('delete-gacha', args=[self.gacha.id]))
        if response.status_code != status.HTTP_204_NO_CONTENT:
            print("Response Data:", response.data)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Gacha.objects.count(), 0)

    def test_delete_active_gacha(self):
        """Test trying to delete an active Gacha"""
        response = self.client.delete(
            reverse('delete-gacha', args=[self.gacha.id]))
        if response.status_code != status.HTTP_400_BAD_REQUEST:
            print("Response Data:", response.data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertTrue(Gacha.objects.filter(pk=self.gacha.id).exists())
