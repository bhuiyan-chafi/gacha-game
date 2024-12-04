from locust import HttpUser, task, between
import random
import string


class ApiGatewayTwoTests(HttpUser):
    wait_time = between(1, 3)  # Simulate wait time between requests
    host = "http://localhost:8002/api/player"
    # Common headers for all requests
    common_headers = {
        "Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjozLCJ1c2VybmFtZSI6InBsYXllcjAwMSIsInJvbGUiOiJwbGF5ZXIiLCJzdGF0dXMiOiJhY3RpdmUiLCJleHAiOjE3MzU5NDQ5OTMsImlhdCI6MTczMzM1Mjk5M30.YOvz2lUqAecFNhPnN6bYa6YmqD_g2pEJll1nb2Lx-C8",
        "Role": ','.join(['player']),
    }

    def generate_random_string(self, length=8):
        """Generate a random string of fixed length."""
        return ''.join(random.choices(string.ascii_letters, k=length))

    def generate_payload(self, request_type):
        """Generate payloads based on request type."""
        if request_type == "create_player":
            return {
                "user_id": random.randint(1000, 9999),
                "first_name": self.generate_random_string(),
                "last_name": self.generate_random_string(),
                "email_address": f"user{random.randint(1, 1000)}@test.com",
                "phone_number": ''.join(random.choices("0123456789", k=10)),
                "bank_details": f"IT{random.randint(1000000000, 9999999999)}",
                "current_balance": random.randint(100, 5000)
            }
        elif request_type == "bid_for_gacha":
            return {"price": random.randint(50, 500)}
        elif request_type == "purchase_game_currency":
            return {"amount": random.randint(10, 1000)}
        return {}

    def handle_response(self, response):
        """Handle response for valid/invalid status codes."""
        if response.status_code in [200, 201]:
            response.success()  # Successful outcomes
        elif response.status_code in [400, 401, 403, 404, 503]:
            print(
                f"Expected error response: {response.status_code} - {response.json()}")
            response.success()  # Treat these as acceptable outcomes
        else:
            print(
                f"Unexpected error: {response.status_code} - {response.text}")
            response.failure(f"Unexpected status code: {response.status_code}")

    # ================= CREATE | UPDATE | DELETE PLAYER ========================
    @task
    def create_player(self):
        """Test the create player endpoint."""
        payload = self.generate_payload("create_player")
        with self.client.post("/create/", json=payload, headers=self.common_headers, catch_response=True) as response:
            self.handle_response(response)

    @task
    def player_details(self):
        """Fetch player details."""
        with self.client.get("/1/details/", headers=self.common_headers, catch_response=True) as response:
            self.handle_response(response)

    @task
    def update_player_details(self):
        """Update player details."""
        payload = {"first_name": "UpdatedName"}
        with self.client.put("/1/details/", json=payload, headers=self.common_headers, catch_response=True) as response:
            self.handle_response(response)

    @task
    def delete_player(self):
        """Delete a player."""
        with self.client.delete("/1/delete/", headers=self.common_headers, catch_response=True) as response:
            self.handle_response(response)

    # ================= LIST & FETCH GACHA DETAILS ========================
    @task
    def list_gachas(self):
        """List all Gachas."""
        with self.client.get("/gacha/list/", headers=self.common_headers, catch_response=True) as response:
            self.handle_response(response)

    @task
    def gacha_details(self):
        """Fetch Gacha details."""
        with self.client.get("/gacha/1/details/", headers=self.common_headers, catch_response=True) as response:
            self.handle_response(response)

    # ================= PLAY SERVICES ========================
    @task
    def roll_to_win_gacha(self):
        """Roll to win a Gacha."""
        payload = {"roll_price": 50}
        with self.client.post("/play-service/roll-to-win/?player_id=1", json=payload, headers=self.common_headers, catch_response=True) as response:
            self.handle_response(response)

    @task
    def create_player_gacha_by_purchase(self):
        """Purchase a Gacha."""
        with self.client.post("/play-service/direct-purchase/?player_id=1&gacha_id=2", headers=self.common_headers, catch_response=True) as response:
            self.handle_response(response)

    @task
    def player_gacha_collections(self):
        """Fetch a player's Gacha collections."""
        with self.client.get("/play-service/player/1/collection/", headers=self.common_headers, catch_response=True) as response:
            self.handle_response(response)

    @task
    def player_gacha_collection_details(self):
        """Fetch details of a player's Gacha collection."""
        with self.client.get("/play-service/player/collection/1/", headers=self.common_headers, catch_response=True) as response:
            self.handle_response(response)

    # ================= AUCTION SERVICE ========================
    @task
    def list_auctions(self):
        """List all auctions."""
        with self.client.get("/auction-service/auction/list/", headers=self.common_headers, catch_response=True) as response:
            self.handle_response(response)

    @task
    def auction_details(self):
        """Fetch auction details."""
        with self.client.get("/auction-service/auction/1/details/", headers=self.common_headers, catch_response=True) as response:
            self.handle_response(response)

    @task
    def place_gacha_for_auction(self):
        """Place a Gacha for auction."""
        payload = {"auction_id": 1}
        with self.client.post("/auction-service/gachas/place/", json=payload, headers=self.common_headers, catch_response=True) as response:
            self.handle_response(response)

    @task
    def list_all_gachas_on_auction(self):
        """List all Gachas on auction."""
        with self.client.get("/auction-service/gachas/1/list/", headers=self.common_headers, catch_response=True) as response:
            self.handle_response(response)

    @task
    def auction_gacha_details(self):
        """Fetch details of a Gacha on auction."""
        with self.client.get("/auction-service/gachas/1/details/", headers=self.common_headers, catch_response=True) as response:
            self.handle_response(response)

    @task
    def bid_for_gacha(self):
        """Place a bid for a Gacha."""
        payload = self.generate_payload("bid_for_gacha")
        with self.client.post("/auction-service/gachas/1/player/1/bid/", json=payload, headers=self.common_headers, catch_response=True) as response:
            self.handle_response(response)

    @task
    def list_all_bids(self):
        """List all bids for a specific Gacha."""
        with self.client.get("/auction-service/gachas/1/bids/", headers=self.common_headers, catch_response=True) as response:
            self.handle_response(response)

    # ================= TRANSACTION SERVICE ========================
    @task
    def player_game_currency_transactions(self):
        """Fetch a player's game currency transactions."""
        with self.client.get("/transaction-service/player/1/all/", headers=self.common_headers, catch_response=True) as response:
            self.handle_response(response)

    @task
    def player_game_currency_purchase(self):
        """Purchase game currency."""
        payload = self.generate_payload("purchase_game_currency")
        with self.client.post("/transaction-service/player/1/purchase/game-currency/", json=payload, headers=self.common_headers, catch_response=True) as response:
            self.handle_response(response)
