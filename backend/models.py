from django.db import models
from django.core.validators import RegexValidator
from datetime import date


# =========================
# MODEL PENDAFTARAN
# =========================
class Pendaftaran(models.Model):

    # =====================
    # PILIHAN
    # =====================
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

    # =====================
    # IDENTITAS UTAMA
    # =====================
    nik = models.CharField(
        max_length=16,
        unique=True,
        verbose_name="NIK (16 Digit)",
        validators=[
            RegexValidator(
                regex=r'^\d{16}$',
                message='NIK harus terdiri dari 16 digit angka'
            )
        ]
    )

    nama_lengkap = models.CharField(
        max_length=100,
        verbose_name="Nama Lengkap"
    )

    tempat_lahir = models.CharField(
        max_length=100,
        verbose_name="Tempat Lahir"
    )

    tanggal_lahir = models.DateField(
        verbose_name="Tanggal Lahir"
    )

    jenis_kelamin = models.CharField(
        max_length=1,
        choices=[('L', 'Laki-laki'), ('P', 'Perempuan')],
        verbose_name="Jenis Kelamin"
    )

    agama = models.CharField(
        max_length=50,
        verbose_name="Agama"
    )

    asal_sekolah = models.CharField(
        max_length=200,
        verbose_name="Asal Sekolah"
    )

    # =====================
    # ALAMAT
    # =====================
    dusun = models.CharField(
        max_length=100,
        blank=True,
        verbose_name="Dusun/Dukuh"
    )

    rt = models.CharField(
        max_length=10,
        blank=True,
        verbose_name="RT"
    )

    rw = models.CharField(
        max_length=10,
        blank=True,
        verbose_name="RW"
    )

    desa_kelurahan = models.CharField(
        max_length=100,
        verbose_name="Desa/Kelurahan"
    )

    kecamatan = models.CharField(
        max_length=100,
        verbose_name="Kecamatan"
    )

    kabupaten_kota = models.CharField(
        max_length=100,
        verbose_name="Kabupaten/Kota"
    )

    # =====================
    # ORANG TUA
    # =====================
    nama_ayah = models.CharField(
        max_length=200,
        blank=True,
        verbose_name="Nama Ayah Kandung"
    )

    nama_ibu = models.CharField(
        max_length=200,
        verbose_name="Nama Ibu Kandung"
    )

    # =====================
    # KONTAK
    # =====================
    no_wa = models.CharField(
        max_length=15,
        verbose_name="No WA Aktif",
        validators=[
            RegexValidator(
                regex=r'^08\d{8,11}$',
                message='Nomor WA harus diawali 08 dan berisi 10–13 digit'
            )
        ]
    )

    # =====================
    # PENDAFTARAN
    # =====================
    jurusan = models.CharField(
        max_length=10,
        choices=JURUSAN_CHOICES,
        verbose_name="Jurusan yang Dipilih"
    )

    jalur = models.CharField(
        max_length=10,
        choices=JALUR_CHOICES,
        blank=True,
        editable=False,
        verbose_name="Jalur Pendaftaran"
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='terdaftar',
        verbose_name="Status Pendaftaran"
    )

    # =====================
    # DATA ADMIN
    # =====================
    nisn = models.CharField(
        max_length=20,
        blank=True,
        verbose_name="NISN"
    )

    nilai_skl = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name="Nilai SKL"
    )

    pekerjaan_ayah = models.CharField(
        max_length=100,
        blank=True,
        verbose_name="Pekerjaan Ayah"
    )

    pekerjaan_ibu = models.CharField(
        max_length=100,
        blank=True,
        verbose_name="Pekerjaan Ibu"
    )

    keringanan_prestasi = models.TextField(
        blank=True,
        null=True,
        verbose_name="Keringanan / Prestasi"
    )

    # =====================
    # PEMBAYARAN
    # =====================
    nominal_pembayaran = models.DecimalField(
        max_digits=10,
        decimal_places=0,
        default=0,
        null=True,
        verbose_name="Nominal Pembayaran (Rp)"
    )

    tanggal_pembayaran = models.DateField(
        null=True,
        blank=True,
        verbose_name="Tanggal Pembayaran"
    )

    # =====================
    # SISTEM
    # =====================
    nomor_pendaftaran = models.CharField(
        max_length=20,
        unique=True,
        editable=False,
        blank=True,
        verbose_name="Nomor Pendaftaran"
    )

    tanggal_pendaftaran = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Tanggal & Waktu Pendaftaran"
    )

    # =====================
    # SAVE OVERRIDE
    # =====================
    def save(self, *args, **kwargs):

        if self.nama_lengkap:
            self.nama_lengkap = " ".join(self.nama_lengkap.upper().split())

        if not self.jalur:
            today = date.today()

            if date(2026, 1, 7) <= today <= date(2026, 4, 30):
                self.jalur = 'KHUSUS'
            elif date(2026, 5, 1) <= today <= date(2026, 6, 30):
                self.jalur = 'UMUM'
            else:
                self.jalur = None

        super().save(*args, **kwargs)

    # =====================
    # PROPERTY (TAMBAHAN)
    # =====================
    @property
    def alamat_lengkap(self):
        parts = [
            f"Dusun {self.dusun}" if self.dusun else None,
            f"RT {self.rt}/RW {self.rw}" if self.rt and self.rw else None,
            self.desa_kelurahan,
            self.kecamatan,
            self.kabupaten_kota,
        ]
        return ", ".join([p for p in parts if p])

    def __str__(self):
        return f"{self.nomor_pendaftaran or 'Belum Ada Nomor'} - {self.nama_lengkap}"

    class Meta:
        verbose_name = "Pendaftaran Siswa Baru"
        verbose_name_plural = "Pendaftaran Siswa Baru"
        ordering = ['-tanggal_pendaftaran']


# =========================
# MODEL LOG AKTIVITAS
# =========================
class LogAktivitas(models.Model):
    user = models.ForeignKey(
        'auth.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    pendaftaran = models.ForeignKey(
        Pendaftaran,
        on_delete=models.CASCADE
    )
    aksi = models.CharField(
        max_length=100
    )
    detail = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.timestamp} - {self.aksi}"

    class Meta:
        ordering = ['-timestamp']
