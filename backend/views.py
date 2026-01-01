from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
from django.db.models import Sum

from .forms import PendaftaranForm
from .models import Pendaftaran, LogAktivitas

# Import buat QR Code
import qrcode
from io import BytesIO
import base64

# Import buat Export Excel
from openpyxl import Workbook
from openpyxl.styles import Font, Alignment, Border, Side, PatternFill
from openpyxl.utils import get_column_letter

def home(request):
    if request.method == 'POST':
        form = PendaftaranForm(request.POST)
        if form.is_valid():
            pendaftaran = form.save()  # Signal otomatis isi nomor + jalur + status
            messages.success(request, 'Pendaftaran berhasil!')
            return redirect('sukses', pk=pendaftaran.pk)
    else:
        form = PendaftaranForm()
    
    return render(request, 'pendaftaran.html', {'form': form})

def sukses(request, pk):
    pendaftaran = Pendaftaran.objects.get(pk=pk)
    return render(request, 'sukses.html', {'pendaftaran': pendaftaran})

def print_kartu(request, pk):
    pendaftaran = Pendaftaran.objects.get(pk=pk)
    
    # Generate QR Code dari nomor pendaftaran
    qr_data = pendaftaran.nomor_pendaftaran
    
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(qr_data)
    qr.make(fit=True)
    
    img = qr.make_image(fill_color="black", back_color="white")
    
    buffer = BytesIO()
    img.save(buffer, format='PNG')
    qr_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
    qr_image = f"data:image/png;base64,{qr_base64}"
    
    return render(request, 'kartu_pendaftaran.html', {
        'pendaftaran': pendaftaran,
        'qr_image': qr_image
    })

# === Dashboard & Fitur Bendahara ===
def bendahara_required(user):
    return user.is_authenticated and user.groups.filter(name='Bendahara').exists()

@login_required
@user_passes_test(bendahara_required, login_url='/admin/login/')
def dashboard_bendahara(request):
    pendaftarans = Pendaftaran.objects.all().order_by('-tanggal_pendaftaran')
    
    # Statistik sederhana
    total = pendaftarans.count()
    terdaftar = pendaftarans.filter(status='terdaftar').count()
    diterima = pendaftarans.filter(status='diterima').count()
    daftar_ulang = pendaftarans.filter(status='daftar_ulang').count()
    ditolak = pendaftarans.filter(status='ditolak').count()

    context = {
        'pendaftarans': pendaftarans,
        'total': total,
        'terdaftar': terdaftar,
        'diterima': diterima,
        'daftar_ulang': daftar_ulang,
        'ditolak': ditolak,
    }
    return render(request, 'dashboard_bendahara.html', context)

@login_required
@user_passes_test(bendahara_required, login_url='/admin/login/')
def ubah_status_daftar_ulang(request, pk):
    pendaftaran = Pendaftaran.objects.get(pk=pk)
    
    if request.method == 'POST':
        new_status = request.POST.get('status')
        if new_status in dict(Pendaftaran.STATUS_CHOICES):
            pendaftaran.status = new_status
            pendaftaran.save()
            messages.success(request, f"Status {pendaftaran.nama_lengkap} berhasil diubah menjadi {pendaftaran.get_status_display()}")
    
    return HttpResponseRedirect(reverse('dashboard_bendahara'))

@login_required
@user_passes_test(bendahara_required, login_url='/admin/login/')
def input_pembayaran(request, pk):
    pendaftaran = Pendaftaran.objects.get(pk=pk)
    
    if request.method == 'POST':
        nominal_str = request.POST.get('nominal_pembayaran')
        tanggal = request.POST.get('tanggal_pembayaran')
        
        if nominal_str:
            try:
                nominal = int(nominal_str)
                old_nominal = pendaftaran.nominal_pembayaran
                old_tanggal = pendaftaran.tanggal_pembayaran
                
                pendaftaran.nominal_pembayaran = nominal
                pendaftaran.tanggal_pembayaran = tanggal or None
                pendaftaran.save()
                
                # Tambah log dengan nama user bendahara
                LogAktivitas.objects.create(
                    user=request.user,  # <<< Ini yang penting, catat user yang input
                    pendaftaran=pendaftaran,
                    aksi="Input Pembayaran",
                    detail=f"Nominal diubah dari Rp {old_nominal} menjadi Rp {nominal}. Tanggal: {tanggal or '-'}"
                )
                
                messages.success(request, f"Pembayaran {pendaftaran.nama_lengkap} berhasil disimpan Rp {nominal}")
            except ValueError:
                messages.error(request, "Nominal harus angka")
    
    return HttpResponseRedirect(reverse('dashboard_bendahara'))

