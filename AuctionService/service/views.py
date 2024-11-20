import requests
from django.conf import settings
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status


def forward_request(method, path, data=None):
    """
    Helper function to forward requests to DbmThree Auction endpoints.
    """
    try:
        url = f"{settings.DATABASE_THREE}{path}"
        print('URL FOR DB THREE: ' + url)
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


@api_view(['GET'])
def listAuctions(request):
    """
    Proxy for listing all auctions.
    """
    return forward_request("GET", "/auction/list/")


@api_view(['POST'])
def createAuction(request):
    """
    Proxy for creating a new auction.
    """
    return forward_request("POST", "/auction/create/", data=request.data)


@api_view(['GET', 'PUT', 'DELETE'])
def auctionDetails(request, id):
    """
    Proxy for getting, updating, or deleting auction details.
    """
    if request.method == 'GET':
        return forward_request("GET", f"/auction/{id}/details/")
    elif request.method == 'PUT':
        return forward_request("PUT", f"/auction/{id}/details/", data=request.data)
    elif request.method == 'DELETE':
        return forward_request("DELETE", f"/auction/{id}/details/")

# ====================== Bidding Views ============================


@api_view(['POST'])
def placeGachaForAuction(request):
    """
    Proxy for placing a gacha for auction.
    """
    return forward_request("POST", "/auction/gachas/place/", data=request.data)


@api_view(['GET'])
def listAllGachasOnAuction(request, auction_id):
    """
    Proxy for listing all gachas on auction for a specific auction ID.
    """
    return forward_request("GET", f"/auction/gachas/{auction_id}/list/")


@api_view(['GET', 'DELETE'])
def auctionGachaDetails(request, auction_gacha_id):
    """
    Proxy for getting details of or deleting a specific gacha on auction.
    """
    if request.method == 'GET':
        return forward_request("GET", f"/auction/gachas/{auction_gacha_id}/details/")
    elif request.method == 'DELETE':
        return forward_request("DELETE", f"/auction/gachas/{auction_gacha_id}/details/")


@api_view(['POST', 'PUT'])
def bidForGacha(request, auction_gacha_id, player_id):
    """
    Proxy for bidding on a gacha in an auction.
    """
    if request.method == 'POST':
        data = request.data.copy()
        data['auction_gacha_id'] = auction_gacha_id
        data['player_id'] = player_id
        return forward_request("POST", f"/auction/gachas/{auction_gacha_id}/player/{player_id}/bid/", data=data)
    elif request.method == 'PUT':
        return forward_request("PUT", f"/auction/gachas/{auction_gacha_id}/player/{player_id}/bid/", data=request.data)


@api_view(['GET'])
def listAllBids(request, auction_gacha_id):
    """
    Proxy for listing all bids for a specific auction gacha.
    """
    return forward_request("GET", f"/auction/gachas/{auction_gacha_id}/bids/")


@api_view(['GET'])
def gachaWinner(request, auction_gacha_id):
    """
    Proxy for retrieving the winner of an auction gacha.
    """
    return forward_request("GET", f"/auction/gachas/{auction_gacha_id}/bids/winner/")
