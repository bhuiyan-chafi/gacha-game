import requests
from django.conf import settings
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import api_view

# ================= TEST IF THE GATEWAY IS RUNNING ========================


@api_view(['GET'])
def gateWayOneTest(request):
    """Test endpoint for the AuthService."""
    return Response({'detail': 'Gateway one has been accessed'}, status=status.HTTP_200_OK)

# === Forward function to forward all the request that needs to access AuthService ===


def forward_request(source, method, path, data=None):
    """
    Helper function to forward requests to AuthService.
    """
    try:
        url = f"{source}{path}"
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
        return Response({"detail": "Auth service unavailable", "error": str(e)}, status=status.HTTP_503_SERVICE_UNAVAILABLE)


# ======================== Authentication Functions =========================


@api_view(['POST'])
def loginUser(request):
    """Login a user via AuthService."""
    return forward_request(settings.AUTH_SERVICE, "POST", "/user/login/", request.data)


@api_view(['POST'])
def logoutUser(request, id):
    """Logout a user via AuthService."""
    path = f"/user/{id}/logout/"
    return forward_request(settings.AUTH_SERVICE, "POST", path)

# ================= CREATE | UPDATE | DELETE USERS ========================


@api_view(['POST'])
def createUser(request):
    """Create a new user via AuthService."""
    return forward_request(settings.AUTH_SERVICE, "POST", "/create/", request.data)


@api_view(['GET'])
def listOfUsers(request):
    """List all users via AuthService."""
    return forward_request(settings.AUTH_SERVICE, "GET", "/list/")


@api_view(['GET', 'PUT'])
def userDetails(request, id):
    """Retrieve or update user details via AuthService."""
    path = f"/{id}/details/"
    return forward_request(settings.AUTH_SERVICE, request.method, path, request.data if request.method == "PUT" else None)


@api_view(['DELETE'])
def deleteUser(request, id):
    """Delete a user via AuthService."""
    path = f"/{id}/delete/"
    return forward_request(settings.AUTH_SERVICE, "DELETE", path)


# ================= CREATE | UPDATE | DELETE ADMINS ========================

@api_view(['GET'])
def listAdmins(request):
    """
    Fetch all admins through ApiGatewayTwo.
    """
    return forward_request(settings.USER_SERVICE, "GET", "/user-service/admin/list/")


@api_view(['POST'])
def createAdmin(request):
    """
    Create a new admin through ApiGatewayTwo.
    """
    return forward_request(settings.USER_SERVICE, "POST", "/user-service/admin/create/", data=request.data)


@api_view(['GET', 'PUT'])
def adminDetails(request, id):
    """
    Fetch or update details of a specific admin through ApiGatewayTwo.
    """
    if request.method == 'GET':
        return forward_request(settings.USER_SERVICE, "GET", f"/user-service/admin/{id}/details/")
    elif request.method == 'PUT':
        return forward_request(settings.USER_SERVICE, "PUT", f"/user-service/admin/{id}/details/", data=request.data)


@api_view(['DELETE'])
def deleteAdmin(request, id):
    """
    Delete a specific admin through ApiGatewayTwo.
    """
    return forward_request(settings.USER_SERVICE, "DELETE", f"/user-service/admin/{id}/delete/")

# ================= CREATE | UPDATE | DELETE PLAYERS ========================


@api_view(['GET'])
def listPlayers(request):
    """
    Fetch all players through ApiGatewayTwo.
    """
    return forward_request(settings.USER_SERVICE, "GET", "/user-service/player/list/")

# both admins and players can see their profiles and update


@api_view(['GET', 'PUT'])
def playerDetails(request, id):
    """
    Fetch or update details of a specific player through ApiGatewayTwo.
    """
    if request.method == 'GET':
        return forward_request(settings.USER_SERVICE, "GET", f"/user-service/player/{id}/details/")
    elif request.method == 'PUT':
        if 'user_id' in request.data:
            return Response(
                {"error": "Updating user_id is not allowed."},
                status=status.HTTP_400_BAD_REQUEST
            )
        return forward_request(settings.USER_SERVICE, "PUT", f"/user-service/player/{id}/details/", data=request.data)
# both admin and player can delete player profile


@api_view(['DELETE'])
def deletePlayer(request, id):
    """
    Delete a specific player through ApiGatewayTwo.
    """
    return forward_request(settings.USER_SERVICE, "DELETE", f"/user-service/player/{id}/delete/")