@login_required
@user_passes_test(bendahara_required, login_url='/admin/login/')
def rekap_daftar_ulang(request):
    pendaftarans = Pendaftaran.objects.filter(status='daftar_ulang').order_by('-tanggal_pembayaran')
    
    total_pembayaran = pendaftarans.aggregate(total=Sum('nominal_pembayaran'))['total'] or 0

    # Ambil nama bendahara yang input pembayaran (dari log terakhir)
    rekap_data = []
    for p in pendaftarans:
        last_log = LogAktivitas.objects.filter(
            pendaftaran=p,
            aksi="Input Pembayaran"
        ).order_by('-timestamp').first()
        
        bendahara_nama = (
            last_log.user.get_full_name() or 
            last_log.user.username or 
            "Tidak Diketahui"
        ) if last_log else "Belum Input"
        
        rekap_data.append({
            'pendaftaran': p,
            'bendahara_nama': bendahara_nama
        })

    context = {
        'rekap_data': rekap_data,
        'total_pembayaran': total_pembayaran,
        'jumlah': pendaftarans.count(),
    }
    return render(request, 'rekap_daftar_ulang.html', context)

@login_required
@user_passes_test(bendahara_required, login_url='/admin/login/')
def export_excel_rekap(request):
    pendaftarans = Pendaftaran.objects.filter(status='daftar_ulang').order_by('-tanggal_pembayaran')
    
    wb = Workbook()
    ws = wb.active
    ws.title = "Rekap Daftar Ulang"

    # Header tabel + kolom baru
    headers = ['No', 'Nomor Pendaftaran', 'Nama Lengkap', 'Jurusan', 'Nominal Bayar (Rp)', 'Tanggal Bayar', 'Bendahara Input', 'No WA']
    ws.append(headers)
    
    # Style header (sama kayak sebelumnya)
    header_font = Font(bold=True, color="FFFFFF")
    header_fill = PatternFill(start_color="28a745", end_color="28a745", fill_type="solid")
    thin_border = Border(left=Side(style='thin'), right=Side(style='thin'), top=Side(style='thin'), bottom=Side(style='thin'))
    
    for cell in ws[1]:
        cell.font = header_font
        cell.fill = header_fill
        cell.alignment = Alignment(horizontal='center', vertical='center')
        cell.border = thin_border

    # Isi data + nama bendahara
    for idx, p in enumerate(pendaftarans, start=1):
        # Ambil nama bendahara dari log terakhir input pembayaran
        last_log = LogAktivitas.objects.filter(
            pendaftaran=p,
            aksi="Input Pembayaran"
        ).order_by('-timestamp').first()
        
        bendahara_nama = (
            last_log.user.get_full_name() or 
            last_log.user.username or 
            "Belum Input"
        ) if last_log else "Belum Input"
        
        ws.append([
            idx,
            p.nomor_pendaftaran,
            p.nama_lengkap,
            p.get_jurusan_display(),
            p.nominal_pembayaran,
            p.tanggal_pembayaran.strftime('%d/%m/%Y') if p.tanggal_pembayaran else '-',
            bendahara_nama,  # <<< Kolom baru
            p.no_wa
        ])

    # Auto adjust column width
    for col in ws.columns:
        max_length = 0
        column = col[0].column_letter
        for cell in col:
            try:
                if len(str(cell.value)) > max_length:
                    max_length = len(str(cell.value))
            except:
                pass
        adjusted_width = (max_length + 2)
        ws.column_dimensions[column].width = adjusted_width

    # Total pembayaran
    total_row = pendaftarans.count() + 3
    ws[f'A{total_row}'] = "TOTAL UANG MASUK"
    ws[f'E{total_row}'] = pendaftarans.aggregate(total=Sum('nominal_pembayaran'))['total'] or 0
    ws[f'A{total_row}'].font = Font(bold=True)
    ws[f'E{total_row}'].font = Font(bold=True, color="28a745")

    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename=rekap_daftar_ulang.xlsx'
    wb.save(response)
    
    return response

def admin_required(user):
    return user.is_authenticated and user.is_staff and not user.is_superuser

@login_required
@user_passes_test(admin_required, login_url='/admin/login/')
def dashboard_admin(request):
    pendaftarans = Pendaftaran.objects.all().order_by('-tanggal_pendaftaran')
    
    total = pendaftarans.count()
    terdaftar = pendaftarans.filter(status='terdaftar').count()
    diterima = pendaftarans.filter(status='diterima').count()
    daftar_ulang = pendaftarans.filter(status='daftar_ulang').count()
    ditolak = pendaftarans.filter(status='ditolak').count()
    
    total_pembayaran = pendaftarans.aggregate(total=Sum('nominal_pembayaran'))['total'] or 0
    
    log_terbaru = LogAktivitas.objects.all().order_by('-timestamp')[:10]

    context = {
        'pendaftarans': pendaftarans,
        'total': total,
        'terdaftar': terdaftar,
        'diterima': diterima,
        'daftar_ulang': daftar_ulang,
        'ditolak': ditolak,
        'total_pembayaran': total_pembayaran,
        'log_terbaru': log_terbaru,
    }
    return render(request, 'dashboard_admin.html', context)