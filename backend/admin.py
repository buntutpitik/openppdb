from django.contrib import admin
from .models import Pendaftaran, LogAktivitas
from .forms_admin import AdminPendaftaranForm


@admin.register(Pendaftaran)
class PendaftaranAdmin(admin.ModelAdmin):
    form = AdminPendaftaranForm  # 🔥 INI KUNCI UTAMA

    list_display = (
        'nomor_pendaftaran',
        'nama_lengkap',
        'nik',
        'jurusan',
        'jalur',
        'no_wa',
        'status',
        'tanggal_pendaftaran',
    )

    readonly_fields = (
        'nomor_pendaftaran',
        'tanggal_pendaftaran',
        'jalur',
    )

    list_filter = ('jurusan', 'jalur', 'status')
    search_fields = ('nama_lengkap', 'nik', 'nomor_pendaftaran', 'no_wa')

    fieldsets = (
        (None, {
            'fields': (
                'nik',
                'nama_lengkap',
                'jurusan',
                'no_wa',
            )
        }),
        ('Data Pribadi', {
            'fields': (
                'tempat_lahir',
                'tanggal_lahir',     # ✅ date picker BALIK
                'jenis_kelamin',
                'agama',
                'asal_sekolah',      # ✅ dropdown/manual BALIK
            )
        }),
        ('Alamat', {
            'fields': (
                'dusun',
                'rt',
                'rw',
                'desa_kelurahan',
                'kecamatan',
                'kabupaten_kota',
            )
        }),
        ('Orang Tua', {
            'fields': (
                'nama_ayah',
                'nama_ibu',
            )
        }),
        ('Administrasi', {
            'fields': (
                'nisn',
                'nilai_skl',
                'keringanan_prestasi',  # ✅ MUNCUL LAGI
                'status',
            )
        }),
        ('Otomatis', {
            'fields': (
                'nomor_pendaftaran',
                'tanggal_pendaftaran',
            ),
            'classes': ('collapse',),
        }),
    )


@admin.register(LogAktivitas)
class LogAktivitasAdmin(admin.ModelAdmin):
    list_display = ('timestamp', 'user', 'pendaftaran', 'aksi')
    list_filter = ('aksi', 'user')
    search_fields = (
        'pendaftaran__nama_lengkap',
        'pendaftaran__nomor_pendaftaran',
    )
    readonly_fields = (
        'timestamp',
        'user',
        'pendaftaran',
        'aksi',
        'detail',
    )
    date_hierarchy = 'timestamp'
