from functools import wraps
from django.http import JsonResponse
from service.jwt_utils import decode_jwt


def jwt_required(allowed_roles=None):
    """
    Decorator to protect views with JWT authentication and optional role-based access.

    :param allowed_roles: List of roles allowed to access the view.
    """
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            auth_header = request.headers.get("Authorization")
            # print("Authorization Header:", auth_header)  # Debugging
            if not auth_header or not auth_header.startswith("Bearer "):
                return JsonResponse({"detail": "Authentication credentials were not provided."}, status=401)

            token = auth_header.split("Bearer ")[1]
            try:
                # Decode JWT and attach user info to the request
                user = decode_jwt(token)
                request.user = user
                # If roles are specified, validate the user's role
                if allowed_roles and user.get("role") not in allowed_roles:
                    return JsonResponse({"detail": "Permission denied."}, status=403)

            except Exception as e:
                return JsonResponse({"detail": str(e)}, status=401)

            return view_func(request, *args, **kwargs)

        return wrapper

    return decorator


def jwt_optional(allowed_roles=None):
    """
    Decorator to optionally protect views with JWT authentication and optional role-based access.

    :param allowed_roles: List of roles allowed to access the view if a token is provided.
    """
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            auth_header = request.headers.get("Authorization")
            if auth_header and auth_header.startswith("Bearer "):
                token = auth_header.split("Bearer ")[1]
                try:
                    # Decode JWT and attach user info to the request
                    user = decode_jwt(token)
                    request.user = user

                    # If roles are specified, validate the user's role
                    if allowed_roles and user.get("role") not in allowed_roles:
                        return JsonResponse({"detail": "Permission denied."}, status=403)
                except Exception as e:
                    return JsonResponse({"detail": str(e)}, status=401)
            else:
                # No token provided; mark the request as unauthenticated
                request.user = None

            return view_func(request, *args, **kwargs)

        return wrapper

    return decorator
