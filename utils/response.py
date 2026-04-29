from rest_framework.response import Response


def common_response(
    *,
    success=True,
    message="Success.",
    data=None,
    errors=None,
    status_code=200,
):
    response_data = {
        "success": success,
        "message": message,
    }

    if success:
        response_data["data"] = data if data is not None else {}
    else:
        response_data["status_code"] = status_code
        response_data["errors"] = errors or {"general": [message]}

    return Response(response_data, status=status_code)