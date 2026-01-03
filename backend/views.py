from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.views.decorators.http import require_POST
from django.core.exceptions import PermissionDenied
from django.core.paginator import Paginator
from django.db.models import Q

from .forms import PendaftaranForm
from .models import Pendaftaran, LogAktivitas

# =========================
# QR CODE (TAJAM & AMAN)
# =========================
import qrcode
from io import BytesIO
import base64


def generate_qr_base64(data):
    qr = qrcode.QRCode(
        version=3,
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=12,
        border=4,
    )
    qr.add_data(data)
    qr.make(fit=True)

    img = qr.make_image(fill_color="black", back_color="white")

    buffer = BytesIO()
    img.save(buffer, format="PNG")
    img_str = base64.b64encode(buffer.getvalue()).decode()

    return f"data:image/png;base64,{img_str}"


# =====================================================
# ROLE CHECK
# =====================================================
def is_admin(user):
    return (
        user.is_authenticated
        and user.groups.filter(name__in=['Admin', 'Panitia']).exists()
    )


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

    qr_data = request.build_absolute_uri(
        f"/kartu/{pendaftaran.nomor_pendaftaran}/"
    )
    qr_image = generate_qr_base64(qr_data)

    return render(request, 'kartu_pendaftaran.html', {
        'pendaftaran': pendaftaran,
        'qr_image': qr_image,
    })


# =====================================================
# ADMIN PANEL
# =====================================================
@login_required
@user_passes_test(is_admin)
def dashboard_admin(request):
    qs = Pendaftaran.objects.all()

    return render(request, 'adminpanel/dashboard.html', {
        'pendaftarans': qs.order_by('-tanggal_pendaftaran')[:10],
        'total': qs.count(),
        'terdaftar': qs.filter(status='terdaftar').count(),
        'diterima': qs.filter(status='diterima').count(),
        'ditolak': qs.filter(status='ditolak').count(),
    })


@login_required
@user_passes_test(is_admin)
def admin_pendaftaran_list(request):
    status_filter = request.GET.get('status')
    jurusan_filter = request.GET.get('jurusan')
    keyword = request.GET.get('q')

    qs = Pendaftaran.objects.all().order_by('-tanggal_pendaftaran')

    if status_filter:
        qs = qs.filter(status=status_filter)

    if jurusan_filter:
        qs = qs.filter(jurusan=jurusan_filter)

    if keyword:
        qs = qs.filter(
            Q(nama_lengkap__icontains=keyword) |
            Q(nik__icontains=keyword) |
            Q(nomor_pendaftaran__icontains=keyword)
        )

    paginator = Paginator(qs, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'adminpanel/pendaftaran_list.html', {
        'pendaftarans': page_obj,
        'status_filter': status_filter,
        'jurusan_filter': jurusan_filter,
        'keyword': keyword,
        'page_obj': page_obj,
    })


@login_required
@user_passes_test(is_admin)
def admin_pendaftaran_tambah(request):
    if request.method == 'POST':
        form = PendaftaranForm(request.POST)
        if form.is_valid():
            pendaftaran = form.save()

            LogAktivitas.objects.create(
                user=request.user,
                pendaftaran=pendaftaran,
                aksi="Tambah Pendaftaran",
                detail="Ditambahkan oleh admin"
            )

            messages.success(request, "Pendaftaran berhasil ditambahkan")
            return redirect('admin_pendaftaran_list')
    else:
        form = PendaftaranForm()

    return render(request, 'adminpanel/pendaftaran_form.html', {
        'form': form
    })


@login_required
@user_passes_test(is_admin)
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

    messages.success(request, "Status berhasil diubah")
    return redirect('admin_pendaftaran_list')
