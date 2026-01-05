from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Count
from .models import Pendaftaran
from .permissions import role_required


@login_required
@role_required("SUPERADMIN", "ADMIN", "PANITIA", "BENDAHARA")
def rekap_asal_sekolah(request):
    data = (
        Pendaftaran.objects
        .values("asal_sekolah")
        .annotate(total=Count("id"))
        .order_by("-total")
    )

    return render(
        request,
        "adminpanel/rekap_asal_sekolah.html",
        {"data": data}
    )
