import requests
from django.conf import settings
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status


def forward_request(method, path, data=None):
    """
    Helper function to forward requests to DbmThree Auction endpoints.
    """
    try:
        url = f"{settings.DATABASE_THREE}{path}"
        if method == "GET":
            response = requests.get(url)
        elif method == "POST":
            response = requests.post(url, json=data)
        elif method == "PUT":
            response = requests.put(url, json=data)
        elif method == "DELETE":
            response = requests.delete(url)
        else:
            raise ValueError(f"Unsupported HTTP method: {method}")

        # Handle successful responses
        if response.status_code == status.HTTP_204_NO_CONTENT:
            return Response({'detail': 'Operation successful.'}, status=status.HTTP_204_NO_CONTENT)

        return Response(response.json(), status=response.status_code)
    except requests.exceptions.RequestException as e:
        return Response({"detail": "DbmThree service unavailable", "error": str(e)}, status=status.HTTP_503_SERVICE_UNAVAILABLE)


@api_view(['GET'])
def listAuctions(request):
    """
    Proxy for listing all auctions.
    """
    return forward_request("GET", "/auction/list/")


@api_view(['POST'])
def createAuction(request):
    """
    Proxy for creating a new auction.
    """
    return forward_request("POST", "/auction/create/", data=request.data)


@api_view(['GET', 'PUT', 'DELETE'])
def auctionDetails(request, id):
    """
    Proxy for getting, updating, or deleting auction details.
    """
    if request.method == 'GET':
        return forward_request("GET", f"/auction/{id}/details/")
    elif request.method == 'PUT':
        return forward_request("PUT", f"/auction/{id}/details/", data=request.data)
    elif request.method == 'DELETE':
        return forward_request("DELETE", f"/auction/{id}/details/")

# ====================== Bidding Views ============================


"""
- first we check if the auction is active and taking gachas for bidding
"""


@api_view(['POST'])
def placeGachaForAuction(request):
    """
    Place a gacha for auction after validating the auction status and collection ID.
    """
    auction_id = request.data.get("auction_id")
    collection_id = request.data.get("collection_id")

    if not auction_id or not collection_id:
        return Response(
            {"detail": "Both auction_id and collection_id are required."},
            status=status.HTTP_400_BAD_REQUEST
        )

    # Step 1: Validate the auction status
    auction_detail_url = f"{settings.AUCTION_SERVICE}/auction/{auction_id}/details/"
    try:
        auction_response = requests.get(auction_detail_url)
        if auction_response.status_code != 200:
            return Response({"detail": "Failed to fetch auction details."}, status=auction_response.status_code)

        auction_data = auction_response.json()
        auction_status = auction_data.get("status")

        if auction_status != "active":
            return Response({"detail": "Auction is not active."}, status=status.HTTP_400_BAD_REQUEST)
    except requests.exceptions.RequestException as e:
        return Response({"detail": "Auction service unavailable.", "error": str(e)}, status=status.HTTP_503_SERVICE_UNAVAILABLE)

    # Step 2: Validate the collection ID
    collection_detail_url = f"{settings.PLAY_SERVICE}/play-service/player/collection/{collection_id}/"
    try:
        collection_response = requests.get(collection_detail_url)
        if collection_response.status_code != 200:
            return Response({"detail": f"Invalid collection ID: {collection_id}"}, status=collection_response.status_code)
    except requests.exceptions.RequestException as e:
        return Response({"detail": "Play service unavailable.", "error": str(e)}, status=status.HTTP_503_SERVICE_UNAVAILABLE)

    # Step 3: Forward the request to the auction service
    return forward_request("POST", "/auction/gachas/place/", data=request.data)


@api_view(['GET'])
def listAllGachasOnAuction(request, auction_id):
    """
    Proxy for listing all gachas on auction for a specific auction ID.
    """
    return forward_request("GET", f"/auction/gachas/{auction_id}/list/")


