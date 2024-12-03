from django.shortcuts import get_object_or_404
from rest_framework.decorators import api_view
from .models import Gacha
from .serializers import GachaSerializer
from rest_framework.response import Response
from rest_framework import status


@api_view()
def listOfGacha(request):
    gacha_query_set = Gacha.objects.all()
    serializer = GachaSerializer(gacha_query_set, many=True)
    return Response(serializer.data)


@api_view(['POST'])
def createGacha(request):
    serializer = GachaSerializer(data=request.data)
    if serializer.is_valid():
        gacha = serializer.save()
        return Response({
            'detail': 'Gacha has been created successfully.',
            'gacha': GachaSerializer(gacha).data
        }, status=status.HTTP_201_CREATED)
    # instead if we write serializer.error_messages it will return structure not the messages
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'PUT'])
def gachaDetails(request, id):
    gacha = get_object_or_404(Gacha, pk=id)
    if request.method == 'GET':
        serializer = GachaSerializer(gacha)
        # return Response(serializer) will not provide results like data: {json}, it will generate error. So stop thinking like you are coding in php.
        return Response(serializer.data)
    elif request.method == 'PUT':
        data = request.data
        # Handle "increment" logic for inventory
        if "inventory" in data and data["inventory"] == "increment":
            gacha.inventory += 1
            gacha.save()
            return Response({
                'detail': 'Gacha inventory incremented by 1',
                'inventory': gacha.inventory
            }, status=status.HTTP_200_OK)
        serializer = GachaSerializer(
            gacha, data, partial=True)  # Allow partial updates
        if serializer.is_valid():
            updated_gacha = serializer.save()
            return Response({
                'detail': 'Gacha updated successfully.',
                'gacha': GachaSerializer(updated_gacha).data
            }, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# to delete a gacha if inactive


@api_view(['DELETE'])
def deleteGacha(request, id):
    gacha = get_object_or_404(Gacha, pk=id)
    # Check if the gacha is active
    if gacha.status == 'active':
        return Response({
            'detail': 'Active gachas cannot be deleted. Please deactivate the gacha first.'
        }, status=status.HTTP_400_BAD_REQUEST)

    # Delete the gacha if inactive
    gacha.delete()
    return Response({
        'detail': 'Gacha deleted successfully.'
    }, status=status.HTTP_204_NO_CONTENT)
