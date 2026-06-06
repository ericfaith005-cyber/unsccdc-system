import os
from pathlib import Path

# --- 1. BASE DIRECTORY ---
BASE_DIR = Path(__file__).resolve().parent.parent

# --- 2. SECURITY CONFIGURATION ---
SECRET_KEY = 'django-insecure-un-sccdc-sovereign-national-master-2026'
DEBUG = True

# --- ⚠️ UPDATED ALLOWED HOSTS (NEW NATIONAL IP) ---
ALLOWED_HOSTS = ['*', '127.0.0.1', 'localhost', '10.122.38.47']

# --- 3. APPLICATION DEFINITION ---
INSTALLED_APPS = [
    'jazzmin',  # MUST BE AT THE TOP FOR THE GALAXY DESIGN
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    
    # POWER TOOLS FOR NATIONAL INFRASTRUCTURE
    'rest_framework',
    'corsheaders',  # THE KEY TO FIXING "OFFLINE" ERRORS
    'api',          # THE SOVEREIGN CORE APP
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',  # MUST BE AT THE VERY TOP FOR UPLINK
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# --- 4. CORS OVERDRIVE (NATIONAL OPEN ACCESS) ---
CORS_ALLOW_ALL_ORIGINS = True
CORS_ALLOW_CREDENTIALS = True

ROOT_URLCONF = 'UNSCCDC.urls'

# --- 5. TEMPLATES (LINKING THE FUTURE VIEW) ---
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')], # LINK TO THE GALAXY STARS HTML
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'UNSCCDC.wsgi.application'

# --- 6. DATABASE (NATIONAL LEDGER) ---
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

AUTH_USER_MODEL = 'api.User'

# --- 7. INTERNATIONALIZATION (UGANDA STANDARD) ---
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'Africa/Kampala' # THE PEARL OF AFRICA
USE_I18N = True
USE_TZ = True

# --- 8. STATIC & MEDIA (NATIONAL ASSETS HUB) ---
STATIC_URL = '/static/'
STATICFILES_DIRS = [os.path.join(BASE_DIR, 'api/static')]
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# --- 9. JAZZMIN PRESTIGE DASHBOARD (ALL ICONS PRESERVED) ---
JAZZMIN_SETTINGS = {
    "site_title": "UNSCCDC NATIONAL HUB",
    "site_header": "UNSCCDC HUB",
    "site_brand": "NATIONAL HUB",
    "welcome_sign": "AUTHENTICATING NATIONAL SOVEREIGN ACCESS",
    "copyright": "UNSCCDC Global Ltd",
    "search_model": ["api.Student", "api.Staff"],
    "show_sidebar": True,
    "navigation_expanded": True,
    
    # FUTURE DESIGN OVERRIDE (Moving Kinetic Grid)
    "custom_css": "css/sovereign.css", 
    "custom_js": None,
    
    # --- 💎 EVERY SINGLE ICON MAPPED & PROTECTED 💎 ---
    "icons": {
        "auth": "fas fa-users-cog",
        "auth.user": "fas fa-user",
        "api.AcademicResultsCenter": "fas fa-medal",      # THE MASTER HUB
        "api.AcademicResult": "fas fa-edit",               # MARKS ENTRY
        "api.Student": "fas fa-user-graduate",             # STUDENTS
        "api.Staff": "fas fa-chalkboard-teacher",          # STAFF
        "api.School": "fas fa-university",                 # SCHOOLS
        "api.Parent": "fas fa-user-shield",                # PARENTS
        "api.FeesTracker": "fas fa-wallet",                # FEES
        "api.Transaction": "fas fa-file-invoice-dollar",   # BURSAR LEDGER
        "api.Subject": "fas fa-book",                      # SUBJECTS
        "api.SchoolPost": "fas fa-broadcast-tower",        # SOCIAL HUB
        "api.NationalTopPerformer": "fas fa-trophy",       # 3D SLIDERS
        "api.BioAndCareer": "fas fa-user-tie",             # CAREER HUB
        "api.SovereignProfessionalInsights": "fas fa-chart-bar", # PRO ANALYTICS
    },
    
    # SIDEBAR PRIORITY ORDER
    "order_with_respect_to": [
        "api.AcademicResultsCenter", 
        "api.AcademicResult",
        "api.Student", 
        "api.Staff", 
        "api.School", 
        "api.Transaction",
        "api.Parent", 
        "api.FeesTracker"
    ],
}

# --- 10. JAZZMIN UI TWEAKS (DARK SOVEREIGN GOLD) ---
JAZZMIN_UI_TWEAKS = {
    "navbar_small_text": False,
    "footer_small_text": False,
    "body_small_text": False,
    "brand_small_text": False,
    "brand_colour": "navbar-dark",
    "accent": "accent-warning",
    "navbar": "navbar-dark",
    "no_navbar_border": True,
    "navbar_fixed": True,
    "layout_boxed": False,
    "footer_fixed": False,
    "sidebar_fixed": True,
    "sidebar": "sidebar-dark-warning", # GOLD SIDEBAR
    "sidebar_nav_small_text": False,
    "sidebar_disable_expand": False,
    "sidebar_nav_child_indent": True,
    "sidebar_nav_compact_style": False,
    "sidebar_nav_legacy_style": False,
    "sidebar_nav_flat_style": False,
    "theme": "darkly",
    "dark_mode_theme": "darkly",
}