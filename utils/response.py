# core/response.py
from rest_framework.response import Response
from rest_framework import status


def success_response(
    data=None,
    message="Request successful",
    http_status=status.HTTP_200_OK
):
    """
    Standardized success response
    """
    return Response({
        "status": "success",
        "message": message,
        "data": data or {}
    }, status=http_status)


def error_response(
    errors=None,
    message="Something went wrong",
    http_status=status.HTTP_400_BAD_REQUEST
):
    """
    Standardized error response
    """
    return Response({
        "status": "error",
        "message": message,
        "errors": errors or {}
    }, status=http_status)