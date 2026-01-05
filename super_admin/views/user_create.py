from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User

from backend.forms_admin import UserCreateForm
from backend.permissions import role_required


@login_required
@role_required("SUPERADMIN")
def user_create(request):
    if request.method == "POST":
        form = UserCreateForm(request.POST)

        if form.is_valid():
            # =========================
            # CREATE USER
            # =========================
            user = User.objects.create_user(
                username=form.cleaned_data["username"],
                password=form.cleaned_data["password"],
            )

            user.is_active = form.cleaned_data["is_active"]
            user.save()

            # =========================
            # ASSIGN ROLE (GROUP)
            # =========================
            roles = form.cleaned_data["roles"]
            user.groups.set(roles)

            return redirect("superadmin:user_list")

    else:
        form = UserCreateForm()

    return render(
        request,
        "super_admin/user_create.html",
        {
            "form": form
        }
    )
