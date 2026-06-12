import dj_database_url  # 💎 THE MISSING PASSPORT
import os
from pathlib import Path
import dj_database_url

BASE_DIR = Path(__file__).resolve().parent.parent

DATABASES = {
    'default': dj_database_url.config(
        # 💎 THE MASTER FALLBACK:
        # If DATABASE_URL is missing (on your laptop), it uses local SQLite
        default=f'sqlite:///{os.path.join(BASE_DIR, "db.sqlite3")}',
        conn_max_age=600
    )
}

SECRET_KEY = 'django-insecure-un-sccdc-sovereign-national-master-2026'
DEBUG = False

ALLOWED_HOSTS = ['unsccdc-system.onrender.com', 'localhost', '127.0.0.1', 'unsccdc-hub.onrender.com', '10.220.66.47',
    '.onrender.com',]
# --- 3. APPLICATION DEFINITION ---
INSTALLED_APPS = [
    'corsheaders',
    'jazzmin',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'api',          # THE SOVEREIGN CORE APP
]

# --- 🏛️ 1. MIDDLEWARE: THE ABSOLUTE ORDER OF POWER ---
MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',  # 💎 MUST BE LINE 1
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.middleware.gzip.GZipMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

CORS_ALLOW_ALL_ORIGINS = True 
CORS_ALLOW_CREDENTIALS = True

# 💎 THE TRUSTED ORIGINS (Replace with your exact GitHub link)
CSRF_TRUSTED_ORIGINS = [
    "https://unsccdc-system.onrender.com",
    "https://schoolsapp-seven.vercel.app/",
    "https://*.vercel.app",
    "https://schoolsapp-iota.vercel.app/",
    "https://ericfaith005-cyber.github.io",
]

CORS_ALLOW_HEADERS = [
    "accept", "accept-encoding", "authorization", "content-type",
    "dnt", "origin", "user-agent", "x-csrftoken", "x-requested-with",
]

ROOT_URLCONF = 'UNSCCDC.urls'

# --- 5. TEMPLATES (LINKING THE FUTURE VIEW) ---
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            os.path.join(BASE_DIR, 'frontend'), # 💎 #1 PRIORITY (THE APP)
            os.path.join(BASE_DIR, 'templates'), # 💎 #2 PRIORITY (THE SOFTWARE)
        ],
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

AUTH_USER_MODEL = 'api.User'

# --- 7. INTERNATIONALIZATION (UGANDA STANDARD) ---
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'Africa/Kampala' # THE PEARL OF AFRICA
USE_I18N = True
USE_TZ = True

# --- 8. STATIC & MEDIA (NATIONAL ASSETS HUB) ---
STATIC_URL = '/static/'
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'static'),
    os.path.join(BASE_DIR, 'frontend'),]
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATICFILES_STORAGE = 'whitenoise.storage.CompressedStaticFilesStorage'
ROOT_URLCONF = 'UNSCCDC.urls'
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

WHITENOISE_MANIFEST_STRICT = False

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
# =============================================================
# 🏛️ THE IMPERIAL COMMAND CENTER BRANDING (settings.py)
# =============================================================

JAZZMIN_SETTINGS = {
    "site_title": "UNSCCDC GLOBAL",
    "site_header": "UNSCCDC",
    "site_brand": "UNSCCDC",
    "welcome_sign": "Uganda National Schools Central Control Digital Centre",
    "copyright": "UNSCCDC GLOBAL Hub 2026",
    "custom_css": "css/unsccdc_prestige.css",
    "custom_js": None,
    
    "theme": "darkly",
    "site_brand": "UNSCCDC",
    
    # 🔗 THE ANIMATED TOP TABS (The "Website" inside the System)
    "topmenu_links": [
        {"name": "1. HOME", "url": "/api/home/", "new_window": False},
        {"name": "2. ABOUT", "url": "/api/about/", "new_window": False},
        {"name": "3. ACADEMICS", "url": "/api/academics/", "new_window": False},
        {"name": "4. FINANCES", "url": "/api/finances/", "new_window": False},
        {"name": "5. PROFILE", "url": "/api/profile/", "new_window": False},
        {"name": "DASHBOARD", "url": "admin:index"}, # Back to standard view
    ],

    "theme": "darkly",
    "show_ui_builder": False,


    # 🛠️ SIDEBAR SETTINGS
    "navigation_expanded": True,
    "hide_apps": [],
    "hide_models": [],
    "icons": {
        "api.Student": "fas fa-user-graduate",
        "api.School": "fas fa-university",
        "api.Staff": "fas fa-chalkboard-teacher",
        "api.SchoolPayLedger": "fas fa-money-check-alt",
        "api.FinancialCommandCenter": "fas fa-chart-line",
    },

    # 🎨 THE DESIGN (DIAMOND OBSIDIAN)
    "theme": "darkly", # Deep Black Theme
    "dark_mode_theme": "darkly",

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

JAZZMIN_UI_TWEAKS = {
    "navbar_small_text": False,
    "footer_small_text": True,
    "body_small_text": False,
    "brand_small_text": False,
    "brand_colour": "navbar-warning", # Golden Brand
    "accent": "accent-warning",       # Golden Accents
    "navbar": "navbar-dark",
    "no_navbar_border": False,
    "navbar_fixed": True,
    "layout_boxed": False,
    "footer_fixed": False,
    "sidebar_fixed": True,
    "sidebar": "sidebar-dark-warning", # Golden Sidebar highlights
    "sidebar_nav_small_text": False,
    "sidebar_disable_expand": False,
    "sidebar_nav_child_indent": True,
    "sidebar_nav_compact_style": False,
    "sidebar_nav_legacy_style": False,
    "sidebar_nav_flat_style": False,
    "theme": "darkly",
    "use_google_fonts": True,
    "show_sidebar": True,
    "navigation_expanded": True,
    "changeform_format": "horizontal_tabs",
    "dark_mode_theme": "darkly",
    "button_classes": {
        "primary": "btn-outline-warning", # Golden buttons
        "secondary": "btn-secondary",
        "info": "btn-info",
        "warning": "btn-warning",
        "danger": "btn-danger",
        "success": "btn-success"
    }
}
# --- 🛡️ THE SOVEREIGN SECURITY SHIELD ---
SECURE_SSL_REDIRECT = True # Forces all connections to be HTTPS
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
