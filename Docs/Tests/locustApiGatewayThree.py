from locust import HttpUser, task, between
import random
import string
# Class to test ApiGatewayThree


class ApiGatewayThreeTestUser(HttpUser):
    wait_time = between(1, 3)  # Simulate wait time between tasks
    host = "http://localhost:8003/api/v3"  # Set the host to your application
    # Helper method to generate a random string

    def random_string(self, length=8):
        return ''.join(random.choices(string.ascii_letters + string.digits, k=length))
    # to create gacha

    @task
    def rollToWinGacha(self):
        # Send the POST request
        response = self.client.post(
            "/play-service/roll-to-win/?player_id=3")  # Use json for payload
        # Log the response for debugging purposes
        if response.status_code == 200 or response.status_code == 201:
            print(f"Success: {response.json()}")
        else:
            print(f"Failure: {response.status_code}, {response.text}")

    @task
    def placeGachaToTheAuction(self):
        # Random data for the gacha API
        data = {
            "auction_id": random.randint(10, 1000),
            "collection_id": random.randint(10, 1000),
            "price": random.randint(10, 10000),
            "status": "active"
        }
        # Send the POST request
        response = self.client.post(
            "/auction-service/gachas/place/", json=data)  # Use json for payload
        # Log the response for debugging purposes
        if response.status_code == 200 or response.status_code == 201:
            print(f"Success: {response.json()}")
        else:
            print(f"Failure: {response.status_code}, {response.text}")

    @task
    def purchaseInGameCurrency(self):
        # Random data for the gacha API
        data = {
            "cash_amount": random.randint(10, 1000)
        }
        # Send the POST request
        response = self.client.post(
            # Use json for payload
            "/transaction-service/player/4/purchase/game-currency/", json=data)
        # Log the response for debugging purposes
        if response.status_code == 200 or response.status_code == 201:
            print(f"Success: {response.json()}")
        else:
            print(f"Failure: {response.status_code}, {response.text}")
