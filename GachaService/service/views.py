import requests
from django.conf import settings
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import api_view


def forward_request(method, path, data=None):
    """
    Helper function to forward requests to DbmTwo Gacha endpoints.
    """
    try:
        url = f"{settings.DATABASE_TWO}{path}"
        # print('Resource Called: ' + url)
        if method == "GET":
            response = requests.get(url)
        elif method == "POST":
            response = requests.post(url, json=data)
        elif method == "PUT":
            response = requests.put(url, json=data)
        elif method == "DELETE":
            response = requests.delete(url)
        else:
            raise ValueError(f"Unsupported HTTP method: {method}")

        # Handle successful responses
        if response.status_code == status.HTTP_204_NO_CONTENT:
            return Response({'detail': 'Operation successful.'}, status=status.HTTP_204_NO_CONTENT)

        return Response(response.json(), status=response.status_code)
    except requests.exceptions.RequestException as e:
        return Response({"detail": "DbmTwo service unavailable", "error": str(e)}, status=status.HTTP_503_SERVICE_UNAVAILABLE)


@api_view(['GET'])
def listOfGacha(request):
    """
    Fetch a list of all Gachas from DbmTwo.
    """
    return forward_request("GET", "/gacha/list/")


@api_view(['POST'])
def createGacha(request):
    """
    Create a new Gacha via DbmTwo.
    """
    return forward_request("POST", "/gacha/create/", request.data)


@api_view(['GET', 'PUT'])
def gachaDetails(request, id):
    """
    Fetch or update Gacha details from DbmTwo.
    """
    if request.method == 'GET':
        return forward_request("GET", f"/gacha/{id}/details/")
    elif request.method == 'PUT':
        return forward_request("PUT", f"/gacha/{id}/details/", request.data)


@api_view(['DELETE'])
def deleteGacha(request, id):
    """
    Delete a Gacha via DbmTwo.
    """
    return forward_request("DELETE", f"/gacha/{id}/delete/")


"""
============================= System Variable Views =================================
"""


@api_view(['POST'])
def createSystemVariableProxy(request):
    """
    Forward request to create a new system variable.
    """
    return forward_request("POST", "/system-variables/create/", request.data)


@api_view(['GET'])
def listSystemVariablesProxy(request):
    """
    Forward request to list all system variables.
    """
    return forward_request("GET", "/system-variables/list/")


@api_view(['GET', 'PUT', 'DELETE'])
def systemVariableDetailsProxy(request, id):
    """
    Forward request to get, update, or delete a single system variable by ID.
    """
    if request.method == "GET":
        return forward_request("GET", f"/system-variables/{id}/details/")
    elif request.method == "PUT":
        return forward_request("PUT", f"/system-variables/{id}/details/", request.data)
    elif request.method == "DELETE":
        return forward_request("DELETE", f"/system-variables/{id}/details/")
