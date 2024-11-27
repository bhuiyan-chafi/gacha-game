import random
import requests
from django.db import transaction
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from .models import PlayerGachaCollection
from .serializers import PlayerGachaCollectionSerializer
from transaction.serializers import InGameCurrencyTransactionSerializer
from django.conf import settings  # To access .env variables

# Create a new player-gacha entry


@api_view(['POST'])
def rollToWinGacha(request):
    player_id = request.query_params.get('player_id')
    # Fetch available Gacha records from the external service
    gacha_service_url = f"{settings.GACHA_RECORDS_SERVICE}/gacha-service/gacha/list/"
    # return Response(gacha_service_url)
    try:
        response = requests.get(gacha_service_url)
        if response.status_code != 200:
            return Response({"detail": "Failed to fetch Gacha records."}, status=status.HTTP_503_SERVICE_UNAVAILABLE)

        available_gachas = response.json()
        available_gacha_ids = [gacha['id']
                               for gacha in available_gachas if gacha['status'] == 'active']
        if not available_gacha_ids:
            return Response({"detail": "No active Gacha items available."}, status=status.HTTP_404_NOT_FOUND)
    except requests.exceptions.RequestException as e:
        return Response({"detail": "Gacha service unavailable.", "error": str(e)}, status=status.HTTP_503_SERVICE_UNAVAILABLE)

    # Fetch the player's current Gacha collection
    owned_gacha_ids = list(PlayerGachaCollection.objects.filter(
        player_id=player_id).values_list('gacha_id', flat=True))

    # Filter out Gachas already owned by the player
    not_owned_gacha_ids = list(set(available_gacha_ids) - set(owned_gacha_ids))
    if not not_owned_gacha_ids:
        return Response({"detail": "Player already owns all available Gachas."}, status=status.HTTP_400_BAD_REQUEST)

    # Randomly select a Gacha from the not-owned list
    selected_gacha_id = random.choice(not_owned_gacha_ids)

    # Create a new PlayerGachaCollection entry
    data = {
        'player_id': player_id,
        'gacha_id': selected_gacha_id
    }
    serializer = PlayerGachaCollectionSerializer(data=data)
    if serializer.is_valid():
        player_gacha = serializer.save()
        return Response({
            'detail': 'Congratulations! You rolled and won a Gacha!',
            'player_gacha': serializer.data
        }, status=status.HTTP_201_CREATED)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
# List all player-gacha entries


