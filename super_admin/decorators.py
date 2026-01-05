from functools import wraps
from django.shortcuts import redirect
from django.http import HttpResponseForbidden


def superadmin_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):

        # 1. Harus login
        if not request.user.is_authenticated:
            return redirect("login")

        # 2. Harus punya profile
        if not hasattr(request.user, "profile"):
            return HttpResponseForbidden("User tidak punya profile")

        # 3. Role HARUS SUPERADMIN
        if request.user.profile.role != "SUPERADMIN":
            return HttpResponseForbidden("Bukan SUPERADMIN")

        return view_func(request, *args, **kwargs)

    return _wrapped_view
