import requests
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.conf import settings


def forward_request(service_url, method, path, data, query_params, headers):
    """
    Helper function to forward requests to UserService.
    """
    try:
        url = f"{service_url}{path}"
        if query_params:
            url = f"{url}?{query_params}"
        print('Service Url: '+url)
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
        return Response({"detail": "Service unavailable", "error": str(e)}, status=status.HTTP_503_SERVICE_UNAVAILABLE)

# ======================== Authentication Functions =========================


@api_view(['POST'])
def createUser(request):
    """Create a new user via AuthService."""
    return forward_request(settings.AUTH_SERVICE, "POST", "/create/", request.data, None, None)


@api_view(['POST'])
def loginUser(request):
    """Login a user via AuthService."""
    return forward_request(settings.AUTH_SERVICE, "POST", "/user/login/", request.data, None, None)


@api_view(['POST'])
def logoutUser(request, id):
    """Logout a user via AuthService."""
    path = f"/user/{id}/logout/"
    headers = {"Authorization": request.headers.get("Authorization")}
    return forward_request(settings.AUTH_SERVICE, "POST", path, request.data, None, headers)


@api_view(['POST'])
def verifyToken(request):
    """Logout a user via AuthService."""
    path = f"/token/verify/"
    headers = {
        "Authorization": request.headers.get("Authorization"),
        "Role": ','.join(settings.PLAYER_ROLE),
    }
    return forward_request(settings.AUTH_SERVICE, "POST", path, request.data, None, headers)


# ======================== Player Functions ========================
# is open of authentication and authorization
@api_view(['POST'])
def createPlayer(request):
    """
    Create a new player after validating user_id through the AUTH_SERVICE
    and ensuring it is not taken by an admin.
    """
    user_id = request.data.get("user_id")

    # Validate user_id
    if not user_id:
        return Response({"error": "user_id is required."}, status=status.HTTP_400_BAD_REQUEST)

    try:
        # Step 1: Check if the user_id exists in the AUTH_SERVICE
        auth_service_url = f"{settings.AUTH_SERVICE}/{user_id}/details/"
        auth_response = requests.get(auth_service_url, verify=False)

        if auth_response.status_code != 200:
            if auth_response.status_code == 404:
                return Response({"error": "user_id not found in AUTH_SERVICE."}, status=status.HTTP_404_NOT_FOUND)
            return Response({"error": "Error validating user_id with AUTH_SERVICE because the response from AuthService is neither 200 or 404."}, status=auth_response.status_code)

        user_data = auth_response.json()
        # return Response({'auth_user': user_data}, status=200)
        # Ensure the returned user_id matches the input user_id
        if str(user_data.get("id")) != str(user_id):
            return Response({"error": "Invalid user_id, the user_id fetched from AUTH_SERVICE does not match the given one."}, status=status.HTTP_400_BAD_REQUEST)

        if user_data.get('role') != settings.PLAYER_ROLE[0]:
            # user_id is already taken by an admin
            return Response(
                {"error": "user_id is associated with an admin and cannot be used for a player."},
                status=status.HTTP_400_BAD_REQUEST
            )
        # Step 3: Proceed to create the Player
        return forward_request(settings.USER_SERVICE, "POST", "/user-service/player/create/", request.data, None, None)

    except requests.RequestException as e:
        # Handle request errors
        return Response({"error": f"Unable to validate user_id: {str(e)}"}, status=status.HTTP_503_SERVICE_UNAVAILABLE)


@api_view(['GET', 'PUT'])
def playerDetails(request, id):
    """
    Fetch or update details of a specific player through ApiGatewayTwo.
    """
    headers = {
        "Authorization": request.headers.get("Authorization"),
        "Role": ','.join(settings.PLAYER_ROLE),
    }
    if request.method == 'GET':
        return forward_request(settings.USER_SERVICE, "GET", f"/user-service/player/{id}/details/", None, None, headers)
    elif request.method == 'PUT':
        if 'user_id' in request.data:
            return Response(
                {"error": "Updating user_id is not allowed."},
                status=status.HTTP_400_BAD_REQUEST
            )
        return forward_request(settings.USER_SERVICE, "PUT", f"/user-service/player/{id}/details/", request.data, None, headers)