@api_view(['GET', 'DELETE'])
def auctionGachaDetails(request, auction_gacha_id):
    """
    Proxy for getting details of or deleting a specific gacha on auction.
    """
    if request.method == 'GET':
        return forward_request("GET", f"/auction/gachas/{auction_gacha_id}/details/")
    elif request.method == 'DELETE':
        return forward_request("DELETE", f"/auction/gachas/{auction_gacha_id}/details/")


"""
- to place a bit or update the current bid
- the price for the bid is already filtered in the gateway
- the following conditions are checked before placing the bid:
-- auction is active
-- bidding gacha is still active in the auction
-- player is not the bidder
-- bidder doesn't have the gacha already
-- bidder has the available balance to bid
"""


@api_view(['POST', 'PUT'])
def bidForGacha(request, auction_gacha_id, player_id):
    bidding_price = request.data.get("price")
    try:
        # Step 1: Validate the auction gacha status
        gacha_detail_url = f"{settings.DATABASE_THREE}/auction/gachas/{auction_gacha_id}/details/"
        gacha_response = requests.get(gacha_detail_url)
        if gacha_response.status_code != 200:
            return Response({"detail": "Failed to fetch auction gacha details."}, status=gacha_response.status_code)

        gacha_data = gacha_response.json()
        if gacha_data.get("status") != "active":
            return Response({"detail": "Auction gacha is not active."}, status=status.HTTP_400_BAD_REQUEST)

        auction_id = gacha_data.get("auction_id")
        collection_id = gacha_data.get("collection_id")

        # Step 2: Validate the auction status
        auction_detail_url = f"{settings.DATABASE_THREE}/auction/{auction_id}/details/"
        auction_response = requests.get(auction_detail_url)
        if auction_response.status_code != 200:
            return Response({"detail": "Failed to fetch auction details."}, status=auction_response.status_code)

        auction_data = auction_response.json()
        if auction_data.get("status") != "active":
            return Response({"detail": "Auction is not active."}, status=status.HTTP_400_BAD_REQUEST)

        # Step 3: Validate the gacha owner
        collection_detail_url = f"{settings.PLAY_SERVICE}/play-service/player/collection/{collection_id}/"
        collection_response = requests.get(collection_detail_url)
        if collection_response.status_code != 200:
            return Response({"detail": "Failed to fetch gacha collection details."}, status=collection_response.status_code)

        collection_data = collection_response.json()
        # player who is selling the gacha
        gacha_owner_id = collection_data.get("player_id")
        # gacha to be sold
        bidding_gacha_id = collection_data.get("gacha_details", {}).get("id")

        if gacha_owner_id == player_id:
            return Response({"detail": "Bidder cannot be the owner of the gacha."}, status=status.HTTP_400_BAD_REQUEST)

        # Step 4: Check if the bidder already owns the gacha
        bidder_collection_url = f"{settings.PLAY_SERVICE}/play-service/player/{player_id}/collection/"
        bidder_collection_response = requests.get(bidder_collection_url)
        if bidder_collection_response.status_code != 200:
            return Response({"detail": "Failed to fetch bidder's gacha collection."},
                            status=bidder_collection_response.status_code)

        bidder_collection = bidder_collection_response.json()
        if 'detail' not in bidder_collection:
            owned_gacha_ids = [item.get("gacha_id")
                               for item in bidder_collection if "gacha_id" in item]
            if bidding_gacha_id in owned_gacha_ids:
                return Response({"detail": "Bidder already owns the gacha being auctioned."}, status=status.HTTP_400_BAD_REQUEST)

        # Step 5: Check if the bidder has sufficient balance
        player_detail_url = f"{settings.USER_SERVICE}/user-service/player/{player_id}/details/"
        player_response = requests.get(player_detail_url)
        if player_response.status_code != 200:
            return Response({"detail": "Failed to fetch bidder's player details."}, status=player_response.status_code)

        player_data = player_response.json()
        current_balance = player_data.get("current_balance")
        if current_balance is None or current_balance < bidding_price:
            return Response({"detail": "Bidder does not have sufficient balance to place the bid."},
                            status=status.HTTP_400_BAD_REQUEST)

        # Step 6: Forward the request
        if request.method == 'POST':
            data = request.data.copy()
            data['auction_gacha_id'] = auction_gacha_id
            data['player_id'] = player_id
            return forward_request("POST", f"/auction/gachas/{auction_gacha_id}/player/{player_id}/bid/", data=data)
        elif request.method == 'PUT':
            return forward_request("PUT", f"/auction/gachas/{auction_gacha_id}/player/{player_id}/bid/", data=request.data)

    except requests.exceptions.RequestException as e:
        return Response({"detail": "Service unavailable.", "error": str(e)}, status=status.HTTP_503_SERVICE_UNAVAILABLE)


