import requests
from django.conf import settings
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from . import helper


def forward_request(method, path, data=None, query_params=None, headers=None):
    """
    Helper function to forward requests to DbmThree.
    """
    # return Response(query_params, status=status.HTTP_200_OK)
    try:
        url = f"{settings.DATABASE_THREE}{path}"
        if query_params:
            url = f"{url}?{query_params}"

        if method == "GET":
            response = requests.get(url, headers=headers, verify=False)
        elif method == "POST":
            response = requests.post(
                url, json=data, headers=headers, verify=False)
        elif method == "PUT":
            response = requests.put(
                url, json=data, headers=headers, verify=False)
        elif method == "DELETE":
            response = requests.delete(url, headers=headers, verify=False)
        else:
            raise ValueError(f"Unsupported HTTP method: {method}")

        # Handle successful responses
        if response.status_code == status.HTTP_204_NO_CONTENT:
            return Response({'detail': 'Operation successful.'}, status=status.HTTP_204_NO_CONTENT)

        return Response(response.json(), status=response.status_code)
    except requests.exceptions.RequestException as e:
        return Response({"detail": "DbmThree service unavailable", "error": str(e)}, status=status.HTTP_503_SERVICE_UNAVAILABLE)


"""
- This service to roll for a gacha will filter the player_id and forward the request to the DBM, if the player_id is not valid or the player does not have enough balance to perform the roll the request stops here.
- We could not check the gacha inventory at this level because we don't know which gacha will be assigned after the random distribution.
"""
# roll with price win a gacha


@api_view(['POST'])
def rollToWinGacha(request):
    """
    Proxy for rolling to win a gacha, validating the player_id with the user-service first.
    """
    # return Response(request.headers, status=status.HTTP_200_OK)
    # Verify the token using the helper function
    verify_token = helper.verifyToken(request)

    # Check if the token verification failed
    if not isinstance(verify_token, bool) or not verify_token:
        return verify_token  # Return the failure response from verifyToken

    player_id = request.query_params.get('player_id')
    # return Response({"player_id": player_id}, status=status.HTTP_200_OK)
    roll_price = request.data.get('roll_price')

    # Validate player_id
    if not player_id:
        return Response({"error": "player_id is required as a query parameter."}, status=status.HTTP_400_BAD_REQUEST)

    # Validate roll_price
    if roll_price is None or roll_price == "":
        return Response({"error": "roll_price is required in the request body and cannot be empty."}, status=status.HTTP_400_BAD_REQUEST)

    try:
        roll_price = float(roll_price)
    except ValueError:
        return Response({"error": "roll_price must be a numeric value."}, status=status.HTTP_400_BAD_REQUEST)

    try:

        user_service_url = f"{settings.USER_SERVICE}/user-service/player/{player_id}/details/"
        response = requests.get(
            user_service_url, headers=request.headers, verify=False)
        if response.status_code == 200:
            # return Response(request.headers, status=status.HTTP_200_OK)
            # Parse the response JSON
            user_data = response.json()
            # return Response(user_data, status=status.HTTP_200_OK)
            # Validate player_id
            # return Response({"player_id": player_id, "player_id_db": str(user_data.get("id"))}, status=status.HTTP_200_OK)
            if str(user_data.get("id")) != str(player_id):
                return Response({"error": "player_id mismatch in user-service."}, status=status.HTTP_400_BAD_REQUEST)

            # Validate current_balance
            current_balance = user_data.get("current_balance")
            if current_balance is None:
                return Response({"error": "current_balance is missing in user-service response."}, status=status.HTTP_400_BAD_REQUEST)

            if current_balance < roll_price:
                return Response({"error": "Insufficient balance for the roll."}, status=status.HTTP_400_BAD_REQUEST)

            # Proceed to forward the request to the gacha collection service
            # return Response({"detail": "calling dbm_three now because every condition satisfied"}, status=status.HTTP_200_OK)
            return forward_request(
                "POST",
                "/gacha-collection/roll-to-win/",
                query_params=f"player_id={player_id}",
                data=request.data, headers=request.headers
            )

        elif response.status_code == 404:
            return Response({"error": "Player not found."}, status=status.HTTP_404_NOT_FOUND)
        else:
            return Response(
                {"error": "Error validating player_id with user-service."},
                status=response.status_code
            )

    except requests.RequestException as e:
        # Handle network errors or request failures
        return Response({"error": f"Unable to validate player_id: {str(e)}"}, status=status.HTTP_503_SERVICE_UNAVAILABLE)


"""
- first we will check if the player is an active player and if so, then make sure s/he has the enough balance to make the purchase.
- next step to access the gacha service to check the inventory of the gacha. Our projection is to keep one last piece of every gacha for the system. So the inventory should be >= 2.
"""