@api_view(['DELETE'])
def deletePlayer(request, id):
    """
    Delete a specific player through ApiGatewayTwo.
    """
    headers = {
        "Authorization": request.headers.get("Authorization"),
        "Role": ','.join(settings.PLAYER_ROLE),
    }
    return forward_request(settings.USER_SERVICE, "DELETE", f"/user-service/player/{id}/delete/", None, None, headers)

# ======================== Gacha Functions ========================


@api_view(['GET'])
def listGachas(request):
    """
    Fetch a list of all Gachas through ApiGatewayTwo.
    """
    headers = {
        "Authorization": request.headers.get("Authorization"),
        "Role": ','.join(settings.PLAYER_ROLE),
    }
    return forward_request(settings.GACHA_SERVICE, "GET", "/gacha-service/gacha/list/", None, None, headers)


@api_view(['GET'])
def gachaDetails(request, id):
    """
    Fetch or update Gacha details through ApiGatewayTwo.
    """
    headers = {
        "Authorization": request.headers.get("Authorization"),
        "Role": ','.join(settings.PLAYER_ROLE),
    }
    return forward_request(settings.GACHA_SERVICE, "GET", f"/gacha-service/gacha/{id}/details/", None, None, headers)


# ======================== PlayService Endpoints ========================
@api_view(['POST'])
def rollToWinGacha(request):
    player_id = request.query_params.get('player_id')
    # Extract roll_price from the request body
    roll_price = request.data.get('roll_price')

    # Validate player_id
    if not player_id:
        return Response({"detail": "player_id is required as a query parameter."}, status=status.HTTP_400_BAD_REQUEST)

    # Validate roll_price
    if roll_price is None or roll_price == "":
        return Response({"detail": "roll_price is required in the request body or not null"}, status=status.HTTP_400_BAD_REQUEST)

    if int(roll_price) not in [50, 75, 90]:
        return Response({"detail": "roll_price must be one of the following values: 50, 75, 90."}, status=status.HTTP_400_BAD_REQUEST)

    # Forward the request to the play-service
    headers = {
        "Authorization": request.headers.get("Authorization"),
        "Role": ','.join(settings.PLAYER_ROLE),
    }
    return forward_request(
        settings.PLAY_SERVICE,
        "POST",
        "/play-service/roll-to-win/", request.data,
        f"player_id={player_id}", headers
    )
# takes the player_id and gacha_id to purchase, next logic is applied inside the PlayService


@api_view(['POST'])
def createPlayerGachaByPurchase(request):
    # return Response(request.headers, status=status.HTTP_200_OK)
    player_id = request.query_params.get('player_id')
    gacha_id = request.query_params.get('gacha_id')

    if not player_id or not gacha_id:
        return Response({"detail": "Both player_id and gacha_id are required as query parameters."}, status=status.HTTP_400_BAD_REQUEST)
    headers = {
        "Authorization": request.headers.get("Authorization"),
        "Role": ','.join(settings.PLAYER_ROLE),
        "Content-Type": "application/json"
    }
    return forward_request(settings.PLAY_SERVICE, "POST", "/play-service/direct-purchase/", None, f"player_id={player_id}&gacha_id={gacha_id}", headers)


@api_view(['GET'])
def playerGachaCollections(request, player_id):
    headers = {
        "Authorization": request.headers.get("Authorization"),
        "Role": ','.join(settings.PLAYER_ROLE),
    }
    return forward_request(settings.PLAY_SERVICE, "GET", f"/play-service/player/{player_id}/collection/", None, None, headers)


@api_view(['GET', 'DELETE'])
def playerGachaCollectionDetails(request, collection_id):
    headers = {
        "Authorization": request.headers.get("Authorization"),
        "Role": ','.join(settings.PLAYER_ROLE),
    }
    if request.method == 'GET':
        return forward_request(settings.PLAY_SERVICE, "GET", f"/play-service/player/collection/{collection_id}/", None, None, headers)
    elif request.method == 'DELETE':
        return forward_request(settings.PLAY_SERVICE, "DELETE", f"/play-service/player/collection/{collection_id}/", None, None, headers)


# ======================== AuctionService Endpoints ========================
@api_view(['GET'])
def listAuctions(request):
    headers = {
        "Authorization": request.headers.get("Authorization"),
        "Role": ','.join(settings.PLAYER_ROLE),
    }
    return forward_request(settings.AUCTION_SERVICE, "GET", "/auction/list/", None, None, headers)

