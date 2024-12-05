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

"""
There are a few things we should know about this logic: 
- the request brings the player_id and the amount of the roll.
- the next step is to check the player's balance though we checked it in the PlayService (because communication among services should be through the services)
- each gacha is categorized: 1-50/normal, 51-95/rare and 96-100/super rare gacha
- if the roll price <= 50 we select a normal gacha based on random distribution
- if the roll price <= 90 we select a rare gacha
- if the roll price <= 100 then we select a super rare gacha
- after selecting a gacha we check the inventory and status(must be active) for ensuring the availability
- then we check if the gacha is already acquired by the player, if not then we declare the gacha for the player
"""


@api_view(['POST'])
def rollToWinGacha(request):
    """
    Roll to win a Gacha, validating the player's balance, filtering Gacha by rarity, updating balance,
    inventory, and creating a transaction record, ensuring atomic operations.
    """
    player_id = request.query_params.get('player_id')
    roll_price = request.data.get('roll_price')

    # Validate player_id
    if not player_id:
        return Response({"detail": "player_id is required as a query parameter."}, status=status.HTTP_400_BAD_REQUEST)

    # Validate roll_price
    if roll_price is None or roll_price == "":
        return Response({"detail": "roll_price is required in the request body and cannot be empty."}, status=status.HTTP_400_BAD_REQUEST)

    try:
        roll_price = float(roll_price)
    except ValueError:
        return Response({"detail": "roll_price must be a numeric value."}, status=status.HTTP_400_BAD_REQUEST)

    if not (20 <= roll_price <= 100):
        return Response({"detail": "roll_price must be between 20 and 100."}, status=status.HTTP_400_BAD_REQUEST)

    # Fetch player details from the user-service
    user_service_url = f"{settings.USER_SERVICE}/player/{player_id}/details/"
    try:
        player_response = requests.get(
            user_service_url, headers=request.headers, verify=False)
        if player_response.status_code != 200:
            return Response({"detail": "Failed to fetch player details."}, status=player_response.status_code)

        player_data = player_response.json()
        current_balance = player_data.get("current_balance")
        if current_balance is None:
            return Response({"detail": "current_balance is missing in player details."}, status=status.HTTP_400_BAD_REQUEST)

        if current_balance < roll_price:
            return Response({"detail": "Insufficient balance for the roll."}, status=status.HTTP_400_BAD_REQUEST)

    except requests.exceptions.RequestException as e:
        return Response({"detail": "User service unavailable.", "error": str(e)}, status=status.HTTP_503_SERVICE_UNAVAILABLE)

    # Fetch available Gacha records from the external service
    gacha_service_url = f"{settings.GACHA_RECORDS_SERVICE}/gacha-service/gacha/list/"
    try:
        response = requests.get(
            gacha_service_url, headers=request.headers, verify=False)
        if response.status_code != 200:
            return Response({"detail": "Failed to fetch Gacha records."}, status=status.HTTP_503_SERVICE_UNAVAILABLE)

        available_gachas = response.json()

        # Filter Gachas based on roll_price and rarity
        if roll_price <= 50:
            filtered_gachas = [
                gacha for gacha in available_gachas if 10 <= gacha['rarity'] <= 50]
        elif roll_price <= 90:
            filtered_gachas = [
                gacha for gacha in available_gachas if 51 <= gacha['rarity'] <= 95]
        elif roll_price <= 100:
            filtered_gachas = [
                gacha for gacha in available_gachas if 96 <= gacha['rarity'] <= 100]

        # Extract active Gacha IDs from filtered list
        available_gacha_ids = [gacha['id']
                               for gacha in filtered_gachas if gacha['status'] == 'active']
        if not available_gacha_ids:
            return Response({"detail": "No active Gacha items available for the selected roll_price."}, status=status.HTTP_404_NOT_FOUND)
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
    gacha_update_url = f"{settings.GACHA_RECORDS_SERVICE}/gacha-service/gacha/{selected_gacha_id}/details/"
    gacha_response = requests.get(
        gacha_update_url, headers=request.headers, verify=False)
    if gacha_response.status_code != 200:
        return Response({"detail": "Failed to fetch gacha details."}, status=status.HTTP_503_SERVICE_UNAVAILABLE)
    gacha_data = gacha_response.json()
    current_inventory = int(gacha_data['inventory'])
    # Begin an atomic transaction
    try:
        with transaction.atomic():
            # Deduct roll_price from player's current_balance
            new_balance = current_balance - roll_price
            balance_response = requests.put(user_service_url, json={
                                            "current_balance": new_balance}, headers=request.headers, verify=False)
            # return Response({"balance_update_response": balance_response.json()}, status=balance_response.status_code)
            if balance_response.status_code != 200:
                raise ValueError("Failed to update player balance.")

            # Reduce inventory for the selected Gacha
            inventory_response = requests.put(
                gacha_update_url, json={"inventory": current_inventory-1}, headers=request.headers, verify=False)
            if inventory_response.status_code != 200:
                raise ValueError("Failed to update Gacha inventory.")

            # Create a transaction record for the roll_price
            transaction_data = {'player_id': player_id, 'amount': -roll_price}
            transaction_serializer = InGameCurrencyTransactionSerializer(
                data=transaction_data)
            if transaction_serializer.is_valid():
                transaction_serializer.save()
            else:
                raise ValueError(transaction_serializer.errors)

            # Create a new PlayerGachaCollection entry
            data = {
                'player_id': player_id,
                'gacha_id': selected_gacha_id
            }
            serializer = PlayerGachaCollectionSerializer(data=data)
            if serializer.is_valid():
                player_gacha = serializer.save()
            else:
                raise ValueError(serializer.errors)

        # Return success response
        return Response({
            'detail': 'Congratulations! You rolled and won a Gacha!',
            'player_gacha': serializer.data
        }, status=status.HTTP_201_CREATED)

    except ValueError as e:
        # Rollback transaction on any failure
        return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    except Exception as e:
        return Response({"detail": "An unexpected error occurred.", "error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


"""
In this phase we just make the purchase: assign the gacha to the player gacha collection, adjust his balance, adjust gacha inventory and add transaction history
"""


@api_view(['POST'])
def createPlayerGachaByPurchase(request):
    # return Response({"location": "dbmthree", "header": request.headers}, status=status.HTTP_200_OK)
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
            player_response = requests.get(
                player_url, headers=request.headers, verify=False)
            player_data = player_response.json()
            # return Response({"location": "dbmthree", "player": player_data}, status=status.HTTP_200_OK)
            current_balance = float(player_data['current_balance'])
            # Fetch gacha details
            gacha_response = requests.get(
                gacha_url, headers=request.headers, verify=False)
            gacha_data = gacha_response.json()
            # return Response({"location": "dbmthree", "gacha": gacha_data}, status=status.HTTP_200_OK)
            price = float(gacha_data['price'])
            inventory = int(gacha_data['inventory'])
            # print('gacha_inventory:' + str(inventory))
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
            # return Response(request.headers, status=status.HTTP_200_OK)
            player_update_response = requests.put(
                player_url, json={'current_balance': new_balance}, headers=request.headers, verify=False)
            # return Response({"location": "dbmthree", "player_updated": player_update_response.json()}, status=status.HTTP_200_OK)
            if player_update_response.status_code != 200:
                raise ValueError("Failed to update player balance.")

            # Update gacha inventory
            new_inventory = inventory - 1
            gacha_update_response = requests.put(
                gacha_url, json={'inventory': new_inventory}, headers=request.headers, verify=False)
            # return Response({"location": "dbmthree", "gacha_updated": gacha_update_response.json()}, status=status.HTTP_200_OK)
            if gacha_update_response.status_code != 200:
                raise ValueError("Failed to update gacha inventory.")

            # Assign the gacha to the player
            player_gacha_data = {'player_id': player_id, 'gacha_id': gacha_id}
            # print(player_gacha_data)
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
    # print('Gacha collection checked for player: '+str(player_id))
    try:
        # Filter the PlayerGachaCollection records for the specified player_id
        gacha_collections = PlayerGachaCollection.objects.filter(
            player_id=player_id)
        # print('Gacha collection checked for player: '+str(player_id))
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
            gacha_response = requests.get(
                gacha_url, headers=request.headers, verify=False)
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
                    gacha_url, json={"inventory": "increment"}, headers=request.headers, verify=False
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
