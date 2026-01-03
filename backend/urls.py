from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [

    # ======================
    # AUTH
    # ======================
    path(
        'accounts/login/',
        auth_views.LoginView.as_view(
            template_name='registration/login.html'
        ),
        name='login'
    ),
    path(
        'accounts/logout/',
        auth_views.LogoutView.as_view(),
        name='logout'
    ),

    # ======================
    # PUBLIC
    # ======================
    path('', views.home, name='home'),
    path('sukses/<int:pk>/', views.sukses, name='sukses'),
    path('kartu/<str:nomor_pendaftaran>/', views.print_kartu, name='print_kartu'),

    # ======================
    # ADMIN
    # ======================
    path(
        'admin/dashboard/',
        views.dashboard_admin,
        name='dashboard_admin'
    ),
    path(
        'admin/pendaftaran/',
        views.admin_pendaftaran_list,
        name='admin_pendaftaran_list'
    ),
    path(
        'admin/pendaftaran/tambah/',
        views.admin_pendaftaran_tambah,
        name='admin_pendaftaran_tambah'
    ),
    path(
        'admin/ubah-status/<int:pk>/',
        views.ubah_status_admin,
        name='ubah_status_admin'
    ),
]
