from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from .models import Player, Admin
from .serializers import PlayerSerializer, AdminSerializer
import requests
from django.conf import settings

# test the app is up and running


@api_view()
def testCoreApp(request):
    return Response('Your app is up and running!')

# =============================== Admin Views ==================================
#   create a admin


@api_view(['POST'])
def createAdmin(request):
    serializer = AdminSerializer(data=request.data)
    if serializer.is_valid():
        admin = serializer.save()
        return Response({
            'detail': 'Admin created successfully.',
            'Admin': AdminSerializer(admin).data
        }, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# list all the Admins


@api_view(['GET'])
def listOfAdmins(request):
    admins = Admin.objects.all()
    serializer = AdminSerializer(admins, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)

#   get information of a single Admin or update a single Admin


@api_view(['GET', 'PUT'])
def AdminDetails(request, id):
    admin = get_object_or_404(Admin, pk=id)
    if request.method == 'GET':
        serializer = AdminSerializer(admin)
        return Response(serializer.data, status=status.HTTP_200_OK)
    elif request.method == 'PUT':
        serializer = AdminSerializer(
            admin, data=request.data, partial=True)  # Allow partial updates
        if serializer.is_valid():
            serializer.save()
            return Response({
                'detail': 'Admin updated successfully.',
                'admin': serializer.data
            }, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
#   to delete a Admin, but deleting a Admin will require communicating with the 'auth' app. If the record from the auth app is deleted than the Admin will be deleted from here.


@api_view(['DELETE'])
def deleteAdmin(request, id):
    # Get the Admin by ID
    admin = get_object_or_404(Admin, pk=id)

    # External API endpoint for auth information
    auth_api_url = f"{settings.API_GATEWAY_ONE}/{admin.user_id}/delete"
    print(auth_api_url)

    # Check if the user can be deleted from the auth app
    try:
        auth_response = requests.delete(auth_api_url)

        # If the auth app allows deletion (returns 204), proceed
        if auth_response.status_code == status.HTTP_204_NO_CONTENT:
            # Delete the Admin record
            admin.delete()
            return Response({
                'detail': 'Admin and associated auth record deleted successfully.'
            }, status=status.HTTP_204_NO_CONTENT)

        # If auth app does not allow deletion, return its error response
        return Response(auth_response.json(), status=status.HTTP_400_BAD_REQUEST)

    except requests.exceptions.RequestException as e:
        # Handle cases where the auth API call fails
        return Response({
            'detail': 'Failed to connect to the auth service.',
            'error': str(e)
        }, status=status.HTTP_503_SERVICE_UNAVAILABLE)


# ===================================== Player Views==========================================
#   create a player
@api_view(['POST'])
def createPlayer(request):
    serializer = PlayerSerializer(data=request.data)
    if serializer.is_valid():
        player = serializer.save()
        return Response({
            'detail': 'Player created successfully.',
            'player': PlayerSerializer(player).data
        }, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# list all the players


@api_view(['GET'])
def listOfPlayers(request):
    players = Player.objects.all()
    serializer = PlayerSerializer(players, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)

#   get information of a single player or update a single player


@api_view(['GET', 'PUT'])
def playerDetails(request, id):
    player = get_object_or_404(Player, pk=id)
    if request.method == 'GET':
        serializer = PlayerSerializer(player)
        return Response(serializer.data, status=status.HTTP_200_OK)
    elif request.method == 'PUT':
        serializer = PlayerSerializer(
            player, data=request.data, partial=True)  # Allow partial updates
        if serializer.is_valid():
            serializer.save()
            return Response({
                'detail': 'Player updated successfully.',
                'player': serializer.data
            }, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
#   to delete a player, but deleting a player will require communicating with the 'auth' app. If the record from the auth app is deleted than the player will be deleted from here.


@api_view(['DELETE'])
def deletePlayer(request, id):
    # Get the player by ID
    player = get_object_or_404(Player, pk=id)

    # External API endpoint for auth information
    auth_api_url = f"{settings.API_GATEWAY_ONE}/{player.user_id}/delete/"
    print(auth_api_url)

    # Check if the user can be deleted from the auth app
    try:
        auth_response = requests.delete(auth_api_url)
        # If the auth app allows deletion (returns 204), proceed
        if auth_response.status_code == status.HTTP_204_NO_CONTENT:
            # Delete the player record
            player.delete()
            return Response({
                'detail': 'Player and associated auth record deleted successfully.'
            }, status=status.HTTP_204_NO_CONTENT)

        # If auth app does not allow deletion, return its error response
        return Response(auth_response.json(), status=status.HTTP_400_BAD_REQUEST)

    except requests.exceptions.RequestException as e:
        # Handle cases where the auth API call fails
        return Response({
            'detail': 'Failed to connect to the auth service.',
            'error': str(e)
        }, status=status.HTTP_503_SERVICE_UNAVAILABLE)
