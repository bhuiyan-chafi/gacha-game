import requests
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.conf import settings


def forward_request(service_url, method, path, data=None, query_params=None):
    """
    Helper function to forward requests to the respective services.
    """
    try:
        url = f"{service_url}{path}"
        print('ServiceUrl: ' + url)
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
        return Response({"detail": "Service unavailable", "error": str(e)}, status=status.HTTP_503_SERVICE_UNAVAILABLE)


# ======================== PlayService Endpoints ========================
@api_view(['POST'])
def rollToWinGacha(request):
    player_id = request.query_params.get('player_id')
    # Extract roll_price from the request body
    roll_price = request.data.get('roll_price')

    # Validate player_id
    if not player_id:
        return Response({"detail": "player_id is required as a query parameter."}, status=status.HTTP_400_BAD_REQUEST)

    # Validate roll_price
    if roll_price is None or roll_price == "":
        return Response({"detail": "roll_price is required in the request body or not null"}, status=status.HTTP_400_BAD_REQUEST)

    if not (20 <= int(roll_price) <= 100):
        return Response({"detail": "roll_price must be between 20 and 100."}, status=status.HTTP_400_BAD_REQUEST)

    # Forward the request to the play-service
    return forward_request(
        settings.PLAY_SERVICE,
        "POST",
        "/play-service/roll-to-win/",
        query_params=f"player_id={player_id}",
        data=request.data
    )
# takes the player_id and gacha_id to purchase, next logic is applied inside the PlayService


@api_view(['POST'])
def createPlayerGachaByPurchase(request):
    player_id = request.query_params.get('player_id')
    gacha_id = request.query_params.get('gacha_id')

    if not player_id or not gacha_id:
        return Response({"detail": "Both player_id and gacha_id are required as query parameters."}, status=status.HTTP_400_BAD_REQUEST)

    return forward_request(settings.PLAY_SERVICE, "POST", "/play-service/direct-purchase/", query_params=f"player_id={player_id}&gacha_id={gacha_id}")


@api_view(['GET'])
def playerGachaCollections(request, player_id):
    return forward_request(settings.PLAY_SERVICE, "GET", f"/play-service/player/{player_id}/collection/")


@api_view(['GET', 'DELETE'])
def playerGachaCollectionDetails(request, collection_id):
    if request.method == 'GET':
        return forward_request(settings.PLAY_SERVICE, "GET", f"/play-service/player/collection/{collection_id}/")
    elif request.method == 'DELETE':
        return forward_request(settings.PLAY_SERVICE, "DELETE", f"/play-service/player/collection/{collection_id}/")


# ======================== AuctionService Endpoints ========================
@api_view(['GET'])
def listAuctions(request):
    return forward_request(settings.AUCTION_SERVICE, "GET", "/auction/list/")


@api_view(['POST'])
def createAuction(request):
    return forward_request(settings.AUCTION_SERVICE, "POST", "/auction/create/", data=request.data)


@api_view(['GET', 'PUT', 'DELETE'])
def auctionDetails(request, id):
    if request.method == 'GET':
        return forward_request(settings.AUCTION_SERVICE, "GET", f"/auction/{id}/details/")
    elif request.method == 'PUT':
        return forward_request(settings.AUCTION_SERVICE, "PUT", f"/auction/{id}/details/", data=request.data)
    elif request.method == 'DELETE':
        return forward_request(settings.AUCTION_SERVICE, "DELETE", f"/auction/{id}/details/")


"""
Before placing a gacha for the bid we have to make sure the auction is now 'active' so it's important to have auction_id in the request.
"""


@api_view(['POST'])
def placeGachaForAuction(request):
    if not request.data.get("auction_id"):
        return Response({"detail": "auction_id is required in the request body."}, status=status.HTTP_400_BAD_REQUEST)
    return forward_request(settings.AUCTION_SERVICE, "POST", "/auction/gachas/place/", data=request.data)


@api_view(['GET'])
def listAllGachasOnAuction(request, auction_id):
    return forward_request(settings.AUCTION_SERVICE, "GET", f"/auction/gachas/{auction_id}/list/")


@api_view(['GET', 'DELETE'])
def auctionGachaDetails(request, auction_gacha_id):
    if request.method == 'GET':
        return forward_request(settings.AUCTION_SERVICE, "GET", f"/auction/gachas/{auction_gacha_id}/details/")
    elif request.method == 'DELETE':
        return forward_request(settings.AUCTION_SERVICE, "DELETE", f"/auction/gachas/{auction_gacha_id}/details/")


"""
- check if the gacha present in the request body and its more than 0, following checks will be completed in the service level
"""


@api_view(['POST', 'PUT'])
def bidForGacha(request, auction_gacha_id, player_id):
    if not request.data.get('price') or request.data.get('price') <= 0:
        return Response({"detail": "price is required and more than 0 in the request body."}, status=status.HTTP_400_BAD_REQUEST)
    if request.method == 'POST':
        data = request.data.copy()
        data['auction_gacha_id'] = auction_gacha_id
        data['player_id'] = player_id
        return forward_request(settings.AUCTION_SERVICE, "POST", f"/auction/gachas/{auction_gacha_id}/player/{player_id}/bid/", data=data)
    elif request.method == 'PUT':
        return forward_request(settings.AUCTION_SERVICE, "PUT", f"/auction/gachas/{auction_gacha_id}/player/{player_id}/bid/", data=request.data)


@api_view(['GET'])
def listAllBids(request, auction_gacha_id):
    return forward_request(settings.AUCTION_SERVICE, "GET", f"/auction/gachas/{auction_gacha_id}/bids/")


@api_view(['GET'])
def gachaWinner(request, auction_gacha_id):
    return forward_request(settings.AUCTION_SERVICE, "GET", f"/auction/gachas/{auction_gacha_id}/bids/winner/")


# ======================== TransactionService Endpoints ========================
@api_view(['GET'])
def playerGameCurrencyTransactions(request, player_id):
    return forward_request(settings.TRANSACTION_SERVICE, "GET", f"/transactions/player/{player_id}/all/")


@api_view(['POST'])
def playerGameCurrencyPurchase(request, player_id):
    return forward_request(settings.TRANSACTION_SERVICE, "POST", f"/transactions/player/{player_id}/purchase/game-currency/", data=request.data)


@api_view(['POST'])
def declareAuctionWinner(request):
    return forward_request(settings.TRANSACTION_SERVICE, "POST", "/transactions/auction/winner/declare/", data=request.data)
