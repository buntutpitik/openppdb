from .base import *

DEBUG = True
ALLOWED_HOSTS = []

# ======================
# AUTH / LOGIN
# ======================
LOGIN_URL = '/accounts/login/'
LOGIN_REDIRECT_URL = '/admin/dashboard/'
LOGOUT_REDIRECT_URL = '/accounts/login/'
