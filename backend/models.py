from django.db import models

# Model untuk data Pendaftaran Siswa Baru (PPDB SMK)
class Pendaftaran(models.Model):
    # Pilihan Jurusan SMK (sesuai SMK kamu)
    JURUSAN_CHOICES = [
        ('TKRO', 'Teknik Kendaraan Ringan Otomotif'),
        ('TSM', 'Teknik Sepeda Motor'),
        ('AKL', 'Akuntansi dan Keuangan Lembaga'),
        ('RPL', 'Rekayasa Perangkat Lunak'),
        ('KUL', 'Kuliner'),
        # Kalau mau tambah lagi nanti, tinggal di sini ya sayang~
    ]

    # Pilihan Jalur Pendaftaran (cuma 2)
    JALUR_CHOICES = [
        ('KHUSUS', 'Jalur Khusus'),
        ('UMUM', 'Jalur Umum'),
    ]

    # Pilihan Status Pendaftaran
    STATUS_CHOICES = [
        ('terdaftar', 'Terdaftar'),
        ('diterima', 'Diterima'),
        ('ditolak', 'Ditolak'),
        ('daftar_ulang', 'Daftar Ulang'),
    ]

    # Identitas utama
    nik = models.CharField(
        max_length=16,
        unique=True,
        verbose_name="NIK (16 Digit)",
        help_text="Masukkan 16 digit NIK dari KK/KTP (wajib dan unik)"
    )

    nama_lengkap = models.CharField(max_length=200, verbose_name="Nama Lengkap")

    tempat_lahir = models.CharField(max_length=100, verbose_name="Tempat Lahir")
    tanggal_lahir = models.DateField(verbose_name="Tanggal Lahir")

    jenis_kelamin = models.CharField(
        max_length=1,
        choices=[('L', 'Laki-laki'), ('P', 'Perempuan')],
        verbose_name="Jenis Kelamin"
    )

    agama = models.CharField(max_length=50, verbose_name="Agama")

    asal_sekolah = models.CharField(max_length=200, verbose_name="Asal Sekolah")

    # Alamat terpisah biar lebih rapi
    dusun = models.CharField(
        max_length=100,
        blank=True,
        verbose_name="Dusun/Hamlet"
    )

    rt = models.CharField(
        max_length=10,
        blank=True,
        verbose_name="RT",
        help_text="Contoh: 001"
    )

    rw = models.CharField(
        max_length=10,
        blank=True,
        verbose_name="RW",
        help_text="Contoh: 002"
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

    # Data orang tua
    nama_ayah = models.CharField(max_length=200, blank=True, verbose_name="Nama Ayah Kandung")
    nama_ibu = models.CharField(max_length=200, verbose_name="Nama Ibu Kandung")

    # Kontak
    no_wa = models.CharField(
        max_length=15,
        verbose_name="No WA Aktif",
        help_text="Nomor WhatsApp yang bisa dihubungi"
    )

    # Jurusan & Jalur
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
        verbose_name="Jalur Pendaftaran",
        help_text="Otomatis terisi berdasarkan tanggal pendaftaran"
    )

    # Status (default Terdaftar pas baru submit)
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='terdaftar',
        verbose_name="Status Pendaftaran"
    )

    # Pembayaran
    nominal_pembayaran = models.DecimalField(
        max_digits=10,
        decimal_places=0,
        default=0,
        verbose_name="Nominal Pembayaran (Rp)",
        help_text="Masukkan nominal yang sudah dibayar (tanpa titik/rupiah)"
    )

    tanggal_pembayaran = models.DateField(
        null=True,
        blank=True,
        verbose_name="Tanggal Pembayaran"
    )

    # Nomor pendaftaran otomatis urut per jurusan
    nomor_pendaftaran = models.CharField(
        max_length=20,
        unique=True,
        editable=False,
        blank=True,
        verbose_name="Nomor Pendaftaran"
    )

    # Tanggal pendaftaran otomatis
    tanggal_pendaftaran = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Tanggal & Waktu Pendaftaran"
    )

    def __str__(self):
        return f"{self.nomor_pendaftaran or 'Belum Ada Nomor'} - {self.nama_lengkap} ({self.jurusan})"

    class Meta:
        verbose_name = "Pendaftaran Siswa Baru"
        verbose_name_plural = "Pendaftaran Siswa Baru"
        ordering = ['-tanggal_pendaftaran']

# Model Log Aktivitas (baru ditambahin)
class LogAktivitas(models.Model):
    user = models.ForeignKey('auth.User', on_delete=models.SET_NULL, null=True, blank=True, verbose_name="User")
    pendaftaran = models.ForeignKey(Pendaftaran, on_delete=models.CASCADE, verbose_name="Pendaftaran")
    aksi = models.CharField(max_length=100, verbose_name="Aksi")
    detail = models.TextField(verbose_name="Detail Perubahan")
    timestamp = models.DateTimeField(auto_now_add=True, verbose_name="Waktu")

    def __str__(self):
        return f"{self.timestamp} - {self.user or 'System'} - {self.aksi} - {self.pendaftaran}"

    class Meta:
        verbose_name = "Log Aktivitas"
        verbose_name_plural = "Log Aktivitas"
        ordering = ['-timestamp']

        