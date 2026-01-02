from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
from django.db.models import Sum
from django.views.decorators.http import require_POST
from django.core.exceptions import PermissionDenied

from .forms import PendaftaranForm
from .models import Pendaftaran, LogAktivitas

# QR Code
import qrcode
from io import BytesIO
import base64

# Export Excel
from openpyxl import Workbook
from openpyxl.styles import Font, Alignment, Border, Side, PatternFill

# =====================================================
# PUBLIC
# =====================================================

def home(request):
    if request.method == 'POST':
        form = PendaftaranForm(request.POST)
        if form.is_valid():
            pendaftaran = form.save()
            messages.success(request, 'Pendaftaran berhasil!')
            return redirect('sukses', pk=pendaftaran.pk)
    else:
        form = PendaftaranForm()

    return render(request, 'pendaftaran.html', {'form': form})


def sukses(request, pk):
    pendaftaran = get_object_or_404(Pendaftaran, pk=pk)
    return render(request, 'sukses.html', {'pendaftaran': pendaftaran})


def print_kartu(request, nomor_pendaftaran):
    pendaftaran = get_object_or_404(
        Pendaftaran,
        nomor_pendaftaran=nomor_pendaftaran
    )

    qr = qrcode.QRCode(version=1, box_size=10, border=4)
    qr.add_data(pendaftaran.nomor_pendaftaran)
    qr.make(fit=True)

    img = qr.make_image(fill_color="black", back_color="white")
    buffer = BytesIO()
    img.save(buffer, format='PNG')

    qr_base64 = base64.b64encode(buffer.getvalue()).decode()

    return render(request, 'kartu_pendaftaran.html', {
        'pendaftaran': pendaftaran,
        'qr_image': f"data:image/png;base64,{qr_base64}"
    })

# =====================================================
# ROLE CHECK
# =====================================================

def bendahara_required(user):
    return user.is_authenticated and user.groups.filter(name='Bendahara').exists()


def admin_required(user):
    return user.is_authenticated and user.is_staff and not user.is_superuser

# =====================================================
# BENDAHARA
# =====================================================

@login_required
@user_passes_test(bendahara_required, login_url='/admin/login/')
def dashboard_bendahara(request):
    qs = Pendaftaran.objects.all().order_by('-tanggal_pendaftaran')

    context = {
        'pendaftarans': qs,
        'total': qs.count(),
        'terdaftar': qs.filter(status='terdaftar').count(),
        'diterima': qs.filter(status='diterima').count(),
        'daftar_ulang': qs.filter(status='daftar_ulang').count(),
        'ditolak': qs.filter(status='ditolak').count(),
    }
    return render(request, 'dashboard_bendahara.html', context)


@login_required
@user_passes_test(bendahara_required, login_url='/admin/login/')
@require_POST
def ubah_status_daftar_ulang(request, pk):
    pendaftaran = get_object_or_404(Pendaftaran, pk=pk)

    if pendaftaran.status != 'diterima':
        messages.error(request, "Hanya status DITERIMA yang bisa daftar ulang")
        return redirect('dashboard_bendahara')

    pendaftaran.status = 'daftar_ulang'
    pendaftaran.save()

    LogAktivitas.objects.create(
        user=request.user,
        pendaftaran=pendaftaran,
        aksi="Ubah Status",
        detail="Status diubah ke DAFTAR ULANG"
    )

    messages.success(request, "Status berhasil diubah")
    return redirect('dashboard_bendahara')


