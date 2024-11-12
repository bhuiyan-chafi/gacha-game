import requests
from django.conf import settings
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import api_view
# =================================== Auth App Services ======================================


@api_view(['GET'])
def authAppTest(request):
    # Proxy to core service
    try:
        print(f"{settings.AUTH_SERVICE_URL}/test")
        response = requests.get(f"{settings.AUTH_SERVICE_URL}/test")
        return Response(response.json(), status=response.status_code)
    except requests.exceptions.RequestException as e:
        return Response({"detail": "Core service unavailable", "error": str(e)}, status=status.HTTP_503_SERVICE_UNAVAILABLE)

# list all the users


@api_view(['GET'])
def listOfUsers(request):
    # Proxy to core service
    try:
        response = requests.get(f"{settings.AUTH_SERVICE_URL}/user/list")
        return Response(response.json(), status=response.status_code)
    except requests.exceptions.RequestException as e:
        return Response({"detail": "Core service unavailable", "error": str(e)}, status=status.HTTP_503_SERVICE_UNAVAILABLE)
# create a user


@api_view(['POST'])
def createUser(request):
    # URL of the backend service's user creation endpoint
    auth_create_user_url = f"{settings.AUTH_SERVICE_URL}/user/create/"

    # Forward the request data to the backend service
    try:
        # Forwarding the POST request with data to the core/auth service
        response = requests.post(auth_create_user_url, json=request.data)

        # Return the response from the backend service to the client
        return Response(response.json(), status=response.status_code)

    except requests.exceptions.RequestException as e:
        # Handle cases where the backend service is unreachable
        return Response({
            'detail': 'Failed to connect to the auth service.',
            'error': str(e)
        }, status=status.HTTP_503_SERVICE_UNAVAILABLE)

# view or update user details


@api_view(['GET', 'PUT'])
def userDetails(request, id):
    service_url = f"{settings.AUTH_SERVICE_URL}/user/{id}/details/"
    try:
        if request.method == 'GET':
            response = requests.get(service_url)
            return Response(response.json(), status=response.status_code)
        elif request.method == 'PUT':
            # Forwarding the POST request with data to the core/auth service
            response = requests.put(service_url, json=request.data)

            # Return the response from the backend service to the client
            return Response(response.json(), status=response.status_code)
    except requests.exceptions.RequestException as e:
        return Response({"detail": "Core service unavailable", "error": str(e)}, status=status.HTTP_503_SERVICE_UNAVAILABLE)

# delete a user


@api_view(['DELETE'])
def deleteUser(request, id):
    try:
        response = requests.delete(
            f"{settings.AUTH_SERVICE_URL}/user/{id}/delete/")
        # why did we checked the status where it is already checked and replied in the application?
        '''The issue arises because 204 No Content specifically means “no content in the response body.” While you are technically returning a JSON response, the HTTP status 204 instructs clients (including requests) to expect no content, which is why response.json() doesn’t work in this case.'''

        if response.status_code == status.HTTP_204_NO_CONTENT:
            return Response({'detail': 'User has been deleted successfully!'}, status.HTTP_204_NO_CONTENT)
        else:
            return Response(response.json(), status=response.status_code)
    except requests.exceptions.RequestException as e:
        return Response({"detail": "Core service unavailable", "error": str(e)}, status=status.HTTP_503_SERVICE_UNAVAILABLE)

# =================================== User App Services ======================================


@api_view(['GET'])
def userAppTest(request):
    # Proxy to user service
    try:
        response = requests.get(f"{settings.USER_SERVICE_URL}/test")
        return Response(response.json(), status=response.status_code)
    except requests.exceptions.RequestException as e:
        return Response({"detail": "User service unavailable", "error": str(e)}, status=status.HTTP_503_SERVICE_UNAVAILABLE)
# =================== User as Player Services ====================
# create a player


@api_view(['POST'])
def createPlayer(request):
    # URL of the backend service's user creation endpoint
    player_create_user_url = f"{settings.USER_SERVICE_URL}/player/create/"

    # Forward the request data to the backend service
    try:
        # Forwarding the POST request with data to the core/auth service
        response = requests.post(player_create_user_url, json=request.data)

        # Return the response from the backend service to the client
        return Response(response.json(), status=response.status_code)

    except requests.exceptions.RequestException as e:
        # Handle cases where the backend service is unreachable
        return Response({
            'detail': 'Failed to connect to the auth service.',
            'error': str(e)
        }, status=status.HTTP_503_SERVICE_UNAVAILABLE)

# list all the players


