from django import forms
from .models import Pendaftaran

class PendaftaranForm(forms.ModelForm):
    class Meta:
        model = Pendaftaran
        exclude = ['nomor_pendaftaran', 'jalur', 'status', 'tanggal_pendaftaran']  # Otomatis, gak muncul di form
        
        widgets = {
            'tanggal_lahir': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'nik': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '16 digit NIK', 'maxlength': '16'}),
            'no_wa': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Contoh: 081234567890'}),
            'jurusan': forms.Select(attrs={'class': 'form-control'}),
        }
        
        labels = {
            'nik': 'NIK (16 Digit)',
            'nama_lengkap': 'Nama Lengkap',
            'jurusan': 'Jurusan yang Dipilih',
            'no_wa': 'No WA Aktif',
            'dusun': 'Dusun',
            'rt': 'RT',
            'rw': 'RW',
            'desa_kelurahan': 'Desa/Kelurahan',
            'kecamatan': 'Kecamatan',
            'kabupaten_kota': 'Kabupaten/Kota',
        }

    def clean_nik(self):
        nik = self.cleaned_data.get('nik')
        if nik and Pendaftaran.objects.filter(nik=nik).exists():
            raise forms.ValidationError("NIK ini sudah pernah digunakan untuk mendaftar.")
        return nik
    # <<< Tambahin ini baru >>>
    def clean_nama_lengkap(self):
        nama = self.cleaned_data.get('nama_lengkap')
        if nama:
            return nama.upper()  # Otomatis jadi kapital semua
        return nama