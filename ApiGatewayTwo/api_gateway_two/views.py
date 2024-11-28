import requests
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.conf import settings


def forward_request(service_url, method, path, data=None):
    """
    Helper function to forward requests to UserService.
    """
    try:
        url = f"{service_url}{path}"
        print('Service Url: '+url)
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
        return Response({"detail": "Service unavailable", "error": str(e)}, status=status.HTTP_503_SERVICE_UNAVAILABLE)


# ======================== Player Endpoints ========================
@api_view(['GET'])
def listPlayers(request):
    """
    Fetch all players through ApiGatewayTwo.
    """
    return forward_request(settings.USER_SERVICE, "GET", "/user-service/player/list/")


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
        auth_response = requests.get(auth_service_url)

        if auth_response.status_code != 200:
            if auth_response.status_code == 404:
                return Response({"error": "user_id not found in AUTH_SERVICE."}, status=status.HTTP_404_NOT_FOUND)
            return Response({"error": "Error validating user_id with AUTH_SERVICE because the response from AuthService is neither 200 or 404."}, status=auth_response.status_code)

        user_data = auth_response.json()

        # Ensure the returned user_id matches the input user_id
        if str(user_data.get("id")) != str(user_id):
            return Response({"error": "Invalid user_id, the user_id fetched from AUTH_SERVICE does not match the given one."}, status=status.HTTP_400_BAD_REQUEST)

        # Step 2: Check if the user_id is associated with an admin
        admin_service_url = f"{settings.USER_SERVICE}/user-service/admin/{user_id}/details/"
        admin_response = requests.get(admin_service_url)

        if admin_response.status_code == 200:
            # user_id is already taken by an admin
            return Response(
                {"error": "user_id is associated with an admin and cannot be used for a player."},
                status=status.HTTP_400_BAD_REQUEST
            )
        elif admin_response.status_code != 404:
            # Handle unexpected responses from the admin endpoint
            return Response({"error": "Error validating user_id with admin check."}, status=admin_response.status_code)

        # Step 3: Proceed to create the Player
        return forward_request(settings.USER_SERVICE, "POST", "/user-service/player/create/", data=request.data)

    except requests.RequestException as e:
        # Handle request errors
        return Response({"error": f"Unable to validate user_id: {str(e)}"}, status=status.HTTP_503_SERVICE_UNAVAILABLE)


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


@api_view(['DELETE'])
def deletePlayer(request, id):
    """
    Delete a specific player through ApiGatewayTwo.
    """
    return forward_request(settings.USER_SERVICE, "DELETE", f"/user-service/player/{id}/delete/")


# ======================== Admin Endpoints ========================
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


# ======================== Gacha Endpoints ========================
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


# ======================== System Variable Endpoints ========================
@api_view(['POST'])
def createSystemVariable(request):
    """
    Create a new system variable through ApiGatewayTwo.
    """
    return forward_request(settings.GACHA_SERVICE, "POST", "/system-variables/create/", data=request.data)


@api_view(['GET'])
def listSystemVariables(request):
    """
    Fetch a list of all system variables through ApiGatewayTwo.
    """
    return forward_request(settings.GACHA_SERVICE, "GET", "/system-variables/list/")


@api_view(['GET', 'PUT', 'DELETE'])
def systemVariableDetails(request, id):
    """
    Fetch, update, or delete a specific system variable through ApiGatewayTwo.
    """
    if request.method == 'GET':
        return forward_request(settings.GACHA_SERVICE, "GET", f"/system-variables/{id}/details/")
    elif request.method == 'PUT':
        return forward_request(settings.GACHA_SERVICE, "PUT", f"/system-variables/{id}/details/", data=request.data)
    elif request.method == 'DELETE':
        return forward_request(settings.GACHA_SERVICE, "DELETE", f"/system-variables/{id}/details/")
