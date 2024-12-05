from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
import requests
from django.conf import settings
from . import helper


def forward_request(method, path, data=None, headers=None):
    """
    Helper function to forward requests to DbmThree endpoints.
    """
    try:
        url = f"{settings.DATABASE_THREE}{path}"
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


@api_view(['GET'])
def playerGameCurrencyTransactions(request, player_id):
    """
    Proxy for retrieving all in-game currency transactions for a specific player.
    """
    # return Response(request.headers, status=status.HTTP_200_OK)
    # Verify the token using the helper function
    verify_token = helper.verifyToken(request)

    # Check if the token verification failed
    if not isinstance(verify_token, bool) or not verify_token:
        return verify_token  # Return the failure response from verifyToken
    return forward_request("GET", f"/transaction/player/{player_id}/all/")


@api_view(['POST'])
def playerGameCurrencyPurchase(request, player_id):
    # return Response({"location": "transaction_services", "headers": request.headers}, status=status.HTTP_200_OK)
    """
    Proxy for handling in-game currency purchases for a specific player.
    """
    # return Response(request.headers, status=status.HTTP_200_OK)
    # Verify the token using the helper function
    verify_token = helper.verifyToken(request)

    # Check if the token verification failed
    if not isinstance(verify_token, bool) or not verify_token:
        return verify_token  # Return the failure response from verifyToken
    return forward_request("POST", f"/transaction/player/{player_id}/purchase/game-currency/", data=request.data, headers=request.headers)
