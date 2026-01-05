from backend.models import ActivityLog


def log_global_activity(
    *,
    actor,
    action,
    target="",
    note="",
    request=None,
):
    """
    Helper untuk mencatat ActivityLog (audit global).
    Wajib dipakai untuk semua log SUPERADMIN.
    """

    ip_address = None
    if request:
        x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
        if x_forwarded_for:
            ip_address = x_forwarded_for.split(",")[0]
        else:
            ip_address = request.META.get("REMOTE_ADDR")

    ActivityLog.objects.create(
        actor=actor if actor.is_authenticated else None,
        action=action,
        target=target,
        note=note,
        ip_address=ip_address,
    )
