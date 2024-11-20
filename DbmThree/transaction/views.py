# player in game currency transactions


from django.conf import settings
from django.urls import reverse
import requests
from own_gacha.models import InGameCurrencyTransaction, PlayerGachaCollection
from rest_framework.response import Response
from rest_framework import status
from own_gacha.serializers import InGameCurrencyTransactionSerializer, PlayerGachaCollectionSerializer
from rest_framework.decorators import api_view
from django.db import transaction

# list of transaction made by the player


@api_view(['GET'])
def playerGameCurrencyTransactions(request, player_id):
    """
    Retrieve all in-game currency transactions for a specific player.
    """
    # Fetch transactions for the given player_id
    transactions = InGameCurrencyTransaction.objects.filter(
        player_id=player_id)

    if not transactions.exists():
        return Response(
            {"detail": f"No transactions found for player {player_id}."},
            status=status.HTTP_404_NOT_FOUND,
        )

    # Serialize the transaction data
    serializer = InGameCurrencyTransactionSerializer(transactions, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)

# buy in game currency using real money


@api_view(['POST'])
def playerGameCurrencyPurchase(request, player_id):
    """
    Handles purchasing game currency for a player.
    Converts cash_amount to game_currency and updates the player's balance.
    """
    # Fetch the cash_amount from the request body
    cash_amount = request.data.get('cash_amount')

    if cash_amount is None:
        return Response({"detail": "cash_amount is required."}, status=status.HTTP_400_BAD_REQUEST)

    try:
        # Convert cash_amount to a float
        cash_amount = float(cash_amount)
        if cash_amount <= 0:
            return Response({"detail": "cash_amount must be greater than 0."}, status=status.HTTP_400_BAD_REQUEST)
    except ValueError:
        return Response({"detail": "cash_amount must be a valid number."}, status=status.HTTP_400_BAD_REQUEST)

    # Calculate game currency
    game_currency = cash_amount * 10

    # URL to fetch and update player details
    player_url = f"{settings.USER_SERVICE}/player/{player_id}/details/"

    try:
        with transaction.atomic():
            # Fetch the player's current balance
            player_response = requests.get(player_url)
            if player_response.status_code != 200:
                return Response({"detail": "Failed to fetch player details."}, status=status.HTTP_503_SERVICE_UNAVAILABLE)

            player_data = player_response.json()
            current_balance = float(player_data.get('current_balance', 0))

            # Update the player's balance
            new_balance = current_balance + game_currency
            update_response = requests.put(
                player_url, data={'current_balance': new_balance})
            if update_response.status_code != 200:
                raise ValueError("Failed to update player balance.")

            # Create a new transaction record
            transaction_data = {
                'player_id': player_id, 'amount': game_currency}
            transaction_serializer = InGameCurrencyTransactionSerializer(
                data=transaction_data)
            if transaction_serializer.is_valid():
                transaction_serializer.save()
            else:
                raise ValueError("Failed to create transaction record.")

            return Response({
                "detail": "Game currency purchased successfully.",
                "transaction": transaction_serializer.data,
                "new_balance": f"{new_balance:.2f}"
            }, status=status.HTTP_201_CREATED)

    except Exception as e:
        return Response({"detail": "Game currency purchase failed.", "error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# making transaction as the auction winner
@api_view(['POST'])
def declareAuctionWinner(request):
    """
    Declare the winner of an auction and handle transactions.
    """
    auction_gacha_id = request.data.get('auction_gacha_id')

    if not auction_gacha_id:
        return Response({"detail": "auction_gacha_id is required."}, status=status.HTTP_400_BAD_REQUEST)

    try:
        with transaction.atomic():
            # 1. Get the winner details
            winner_url = reverse(
                'gacha-winner', kwargs={'auction_gacha_id': auction_gacha_id})
            winner_response = requests.get(
                f"http://{request.get_host()}{winner_url}")
            if winner_response.status_code != 200:
                raise ValueError("Failed to fetch auction winner.")

            winner_data = winner_response.json()
            # return Response({'winner': winner_data})
            bidder_id = winner_data["winner"]["bidder_id"]
            winning_price = float(winner_data["winner"]["price"])

            # 2. Get auction gacha details
            gacha_details_url = reverse(
                'auction-gacha-details', kwargs={'auction_gacha_id': auction_gacha_id})
            gacha_details_response = requests.get(
                f"http://{request.get_host()}{gacha_details_url}")
            if gacha_details_response.status_code != 200:
                raise ValueError("Failed to fetch auction gacha details.")

            gacha_data = gacha_details_response.json()
            # return Response({'auction_gacha_details': gacha_data})
            collection_id = gacha_data["collection_id"]

            # 3. Get seller information (player_id and gacha_id from PlayerGachaCollection)
            collection_record = PlayerGachaCollection.objects.get(
                pk=collection_id)
            seller_id = collection_record.player_id
            selling_gacha_id = collection_record.gacha_id

            # 4. Reduce winner's balance
            winner_player_url = f"{settings.USER_SERVICE}/player/{bidder_id}/details/"
            winner_player_response = requests.get(winner_player_url)
            if winner_player_response.status_code != 200:
                raise ValueError("Failed to fetch winner player details.")

            winner_player_data = winner_player_response.json()
            # return Response({'winner_player': winner_player_data})
            winner_current_balance = float(
                winner_player_data["current_balance"])
            if winner_current_balance < winning_price:
                raise ValueError("Winner does not have enough balance.")

            new_winner_balance = winner_current_balance - winning_price
            update_winner_response = requests.put(
                winner_player_url, data={'current_balance': new_winner_balance})
            if update_winner_response.status_code != 200:
                raise ValueError("Failed to update winner's balance.")

            # 5. Add gacha collection entry for winner
            winner_gacha_data = {
                "player_id": bidder_id,
                "gacha_id": selling_gacha_id
            }
            # return Response({'winner_gacha_data': winner_gacha_data})
            winner_gacha_serializer = PlayerGachaCollectionSerializer(
                data=winner_gacha_data)
            if winner_gacha_serializer.is_valid():
                winner_gacha_serializer.save()
            else:
                raise ValueError(
                    "Failed to add gacha collection for the winner.")

            # 6. Increase seller's balance
            seller_player_url = f"{settings.USER_SERVICE}/player/{seller_id}/details/"
            seller_player_response = requests.get(seller_player_url)
            # return Response({'seller_player_response': seller_player_response})
            if seller_player_response.status_code != 200:
                raise ValueError("Failed to fetch seller player details.")

            seller_player_data = seller_player_response.json()
            seller_current_balance = float(
                seller_player_data["current_balance"])
            new_seller_balance = seller_current_balance + winning_price
            update_seller_response = requests.put(
                seller_player_url, data={'current_balance': new_seller_balance})
            if update_seller_response.status_code != 200:
                raise ValueError("Failed to update seller's balance.")

            # 7. Remove gacha collection record for the seller
            collection_record.delete()

            return Response({"detail": "Auction winner declared successfully."}, status=status.HTTP_200_OK)

    except Exception as e:
        return Response({"detail": "Error processing auction winner.", "error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
