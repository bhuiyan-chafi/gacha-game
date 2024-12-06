import requests
from django.conf import settings
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import api_view
from . import helper


def forward_request(method, path, data=None):
    """
    Helper function to forward requests to DbmTwo Gacha endpoints.
    """
    try:
        url = f"{settings.DATABASE_TWO}{path}"
        # print('Resource Called: ' + url)
        if method == "GET":
            response = requests.get(url, verify=settings.SSL_VERIFY, timeout=5)
        elif method == "POST":
            response = requests.post(
                url, json=data, verify=settings.SSL_VERIFY, timeout=5)
        elif method == "PUT":
            response = requests.put(
                url, json=data, verify=settings.SSL_VERIFY, timeout=5)
        elif method == "DELETE":
            response = requests.delete(
                url, verify=settings.SSL_VERIFY, timeout=5)
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
    # return Response(request.headers, status=status.HTTP_200_OK)
    # Verify the token using the helper function
    verify_token = helper.verifyToken(request)

    # Check if the token verification failed
    if not isinstance(verify_token, bool) or not verify_token:
        return verify_token  # Return the failure response from verifyToken

    return forward_request("GET", "/gacha/list/")


@api_view(['POST'])
def createGacha(request):
    """
    Create a new Gacha via DbmTwo.
    """
    # return Response(request.headers, status=status.HTTP_200_OK)
    # Verify the token using the helper function
    verify_token = helper.verifyToken(request)

    # Check if the token verification failed
    if not isinstance(verify_token, bool) or not verify_token:
        return verify_token  # Return the failure response from verifyToken

    return forward_request("POST", "/gacha/create/", request.data)


@api_view(['GET', 'PUT'])
def gachaDetails(request, id):
    """
    Fetch or update Gacha details from DbmTwo.
    """
    # return Response(request.headers, status=status.HTTP_200_OK)
    # Verify the token using the helper function
    verify_token = helper.verifyToken(request)

    # Check if the token verification failed
    if not isinstance(verify_token, bool) or not verify_token:
        return verify_token  # Return the failure response from verifyToken

    if request.method == 'GET':
        return forward_request("GET", f"/gacha/{id}/details/")
    elif request.method == 'PUT':
        return forward_request("PUT", f"/gacha/{id}/details/", request.data)


@api_view(['DELETE'])
def deleteGacha(request, id):
    """
    Delete a Gacha via DbmTwo.
    """
    # return Response(request.headers, status=status.HTTP_200_OK)
    # Verify the token using the helper function
    verify_token = helper.verifyToken(request)

    # Check if the token verification failed
    if not isinstance(verify_token, bool) or not verify_token:
        return verify_token  # Return the failure response from verifyToken

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
