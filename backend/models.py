from django.db import models, transaction
from django.core.validators import RegexValidator
from django.contrib.auth.models import User
from django.conf import settings
from datetime import date
from django.db.models import Sum

# =========================
# KONSTANTA
# =========================
BIAYA_DAFTAR_ULANG = 250_000


# =========================
# MODEL ROLE / PROFIL USER
# =========================
class UserProfile(models.Model):

    ROLE_CHOICES = [
        ('SUPERADMIN', 'Super Admin'),
        ('ADMIN', 'Admin'),
        ('PANITIA', 'Panitia'),
        ('BENDAHARA', 'Bendahara'),
        ('KEPALA_SEKOLAH', 'Kepala Sekolah'),
    ]

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='profile'
    )

    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        default='PANITIA'
    )

    def __str__(self):
        return f"{self.user.username} ({self.role})"


# =========================
# MODEL PENDAFTARAN
# =========================
class Pendaftaran(models.Model):

    JURUSAN_CHOICES = [
        ('TKRO', 'Teknik Kendaraan Ringan Otomotif'),
        ('TSM', 'Teknik Sepeda Motor'),
        ('AKL', 'Akuntansi dan Keuangan Lembaga'),
        ('RPL', 'Rekayasa Perangkat Lunak'),
        ('KUL', 'Kuliner'),
    ]

    JALUR_CHOICES = [
        ('KHUSUS', 'Jalur Khusus'),
        ('UMUM', 'Jalur Umum'),
    ]

    STATUS_CHOICES = [
        ('terdaftar', 'Terdaftar'),
        ('diterima', 'Diterima'),
        ('ditolak', 'Ditolak'),
        ('daftar_ulang', 'Daftar Ulang'),
    ]

    nik = models.CharField(
        max_length=16,
        unique=True,
        validators=[RegexValidator(
            regex=r'^\d{16}$',
            message='NIK harus 16 digit angka'
        )]
    )

    nama_lengkap = models.CharField(max_length=100)
    tempat_lahir = models.CharField(max_length=100)
    tanggal_lahir = models.DateField()

    jenis_kelamin = models.CharField(
        max_length=1,
        choices=[('L', 'Laki-laki'), ('P', 'Perempuan')]
    )

    agama = models.CharField(max_length=50)
    asal_sekolah = models.CharField(max_length=200)

    dusun = models.CharField(max_length=100, blank=True)
    rt = models.CharField(max_length=10, blank=True)
    rw = models.CharField(max_length=10, blank=True)
    desa_kelurahan = models.CharField(max_length=100)
    kecamatan = models.CharField(max_length=100)
    kabupaten_kota = models.CharField(max_length=100)

    nama_ayah = models.CharField(max_length=200, blank=True)
    nama_ibu = models.CharField(max_length=200, blank=True)

    no_wa = models.CharField(
        max_length=15,
        validators=[RegexValidator(
            regex=r'^08\d{8,11}$',
            message='Nomor WA harus diawali 08 dan 10–13 digit'
        )]
    )

    jurusan = models.CharField(
        max_length=10,
        choices=JURUSAN_CHOICES
    )

    jalur = models.CharField(
        max_length=10,
        choices=JALUR_CHOICES,
        blank=True,
        editable=False
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='terdaftar'
    )

    nisn = models.CharField(max_length=20, blank=True)
    nilai_skl = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True
    )

    pekerjaan_ayah = models.CharField(max_length=100, blank=True)
    pekerjaan_ibu = models.CharField(max_length=100, blank=True)

    keringanan_prestasi = models.TextField(blank=True, null=True)

    nomor_pendaftaran = models.CharField(
        max_length=25,
        unique=True,
        editable=False,
        blank=True
    )

    tanggal_pendaftaran = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if self.nama_lengkap:
            self.nama_lengkap = " ".join(self.nama_lengkap.upper().split())

        if not self.jalur:
            today = date.today()
            if date(2026, 1, 7) <= today <= date(2026, 4, 30):
                self.jalur = 'KHUSUS'
            elif date(2026, 5, 1) <= today <= date(2026, 6, 30):
                self.jalur = 'UMUM'

        if not self.nomor_pendaftaran:
            with transaction.atomic():
                tahun = date.today().year
                prefix = f"MARSA-{tahun}-{self.jurusan}"

                last = Pendaftaran.objects.select_for_update().filter(
                    nomor_pendaftaran__startswith=prefix
                ).order_by('-nomor_pendaftaran').first()

                next_number = int(last.nomor_pendaftaran.split('-')[-1]) + 1 if last else 1
                self.nomor_pendaftaran = f"{prefix}-{next_number:04d}"

        super().save(*args, **kwargs)

    @property
    def total_bayar(self):
        return self.pembayaran_daftar_ulang.aggregate(
            total=Sum('nominal')
        )['total'] or 0

    @property
    def sisa_bayar(self):
        return BIAYA_DAFTAR_ULANG - self.total_bayar

    @property
    def is_lunas(self):
        return self.total_bayar >= BIAYA_DAFTAR_ULANG

    def __str__(self):
        return f"{self.nomor_pendaftaran} - {self.nama_lengkap}"

    class Meta:
        ordering = ['-tanggal_pendaftaran']


# =========================
# MODEL CICILAN DAFTAR ULANG
# =========================
class PembayaranDaftarUlang(models.Model):

    pendaftaran = models.ForeignKey(
        Pendaftaran,
        on_delete=models.CASCADE,
        related_name='pembayaran_daftar_ulang'
    )

    tanggal = models.DateField(auto_now_add=True)
    nominal = models.PositiveIntegerField()

    petugas = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True
    )

    keterangan = models.CharField(
        max_length=255,
        blank=True
    )

    def __str__(self):
        return f"{self.pendaftaran.nomor_pendaftaran} - Rp {self.nominal}"


# =========================
# LOG AKTIVITAS PENDAFTARAN (EXISTING)
# =========================
class LogAktivitas(models.Model):

    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    pendaftaran = models.ForeignKey(
        Pendaftaran,
        on_delete=models.CASCADE
    )

    aksi = models.CharField(max_length=100)
    detail = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-timestamp']


# =========================
# LOG AKTIVITAS GLOBAL (SUPERADMIN)
# =========================
class ActivityLog(models.Model):
    """
    Log audit global (SUPERADMIN).
    Append-only.
    """

    ACTION_CHOICES = (
        ("TOGGLE_USER_ACTIVE", "Toggle User Active"),
        ("UPDATE_USER_ROLE", "Update User Role"),
        ("EXPORT_DATA", "Export Data"),
        ("LOGIN", "Login"),
        ("LOGOUT", "Logout"),
        ("OTHER", "Other"),
    )

    actor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name="global_activity_logs"
    )

    action = models.CharField(
        max_length=50,
        choices=ACTION_CHOICES
    )

    # FIELD LAMA — JANGAN DIHAPUS
    target_username = models.CharField(
        max_length=150,
        blank=True
    )

    # FIELD BARU — GENERIK
    target = models.CharField(
        max_length=255,
        blank=True
    )

    note = models.TextField(blank=True)

    ip_address = models.GenericIPAddressField(
        null=True,
        blank=True
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.action} by {self.actor}"

