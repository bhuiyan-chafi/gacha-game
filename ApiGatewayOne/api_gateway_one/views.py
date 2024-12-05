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


def forward_request(source, method, path, data=None, headers=None):
    """
    Helper function to forward requests to AuthService.
    """
    try:
        url = f"{source}{path}"
        headers = headers or {}
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
    headers = {"Authorization": request.headers.get("Authorization")}
    return forward_request(settings.AUTH_SERVICE, "POST", path, request.data, headers)


@api_view(['POST'])
def verifyToken(request):
    """Logout a user via AuthService."""
    path = f"/token/verify/"
    headers = {
        "Authorization": request.headers.get("Authorization"),
        "Role": ','.join(settings.ADMIN_ROLE),
    }
    return forward_request(settings.AUTH_SERVICE, "POST", path, request.data, headers)

# ================= CREATE | UPDATE | DELETE USERS ========================


@api_view(['POST'])
def createUser(request):
    """Create a new user via AuthService."""
    return forward_request(settings.AUTH_SERVICE, "POST", "/create/", request.data)


@api_view(['GET'])
def listOfUsers(request):
    """List all users via AuthService."""
    # we are not sending the roles here because the userlist is inside AuthService which already has the role implemented: see views.py in AuthService
    headers = {
        "Authorization": request.headers.get("Authorization"),
    }
    return forward_request(settings.AUTH_SERVICE, "GET", "/list/", None, headers)


@api_view(['GET', 'PUT'])
def userDetails(request, id):
    headers = {
        "Authorization": request.headers.get("Authorization"),

    }
    """Retrieve or update user details via AuthService."""
    path = f"/{id}/details/"
    return forward_request(settings.AUTH_SERVICE, request.method, path, request.data if request.method == "PUT" else None, headers)


@api_view(['DELETE'])
def deleteUser(request, id):
    """Delete a user via AuthService."""
    headers = {
        "Authorization": request.headers.get("Authorization"),
    }
    path = f"/{id}/delete/"
    return forward_request(settings.AUTH_SERVICE, "DELETE", path, None, headers)


# ================= CREATE | UPDATE | DELETE ADMINS ========================

@api_view(['GET'])
def listAdmins(request):
    # return Response(request.headers, 200)
    """
    Fetch all admins through ApiGatewayTwo.
    """
    headers = {
        "Authorization": request.headers.get("Authorization"),
        # Convert list to a comma-separated string
        "Role": ','.join(settings.ADMIN_ROLE),
    }
    return forward_request(settings.USER_SERVICE, "GET", "/user-service/admin/list/", None, headers)


@api_view(['POST'])
def createAdmin(request):
    """
    Create a new admin through ApiGatewayTwo.
    """
    return forward_request(settings.USER_SERVICE, "POST", "/user-service/admin/create/", request.data)


@api_view(['GET', 'PUT'])
def adminDetails(request, id):
    """
    Fetch or update details of a specific admin through ApiGatewayTwo.
    """
    headers = {
        "Authorization": request.headers.get("Authorization"),
        # Convert list to a comma-separated string
        "Role": ','.join(settings.ADMIN_ROLE),
    }
    if request.method == 'GET':
        return forward_request(settings.USER_SERVICE, "GET", f"/user-service/admin/{id}/details/", None, headers)
    elif request.method == 'PUT':
        return forward_request(settings.USER_SERVICE, "PUT", f"/user-service/admin/{id}/details/", request.data, headers)


@api_view(['DELETE'])
def deleteAdmin(request, id):
    """
    Delete a specific admin through ApiGatewayTwo.
    """
    headers = {
        "Authorization": request.headers.get("Authorization"),
        # Convert list to a comma-separated string
        "Role": ','.join(settings.ADMIN_ROLE),
    }
    return forward_request(settings.USER_SERVICE, "DELETE", f"/user-service/admin/{id}/delete/", None, headers)

# ================= CREATE | UPDATE | DELETE PLAYERS ========================