# players can only view auction details


@api_view(['GET'])
def auctionDetails(request, id):
    headers = {
        "Authorization": request.headers.get("Authorization"),
        "Role": ','.join(settings.PLAYER_ROLE),
    }
    return forward_request(settings.AUCTION_SERVICE, "GET", f"/auction/{id}/details/", None, None, headers)


"""
Before placing a gacha for the bid we have to make sure the auction is now 'active' so it's important to have auction_id in the request.
"""


@api_view(['POST'])
def placeGachaForAuction(request):
    headers = {
        "Authorization": request.headers.get("Authorization"),
        "Role": ','.join(settings.PLAYER_ROLE),
    }
    if not request.data.get("auction_id"):
        return Response({"detail": "auction_id is required in the request body."}, status=status.HTTP_400_BAD_REQUEST)
    return forward_request(settings.AUCTION_SERVICE, "POST", "/auction/gachas/place/", request.data, None, headers)


@api_view(['GET'])
def listAllGachasOnAuction(request, auction_id):
    headers = {
        "Authorization": request.headers.get("Authorization"),
        "Role": ','.join(settings.PLAYER_ROLE),
    }
    return forward_request(settings.AUCTION_SERVICE, "GET", f"/auction/gachas/{auction_id}/list/", None, None, headers)


@api_view(['GET', 'DELETE'])
def auctionGachaDetails(request, auction_gacha_id):
    headers = {
        "Authorization": request.headers.get("Authorization"),
        "Role": ','.join(settings.PLAYER_ROLE),
    }
    if request.method == 'GET':
        return forward_request(settings.AUCTION_SERVICE, "GET", f"/auction/gachas/{auction_gacha_id}/details/", None, None, headers)
    elif request.method == 'DELETE':
        return forward_request(settings.AUCTION_SERVICE, "DELETE", f"/auction/gachas/{auction_gacha_id}/details/", None, None, headers)


"""
- check if the gacha present in the request body and its more than 0, following checks will be completed in the service level
"""


@api_view(['POST', 'PUT'])
def bidForGacha(request, auction_gacha_id, player_id):
    headers = {
        "Authorization": request.headers.get("Authorization"),
        "Role": ','.join(settings.PLAYER_ROLE),
    }
    if not request.data.get('price') or request.data.get('price') <= 0:
        return Response({"detail": "price is required and more than 0 in the request body."}, status=status.HTTP_400_BAD_REQUEST)
    if request.method == 'POST':
        data = request.data.copy()
        data['auction_gacha_id'] = auction_gacha_id
        data['player_id'] = player_id
        return forward_request(settings.AUCTION_SERVICE, "POST", f"/auction/gachas/{auction_gacha_id}/player/{player_id}/bid/", data, None, headers)
    elif request.method == 'PUT':
        return forward_request(settings.AUCTION_SERVICE, "PUT", f"/auction/gachas/{auction_gacha_id}/player/{player_id}/bid/", request.data, None, headers)


@api_view(['GET'])
def listAllBids(request, auction_gacha_id):
    headers = {
        "Authorization": request.headers.get("Authorization"),
        "Role": ','.join(settings.PLAYER_ROLE),
    }
    return forward_request(settings.AUCTION_SERVICE, "GET", f"/auction/gachas/{auction_gacha_id}/bids/", None, None, headers)

# ======================== TransactionService Endpoints ========================


@api_view(['GET'])
def playerGameCurrencyTransactions(request, player_id):
    headers = {
        "Authorization": request.headers.get("Authorization"),
        "Role": ','.join(settings.PLAYER_ROLE),
    }
    return forward_request(settings.TRANSACTION_SERVICE, "GET", f"/transactions/player/{player_id}/all/", None, None, headers)


@api_view(['POST'])
def playerGameCurrencyPurchase(request, player_id):
    headers = {
        "Authorization": request.headers.get("Authorization"),
        "Role": ','.join(settings.PLAYER_ROLE),
    }
    return forward_request(settings.TRANSACTION_SERVICE, "POST", f"/transactions/player/{player_id}/purchase/game-currency/", request.data, None, headers)
