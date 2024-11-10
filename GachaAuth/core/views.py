from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import User
from .serializers import UserSerializer
from django.shortcuts import get_object_or_404
from rest_framework import status

@api_view()
def testCore(request):
    return Response('You app is working!')

@api_view(['POST'])
def createUser(request):
    serializer = UserSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()
        return Response({
            'detail' : 'User has been created successfully.',
            'user' : UserSerializer(user).data
        },status=status.HTTP_201_CREATED)
    # instead if we write serializer.error_messages it will return structure not the messages
    return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)

@api_view()
def listOfUsers(request):
    users_query_set = User.objects.all()
    serializer = UserSerializer(users_query_set, many=True)
    return Response(serializer.data)

@api_view()
def userDetails(request, id):
    user = get_object_or_404(User, pk=id)
    serializer = UserSerializer(user)
    # return Response(serializer.data) will not provide results like data: {json}, it will generate error. So stop thinking like you are coding in php. 
    return Response(serializer.data)