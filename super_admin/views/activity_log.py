from django.shortcuts import render
from backend.models import ActivityLog
from super_admin.decorators import superadmin_required


@superadmin_required
def activity_log_list(request):
    logs = ActivityLog.objects.select_related("actor").all()

    return render(
        request,
        "super_admin/activity_log_list.html",
        {
            "logs": logs
        }
    )