@api_view(['GET'])
def listPlayers(request):
    """
    Fetch all players through ApiGatewayTwo.
    """
    headers = {
        "Authorization": request.headers.get("Authorization"),
        # Convert list to a comma-separated string
        "Role": ','.join(settings.ADMIN_ROLE),
    }
    return forward_request(settings.USER_SERVICE, "GET", "/user-service/player/list/", None, headers)

# both admins and players can see their profiles and update


@api_view(['GET', 'PUT'])
def playerDetails(request, id):
    """
    Fetch or update details of a specific player through ApiGatewayTwo.
    """
    headers = {
        "Authorization": request.headers.get("Authorization"),
        # Convert list to a comma-separated string
        "Role": ','.join(settings.ADMIN_ROLE),
    }
    if request.method == 'GET':
        return forward_request(settings.USER_SERVICE, "GET", f"/user-service/player/{id}/details/", None, headers)
    elif request.method == 'PUT':
        if 'user_id' in request.data:
            return Response(
                {"error": "Updating user_id is not allowed."},
                status=status.HTTP_400_BAD_REQUEST
            )
        return forward_request(settings.USER_SERVICE, "PUT", f"/user-service/player/{id}/details/", request.data, headers)
# both admin and player can delete player profile


@api_view(['DELETE'])
def deletePlayer(request, id):
    """
    Delete a specific player through ApiGatewayTwo.
    """
    headers = {
        "Authorization": request.headers.get("Authorization"),
        "Role": ','.join(settings.ADMIN_ROLE),
    }
    return forward_request(settings.USER_SERVICE, "DELETE", f"/user-service/player/{id}/delete/", None, headers)

# ================= CREATE | UPDATE | DELETE GACHAS ========================


@api_view(['GET'])
def listGachas(request):
    """
    Fetch a list of all Gachas through ApiGatewayTwo.
    """
    headers = {
        "Authorization": request.headers.get("Authorization"),
        "Role": ','.join(settings.ADMIN_ROLE),
    }
    return forward_request(settings.GACHA_SERVICE, "GET", "/gacha-service/gacha/list/", None, headers)


@api_view(['POST'])
def createGacha(request):
    """
    Create a new Gacha through ApiGatewayTwo.
    """
    headers = {
        "Authorization": request.headers.get("Authorization"),
        "Role": ','.join(settings.ADMIN_ROLE),
    }
    return forward_request(settings.GACHA_SERVICE, "POST", "/gacha-service/gacha/create/", request.data, headers)


@api_view(['GET', 'PUT'])
def gachaDetails(request, id):
    """
    Fetch or update Gacha details through ApiGatewayTwo.
    """
    headers = {
        "Authorization": request.headers.get("Authorization"),
        "Role": ','.join(settings.ADMIN_ROLE),
    }
    if request.method == 'GET':
        return forward_request(settings.GACHA_SERVICE, "GET", f"/gacha-service/gacha/{id}/details/", None, headers)
    elif request.method == 'PUT':
        return forward_request(settings.GACHA_SERVICE, "PUT", f"/gacha-service/gacha/{id}/details/", request.data, headers)


@api_view(['DELETE'])
def deleteGacha(request, id):
    """
    Delete a Gacha through ApiGatewayTwo.
    """
    headers = {
        "Authorization": request.headers.get("Authorization"),
        "Role": ','.join(settings.ADMIN_ROLE),
    }
    return forward_request(settings.GACHA_SERVICE, "DELETE", f"/gacha-service/gacha/{id}/delete/", None, headers)

# ================= PLAYER COLLECTION: ALL + SINGLE GACHA/S ========================


@api_view(['GET'])
def playerGachaCollections(request, player_id):
    headers = {
        "Authorization": request.headers.get("Authorization"),
        "Role": ','.join(settings.ADMIN_ROLE),
    }
    return forward_request(settings.PLAY_SERVICE, "GET", f"/play-service/player/{player_id}/collection/", None, headers)
# Admins can see a single collection details


