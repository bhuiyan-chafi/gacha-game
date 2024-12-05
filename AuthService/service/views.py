import requests
from django.conf import settings
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import api_view
from service.jwt_utils import generate_jwt
from service.decorators import jwt_required, jwt_optional
# =================================== Auth App Services ======================================


@api_view(['GET'])
def authAppTest(request):
    # Proxy to core service
    try:
        print(f"{settings.DATABASE_ONE}/test")
        response = requests.get(f"{settings.DATABASE_ONE}/test/", verify=False)
        return Response(response.json(), status=response.status_code)
    except requests.exceptions.RequestException as e:
        return Response({"detail": "Core service unavailable", "error": str(e)}, status=status.HTTP_503_SERVICE_UNAVAILABLE)

# list all the users


@api_view(['POST'])
@jwt_required(allowed_roles=["admin", "player"])
def verifyToken(request):
    # check response from the decorator
    # return Response({"detail": "Access granted", "user": request.user}, status=status.HTTP_200_OK)
    # Get roles string from the headers
    roles_header = request.headers.get('Role', '')
    roles_list = roles_header.split(',')  # Split roles string into a list

    if request.user.get('role') not in roles_list:
        return Response({"detail": "Requested user is not Authorized user"}, status=status.HTTP_403_FORBIDDEN)
    return Response({"token": "valid"}, status=status.HTTP_200_OK)


@api_view(['GET'])
@jwt_required(allowed_roles=["admin"])
def listOfUsers(request):
    # Proxy to core service
    try:
        response = requests.get(
            f"{settings.DATABASE_ONE}/user/list", verify=False)
        return Response(response.json(), status=response.status_code)
    except requests.exceptions.RequestException as e:
        return Response({"detail": "Core service unavailable", "error": str(e)}, status=status.HTTP_503_SERVICE_UNAVAILABLE)
# create a user which is open for authentication and authorization


@api_view(['POST'])
def createUser(request):
    # URL of the backend service's user creation endpoint
    auth_create_user_url = f"{settings.DATABASE_ONE}/user/create/"

    # Forward the request data to the backend service
    try:
        # Forwarding the POST request with data to the core/auth service
        response = requests.post(auth_create_user_url,
                                 json=request.data, verify=False)

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
@jwt_optional(allowed_roles=["admin", "player"])
def userDetails(request, id):
    service_url = f"{settings.DATABASE_ONE}/user/{id}/details/"
    try:
        if request.method == 'GET':
            response = requests.get(service_url, verify=False)
            return Response(response.json(), status=response.status_code)
        elif request.method == 'PUT':
            # Check if the request is authenticated and if the user is an admin
            if request.user and request.user.get("role") not in ["admin", "player"]:
                return Response({"detail": "Permission denied."}, status=status.HTTP_403_FORBIDDEN)

            # Forwarding the POST request with data to the core/auth service
            response = requests.put(
                service_url, json=request.data, verify=False)

            # Return the response from the backend service to the client
            return Response(response.json(), status=response.status_code)
    except requests.exceptions.RequestException as e:
        return Response({"detail": "Core service unavailable", "error": str(e)}, status=status.HTTP_503_SERVICE_UNAVAILABLE)
# delete a user


@api_view(['DELETE'])
@jwt_required(allowed_roles=["admin", "player"])
def deleteUser(request, id):
    try:
        response = requests.delete(
            f"{settings.DATABASE_ONE}/user/{id}/delete/", verify=False)
        # why did we checked the status where it is already checked and replied in the application?
        '''The issue arises because 204 No Content specifically means “no content in the response body.” While you are technically returning a JSON response, the HTTP status 204 instructs clients (including requests) to expect no content, which is why response.json() doesn’t work in this case.'''

        if response.status_code == status.HTTP_204_NO_CONTENT:
            return Response({'detail': 'User has been deleted successfully!'}, status.HTTP_204_NO_CONTENT)
        else:
            return Response(response.json(), status=response.status_code)
    except requests.exceptions.RequestException as e:
        return Response({"detail": "Core service unavailable", "error": str(e)}, status=status.HTTP_503_SERVICE_UNAVAILABLE)

# =================================== Authentication Functions ========================================

# does not require authentication and authorization


@api_view(['POST'])
def loginUser(request):
    """
    Proxy to login a user through the core service.
    """
    # Define the core service login endpoint
    login_url = f"{settings.DATABASE_ONE}/user/login/"

    try:
        # Forward the login request to the core service
        response = requests.post(login_url, json=request.data, verify=False)
        if response.status_code != status.HTTP_200_OK:
            return Response({"detail": "User does not match with given credentials!"}, status=response.status_code)
        user = response.json().get('user')
        payload = {
            "user_id": user["id"],
            "username": user["username"],
            "role": user["role"],
            "status": user["status"]
        }
        token = generate_jwt(payload)
        # Return the response from the core service
        return Response({"access_token": token, "user": payload}, status=response.status_code)
    except requests.exceptions.RequestException as e:
        # Handle connection errors to the core service
        return Response({
            "detail": "Failed to connect to the core service.",
            "error": str(e)
        }, status=status.HTTP_503_SERVICE_UNAVAILABLE)


@api_view(['POST'])
@jwt_required(allowed_roles=["admin", "player"])
def logoutUser(request, id):
    """
    Proxy to logout a user through the core service.
    """
    # Define the core service logout endpoint
    logout_url = f"{settings.DATABASE_ONE}/user/{id}/logout/"

    try:
        # Forward the logout request to the core service
        response = requests.post(logout_url, verify=False)

        # Return the response from the core service
        return Response(response.json(), status=response.status_code)
    except requests.exceptions.RequestException as e:
        # Handle connection errors to the core service
        return Response({
            "detail": "Failed to connect to the core service.",
            "error": str(e)
        }, status=status.HTTP_503_SERVICE_UNAVAILABLE)
