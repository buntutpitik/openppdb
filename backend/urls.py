from django.urls import path
from django.contrib import admin

# Ubah judul admin panel
admin.site.site_header = "Admin Panel PPDB SMK Marsa"  # Header biru atas
admin.site.site_title = "PPDB SMK Marsa"               # Judul tab browser
admin.site.index_title = "Selamat Datang di Dashboard Admin PPDB SMK Marsa"  # Judul halaman utama admin
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('sukses/<int:pk>/', views.sukses, name='sukses'),
    path('kartu/<int:pk>/', views.print_kartu, name='print_kartu'),
    path('bendahara/dashboard/', views.dashboard_bendahara, name='dashboard_bendahara'),
    path('bendahara/ubah-status/<int:pk>/', views.ubah_status_daftar_ulang, name='ubah_status_daftar_ulang'),
    path('bendahara/input-pembayaran/<int:pk>/', views.input_pembayaran, name='input_pembayaran'),
    path('bendahara/rekap-daftar-ulang/', views.rekap_daftar_ulang, name='rekap_daftar_ulang'),
    path('bendahara/export-excel/', views.export_excel_rekap, name='export_excel_rekap'),
    path('admin/dashboard/', views.dashboard_admin, name='dashboard_admin'),
]