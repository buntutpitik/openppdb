from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import HttpResponse
from django.views.decorators.http import require_POST
from django.core.exceptions import PermissionDenied

from .forms import PendaftaranForm
from .models import Pendaftaran, LogAktivitas

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
    return render(request, 'kartu_pendaftaran.html', {
        'pendaftaran': pendaftaran
    })

# =====================================================
# ADMIN
# =====================================================

@login_required
@user_passes_test(is_admin)
def dashboard_admin(request):
    qs = Pendaftaran.objects.all().order_by('-tanggal_pendaftaran')

    return render(request, 'admin/dashboard_admin.html', {
        'pendaftarans': qs,
        'total': qs.count(),
        'terdaftar': qs.filter(status='terdaftar').count(),
        'diterima': qs.filter(status='diterima').count(),
        'daftar_ulang': qs.filter(status='daftar_ulang').count(),
        'ditolak': qs.filter(status='ditolak').count(),
    })


@login_required
@user_passes_test(is_admin)
def admin_pendaftaran_list(request):
    pendaftarans = Pendaftaran.objects.all().order_by('-tanggal_pendaftaran')

    return render(request, 'admin/pendaftaran_list.html', {
        'pendaftarans': pendaftarans
    })


@login_required
@user_passes_test(is_admin)
def admin_pendaftaran_tambah(request):
    if request.method == 'POST':
        form = PendaftaranForm(request.POST)
        if form.is_valid():
            pendaftaran = form.save(commit=False)
            pendaftaran.created_by_admin = True
            pendaftaran.save()

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

    return render(request, 'admin/pendaftaran_form.html', {
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
