import requests
from django.shortcuts import get_object_or_404
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.db import transaction
from own_gacha.models import PlayerGachaCollection
from .models import Auction, AuctionGachaBid, AuctionGachas
from .serializers import AuctionGachaBidSerializer, AuctionSerializer, AuctionGachasSerializer
from django.conf import settings

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
        # Fetch the auction_gacha details
        auction_gacha = get_object_or_404(AuctionGachas, pk=auction_gacha_id)

        # Extract asking price from auction_gacha
        asking_price = auction_gacha.price

        # Validate the bid price
        new_price = float(data.get('price', 0))

        # Check if the bid price is less than the asking price
        if new_price < asking_price:
            return Response({
                'detail': f"Bid price must be greater than or equal to the asking price ({asking_price})."
            }, status=status.HTTP_400_BAD_REQUEST)
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
    bids = AuctionGachaBid.objects.filter(
        auction_gacha_id=auction_gacha_id).order_by('-price')

    if not bids.exists():
        return Response(
            {"detail": f"No bids found for auction gacha ID {auction_gacha_id}."},
            status=status.HTTP_404_NOT_FOUND,
        )

    # Serialize the data and return the response
    serializer = AuctionGachaBidSerializer(bids, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)


"""
- we update the owner of the gacha by the bidder
- we update the balance of each player [player, bidder]
"""


@api_view(['POST'])
def gachaWinner(request):
    # Extract data from the request body
    # return Response({"location": "dbmthree", "headers": request.headers}, status=status.HTTP_200_OK)
    auction_gacha_id = request.data.get("auction_gacha_id")
    bidder_id = request.data.get("bidder_id")
    print('Bidder ID: ', bidder_id)
    price = request.data.get("price")
    try:
        with transaction.atomic():
            # Step 1: Get the AuctionGacha record
            auction_gacha = get_object_or_404(
                AuctionGachas, id=auction_gacha_id)
            auction_gacha_serializer = AuctionGachasSerializer(auction_gacha)

            # Extract the collection_id
            collection_id = auction_gacha_serializer.data.get("collection_id")
            auction_id = auction_gacha_serializer.data.get("auction_id")
            if not collection_id:
                return Response(
                    {"detail": "Collection ID not found for the given auction gacha."},
                    status=status.HTTP_404_NOT_FOUND
                )

            # Step 2: Get the PlayerGachaCollection record
            player_gacha_collection = get_object_or_404(
                PlayerGachaCollection, id=collection_id)
            seller_id = player_gacha_collection.player_id
            print('Seller ID: ', seller_id)
            # Step 3: Fetch seller and bidder details
            seller_detail_url = f"{settings.USER_SERVICE}/player/{seller_id}/details/"
            bidder_detail_url = f"{settings.USER_SERVICE}/player/{bidder_id}/details/"

            seller_response = requests.get(
                seller_detail_url, headers=request.headers)
            # return Response({"location": "dbmthree", "seller_response": seller_response.json()}, status=status.HTTP_200_OK)
            bidder_response = requests.get(
                bidder_detail_url, headers=request.headers)
            # return Response({"location": "dbmthree", "bidder_response": bidder_response.json()}, status=status.HTTP_200_OK)

            if seller_response.status_code != 200:
                raise Exception("Failed to fetch seller details.")
            if bidder_response.status_code != 200:
                raise Exception("Failed to fetch bidder details.")

            seller_data = seller_response.json()
            bidder_data = bidder_response.json()

            # Step 4: Update balances
            seller_balance_url = f"{settings.USER_SERVICE}/player/{seller_id}/details/"
            bidder_balance_url = f"{settings.USER_SERVICE}/player/{bidder_id}/details/"

            # Adjust balances: subtract from bidder, add to seller
            seller_new_balance = seller_data['current_balance'] + price
            bidder_new_balance = bidder_data['current_balance'] - price

            # Update seller's balance
            seller_update_response = requests.put(
                seller_balance_url,
                json={"current_balance": seller_new_balance}, headers=request.headers
            )
            # return Response({"location": "dbmthree", "seller_update_response": seller_update_response.json()}, status=status.HTTP_200_OK)
            if seller_update_response.status_code != 200:
                raise Exception("Failed to update seller's balance.")

            # Update bidder's balance
            bidder_update_response = requests.put(
                bidder_balance_url,
                json={"current_balance": bidder_new_balance}, headers=request.headers
            )
            # return Response({"location": "dbmthree", "bidder_update_response": bidder_update_response.json()}, status=status.HTTP_200_OK)
            if bidder_update_response.status_code != 200:
                raise Exception("Failed to update bidder's balance.")

            # Step 5: Transfer ownership
            player_gacha_collection.player_id = bidder_id
            player_gacha_collection.save()

            return Response(
                {"detail": "Gacha ownership transferred and balances updated successfully.",
                 "winner": request.data},
                status=status.HTTP_200_OK
            )

    except Exception as e:
        return Response(
            {"detail": "An error occurred while processing the gacha winner.",
             "error": str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
