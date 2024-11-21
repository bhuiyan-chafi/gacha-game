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
    Create a new player through ApiGatewayTwo.
    """
    return forward_request(settings.USER_SERVICE, "POST", "/user-service/player/create/", data=request.data)


@api_view(['GET', 'PUT'])
def playerDetails(request, id):
    """
    Fetch or update details of a specific player through ApiGatewayTwo.
    """
    if request.method == 'GET':
        return forward_request(settings.USER_SERVICE, "GET", f"/user-service/player/{id}/details/")
    elif request.method == 'PUT':
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
