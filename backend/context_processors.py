def user_roles(request):
    """
    Kirim daftar role user (Django Group) ke semua template
    """
    if not request.user.is_authenticated:
        return {}

    return {
        "user_roles": list(
            request.user.groups.values_list("name", flat=True)
        )
    }
