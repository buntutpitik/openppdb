from functools import wraps
from django.core.exceptions import PermissionDenied


def get_user_roles(user):
    """
    Ambil daftar role dari Django Group.
    Return list kosong kalau user belum punya group.
    """
    if not user.is_authenticated:
        return []

    return list(
        user.groups.values_list('name', flat=True)
    )


def role_required(*allowed_roles):
    """
    Decorator permission berbasis ROLE (Django Group)

    Contoh:
    @role_required('SUPERADMIN', 'ADMIN', 'PANITIA')
    """

    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):

            if not request.user.is_authenticated:
                raise PermissionDenied("User belum login")

            user_roles = get_user_roles(request.user)

            # belum punya role sama sekali
            if not user_roles:
                raise PermissionDenied(
                    "User belum memiliki role"
                )

            # cek apakah ada role yang cocok
            if not any(role in allowed_roles for role in user_roles):
                raise PermissionDenied(
                    f"Akses ditolak. Role user: {user_roles}"
                )

            return view_func(request, *args, **kwargs)

        return _wrapped_view

    return decorator


# ==================================================
# SHORTCUT DECORATOR (BIAR VIEW RAPI)
# ==================================================

def superadmin_required(view_func):
    """
    Khusus SUPERADMIN saja
    """
    return role_required('SUPERADMIN')(view_func)


def bendahara_required(view_func):
    """
    BENDAHARA (termasuk kalau dia juga PANITIA)
    """
    return role_required('BENDAHARA')(view_func)


def panitia_required(view_func):
    """
    PANITIA (atau role lain yang diizinkan)
    """
    return role_required('PANITIA')(view_func)
