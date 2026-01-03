from django import forms
from .models import Pendaftaran
from django.core.exceptions import ValidationError
import re


class PendaftaranForm(forms.ModelForm):

    # ⬇️ FINAL: asal sekolah bebas (dropdown + manual di-handle HTML)
    asal_sekolah = forms.CharField(
        label="Asal Sekolah",
        max_length=200,
        widget=forms.TextInput(attrs={
            'class': 'form-control'
        })
    )

    class Meta:
        model = Pendaftaran
        fields = [
            'nik',
            'nama_lengkap',
            'tempat_lahir',
            'tanggal_lahir',
            'jenis_kelamin',
            'agama',
            'asal_sekolah',
            'dusun',
            'rt',
            'rw',
            'desa_kelurahan',
            'kecamatan',
            'kabupaten_kota',
            'nama_ayah',
            'nama_ibu',
            'no_wa',
            'jurusan',
        ]
        widgets = {
            'tanggal_lahir': forms.DateInput(attrs={'type': 'date'}),
        }

         # ⬇️ TAMBAHIN DI SINI
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name, field in self.fields.items():
            # jangan timpa asal_sekolah (sudah di-set manual)
            if name != 'asal_sekolah':
                field.widget.attrs.setdefault(
                    'class',
                    'form-control'
                )


    # ================= VALIDASI =================

    def clean_nik(self):
        nik = self.cleaned_data.get('nik')

        if not re.match(r'^\d{16}$', nik):
            raise ValidationError("NIK harus terdiri dari 16 digit angka.")

        if Pendaftaran.objects.filter(nik=nik).exists():
            raise ValidationError("NIK ini sudah terdaftar.")

        return nik

    def clean_no_wa(self):
        no_wa = self.cleaned_data.get('no_wa')

        if not no_wa.startswith('08'):
            raise ValidationError("Nomor WA harus diawali 08.")

        if len(no_wa) < 10 or len(no_wa) > 13:
            raise ValidationError("Nomor WA harus 10–13 digit.")

        return no_wa

    def clean(self):
        cleaned_data = super().clean()

        # 🔒 field otomatis (anti manipulasi)
        self.instance.status = 'terdaftar'
        self.instance.jalur = None
        self.instance.nomor_pendaftaran = None

        return cleaned_data
