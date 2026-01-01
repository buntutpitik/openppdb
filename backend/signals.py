from django.db.models.signals import pre_save
from django.dispatch import receiver
from datetime import date
from .models import Pendaftaran

@receiver(pre_save, sender=Pendaftaran)
def generate_nomor_dan_jalur(sender, instance, **kwargs):
    # === Set Jalur Otomatis Berdasarkan Tanggal ===
    if not instance.jalur:
        today = date.today()

        TANGGAL_MULAI_KHUSUS = date(2026, 1, 7)
        TANGGAL_AKHIR_KHUSUS = date(2026, 4, 30)

        if TANGGAL_MULAI_KHUSUS <= today <= TANGGAL_AKHIR_KHUSUS:
            instance.jalur = 'KHUSUS'
        else:
            instance.jalur = 'UMUM'

    # === Generate Nomor Pendaftaran HANYA SEKALI (pas pertama daftar) ===
    # Kalau nomor udah ada, gak usah generate lagi (biar tetap meskipun jurusan diubah)
    if not instance.nomor_pendaftaran:
        # Kode jalur (pakai jalur saat daftar pertama)
        kode_jalur = '01' if instance.jalur == 'KHUSUS' else '02'
        
        # Kode jurusan (pakai jurusan saat daftar pertama)
        kode_jurusan = instance.jurusan

        # Cari urutan terakhir per jurusan (global, lanjut terus)
        last_entry = Pendaftaran.objects.filter(
            jurusan=instance.jurusan
        ).exclude(nomor_pendaftaran__isnull=True
        ).exclude(nomor_pendaftaran=''
        ).order_by('-nomor_pendaftaran').first()

        if last_entry and last_entry.nomor_pendaftaran:
            try:
                urutan = int(last_entry.nomor_pendaftaran.split('-')[-1]) + 1
            except:
                urutan = 1
        else:
            urutan = 1

        # Format tetap: MARSA26-01/02-JURUSAN-URUTAN
        instance.nomor_pendaftaran = f"MARSA26-{kode_jalur}-{kode_jurusan}-{urutan:03d}"

from django.contrib.auth.models import User
from .models import LogAktivitas

@receiver(pre_save, sender=Pendaftaran)
def log_perubahan_pendaftaran(sender, instance, **kwargs):
    if instance.pk:  # Kalau update (bukan create baru)
        old = Pendaftaran.objects.get(pk=instance.pk)
        changes = []
        
        if old.status != instance.status:
            changes.append(f"Status: {old.get_status_display()} → {instance.get_status_display()}")
        
        if old.nominal_pembayaran != instance.nominal_pembayaran:
            changes.append(f"Nominal Pembayaran: Rp {old.nominal_pembayaran} → Rp {instance.nominal_pembayaran}")
        
        if old.tanggal_pembayaran != instance.tanggal_pembayaran:
            changes.append(f"Tanggal Pembayaran: {old.tanggal_pembayaran} → {instance.tanggal_pembayaran}")
        
        if old.jurusan != instance.jurusan:
            changes.append(f"Jurusan: {old.get_jurusan_display()} → {instance.get_jurusan_display()}")
        
        if changes:
            # Ambil user dari request kalau ada (nanti kita tambah di view)
            # Untuk sekarang, kita catat "System" atau dari admin
            LogAktivitas.objects.create(
                user=None,  # Nanti kita tambah user dari request
                pendaftaran=instance,
                aksi="Perubahan Data",
                detail = "; ".join(changes)
            )
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import LogAktivitas
from .middleware import get_current_user

@receiver(post_save, sender=Pendaftaran)
def log_perubahan_pendaftaran(sender, instance, created, **kwargs):
    user = get_current_user()
    
    if created:
        LogAktivitas.objects.create(
            user=user,
            pendaftaran=instance,
            aksi="Pendaftaran Baru",
            detail=f"Pendaftaran baru oleh {instance.nama_lengkap}"
        )
    else:
        # Catat perubahan (sederhana dulu)
        LogAktivitas.objects.create(
            user=user,
            pendaftaran=instance,
            aksi="Perubahan Data",
            detail="Data pendaftaran diubah (status, nominal, dll)"
        )