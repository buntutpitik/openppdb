from django import forms
from .forms import PendaftaranForm
from .models import (
    Pendaftaran,
    PembayaranDaftarUlang,
)


class AdminPendaftaranForm(PendaftaranForm):
    """
    FORM ADMIN
    = FORM PUBLIK
    + FIELD ADMIN
    + ASAL SEKOLAH DROPDOWN + LAINNYA
    """

    ASAL_SEKOLAH_CHOICES = [
        ('MTS AT TAUHID JOGOMERTAN', 'MTS AT TAUHID JOGOMERTAN'),
        ('MTS DARUSSADAH KRITIG PETANAHAN', 'MTS DARUSSADAH KRITIG PETANAHAN'),
        ('MTS MAFATIKHUL HUDA JOGOSIMO', 'MTS MAFATIKHUL HUDA JOGOSIMO'),
        ('MTS MAMBAUL ULUM PURING', 'MTS MAMBAUL ULUM PURING'),
        ('MTS N 2 KEBUMEN', 'MTS N 2 KEBUMEN'),
        ('MTS N 5 KEBUMEN', 'MTS N 5 KEBUMEN'),
        ('MTS N 6 KEBUMEN', 'MTS N 6 KEBUMEN'),
        ('MTS ROUDLOTUL HUDA KEBADONGAN', 'MTS ROUDLOTUL HUDA KEBADONGAN'),
        ('MTS SALAFIYAH SYAFIIYAH GROGOLPENATUS', 'MTS SALAFIYAH SYAFIIYAH GROGOLPENATUS'),
        ('MTS YAPIKA TANJUNGSARI', 'MTS YAPIKA TANJUNGSARI'),
        ('SMP ISLAM DAARUT TAIBIN', 'SMP ISLAM DAARUT TAIBIN'),
        ('SMP MAARIF 3 KEBUMEN', 'SMP MAARIF 3 KEBUMEN'),
        ('SMP N 1 BULUSPESANTREN', 'SMP N 1 BULUSPESANTREN'),
        ('SMP N 1 KLIRONG', 'SMP N 1 KLIRONG'),
        ('SMP N 1 PEJAGOAN', 'SMP N 1 PEJAGOAN'),
        ('SMP N 1 PETANAHAN', 'SMP N 1 PETANAHAN'),
        ('SMP N 1 PURING', 'SMP N 1 PURING'),
        ('SMP N 1 SRUWENG', 'SMP N 1 SRUWENG'),
        ('SMP N 2 ADIMULYO', 'SMP N 2 ADIMULYO'),
        ('SMP N 2 AYAH', 'SMP N 2 AYAH'),
        ('SMP N 2 PURING', 'SMP N 2 PURING'),
        ('SMP N 4 KEBUMEN', 'SMP N 4 KEBUMEN'),
        ('SMP PGRI 1 KLIRONG', 'SMP PGRI 1 KLIRONG'),
        ('SMP PGRI 1 PURING', 'SMP PGRI 1 PURING'),
        ('SMP PGRI BULUSPESANTREN', 'SMP PGRI BULUSPESANTREN'),
        ('SMP QURANI GROGOLBENINGSARI', 'SMP QURANI GROGOLBENINGSARI'),
        ('LAINNYA', 'LAINNYA'),
    ]

    KERINGANAN_CHOICES = [
        ('yatim', 'Yatim'),
        ('yatim_piatu', 'Yatim Piatu'),
        ('anak_ke_3', 'Anak ke-3 dan seterusnya'),
        ('anak_alumni', 'Anak Alumni'),
        ('bersaudara', 'Siswa Bersaudara Tahun Ajaran Sama'),
        ('prestasi_nasional', 'Prestasi POPDA Nasional'),
        ('prestasi_provinsi', 'Prestasi POPDA Provinsi'),
        ('prestasi_kabupaten', 'Prestasi POPDA Kabupaten'),
        ('top10_negeri', '10 Besar Paralel Negeri'),
        ('top5_swasta', '5 Besar Paralel Swasta'),
        ('juara1_harlah', 'Juara 1 Harlah'),
        ('juara2_harlah', 'Juara 2 Harlah'),
    ]

    # ===== FIELD ADMIN TAMBAHAN =====
    nisn = forms.CharField(label="NISN", required=False)
    nilai_skl = forms.DecimalField(label="Nilai SKL", required=False)
    pekerjaan_ayah = forms.CharField(label="Pekerjaan Ayah", required=False)
    pekerjaan_ibu = forms.CharField(label="Pekerjaan Ibu", required=False)

    keringanan_prestasi = forms.MultipleChoiceField(
        label="Keringanan / Prestasi",
        choices=KERINGANAN_CHOICES,
        required=False,
        widget=forms.CheckboxSelectMultiple
    )

    status = forms.ChoiceField(
        label="Status Pendaftaran",
        choices=Pendaftaran.STATUS_CHOICES
    )

    class Meta:
        model = Pendaftaran
        fields = (
            list(PendaftaranForm.Meta.fields)
            + [
                'nisn',
                'nilai_skl',
                'pekerjaan_ayah',
                'pekerjaan_ibu',
                'keringanan_prestasi',
                'status',
            ]
        )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # === FIX DATE PICKER (ADMIN ONLY) ===
        if 'tanggal_lahir' in self.fields:
            self.fields['tanggal_lahir'].widget = forms.DateInput(
                attrs={
                    'type': 'date',
                    'class': 'form-control'
                }
            )

        # HAPUS ASAL SEKOLAH FORM PUBLIK
        self.fields.pop('asal_sekolah', None)

        # PASANG ULANG VERSI ADMIN
        self.fields['asal_sekolah'] = forms.ChoiceField(
            label="Asal Sekolah",
            choices=self.ASAL_SEKOLAH_CHOICES
        )
        self.fields['asal_sekolah_lainnya'] = forms.CharField(
            label="Asal Sekolah (Lainnya)",
            required=False
        )

        # DATA LAMA TETAP AMAN
        if self.instance.pk and self.instance.asal_sekolah:
            if self.instance.asal_sekolah not in dict(self.ASAL_SEKOLAH_CHOICES):
                self.initial['asal_sekolah'] = 'LAINNYA'
                self.initial['asal_sekolah_lainnya'] = self.instance.asal_sekolah

        # STYLING
        for name, field in self.fields.items():
            if isinstance(field.widget, forms.CheckboxSelectMultiple):
                field.widget.attrs.pop('class', None)
            else:
                field.widget.attrs.setdefault('class', 'form-control')

    def clean(self):
        cleaned = super().clean()

        asal = cleaned.get('asal_sekolah')
        lain = cleaned.get('asal_sekolah_lainnya')

        if asal == 'LAINNYA':
            if not lain:
                self.add_error('asal_sekolah_lainnya', 'Wajib diisi.')
            else:
                cleaned['asal_sekolah'] = lain

        return cleaned

    def save(self, commit=True):
        instance = super().save(commit=False)

        # 🔒 JANGAN TURUNKAN STATUS JIKA SUDAH DAFTAR ULANG / LUNAS
        if instance.pk:
            old = Pendaftaran.objects.get(pk=instance.pk)
            if old.status in ['daftar_ulang', 'lunas']:
                instance.status = old.status

        if commit:
            instance.save()
        return instance


class KonfirmasiDaftarUlangForm(forms.ModelForm):
    """
    FORM KONFIRMASI STATUS DAFTAR ULANG
    """
    class Meta:
        model = Pendaftaran
        fields = ['status']


class PembayaranDaftarUlangForm(forms.ModelForm):
    """
    FORM CICILAN DAFTAR ULANG
    """

    class Meta:
        model = PembayaranDaftarUlang
        fields = ['nominal', 'keterangan']
        widgets = {
            'nominal': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nominal pembayaran'
            }),
            'keterangan': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Contoh: Cicilan 1'
            }),
        }

    def clean_nominal(self):
        nominal = self.cleaned_data.get('nominal')
        if nominal is not None and nominal <= 0:
            raise forms.ValidationError("Nominal harus lebih dari 0.")
        return nominal
