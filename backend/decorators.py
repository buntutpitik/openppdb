from django.core.exceptions import PermissionDenied


def superadmin_required(view_func):
    """
    Hanya mengizinkan user dengan role SUPERADMIN.
    """
    def _wrapped_view(request, *args, **kwargs):
        user = request.user

        if not user.is_authenticated:
            raise PermissionDenied

        if not hasattr(user, "profile"):
            raise PermissionDenied

        if user.profile.role != "SUPERADMIN":
            raise PermissionDenied

        return view_func(request, *args, **kwargs)

    return _wrapped_view
