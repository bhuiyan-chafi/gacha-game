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


@api_view(['POST'])
def rollToWinGacha(request):
    """
    Proxy for rolling to win a gacha.
    """
    player_id = request.query_params.get('player_id')
    if not player_id:
        return Response({"detail": "player_id is required as a query parameter."}, status=status.HTTP_400_BAD_REQUEST)

    return forward_request("POST", "/gacha-collection/roll-to-win/", query_params=f"player_id={player_id}")


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
