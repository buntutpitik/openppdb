from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404, redirect, render
from django.core.exceptions import PermissionDenied

from backend.permissions import role_required


@role_required("SUPERADMIN")
def user_list(request):
    users = (
        User.objects
        .all()
        .order_by("username")
    )

    return render(
        request,
        "super_admin/user_list.html",
        {
            "users": users
        }
    )


@role_required("SUPERADMIN")
def toggle_user_active(request, user_id):
    """
    Aktifkan / nonaktifkan user.
    Hanya SUPERADMIN.
    """

    if request.method != "POST":
        raise PermissionDenied("Metode tidak diizinkan")

    target_user = get_object_or_404(User, pk=user_id)

    # ❌ tidak boleh menonaktifkan diri sendiri
    if target_user == request.user:
        raise PermissionDenied(
            "Tidak boleh menonaktifkan akun sendiri"
        )

    target_user.is_active = not target_user.is_active
    target_user.save()

    return redirect("superadmin:user_list")