# ================= CREATE | UPDATE | DELETE GACHAS ========================


@api_view(['GET'])
def listGachas(request):
    """
    Fetch a list of all Gachas through ApiGatewayTwo.
    """
    return forward_request(settings.GACHA_SERVICE, "GET", "/gacha-service/gacha/list/")


@api_view(['POST'])
def createGacha(request):
    """
    Create a new Gacha through ApiGatewayTwo.
    """
    return forward_request(settings.GACHA_SERVICE, "POST", "/gacha-service/gacha/create/", data=request.data)


@api_view(['GET', 'PUT'])
def gachaDetails(request, id):
    """
    Fetch or update Gacha details through ApiGatewayTwo.
    """
    if request.method == 'GET':
        return forward_request(settings.GACHA_SERVICE, "GET", f"/gacha-service/gacha/{id}/details/")
    elif request.method == 'PUT':
        return forward_request(settings.GACHA_SERVICE, "PUT", f"/gacha-service/gacha/{id}/details/", data=request.data)


@api_view(['DELETE'])
def deleteGacha(request, id):
    """
    Delete a Gacha through ApiGatewayTwo.
    """
    return forward_request(settings.GACHA_SERVICE, "DELETE", f"/gacha-service/gacha/{id}/delete/")

# ================= PLAYER COLLECTION: ALL + SINGLE GACHA/S ========================


@api_view(['GET'])
def playerGachaCollections(request, player_id):
    return forward_request(settings.PLAY_SERVICE, "GET", f"/play-service/player/{player_id}/collection/")
# Admins can see a single collection details


@api_view(['GET', 'DELETE'])
def playerGachaCollectionDetails(request, collection_id):
    if request.method == 'GET':
        return forward_request(settings.PLAY_SERVICE, "GET", f"/play-service/player/collection/{collection_id}/")
    elif request.method == 'DELETE':
        return forward_request(settings.PLAY_SERVICE, "DELETE", f"/play-service/player/collection/{collection_id}/")
# ================= VIEW PLAYER TRANSACTIONS ========================


@api_view(['GET'])
def playerGameCurrencyTransactions(request, player_id):
    return forward_request(settings.TRANSACTION_SERVICE, "GET", f"/transactions/player/{player_id}/all/")


# ================= CREATE | UPDATE | DELETE AUCTIONS ========================


@api_view(['GET'])
def listAuctions(request):
    return forward_request(settings.AUCTION_SERVICE, "GET", "/auction/list/")
# only admins can create an auction


@api_view(['POST'])
def createAuction(request):
    return forward_request(settings.AUCTION_SERVICE, "POST", "/auction/create/", data=request.data)
# manage auction details


@api_view(['GET', 'PUT', 'DELETE'])
def auctionDetails(request, id):
    if request.method == 'GET':
        return forward_request(settings.AUCTION_SERVICE, "GET", f"/auction/{id}/details/")
    elif request.method == 'PUT':
        return forward_request(settings.AUCTION_SERVICE, "PUT", f"/auction/{id}/details/", data=request.data)
    elif request.method == 'DELETE':
        return forward_request(settings.AUCTION_SERVICE, "DELETE", f"/auction/{id}/details/")
# admins can view gachas on auction

# ================= VIEW AUCTION GACHAS ========================


@api_view(['GET'])
def listAllGachasOnAuction(request, auction_id):
    return forward_request(settings.AUCTION_SERVICE, "GET", f"/auction/gachas/{auction_id}/list/")


@api_view(['GET', 'DELETE'])
def auctionGachaDetails(request, auction_gacha_id):
    if request.method == 'GET':
        return forward_request(settings.AUCTION_SERVICE, "GET", f"/auction/gachas/{auction_gacha_id}/details/")
    elif request.method == 'DELETE':
        return forward_request(settings.AUCTION_SERVICE, "DELETE", f"/auction/gachas/{auction_gacha_id}/details/")

# ================= VIEW AUCTION BIDS ========================


@api_view(['GET'])
def listAllBids(request, auction_gacha_id):
    return forward_request(settings.AUCTION_SERVICE, "GET", f"/auction/gachas/{auction_gacha_id}/bids/")

# ================= DECLARE THE WINNER ========================


@api_view(['GET'])
def gachaWinner(request, auction_gacha_id):
    return forward_request(settings.AUCTION_SERVICE, "GET", f"/auction/gachas/{auction_gacha_id}/bids/winner/")
