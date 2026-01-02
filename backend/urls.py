from django.urls import path
from django.contrib import admin
from . import views

# =====================================================
# CUSTOM ADMIN TITLE
# =====================================================
admin.site.site_header = "Admin Panel PPDB SMK Marsa"
admin.site.site_title = "PPDB SMK Marsa"
admin.site.index_title = "Dashboard Admin PPDB SMK Marsa"

# =====================================================
# URL PATTERNS
# =====================================================
urlpatterns = [

    # ======================
    # PUBLIC
    # ======================
    path('', views.home, name='home'),
    path('sukses/<int:pk>/', views.sukses, name='sukses'),

    path(
    'kartu/<str:nomor_pendaftaran>/',
    views.print_kartu,
    name='print_kartu'
    ),

    # ======================
    # BENDAHARA
    # ======================
    path(
        'bendahara/dashboard/',
        views.dashboard_bendahara,
        name='dashboard_bendahara'
    ),

    path(
        'bendahara/ubah-status/<int:pk>/',
        views.ubah_status_daftar_ulang,
        name='ubah_status_daftar_ulang'
    ),

    path(
        'bendahara/input-pembayaran/<int:pk>/',
        views.input_pembayaran,
        name='input_pembayaran'
    ),

    path(
        'bendahara/rekap-daftar-ulang/',
        views.rekap_daftar_ulang,
        name='rekap_daftar_ulang'
    ),

    path(
        'bendahara/export-excel/',
        views.export_excel_rekap,
        name='export_excel_rekap'
    ),

    # ======================
    # ADMIN (NON SUPERUSER)
    # ======================
    path(
        'admin/dashboard/',
        views.dashboard_admin,
        name='dashboard_admin'
    ),

    path(
        'admin/ubah-status/<int:pk>/',
        views.ubah_status_admin,
        name='ubah_status_admin'
    ),
]
