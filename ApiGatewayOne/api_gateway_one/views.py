import requests
from django.conf import settings
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import api_view


def forward_request(method, path, data=None):
    """
    Helper function to forward requests to AuthService.
    """
    try:
        url = f"{settings.AUTH_SERVICE}{path}"
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


@api_view(['GET'])
def authServiceTest(request):
    """Test endpoint for the AuthService."""
    return forward_request("GET", "/test/")


@api_view(['POST'])
def createUser(request):
    """Create a new user via AuthService."""
    return forward_request("POST", "/create/", request.data)


@api_view(['GET'])
def listOfUsers(request):
    """List all users via AuthService."""
    return forward_request("GET", "/list/")


@api_view(['GET', 'PUT'])
def userDetails(request, id):
    """Retrieve or update user details via AuthService."""
    path = f"/{id}/details/"
    return forward_request(request.method, path, request.data if request.method == "PUT" else None)


@api_view(['DELETE'])
def deleteUser(request, id):
    """Delete a user via AuthService."""
    path = f"/{id}/delete/"
    return forward_request("DELETE", path)