@api_view(['GET'])
def listOfPlayers(request):
    try:
        response = requests.get(f"{settings.USER_SERVICE_URL}/player/list")
        return Response(response.json(), status=response.status_code)
    except requests.exceptions.RequestException as e:
        return Response({"detail": "Core service unavailable", "error": str(e)}, status=status.HTTP_503_SERVICE_UNAVAILABLE)

# view or update player details


@api_view(['GET', 'PUT'])
def playerDetails(request, id):
    service_url = f"{settings.USER_SERVICE_URL}/player/{id}/details/"
    try:
        if request.method == 'GET':
            response = requests.get(service_url)
            return Response(response.json(), status=response.status_code)
        elif request.method == 'PUT':
            # Forwarding the POST request with data to the core/auth service
            response = requests.put(service_url, json=request.data)

            # Return the response from the backend service to the client
            return Response(response.json(), status=response.status_code)
    except requests.exceptions.RequestException as e:
        return Response({"detail": "Core service unavailable", "error": str(e)}, status=status.HTTP_503_SERVICE_UNAVAILABLE)

# delete a user


@api_view(['DELETE'])
def deletePlayer(request, id):
    try:
        response = requests.delete(
            f"{settings.USER_SERVICE_URL}/player/{id}/delete/")
        # why did we checked the status where it is already checked and replied in the application?
        '''The issue arises because 204 No Content specifically means “no content in the response body.” While you are technically returning a JSON response, the HTTP status 204 instructs clients (including requests) to expect no content, which is why response.json() doesn’t work in this case.'''

        if response.status_code == status.HTTP_204_NO_CONTENT:
            return Response({'detail': 'Player has been deleted successfully!'}, status.HTTP_204_NO_CONTENT)
        else:
            return Response(response.json(), status=response.status_code)
    except requests.exceptions.RequestException as e:
        return Response({"detail": "Core service unavailable", "error": str(e)}, status=status.HTTP_503_SERVICE_UNAVAILABLE)

# =================== User as Admin Services ====================

# create a admin


@api_view(['POST'])
def createAdmin(request):
    # URL of the backend service's user creation endpoint
    admin_create_user_url = f"{settings.USER_SERVICE_URL}/admin/create/"

    # Forward the request data to the backend service
    try:
        # Forwarding the POST request with data to the core/auth service
        response = requests.post(admin_create_user_url, json=request.data)

        # Return the response from the backend service to the client
        return Response(response.json(), status=response.status_code)

    except requests.exceptions.RequestException as e:
        # Handle cases where the backend service is unreachable
        return Response({
            'detail': 'Failed to connect to the auth service.',
            'error': str(e)
        }, status=status.HTTP_503_SERVICE_UNAVAILABLE)

# list all the admins


@api_view(['GET'])
def listOfAdmins(request):
    try:
        response = requests.get(f"{settings.USER_SERVICE_URL}/admin/list")
        return Response(response.json(), status=response.status_code)
    except requests.exceptions.RequestException as e:
        return Response({"detail": "Core service unavailable", "error": str(e)}, status=status.HTTP_503_SERVICE_UNAVAILABLE)

# view or update admin details


@api_view(['GET', 'PUT'])
def adminDetails(request, id):
    service_url = f"{settings.USER_SERVICE_URL}/admin/{id}/details/"
    try:
        if request.method == 'GET':
            response = requests.get(service_url)
            return Response(response.json(), status=response.status_code)
        elif request.method == 'PUT':
            # Forwarding the POST request with data to the core/auth service
            response = requests.put(service_url, json=request.data)

            # Return the response from the backend service to the client
            return Response(response.json(), status=response.status_code)
    except requests.exceptions.RequestException as e:
        return Response({"detail": "Core service unavailable", "error": str(e)}, status=status.HTTP_503_SERVICE_UNAVAILABLE)

# delete a admin


@api_view(['DELETE'])
def deleteAdmin(request, id):
    try:
        response = requests.delete(
            f"{settings.USER_SERVICE_URL}/admin/{id}/delete/")
        # why did we checked the status where it is already checked and replied in the application?
        '''The issue arises because 204 No Content specifically means “no content in the response body.” While you are technically returning a JSON response, the HTTP status 204 instructs clients (including requests) to expect no content, which is why response.json() doesn’t work in this case.'''

        if response.status_code == status.HTTP_204_NO_CONTENT:
            return Response({'detail': 'Admin has been deleted successfully!'}, status.HTTP_204_NO_CONTENT)
        else:
            return Response(response.json(), status=response.status_code)
    except requests.exceptions.RequestException as e:
        return Response({"detail": "Core service unavailable", "error": str(e)}, status=status.HTTP_503_SERVICE_UNAVAILABLE)
