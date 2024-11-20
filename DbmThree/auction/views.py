from django.shortcuts import get_object_or_404
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .models import Auction, AuctionGachaBid, AuctionGachas
from .serializers import AuctionGachaBidSerializer, AuctionSerializer, AuctionGachasSerializer

# List all auctions


@api_view(['GET'])
def listAuctions(request):
    auctions = Auction.objects.all()
    serializer = AuctionSerializer(auctions, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)

# create a new auction


@api_view(['POST'])
def createAuction(request):
    serializer = AuctionSerializer(data=request.data)
    if serializer.is_valid():
        auction = serializer.save()
        return Response({
            'detail': 'Auction created successfully.',
            'auction': AuctionSerializer(auction).data
        }, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# see details or update or delete a auction


@api_view(['GET', 'PUT', 'DELETE'])
def auctionDetails(request, id):
    auction = get_object_or_404(Auction, pk=id)

    if request.method == 'GET':
        # Fetch and return auction details
        serializer = AuctionSerializer(auction)
        return Response(serializer.data, status=status.HTTP_200_OK)

    elif request.method == 'PUT':
        # Update auction details
        serializer = AuctionSerializer(
            auction, data=request.data, partial=True)
        if serializer.is_valid():
            updated_auction = serializer.save()
            return Response({
                'detail': 'Auction updated successfully.',
                'auction': AuctionSerializer(updated_auction).data
            }, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        # Ensure the auction is not active before deleting
        if auction.status == 'active':
            return Response({
                'detail': 'Active auctions cannot be deleted. Please deactivate the auction first.'
            }, status=status.HTTP_400_BAD_REQUEST)

        # Delete the auction
        auction.delete()
        return Response({
            'detail': 'Auction deleted successfully.'
        }, status=status.HTTP_204_NO_CONTENT)

# 1. Place a gacha for the auction


@api_view(['POST'])
def placeGachaForAuction(request):
    """
    Endpoint to place a gacha for auction.
    The request must include auction_id, collection_id, and price.
    """
    serializer = AuctionGachasSerializer(data=request.data)
    if serializer.is_valid():
        # Save the new AuctionGachas entry
        auction_gacha = serializer.save()
        return Response({
            'detail': 'Gacha successfully placed for auction.',
            'auction_gacha': AuctionGachasSerializer(auction_gacha).data
        }, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# 2. List all gachas on auction for a specific auction_id
@api_view(['GET'])
def listAllGachasOnAuction(request, auction_id):
    """
    Endpoint to list all gachas on auction for a specific auction.
    """
    # Verify if the auction exists
    get_object_or_404(Auction, pk=auction_id)

    # Fetch all gachas for this auction
    gachas_on_auction = AuctionGachas.objects.filter(auction_id=auction_id)
    serializer = AuctionGachasSerializer(gachas_on_auction, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)


# 3. Remove a gacha from the auction
@api_view(['GET', 'DELETE'])
def auctionGachaDetails(request, auction_gacha_id):
    """
    Endpoint to manage a gacha in the auction.
    GET: Retrieve details of the auction gacha.
    DELETE: Remove a gacha from the auction (if not sold).
    """
    auction_gacha = get_object_or_404(AuctionGachas, pk=auction_gacha_id)

    if request.method == 'GET':
        # Serialize and return the auction gacha details
        serializer = AuctionGachasSerializer(auction_gacha)
        return Response(serializer.data, status=status.HTTP_200_OK)

    elif request.method == 'DELETE':
        # Prevent removal if the gacha is already sold
        if auction_gacha.status == 'sold':
            return Response({
                'detail': 'Cannot remove a sold gacha from the auction.'
            }, status=status.HTTP_400_BAD_REQUEST)

        # Delete the gacha from the auction
        auction_gacha.delete()
        return Response({'detail': 'Gacha removed from auction successfully.'}, status=status.HTTP_204_NO_CONTENT)

# bid to acquire a gacha


@api_view(['POST', 'PUT'])
def bidForGacha(request, auction_gacha_id, player_id):
    """
    Handles bids for gachas in an auction.
    POST: Creates a new bid.
    PUT: Updates the price of an existing bid.
    """
    if request.method == 'POST':
        # Create a new bid
        data = request.data.copy()  # Make a mutable copy of request.data
        data['auction_gacha_id'] = auction_gacha_id
        data['bidder_id'] = player_id

        # Fetch the highest bid for this auction_gacha_id
        highest_bid = AuctionGachaBid.objects.filter(
            auction_gacha_id=auction_gacha_id
        ).order_by('-price').first()

        # Validate the bid price
        new_price = float(data.get('price', 0))
        if highest_bid and new_price <= highest_bid.price:
            return Response({
                'detail': f"Bid price must be greater than the current highest bid ({highest_bid.price})."
            }, status=status.HTTP_400_BAD_REQUEST)

        serializer = AuctionGachaBidSerializer(data=data)
        if serializer.is_valid():
            bid = serializer.save()
            return Response({
                'detail': 'Bid placed successfully.',
                'bid': AuctionGachaBidSerializer(bid).data
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'PUT':
        # Update the price of an existing bid
        bid = get_object_or_404(
            AuctionGachaBid, auction_gacha_id=auction_gacha_id, bidder_id=player_id
        )
        if 'price' not in request.data:
            return Response({'detail': 'Price is required for updating a bid.'}, status=status.HTTP_400_BAD_REQUEST)

        new_price = float(request.data['price'])

        # Fetch the highest bid for this auction_gacha_id
        highest_bid = AuctionGachaBid.objects.filter(
            auction_gacha_id=auction_gacha_id
        ).exclude(pk=bid.pk).order_by('-price').first()

        if highest_bid and new_price <= highest_bid.price:
            return Response({
                'detail': f"Bid price must be greater than the current highest bid ({highest_bid.price})."
            }, status=status.HTTP_400_BAD_REQUEST)

        # Update only the price field
        bid.price = new_price
        bid.save()
        return Response({
            'detail': 'Bid updated successfully.',
            'bid': AuctionGachaBidSerializer(bid).data
        }, status=status.HTTP_200_OK)

# list all bids


@api_view(['GET'])
def listAllBids(request, auction_gacha_id):
    """
    Fetch all bids for a specific auction_gacha_id.
    """
    # Check if there are any bids associated with the given auction_gacha_id
    bids = AuctionGachaBid.objects.filter(auction_gacha_id=auction_gacha_id)

    if not bids.exists():
        return Response(
            {"detail": f"No bids found for auction gacha ID {auction_gacha_id}."},
            status=status.HTTP_404_NOT_FOUND,
        )

    # Serialize the data and return the response
    serializer = AuctionGachaBidSerializer(bids, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)

# get the winner


@api_view(['GET'])
def gachaWinner(request, auction_gacha_id):
    """
    Retrieve the highest bidder for a specific auction gacha.
    """
    # Ensure the auction_gacha exists
    auction_gacha = get_object_or_404(AuctionGachas, pk=auction_gacha_id)

    # Get the highest bid for the given auction_gacha_id
    highest_bid = AuctionGachaBid.objects.filter(
        auction_gacha_id=auction_gacha_id
    ).order_by('-price').first()

    if not highest_bid:
        return Response(
            {"detail": f"No bids found for auction gacha ID {auction_gacha_id}."},
            status=status.HTTP_404_NOT_FOUND
        )

    # Serialize the highest bid
    serializer = AuctionGachaBidSerializer(highest_bid)
    return Response({
        "auction_gacha_id": auction_gacha_id,
        "winner": serializer.data
    }, status=status.HTTP_200_OK)
