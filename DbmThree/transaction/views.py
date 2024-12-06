# player in game currency transactions


from django.conf import settings
from django.urls import reverse
import requests
from own_gacha.models import PlayerGachaCollection
from transaction.models import InGameCurrencyTransaction
from rest_framework.response import Response
from rest_framework import status
from own_gacha.serializers import PlayerGachaCollectionSerializer
from transaction.serializers import InGameCurrencyTransactionSerializer
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
    # return Response({"location": "dbmthree->transactions", "headers": request.headers}, status=status.HTTP_200_OK)
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
            player_response = requests.get(
                player_url, headers=request.headers, verify=settings.SSL_VERIFY, timeout=5)
            # return Response({"location": "dbmthree->transactions", "player_response": player_response.json()}, status=status.HTTP_200_OK)

            if player_response.status_code != 200:
                return Response({"detail": "Failed to fetch player details."}, status=status.HTTP_404_NOT_FOUND)

            player_data = player_response.json()
            current_balance = float(player_data.get('current_balance', 0))

            # Update the player's balance
            new_balance = current_balance + game_currency
            update_response = requests.put(
                player_url, json={'current_balance': new_balance}, headers=request.headers, verify=settings.SSL_VERIFY, timeout=5)
            # return Response({"location": "dbmthree->transactions", "update_response": update_response.json()}, status=status.HTTP_200_OK)

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