@api_view(['GET'])
def listAllBids(request, auction_gacha_id):
    """
    Proxy for listing all bids for a specific auction gacha.
    """
    return forward_request("GET", f"/auction/gachas/{auction_gacha_id}/bids/")


"""
- we declare the winner here
- the system will load all the bids for a gacha listed in the auction
- then it will loop through the list
- as we did not deduct the price while taking the bid we will check the player balance now, because they are notified after each bid to keep the balance in their wallet
- if the player doesn't have the balance required it will loop next and declare the next player as winner
- if the operation is successful in the db-manager we get a 200 response and we see the winner
- rest of the logic goes to the dbmThree service
"""


@api_view(['GET'])
def gachaWinner(request, auction_gacha_id):
    """
    Determine the winner of an auction gacha by checking each highest bidder's eligibility.
    """
    # Step 1: Load all bids for the auction gacha
    bids_url = f"{settings.DATABASE_THREE}/auction/gachas/{auction_gacha_id}/bids/"
    try:
        bids_response = requests.get(bids_url)
        if bids_response.status_code != 200:
            return Response(
                {"detail": "Failed to fetch bids for the auction gacha."},
                status=bids_response.status_code,
            )

        bids = bids_response.json()
        if not isinstance(bids, list) or not bids:
            return Response(
                {"detail": "No bids found for the auction gacha."},
                status=status.HTTP_404_NOT_FOUND,
            )

        # Step 2: Loop through the bids (already sorted by price, highest first)
        for bid in bids:
            bidder_id = bid.get("bidder_id")
            bid_price = bid.get("price")

            if not bidder_id or bid_price is None:
                continue  # Skip invalid bid entries

            # Step 3: Check bidder's current balance
            bidder_detail_url = f"{settings.USER_SERVICE}/user-service/player/{bidder_id}/details/"
            try:
                bidder_response = requests.get(bidder_detail_url)
                if bidder_response.status_code != 200:
                    continue  # Skip this bidder and move to the next

                bidder_data = bidder_response.json()
                current_balance = bidder_data.get("current_balance")

                if current_balance is None or current_balance <= bid_price:
                    continue  # Skip if balance is insufficient

                # Step 4: Declare the winner
                winner_data = {
                    "auction_gacha_id": auction_gacha_id,
                    "bidder_id": bidder_id,
                    "price": bid_price,
                }
                declare_winner_url = f"{settings.DATABASE_THREE}/auction/gachas/bids/winner/"
                declare_winner_response = requests.post(
                    declare_winner_url, json=winner_data)

                if declare_winner_response.status_code == 200:
                    return Response(
                        {"detail": "Winner declared successfully.",
                            "winner": winner_data},
                        status=status.HTTP_200_OK,
                    )
                else:
                    return Response(
                        {"detail": "Failed to declare the winner.",
                            "error": declare_winner_response.json()},
                        status=declare_winner_response.status_code,
                    )

            except requests.exceptions.RequestException:
                continue  # Skip this bidder and move to the next

        # Step 5: If no winner could be declared
        return Response(
            {"detail": "No eligible bidder found to declare as winner."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    except requests.exceptions.RequestException as e:
        return Response(
            {"detail": "Service unavailable.", "error": str(e)},
            status=status.HTTP_503_SERVICE_UNAVAILABLE,
        )
