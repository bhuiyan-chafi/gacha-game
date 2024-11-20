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
        print(f"{settings.DATABASE_ONE}/test")
        response = requests.get(f"{settings.DATABASE_ONE}/test/")
        return Response(response.json(), status=response.status_code)
    except requests.exceptions.RequestException as e:
        return Response({"detail": "Core service unavailable", "error": str(e)}, status=status.HTTP_503_SERVICE_UNAVAILABLE)

# list all the users


@api_view(['GET'])
def listOfUsers(request):
    # Proxy to core service
    try:
        response = requests.get(f"{settings.DATABASE_ONE}/user/list")
        return Response(response.json(), status=response.status_code)
    except requests.exceptions.RequestException as e:
        return Response({"detail": "Core service unavailable", "error": str(e)}, status=status.HTTP_503_SERVICE_UNAVAILABLE)
# create a user


@api_view(['POST'])
def createUser(request):
    # URL of the backend service's user creation endpoint
    auth_create_user_url = f"{settings.DATABASE_ONE}/user/create/"

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
    service_url = f"{settings.DATABASE_ONE}/user/{id}/details/"
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
            f"{settings.DATABASE_ONE}/user/{id}/delete/")
        # why did we checked the status where it is already checked and replied in the application?
        '''The issue arises because 204 No Content specifically means “no content in the response body.” While you are technically returning a JSON response, the HTTP status 204 instructs clients (including requests) to expect no content, which is why response.json() doesn’t work in this case.'''

        if response.status_code == status.HTTP_204_NO_CONTENT:
            return Response({'detail': 'User has been deleted successfully!'}, status.HTTP_204_NO_CONTENT)
        else:
            return Response(response.json(), status=response.status_code)
    except requests.exceptions.RequestException as e:
        return Response({"detail": "Core service unavailable", "error": str(e)}, status=status.HTTP_503_SERVICE_UNAVAILABLE)