@login_required
@user_passes_test(bendahara_required, login_url='/admin/login/')
@require_POST
def input_pembayaran(request, pk):
    pendaftaran = get_object_or_404(Pendaftaran, pk=pk)

    if pendaftaran.status != 'daftar_ulang':
        messages.error(request, "Pembayaran hanya untuk DAFTAR ULANG")
        return redirect('dashboard_bendahara')

    try:
        nominal = int(request.POST.get('nominal_pembayaran'))
    except:
        messages.error(request, "Nominal harus angka")
        return redirect('dashboard_bendahara')

    tanggal = request.POST.get('tanggal_pembayaran')
    old_nominal = pendaftaran.nominal_pembayaran

    pendaftaran.nominal_pembayaran = nominal
    pendaftaran.tanggal_pembayaran = tanggal or None
    pendaftaran.save()

    LogAktivitas.objects.create(
        user=request.user,
        pendaftaran=pendaftaran,
        aksi="Input Pembayaran",
        detail=f"Nominal dari Rp {old_nominal} ke Rp {nominal}"
    )

    messages.success(request, "Pembayaran berhasil disimpan")
    return redirect('dashboard_bendahara')


@login_required
@user_passes_test(bendahara_required, login_url='/admin/login/')
def rekap_daftar_ulang(request):
    qs = Pendaftaran.objects.filter(status='daftar_ulang')

    data = []
    for p in qs:
        log = LogAktivitas.objects.filter(
            pendaftaran=p,
            aksi="Input Pembayaran"
        ).order_by('-timestamp').first()

        data.append({
            'pendaftaran': p,
            'bendahara': log.user.get_full_name() if log and log.user else "-"
        })

    return render(request, 'rekap_daftar_ulang.html', {
        'rekap_data': data,
        'total_pembayaran': qs.aggregate(total=Sum('nominal_pembayaran'))['total'] or 0,
        'jumlah': qs.count()
    })


@login_required
@user_passes_test(bendahara_required, login_url='/admin/login/')
def export_excel_rekap(request):
    qs = Pendaftaran.objects.filter(status='daftar_ulang')

    wb = Workbook()
    ws = wb.active
    ws.title = "Rekap Daftar Ulang"

    headers = [
        'No', 'Nomor', 'Nama', 'Jurusan',
        'Nominal', 'Tanggal', 'Bendahara', 'WA'
    ]
    ws.append(headers)

    for i, p in enumerate(qs, 1):
        log = LogAktivitas.objects.filter(
            pendaftaran=p,
            aksi="Input Pembayaran"
        ).order_by('-timestamp').first()

        ws.append([
            i,
            p.nomor_pendaftaran,
            p.nama_lengkap,
            p.get_jurusan_display(),
            p.nominal_pembayaran,
            p.tanggal_pembayaran or '-',
            log.user.username if log and log.user else '-',
            p.no_wa
        ])

    response = HttpResponse(
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    response['Content-Disposition'] = 'attachment; filename=rekap_daftar_ulang.xlsx'
    wb.save(response)
    return response

# =====================================================
# ADMIN
# =====================================================

@login_required
@user_passes_test(admin_required, login_url='/admin/login/')
def dashboard_admin(request):
    qs = Pendaftaran.objects.all()

    return render(request, 'dashboard_admin.html', {
        'pendaftarans': qs,
        'total': qs.count(),
        'terdaftar': qs.filter(status='terdaftar').count(),
        'diterima': qs.filter(status='diterima').count(),
        'daftar_ulang': qs.filter(status='daftar_ulang').count(),
        'ditolak': qs.filter(status='ditolak').count(),
        'total_pembayaran': qs.aggregate(total=Sum('nominal_pembayaran'))['total'] or 0,
        'log_terbaru': LogAktivitas.objects.all()[:10]
    })


@login_required
@user_passes_test(admin_required, login_url='/admin/login/')
@require_POST
def ubah_status_admin(request, pk):
    pendaftaran = get_object_or_404(Pendaftaran, pk=pk)
    status = request.POST.get('status')

    if status not in ['diterima', 'ditolak']:
        raise PermissionDenied

    pendaftaran.status = status
    pendaftaran.save()

    LogAktivitas.objects.create(
        user=request.user,
        pendaftaran=pendaftaran,
        aksi="Ubah Status",
        detail=f"Status diubah ke {pendaftaran.get_status_display()}"
    )

    messages.success(request, "Status diperbarui")
    return redirect('dashboard_admin')
