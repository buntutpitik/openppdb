from openpyxl import Workbook
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.db.models import Count

from backend.models import Pendaftaran, ActivityLog
from backend.permissions import admin_required


@login_required
@admin_required
def export_rekap_asal_sekolah_excel(request):
    # ==========================
    # QUERY REKAP
    # ==========================
    data = (
        Pendaftaran.objects
        .values("asal_sekolah")
        .annotate(total=Count("id"))
        .order_by("-total")
    )

    # ==========================
    # BUAT EXCEL
    # ==========================
    wb = Workbook()
    ws = wb.active
    ws.title = "Rekap Asal Sekolah"

    # HEADER
    ws.append(["No", "Asal Sekolah", "Jumlah Pendaftar"])

    # ISI DATA
    for idx, row in enumerate(data, start=1):
        ws.append([
            idx,
            row["asal_sekolah"] or "-",
            row["total"]
        ])

    # ==========================
    # LOG AKTIVITAS
    # ==========================
    ActivityLog.objects.create(
        actor=request.user,
        action="EXPORT_DATA",
        target="Rekap Asal Sekolah",
        note="Export Excel rekap asal sekolah",
        ip_address=request.META.get("REMOTE_ADDR")
    )

    # ==========================
    # RESPONSE DOWNLOAD
    # ==========================
    response = HttpResponse(
        content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
    response["Content-Disposition"] = (
        'attachment; filename="rekap_asal_sekolah.xlsx"'
    )

    wb.save(response)
    return response
