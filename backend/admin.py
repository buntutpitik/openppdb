from django.contrib import admin
from .models import Pendaftaran

@admin.register(Pendaftaran)
class PendaftaranAdmin(admin.ModelAdmin):
    list_display = ('nomor_pendaftaran', 'nama_lengkap', 'nik', 'jurusan', 'jalur', 'no_wa', 'status', 'tanggal_pendaftaran')
    readonly_fields = ('nomor_pendaftaran', 'tanggal_pendaftaran', 'jalur')  # Tambahin jalur ke readonly biar aman
    list_filter = ('jurusan', 'jalur', 'status')
    search_fields = ('nama_lengkap', 'nik', 'nomor_pendaftaran', 'no_wa')
    fieldsets = (
        (None, {
            'fields': ('nik', 'nama_lengkap', 'jurusan', 'no_wa')
        }),
        ('Data Pribadi', {
            'fields': ('tempat_lahir', 'tanggal_lahir', 'jenis_kelamin', 'agama', 'asal_sekolah')
        }),
        ('Alamat', {
            'fields': ('dusun', 'rt', 'rw', 'desa_kelurahan', 'kecamatan', 'kabupaten_kota')
        }),
        ('Orang Tua', {
            'fields': ('nama_ayah', 'nama_ibu')
        }),
        ('Otomatis', {
            'fields': ('nomor_pendaftaran', 'status', 'tanggal_pendaftaran'),  # Hapus 'jalur' dari sini
            'classes': ('collapse',)
        }),
    )

from .models import LogAktivitas

@admin.register(LogAktivitas)
class LogAktivitasAdmin(admin.ModelAdmin):
    list_display = ('timestamp', 'user', 'pendaftaran', 'aksi')
    list_filter = ('aksi', 'user')
    search_fields = ('pendaftaran__nama_lengkap', 'pendaftaran__nomor_pendaftaran')
    readonly_fields = ('timestamp', 'user', 'pendaftaran', 'aksi', 'detail')
    date_hierarchy = 'timestamp'