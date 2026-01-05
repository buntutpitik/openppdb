from django.contrib.auth.models import User, Group
from django.shortcuts import get_object_or_404, redirect, render
from django.core.exceptions import PermissionDenied

from backend.permissions import role_required


@role_required("SUPERADMIN")
def user_list(request):
    users = User.objects.all().order_by("username")

    user_data = []
    for user in users:
        user_data.append({
            "user": user,
            "roles": set(user.groups.values_list("name", flat=True))
        })

    return render(
        request,
        "super_admin/user_list.html",
        {
            "users": user_data
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
        raise PermissionDenied("Tidak boleh menonaktifkan akun sendiri")

    target_user.is_active = not target_user.is_active
    target_user.save()

    return redirect("superadmin:user_list")


@role_required("SUPERADMIN")
def update_user_role(request, user_id):
    if request.method != "POST":
        raise PermissionDenied("Metode tidak diizinkan")

    target_user = get_object_or_404(User, pk=user_id)

    # roles dari checkbox
    roles = request.POST.getlist("roles")

    # ❌ proteksi: SUPERADMIN tidak boleh kehilangan semua role
    if target_user == request.user and "SUPERADMIN" not in roles:
        raise PermissionDenied("SUPERADMIN tidak boleh menghapus role sendiri")

    # bersihkan role lama
    target_user.groups.clear()

    # assign role baru
    for role in roles:
        group, _ = Group.objects.get_or_create(name=role)
        target_user.groups.add(group)

    return redirect("superadmin:user_list")
