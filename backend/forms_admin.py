from django import forms
from django.contrib.auth.models import User, Group

from .forms import PendaftaranForm
from .models import (
    Pendaftaran,
    PembayaranDaftarUlang,
)


# =====================================================
# FORM ADMIN PENDAFTARAN
# =====================================================
class AdminPendaftaranForm(PendaftaranForm):
    """
    FORM ADMIN
    = FORM PUBLIK
    + FIELD ADMIN
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
    ]

    nisn = forms.CharField(label="NISN", required=False)
    nilai_skl = forms.DecimalField(label="Nilai SKL", required=False)

    keringanan_prestasi = forms.MultipleChoiceField(
        choices=KERINGANAN_CHOICES,
        required=False,
        widget=forms.CheckboxSelectMultiple
    )

    status = forms.ChoiceField(
        choices=Pendaftaran.STATUS_CHOICES
    )

    class Meta:
        model = Pendaftaran
        fields = list(PendaftaranForm.Meta.fields) + [
            'nisn',
            'nilai_skl',
            'keringanan_prestasi',
            'status',
        ]


# =====================================================
# FORM KONFIRMASI DAFTAR ULANG
# =====================================================
class KonfirmasiDaftarUlangForm(forms.ModelForm):
    class Meta:
        model = Pendaftaran
        fields = ['status']


# =====================================================
# FORM PEMBAYARAN DAFTAR ULANG
# =====================================================
class PembayaranDaftarUlangForm(forms.ModelForm):
    class Meta:
        model = PembayaranDaftarUlang
        fields = ['nominal', 'keterangan']


# =====================================================
# ✅ FORM CREATE USER (SUPERADMIN)
# =====================================================
ROLE_NAMES = [
    "SUPERADMIN",
    "ADMIN",
    "PANITIA",
    "BENDAHARA",
]


class UserCreateForm(forms.Form):
    username = forms.CharField(
        label="Username",
        max_length=150
    )

    password = forms.CharField(
        label="Password Awal",
        widget=forms.PasswordInput
    )

    roles = forms.ModelMultipleChoiceField(
        label="Role",
        queryset=Group.objects.filter(name__in=ROLE_NAMES),
        widget=forms.CheckboxSelectMultiple
    )

    is_active = forms.BooleanField(
        label="Aktifkan User",
        required=False,
        initial=True
    )

    def clean_username(self):
        username = self.cleaned_data["username"]
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError(
                "Username sudah digunakan"
            )
        return username
