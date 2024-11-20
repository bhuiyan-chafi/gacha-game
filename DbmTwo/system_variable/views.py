from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from .models import SystemVariable
from .serializers import SystemVariableSerializer

# Create a new system variable


@api_view(['POST'])
def createSystemVariable(request):
    serializer = SystemVariableSerializer(data=request.data)
    if serializer.is_valid():
        system_variable = serializer.save()
        return Response({
            'detail': 'System variable created successfully.',
            'system_variable': serializer.data
        }, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# List all system variables


@api_view(['GET'])
def listSystemVariables(request):
    system_variables = SystemVariable.objects.all()
    serializer = SystemVariableSerializer(system_variables, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)

# Get, update, or delete a single system variable by ID


@api_view(['GET', 'PUT', 'DELETE'])
def systemVariableDetails(request, id):
    system_variable = get_object_or_404(SystemVariable, pk=id)

    if request.method == 'GET':
        serializer = SystemVariableSerializer(system_variable)
        return Response(serializer.data, status=status.HTTP_200_OK)

    elif request.method == 'PUT':
        serializer = SystemVariableSerializer(
            system_variable, data=request.data, partial=True)
        if serializer.is_valid():
            updated_system_variable = serializer.save()
            return Response({
                'detail': 'System variable updated successfully.',
                'system_variable': serializer.data
            }, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        system_variable.delete()
        return Response({
            'detail': 'System variable deleted successfully.'
        }, status=status.HTTP_204_NO_CONTENT)
