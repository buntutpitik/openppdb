from django.urls import path
from super_admin.views.activity_log import activity_log_list
from super_admin.views.dashboard import dashboard
from super_admin.views.user_list import (
    user_list,
    toggle_user_active,
)
from super_admin.views.user_create import user_create
from super_admin.views.user_role_update import update_user_role

app_name = "superadmin"

urlpatterns = [
    # ======================
    # DASHBOARD
    # ======================
    path(
        "dashboard/",
        dashboard,
        name="dashboard"
    ),

    # ======================
    # USER MANAGEMENT
    # ======================
    path(
        "users/",
        user_list,
        name="user_list"
    ),

    path(
        "users/<int:user_id>/role/",
        update_user_role,
        name="update_user_role"
    ),

    path(
        "users/<int:user_id>/toggle-active/",
        toggle_user_active,
        name="toggle_user_active"
    ),

    path(
        "users/create/",
        user_create,
        name="user_create"
    ),

     path(
        "activity-log/",
        activity_log_list,
        name="activity_log"
    ),

]