@api_view(['GET', 'DELETE'])
def playerGachaCollectionDetails(request, collection_id):
    headers = {
        "Authorization": request.headers.get("Authorization"),
        "Role": ','.join(settings.ADMIN_ROLE),
    }
    if request.method == 'GET':
        return forward_request(settings.PLAY_SERVICE, "GET", f"/play-service/player/collection/{collection_id}/", None, headers)
    elif request.method == 'DELETE':
        return forward_request(settings.PLAY_SERVICE, "DELETE", f"/play-service/player/collection/{collection_id}/", None, headers)
# ================= VIEW PLAYER TRANSACTIONS ========================


@api_view(['GET'])
def playerGameCurrencyTransactions(request, player_id):
    headers = {
        "Authorization": request.headers.get("Authorization"),
        "Role": ','.join(settings.ADMIN_ROLE),
    }
    return forward_request(settings.TRANSACTION_SERVICE, "GET", f"/transactions/player/{player_id}/all/", None, headers)


# ================= CREATE | UPDATE | DELETE AUCTIONS ========================


@api_view(['GET'])
def listAuctions(request):
    headers = {
        "Authorization": request.headers.get("Authorization"),
        "Role": ','.join(settings.ADMIN_ROLE),
    }
    return forward_request(settings.AUCTION_SERVICE, "GET", "/auction/list/", None, headers)
# only admins can create an auction


@api_view(['POST'])
def createAuction(request):
    headers = {
        "Authorization": request.headers.get("Authorization"),
        "Role": ','.join(settings.ADMIN_ROLE),
    }
    return forward_request(settings.AUCTION_SERVICE, "POST", "/auction/create/", request.data, headers)
# manage auction details


@api_view(['GET', 'PUT', 'DELETE'])
def auctionDetails(request, id):
    headers = {
        "Authorization": request.headers.get("Authorization"),
        "Role": ','.join(settings.ADMIN_ROLE),
    }
    if request.method == 'GET':
        return forward_request(settings.AUCTION_SERVICE, "GET", f"/auction/{id}/details/", None, headers)
    elif request.method == 'PUT':
        return forward_request(settings.AUCTION_SERVICE, "PUT", f"/auction/{id}/details/", request.data, headers)
    elif request.method == 'DELETE':
        return forward_request(settings.AUCTION_SERVICE, "DELETE", f"/auction/{id}/details/", None, headers)
# admins can view gachas on auction

# ================= VIEW AUCTION GACHAS ========================


@api_view(['GET'])
def listAllGachasOnAuction(request, auction_id):
    headers = {
        "Authorization": request.headers.get("Authorization"),
        "Role": ','.join(settings.ADMIN_ROLE),
    }
    return forward_request(settings.AUCTION_SERVICE, "GET", f"/auction/gachas/{auction_id}/list/", None, headers)


@api_view(['GET', 'DELETE'])
def auctionGachaDetails(request, auction_gacha_id):
    headers = {
        "Authorization": request.headers.get("Authorization"),
        "Role": ','.join(settings.ADMIN_ROLE),
    }
    if request.method == 'GET':
        return forward_request(settings.AUCTION_SERVICE, "GET", f"/auction/gachas/{auction_gacha_id}/details/", None, headers)
    elif request.method == 'DELETE':
        return forward_request(settings.AUCTION_SERVICE, "DELETE", f"/auction/gachas/{auction_gacha_id}/details/", None, headers)

# ================= VIEW AUCTION BIDS ========================


@api_view(['GET'])
def listAllBids(request, auction_gacha_id):
    headers = {
        "Authorization": request.headers.get("Authorization"),
        "Role": ','.join(settings.ADMIN_ROLE),
    }
    return forward_request(settings.AUCTION_SERVICE, "GET", f"/auction/gachas/{auction_gacha_id}/bids/", None, headers)

# ================= DECLARE THE WINNER ========================


@api_view(['GET'])
def gachaWinner(request, auction_gacha_id):
    headers = {
        "Authorization": request.headers.get("Authorization"),
        "Role": ','.join(settings.ADMIN_ROLE),
        "Content-Type": 'application/json'
    }
    return forward_request(settings.AUCTION_SERVICE, "GET", f"/auction/gachas/{auction_gacha_id}/bids/winner/", None, headers)
