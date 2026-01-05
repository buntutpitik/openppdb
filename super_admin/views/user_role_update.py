from django.contrib.auth.models import User, Group
from django.shortcuts import get_object_or_404, redirect
from django.core.exceptions import PermissionDenied
from django.views.decorators.http import require_POST

from backend.permissions import role_required


ALLOWED_ROLES = [
    "SUPERADMIN",
    "ADMIN",
    "PANITIA",
    "BENDAHARA",
]


@require_POST
@role_required("SUPERADMIN")
def update_user_role(request, user_id):
    target_user = get_object_or_404(User, pk=user_id)

    # ambil multi role dari checkbox
    selected_roles = request.POST.getlist("roles")

    # filter role liar
    selected_roles = [
        r for r in selected_roles if r in ALLOWED_ROLES
    ]

    # ❌ tidak boleh menghapus semua role
    if not selected_roles:
        raise PermissionDenied(
            "User harus memiliki minimal satu role"
        )

    # ❌ SUPERADMIN tidak boleh mencabut semua rolenya sendiri
    if target_user == request.user:
        if "SUPERADMIN" not in selected_roles:
            raise PermissionDenied(
                "SUPERADMIN tidak boleh mencabut role dirinya sendiri"
            )

    # hapus semua role lama
    target_user.groups.clear()

    # set role baru
    for role_name in selected_roles:
        group, _ = Group.objects.get_or_create(
            name=role_name
        )
        target_user.groups.add(group)

    return redirect("superadmin:user_list")
