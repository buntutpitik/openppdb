from django import forms
from django.core.exceptions import ValidationError
from .models import Pendaftaran
import re


class PendaftaranForm(forms.ModelForm):

    # Asal sekolah manual (bebas)
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

    # ================= INIT =================

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for name, field in self.fields.items():
            if name != 'asal_sekolah':
                field.widget.attrs.setdefault('class', 'form-control')

    # ================= VALIDASI =================

    def clean_nik(self):
        nik = self.cleaned_data.get('nik')

        if not re.match(r'^\d{16}$', nik):
            raise ValidationError("NIK harus terdiri dari 16 digit angka.")

        qs = Pendaftaran.objects.filter(nik=nik)
        if self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)

        if qs.exists():
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

        # 🔐 hanya set default saat CREATE
        if not self.instance.pk:
            self.instance.status = 'terdaftar'
            self.instance.jalur = None

        return cleaned_data
