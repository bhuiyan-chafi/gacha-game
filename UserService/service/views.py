import requests
from django.conf import settings
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework import status
from . import helper


def forward_request(method, path, data=None, headers=None):
    """
    Helper function to forward requests to UserService Service.
    """
    try:
        url = f"{settings.DATABASE_TWO}{path}"
        if method == "GET":
            response = requests.get(
                url, verify=settings.SSL_VERIFY, timeout=5, headers=headers)
        elif method == "POST":
            response = requests.post(
                url, json=data, verify=settings.SSL_VERIFY, timeout=5, headers=headers)
        elif method == "PUT":
            response = requests.put(
                url, json=data, verify=settings.SSL_VERIFY, timeout=5, headers=headers)
        elif method == "DELETE":
            response = requests.delete(
                url, verify=settings.SSL_VERIFY, timeout=5, headers=headers)
        else:
            raise ValueError(f"Unsupported HTTP method: {method}")

        # Handle successful responses
        if response.status_code == status.HTTP_204_NO_CONTENT:
            return Response({'detail': 'Operation successful.'}, status=status.HTTP_204_NO_CONTENT)

        return Response(response.json(), status=response.status_code)
    except requests.exceptions.RequestException as e:
        return Response({"detail": "UserService service unavailable", "error": str(e)}, status=status.HTTP_503_SERVICE_UNAVAILABLE)

# ======================== Player Endpoints ========================


@api_view(['GET'])
def listPlayersFromUserService(request):
    """
    Fetch all players from the UserService service.
    """
    # return Response(request.headers, status=status.HTTP_200_OK)
    """
    Fetch all admins from the UserService service.
    """
    # Verify the token using the helper function
    verify_token = helper.verifyToken(request)

    # Check if the token verification failed
    if not isinstance(verify_token, bool) or not verify_token:
        return verify_token  # Return the failure response from verifyToken

    return forward_request("GET", "/player/list/", headers=request.headers)


@api_view(['POST'])
def createPlayerInUserService(request):
    """
    Create a new player in the UserService service.
    """
    return forward_request("POST", "/player/create/", data=request.data, headers=request.headers)


@api_view(['GET', 'PUT'])
def playerDetailsFromUserService(request, id):
    """
    Fetch or update details of a specific player in the UserService service.
    """
    """
    Fetch all admins from the UserService service.
    """
    # Verify the token using the helper function
    verify_token = helper.verifyToken(request)

    # Check if the token verification failed
    if not isinstance(verify_token, bool) or not verify_token:
        return verify_token  # Return the failure response from verifyToken

    if request.method == 'GET':
        return forward_request("GET", f"/player/{id}/details/", headers=request.headers)
    elif request.method == 'PUT':
        return forward_request("PUT", f"/player/{id}/details/", data=request.data, headers=request.headers)


@api_view(['DELETE'])
def deletePlayerFromUserService(request, id):
    """
    Delete a specific player in the UserService service.
    """
    # return Response(request.headers, status=status.HTTP_200_OK)
    """
    Fetch all admins from the UserService service.
    """
    # Verify the token using the helper function
    verify_token = helper.verifyToken(request)

    # Check if the token verification failed
    if not isinstance(verify_token, bool) or not verify_token:
        return verify_token  # Return the failure response from verifyToken

    return forward_request("DELETE", f"/player/{id}/delete/", headers=request.headers)

# ======================== Admin Endpoints ========================


@api_view(['GET'])
def listAdminsFromUserService(request):
    """
    Fetch all admins from the UserService service.
    """
    # return Response(request.headers, status=status.HTTP_200_OK)
    # Verify the token using the helper function
    verify_token = helper.verifyToken(request)

    # Check if the token verification failed
    if not isinstance(verify_token, bool) or not verify_token:
        return verify_token  # Return the failure response from verifyToken

    # If the token is valid, proceed to forward the request
    return forward_request("GET", "/admin/list/", headers=request.headers)


@api_view(['POST'])
def createAdminInUserService(request):
    """
    Create a new admin in the UserService service.
    """
    return forward_request("POST", "/admin/create/", data=request.data, headers=request.headers)


@api_view(['GET', 'PUT'])
def adminDetailsFromUserService(request, id):
    # return Response(request.headers, status=status.HTTP_200_OK)
    # """
    # Fetch or update details of a specific admin in the UserService service.
    # """
    # # Verify the token using the helper function
    # verify_token = helper.verifyToken(request)

    # # Check if the token verification failed
    # if not isinstance(verify_token, bool) or not verify_token:
    #     return verify_token  # Return the failure response from verifyToken
    if request.method == 'GET':
        return forward_request("GET", f"/admin/{id}/details/")
    elif request.method == 'PUT':
        return forward_request("PUT", f"/admin/{id}/details/", data=request.data, headers=request.headers)


@api_view(['DELETE'])
def deleteAdminFromUserService(request, id):
    # return Response({'headers': request.headers}, status=200)
    """
    Delete a specific admin in the UserService service.
    """
    # Verify the token using the helper function
    verify_token = helper.verifyToken(request)

    # Check if the token verification failed
    if not isinstance(verify_token, bool) or not verify_token:
        return verify_token  # Return the failure response from verifyToken
    return forward_request("DELETE", f"/admin/{id}/delete/", headers=request.headers)
