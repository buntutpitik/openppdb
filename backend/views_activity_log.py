from django.shortcuts import render
from backend.models import ActivityLog
from backend.decorators import superadmin_required


@superadmin_required
def activity_log_list(request):
    """
    List log audit global (SUPERADMIN only).
    Read-only.
    """

    logs = (
        ActivityLog.objects
        .select_related("actor")
        .all()[:500]
    )

    return render(
        request,
        "admin/activity_log_list.html",
        {
            "logs": logs,
        }
    )
