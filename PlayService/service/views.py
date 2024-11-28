import requests
from django.conf import settings
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status


def forward_request(method, path, data=None, query_params=None):
    """
    Helper function to forward requests to DbmThree.
    """
    try:
        url = f"{settings.DATABASE_THREE}{path}"
        if query_params:
            url = f"{url}?{query_params}"

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
        return Response({"detail": "DbmThree service unavailable", "error": str(e)}, status=status.HTTP_503_SERVICE_UNAVAILABLE)


"""
This proxy will filter the player_id and forward the request to the DBM, if the player_id is not valid the request stops here.
"""
# roll with price win a gacha


@api_view(['POST'])
def rollToWinGacha(request):
    """
    Proxy for rolling to win a gacha, validating the player_id with the user-service first.
    """
    player_id = request.query_params.get('player_id')
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
        # Validate player_id by calling the user-service
        user_service_url = f"{settings.USER_SERVICE}/user-service/player/{player_id}/details/"
        response = requests.get(user_service_url)

        if response.status_code == 200:
            # Parse the response JSON
            user_data = response.json()

            # Validate player_id
            if str(user_data.get("id")) != str(player_id):
                return Response({"error": "player_id mismatch in user-service."}, status=status.HTTP_400_BAD_REQUEST)

            # Validate current_balance
            current_balance = user_data.get("current_balance")
            if current_balance is None:
                return Response({"error": "current_balance is missing in user-service response."}, status=status.HTTP_400_BAD_REQUEST)

            if current_balance < roll_price:
                return Response({"error": "Insufficient balance for the roll."}, status=status.HTTP_400_BAD_REQUEST)

            # Proceed to forward the request to the gacha collection service
            return forward_request(
                "POST",
                "/gacha-collection/roll-to-win/",
                query_params=f"player_id={player_id}",
                data=request.data
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


@api_view(['POST'])
def createPlayerGachaByPurchase(request):
    """
    Proxy for purchasing a gacha directly.
    """
    player_id = request.query_params.get('player_id')
    gacha_id = request.query_params.get('gacha_id')

    if not player_id or not gacha_id:
        return Response({"detail": "Both player_id and gacha_id are required as query parameters."}, status=status.HTTP_400_BAD_REQUEST)

    return forward_request("POST", "/gacha-collection/direct-purchase/", query_params=f"player_id={player_id}&gacha_id={gacha_id}")


@api_view(['GET'])
def playerGachaCollections(request, player_id):
    """
    Proxy for fetching a player's gacha collection.
    """
    return forward_request("GET", f"/gacha-collection/player/{player_id}/collection/")


@api_view(['GET', 'DELETE'])
def playerGachaCollectionDetails(request, collection_id):
    """
    Proxy for fetching or deleting a specific player's gacha collection record.
    """
    if request.method == 'GET':
        return forward_request("GET", f"/gacha-collection/player/collection/{collection_id}/")
    elif request.method == 'DELETE':
        return forward_request("DELETE", f"/gacha-collection/player/collection/{collection_id}/")
