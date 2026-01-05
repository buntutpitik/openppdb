from django.http import HttpResponseForbidden
from django.shortcuts import redirect
from django.conf import settings


def superadmin_required(view_func):
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect(settings.LOGIN_URL)

        if getattr(request.user, "role", None) != "SUPERADMIN":
            return HttpResponseForbidden("403 Forbidden")

        return view_func(request, *args, **kwargs)

    return _wrapped_view
