from django.db.models.signals import pre_save
from django.dispatch import receiver
from django.utils import timezone

from .models import Pendaftaran


@receiver(pre_save, sender=Pendaftaran)
def set_jalur_and_nomor_pendaftaran(sender, instance, **kwargs):
    # =========================
    # SET JALUR OTOMATIS
    # =========================
    if not instance.jalur:
        today = timezone.now().date()

        # 🔧 ATUR TANGGAL BATAS DI SINI
        BATAS_JALUR_KHUSUS = timezone.datetime(
            today.year, 6, 30
        ).date()

        if today <= BATAS_JALUR_KHUSUS:
            instance.jalur = 'KHUSUS'
        else:
            instance.jalur = 'UMUM'

    # =========================
    # SET NOMOR PENDAFTARAN
    # =========================
    if not instance.nomor_pendaftaran:
        tahun = timezone.now().year
        jurusan = instance.jurusan

        last = (
            Pendaftaran.objects
            .filter(
                jurusan=jurusan,
                tanggal_pendaftaran__year=tahun
            )
            .order_by('-id')
            .first()
        )

        if last and last.nomor_pendaftaran:
            try:
                last_number = int(last.nomor_pendaftaran.split('-')[-1])
            except (ValueError, IndexError):
                last_number = 0
        else:
            last_number = 0

        next_number = last_number + 1

        instance.nomor_pendaftaran = (
            f"PPDB-{tahun}-{jurusan}-{next_number:04d}"
        )