@api_view(['POST'])
def createPlayerGachaByPurchase(request):
    # Verify the token using the helper function
    verify_token = helper.verifyToken(request)

    # Check if the token verification failed
    if not isinstance(verify_token, bool) or not verify_token:
        return verify_token  # Return the failure response from verifyToken

    player_id = request.query_params.get('player_id')
    gacha_id = request.query_params.get('gacha_id')

    if not player_id or not gacha_id:
        return Response({"detail": "Both player_id and gacha_id are required as query parameters."}, status=status.HTTP_400_BAD_REQUEST)
    # Step 1: Check if the player already owns the gacha
    player_collection_url = f"{settings.DATABASE_THREE}/gacha-collection/player/{player_id}/collection/"
    try:
        collection_response = requests.get(
            player_collection_url, headers=request.headers, verify=False)
        if collection_response.status_code != 200:
            return Response({"detail": "Failed to fetch player's gacha collection."}, status=collection_response.status_code)

        player_collection = collection_response.json()
        """
        If the player does not have any collection then we get a response with 'detail', so if the detail is present in the response it indicates there is no gacha in his/her collection. But remember the response is not empty.
        """
        if 'detail' not in player_collection:
            owned_gacha_ids = [item['gacha_id'] for item in player_collection]
            if int(gacha_id) in owned_gacha_ids:
                return Response({"detail": "Player already owns the selected gacha."}, status=status.HTTP_400_BAD_REQUEST)
    except requests.exceptions.RequestException as e:
        return Response({"detail": "Collection service unavailable.", "error": str(e)}, status=status.HTTP_503_SERVICE_UNAVAILABLE)

    # Step 2: Validate the player
    user_detail_url = f"{settings.USER_SERVICE}/user-service/player/{player_id}/details/"
    try:
        player_response = requests.get(
            user_detail_url, headers=request.headers, verify=False)
        if player_response.status_code != 200:
            return Response({"detail": "Failed to fetch player details."}, status=player_response.status_code)

        player_data = player_response.json()
        current_balance = player_data.get("current_balance")
        if current_balance is None:
            return Response({"detail": "Player's current balance is missing."}, status=status.HTTP_400_BAD_REQUEST)
    except requests.exceptions.RequestException as e:
        return Response({"detail": "User service cannot be accessed from the PlayService.", "error": str(e)}, status=status.HTTP_503_SERVICE_UNAVAILABLE)

    # Step 3: Validate the gacha
    gacha_detail_url = f"{settings.GACHA_RECORDS_SERVICE}/gacha-service/gacha/{gacha_id}/details/"
    try:
        gacha_response = requests.get(
            gacha_detail_url, headers=request.headers, verify=False)
        if gacha_response.status_code != 200:
            return Response({"detail": "Failed to fetch gacha details."}, status=gacha_response.status_code)

        gacha_data = gacha_response.json()
        if gacha_data.get("status") != "active":
            return Response({"detail": "Gacha is not active."}, status=status.HTTP_400_BAD_REQUEST)

        gacha_price = gacha_data.get("price")
        gacha_inventory = gacha_data.get("inventory")
        if gacha_price is None or gacha_inventory is None:
            return Response({"detail": "Gacha price or inventory is missing."}, status=status.HTTP_400_BAD_REQUEST)

        if current_balance < gacha_price:
            return Response({"detail": "Player does not have enough balance to purchase the gacha."}, status=status.HTTP_400_BAD_REQUEST)

        if gacha_inventory < 2:
            return Response({"detail": "Gacha inventory is insufficient for purchase."}, status=status.HTTP_400_BAD_REQUEST)
    except requests.exceptions.RequestException as e:
        return Response({"detail": "Gacha service unavailable.", "error": str(e)}, status=status.HTTP_503_SERVICE_UNAVAILABLE)

    # Step 4: Forward the request to the gacha-collection service
    return forward_request(
        "POST",
        "/gacha-collection/direct-purchase/",
        query_params=f"player_id={player_id}&gacha_id={gacha_id}", headers=request.headers
    )


@api_view(['GET'])
def playerGachaCollections(request, player_id):
    """
    Proxy for fetching a player's gacha collection.
    """
    # return Response(request.headers, status=status.HTTP_200_OK)
    # Verify the token using the helper function
    verify_token = helper.verifyToken(request)

    # Check if the token verification failed
    if not isinstance(verify_token, bool) or not verify_token:
        return verify_token  # Return the failure response from verifyToken
    return forward_request("GET", f"/gacha-collection/player/{player_id}/collection/")


@api_view(['GET', 'DELETE'])
def playerGachaCollectionDetails(request, collection_id):
    """
    Proxy for fetching or deleting a specific player's gacha collection record.
    """
    # return Response(request.headers, status=status.HTTP_200_OK)
    # Verify the token using the helper function
    verify_token = helper.verifyToken(request)

    # Check if the token verification failed
    if not isinstance(verify_token, bool) or not verify_token:
        return verify_token  # Return the failure response from verifyToken
    if request.method == 'GET':
        return forward_request("GET", f"/gacha-collection/player/collection/{collection_id}/", headers=request.headers)
    elif request.method == 'DELETE':
        return forward_request("DELETE", f"/gacha-collection/player/collection/{collection_id}/", headers=request.headers)
