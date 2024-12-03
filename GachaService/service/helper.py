import requests
from django.conf import settings
from django.http import JsonResponse
from rest_framework.response import Response
from rest_framework import status


def verifyToken(request):
    """
    Verifies the token by forwarding it to the AuthService's /token/verify/ endpoint.
    """
    # Extract the Authorization header
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        return Response(
            {"detail": "Authentication token was not present in the header"},
            status=status.HTTP_401_UNAUTHORIZED,
        )

    # Define the verify URL
    verify_url = f"{settings.AUTH_SERVICE}/token/verify/"

    try:
        # Forward the request to the AuthService's /token/verify/ endpoint
        auth_response = requests.post(
            verify_url, json=None, headers=request.headers)

        # Check the response status code
        if auth_response.status_code != 200:
            return Response(auth_response.json(), status=auth_response.status_code)

        # If the token is valid, return True
        return True

    except requests.exceptions.RequestException as e:
        # Handle errors during the request
        return Response(
            {"detail": "Failed to connect to the AuthService.",
                "error": str(e)},
            status=status.HTTP_503_SERVICE_UNAVAILABLE,
        )