@api_view(['POST'])
def createPlayerGachaByPurchase(request):
    # Get query parameters
    player_id = request.query_params.get(
        'player_id')  # or request.GET.get('player_id')
    gacha_id = request.query_params.get(
        'gacha_id')  # or request.GET.get('gacha_id')

    # Validate query parameters
    if not player_id or not gacha_id:
        return Response({"detail": "Both player_id and gacha_id are required."}, status=status.HTTP_400_BAD_REQUEST)

    try:
        player_id = int(player_id)
        gacha_id = int(gacha_id)
    except ValueError:
        return Response({"detail": "player_id and gacha_id must be integers."}, status=status.HTTP_400_BAD_REQUEST)

    player_url = f"{settings.USER_SERVICE}/player/{player_id}/details/"
    gacha_url = f"{settings.GACHA_RECORDS_SERVICE}/gacha-service/gacha/{gacha_id}/details/"
    try:
        with transaction.atomic():
            # Fetch player details
            player_response = requests.get(player_url)
            if player_response.status_code != 200:
                return Response({"detail": "Failed to fetch player details."}, status=status.HTTP_503_SERVICE_UNAVAILABLE)
            player_data = player_response.json()
            current_balance = float(player_data['current_balance'])
            print('current_balance:' + str(current_balance))
            # Fetch gacha details
            gacha_response = requests.get(gacha_url)
            if gacha_response.status_code != 200:
                return Response({"detail": "Failed to fetch gacha details."}, status=status.HTTP_503_SERVICE_UNAVAILABLE)
            gacha_data = gacha_response.json()
            price = float(gacha_data['price'])
            inventory = int(gacha_data['inventory'])
            print('gacha_inventory:' + str(inventory))
            # Validate purchase
            if inventory <= 0:
                return Response({"detail": "The selected gacha is out of stock."}, status=status.HTTP_400_BAD_REQUEST)
            if current_balance < price:
                return Response({"detail": "Insufficient balance to purchase the gacha."}, status=status.HTTP_400_BAD_REQUEST)

            # Create a currency transaction record
            transaction_data = {'player_id': player_id, 'amount': -price}
            transaction_serializer = InGameCurrencyTransactionSerializer(
                data=transaction_data)
            if transaction_serializer.is_valid():
                transaction_serializer.save()
            else:
                return Response(transaction_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

            # Update player balance
            new_balance = current_balance - price
            player_update_response = requests.put(
                player_url, data={'current_balance': new_balance})
            if player_update_response.status_code != 200:
                raise ValueError("Failed to update player balance.")

            # Update gacha inventory
            new_inventory = inventory - 1
            gacha_update_response = requests.put(
                gacha_url, data={'inventory': new_inventory})
            if gacha_update_response.status_code != 200:
                raise ValueError("Failed to update gacha inventory.")

            # Assign the gacha to the player
            player_gacha_data = {'player_id': player_id, 'gacha_id': gacha_id}
            print(player_gacha_data)
            player_gacha_serializer = PlayerGachaCollectionSerializer(
                data=player_gacha_data)
            if player_gacha_serializer.is_valid():
                player_gacha_serializer.save()
            else:
                raise ValueError(
                    "Failed to assign gacha to player. The player already has the gacha.")

            return Response({
                'detail': 'Gacha purchased successfully.',
                'transaction': transaction_serializer.data,
                'player_gacha': player_gacha_serializer.data
            }, status=status.HTTP_201_CREATED)

    except Exception as e:
        return Response({"detail": "Purchase failed.", "error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# Get player gacha collections


@api_view(['GET'])
def playerGachaCollections(request, player_id):
    try:
        # Filter the PlayerGachaCollection records for the specified player_id
        gacha_collections = PlayerGachaCollection.objects.filter(
            player_id=player_id)

        # Check if the player has any gacha records
        if not gacha_collections.exists():
            return Response({
                'detail': f'No gacha records found for player with ID {player_id}.'
            }, status=status.HTTP_200_OK)

        # Serialize the gacha collection data
        serializer = PlayerGachaCollectionSerializer(
            gacha_collections, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)

    except Exception as e:
        # Handle any unexpected errors
        return Response({
            'detail': 'An error occurred while fetching gacha collections.',
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# Get player single gacha details


@api_view(['GET', 'DELETE'])
def playerGachaCollectionDetails(request, collection_id):
    # Fetch the player-gacha collection record
    player_gacha = get_object_or_404(PlayerGachaCollection, pk=collection_id)

    if request.method == 'GET':
        # Fetch gacha details from the GACHA_RECORDS_SERVICE
        gacha_url = f"{settings.GACHA_RECORDS_SERVICE}/gacha-service/gacha/{player_gacha.gacha_id}/details/"
        try:
            gacha_response = requests.get(gacha_url)
            if gacha_response.status_code != 200:
                return Response(
                    {"detail": "Failed to fetch gacha details."},
                    status=status.HTTP_503_SERVICE_UNAVAILABLE
                )

            # Prepare response with player-gacha and gacha details
            gacha_details = gacha_response.json()
            return Response({
                "player_id": player_gacha.player_id,
                "gacha_details": gacha_details
            }, status=status.HTTP_200_OK)

        except requests.exceptions.RequestException as e:
            return Response(
                {"detail": "Error connecting to gacha service.",
                    "error": str(e)},
                status=status.HTTP_503_SERVICE_UNAVAILABLE
            )

    elif request.method == 'DELETE':
        gacha_url = f"{settings.GACHA_RECORDS_SERVICE}/{player_gacha.gacha_id}/details/"

        try:
            with transaction.atomic():
                # Delete the player-gacha collection record
                player_gacha.delete()

                # Increase gacha inventory by 1
                gacha_update_response = requests.put(
                    gacha_url, json={"inventory": "increment"}
                )

                if gacha_update_response.status_code != 200:
                    raise ValueError("Failed to update gacha inventory.")

                return Response(
                    {"detail": "Player-gacha collection record deleted successfully."},
                    status=status.HTTP_204_NO_CONTENT
                )

        except Exception as e:
            return Response(
                {"detail": "Failed to delete the player-gacha collection.",
                    "error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
