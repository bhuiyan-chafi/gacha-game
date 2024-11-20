from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import User
from .serializers import UserSerializer, UpdateUserSerializer
from django.shortcuts import get_object_or_404
from rest_framework import status

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
        }, status=status.HTTP_400_BAD_REQUEST)

    # Delete the user if inactive
    user.delete()
    return Response({
        'detail': 'User deleted successfully.'
    }, status=status.HTTP_204_NO_CONTENT)
