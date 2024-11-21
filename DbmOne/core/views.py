from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import User
from .serializers import UserSerializer, UpdateUserSerializer
from django.shortcuts import get_object_or_404
from rest_framework import status
from django.contrib.auth.hashers import check_password

# This endpoint will check if the app is running and working fine


@api_view()
def testCore(request):
    return Response('You app is working!')

# here we are creating the user


@api_view(['POST'])
def createUser(request):
    serializer = UserSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()
        return Response({
            'detail': 'User has been created successfully.',
            'user': UserSerializer(user).data
        }, status=status.HTTP_201_CREATED)
    # instead if we write serializer.error_messages it will return structure not the messages
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# to view all the users


@api_view()
def listOfUsers(request):
    users_query_set = User.objects.all()
    serializer = UserSerializer(users_query_set, many=True)
    return Response(serializer.data)

# the same function will create and update users, the update does not necessarily require password because password reset will be another feature implemented later


@api_view(['GET', 'PUT'])
def userDetails(request, id):
    user = get_object_or_404(User, pk=id)
    if request.method == 'GET':
        serializer = UserSerializer(user)
        # return Response(serializer) will not provide results like data: {json}, it will generate error. So stop thinking like you are coding in php.
        return Response(serializer.data)
    elif request.method == 'PUT':
        serializer = UpdateUserSerializer(
            user, data=request.data, partial=True)  # Allow partial updates
        if serializer.is_valid():
            updated_user = serializer.save()
            return Response({
                'detail': 'User updated successfully.',
                'user': UpdateUserSerializer(updated_user).data
            }, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# to delete a user if inactive


@api_view(['DELETE'])
def deleteUser(request, id):
    user = get_object_or_404(User, pk=id)
    # Check if the user is active
    if user.status == 'active':
        return Response({
            'detail': 'Active users cannot be deleted. Please deactivate the user first.'
        }, status=status.HTTP_204_NO_CONTENT)

    # Delete the user if inactive
    user.delete()
    return Response({
        'detail': 'User deleted successfully.'
    }, status=status.HTTP_204_NO_CONTENT)


@api_view(['POST'])
def loginUser(request):
    """
    Authenticate a user with username and password.
    """
    username = request.data.get('username')
    password = request.data.get('password')

    if not username or not password:
        return Response({"detail": "Username and password are required."}, status=status.HTTP_400_BAD_REQUEST)

    try:
        # Find the user by username
        user = User.objects.get(username=username)

        # Check if the provided password matches the hashed password
        if check_password(password, user.password):
            # Return user details
            serializer = UserSerializer(user)
            return Response({
                "detail": "Login successful.",
                "user": serializer.data
            }, status=status.HTTP_200_OK)
        else:
            return Response({"detail": "Invalid password."}, status=status.HTTP_401_UNAUTHORIZED)

    except User.DoesNotExist:
        return Response({"detail": "User not found."}, status=status.HTTP_404_NOT_FOUND)


@api_view(['POST'])
def logoutUser(request, id):
    """
    Log out a user by ID.
    """
    try:
        # Find the user by ID
        user = User.objects.get(pk=id)

        # Optional: If you have a "logged-in" state, update it here (not in this example).
        # Example: user.logged_in = False; user.save()

        return Response({"detail": "Logout successful."}, status=status.HTTP_200_OK)

    except User.DoesNotExist:
        return Response({"detail": "User not found."}, status=status.HTTP_404_NOT_FOUND)
