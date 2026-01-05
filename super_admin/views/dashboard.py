from django.shortcuts import render
from backend.permissions import role_required


@role_required("SUPERADMIN")
def dashboard(request):
    return render(
        request,
        "super_admin/dashboard.html"
    )
