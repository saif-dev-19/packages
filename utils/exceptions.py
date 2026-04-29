from rest_framework.views import exception_handler
from rest_framework.exceptions import ValidationError


def normalize_errors(errors):
    """
    Convert DRF errors into frontend-friendly format.
    non_field_errors -> general
    """
    if isinstance(errors, dict):
        formatted_errors = {}

        for field, messages in errors.items():
            key = "general" if field == "non_field_errors" else field

            if isinstance(messages, list):
                formatted_errors[key] = [str(message) for message in messages]
            elif isinstance(messages, dict):
                formatted_errors[key] = normalize_errors(messages)
            else:
                formatted_errors[key] = [str(messages)]

        return formatted_errors

    if isinstance(errors, list):
        return {
            "general": [str(message) for message in errors]
        }

    return {
        "general": [str(errors)]
    }


def custom_exception_handler(exc, context):
    response = exception_handler(exc, context)

    if response is None:
        return response

    if isinstance(exc, ValidationError):
        response.data = {
            "success": False,
            "message": "Validation failed.",
            "status_code": response.status_code,
            "errors": normalize_errors(response.data),
        }
        return response

    detail = response.data.get("detail", "Something went wrong.")

    response.data = {
        "success": False,
        "message": str(detail),
        "status_code": response.status_code,
        "errors": {
            "general": [str(detail)]
        },
    }

    return response