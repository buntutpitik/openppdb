from django.contrib.auth.models import User, Group
from django.shortcuts import get_object_or_404, redirect
from backend.permissions import role_required
from django.views.decorators.http import require_POST


@require_POST
@role_required("SUPERADMIN")
def update_user_role(request, user_id):
    user = get_object_or_404(User, pk=user_id)

    new_role = request.POST.get("role")

    if not new_role:
        return redirect("superadmin:user_list")

    # hapus semua role lama
    user.groups.clear()

    # set role baru
    group, _ = Group.objects.get_or_create(name=new_role)
    user.groups.add(group)

    return redirect("superadmin:user_list")
