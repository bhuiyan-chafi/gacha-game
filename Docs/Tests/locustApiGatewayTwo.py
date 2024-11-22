from locust import HttpUser, task, between
import random
import string

# Class to test ApiGatewayTwo


class ApiGatewayTwoTestUser(HttpUser):
    wait_time = between(1, 3)  # Simulate wait time between tasks
    host = "http://localhost:8002/api/v2"  # Set the host to your application

    # Helper method to generate a random string
    def random_string(self, length=8):
        return ''.join(random.choices(string.ascii_letters + string.digits, k=length))
    # to create gacha

    @task
    def createGacha(self):
        # Random data for the gacha API
        data = {
            # Use self to call the helper method
            "name": self.random_string(10),
            "rarity": random.randint(10, 1000),
            "inventory": random.randint(10, 1000),
            "price": random.randint(10, 1000),
        }
        # Send the POST request
        response = self.client.post(
            "/gacha/create/", json=data)  # Use json for payload
        # Log the response for debugging purposes
        if response.status_code == 200 or response.status_code == 201:
            print(f"Success: {response.json()}")
        else:
            print(f"Failure: {response.status_code}, {response.text}")
    # to create a player account

    @task
    def createPlayer(self):
        # Random data for the gacha API
        data = {
            # Use self to call the helper method
            "user_id": random.randint(10, 1000),
            "first_name": self.random_string(10),
            "last_name": self.random_string(10),
            "email_address": self.random_string(3)+'@gmail.com',
            "phone_number": random.randint(10, 1000),
            "bank_details": random.randint(10, 1000),
            "current_balance": random.randint(10, 1000),
        }
        # Send the POST request
        response = self.client.post(
            "/player/create/", json=data)  # Use json for payload
        # Log the response for debugging purposes
        if response.status_code == 200 or response.status_code == 201:
            print(f"Success: {response.json()}")
        else:
            print(f"Failure: {response.status_code}, {response.text}")
