import os
from pathlib import Path
import dj_database_url  # 💎 THE SATELLITE PASSPORT

# 🏛️ 1. BASE DIRECTORY
# This tells the Brain exactly where its heart is located
BASE_DIR = Path(__file__).resolve().parent.parent

# 🛰️ 2. ENVIRONMENT DETECTION
# We detect if we are in the clouds (Render) or at home (Laptop)
IS_RENDER = 'RENDER' in os.environ

# 🛡️ 3. SECURITY GATE SWITCH
if IS_RENDER:
    # --- 🏰 CLOUD FORTRESS SETTINGS (RENDER) ---
    DEBUG = False
    ALLOWED_HOSTS = ['unsccdc-system.onrender.com', 'unsccdc-hub.onrender.com', '.onrender.com']
    SECURE_SSL_REDIRECT = False # 💎 CRITICAL: Let Render's proxy handle the tie
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
else:
    # --- 🏠 LOCAL LAB SETTINGS (LAPTOP) ---
    DEBUG = True
    ALLOWED_HOSTS = ['*', '172.24.144.47', 'localhost', '127.0.0.1']
    SECURE_SSL_REDIRECT = False
    SESSION_COOKIE_SECURE = False
    CSRF_COOKIE_SECURE = False
    

DATABASES = {
    'default': dj_database_url.config(
        # 💎 THE MASTER FALLBACK:
        # If DATABASE_URL is missing (on your laptop), it creates a local db.sqlite3
        default=f'sqlite:///{os.path.join(BASE_DIR, "db.sqlite3")}',
        conn_max_age=600
    )
}


SECRET_KEY = 'django-insecure-un-sccdc-sovereign-national-master-2026'


CORS_ALLOW_ALL_ORIGINS = True 
CORS_ALLOW_CREDENTIALS = True


CSRF_TRUSTED_ORIGINS = [
    "https://unsccdc-system.onrender.com",
    "https://*.onrender.com",
    "https://schoolapp-lac.vercel.app", # 💎 TRUST YOUR SPECIFIC APP
]
CORS_ALLOW_HEADERS = [
    "accept",
    "accept-encoding",
    "authorization",
    "content-type",
    "dnt",
    "origin",
    "user-agent",
    "x-csrftoken",
    "x-requested-with",
]

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

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',           # 💎 THE Hub Hub Hub Hub Hub KEY FIX (MUST BE TOP)
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            os.path.join(BASE_DIR, 'frontend'),  # 💎 #1 PRIORITY: THE MOBILE Hub
            os.path.join(BASE_DIR, 'templates'), # 💎 #2 PRIORITY: THE OFFICE
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

# 🔑 Hub IDENTITY KEYS
WSGI_APPLICATION = 'UNSCCDC.wsgi.application'
ROOT_URLCONF = 'UNSCCDC.urls' # 💎 Consolidated here
AUTH_USER_MODEL = 'api.User'
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# --- 7. INTERNATIONALIZATION (UGANDA NATIONAL STANDARD) ---
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'Africa/Kampala' # 🇺🇬 THE PEARL OF AFRICA
USE_I18N = True
USE_TZ = True


STATIC_URL = '/static/'

# Render collects all files from these rooms into the staticfiles folder
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'static'),
    os.path.join(BASE_DIR, 'frontend'), # 🛰️ Includes your Flutter assets
]

STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

# 🛡️ THE PRODUCTION SHIELD (WhiteNoise)
# This makes your system the FASTEST in the world by compressing files
STATICFILES_STORAGE = 'whitenoise.storage.CompressedStaticFilesStorage'
WHITENOISE_MANIFEST_STRICT = False # 💎 Prevents crashes if an icon is missing

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

JAZZMIN_SETTINGS = {
    # 🏛️ 1. BRANDING & TITLES
    "site_title": "UNSCCDC GLOBAL",
    "site_header": "UNSCCDC",
    "site_brand": "UNSCCDC GLOBAL",
    "welcome_sign": "Uganda National Schools Central Control Digital Centre",
    "copyright": "UNSCCDC GLOBAL 2026",
    "user_avatar": "photo", # 📸 Points to the 'photo' field in your User/Staff model

    # 🎨 2. THE Hub Hub Hub Hub Hub DESIGN (CSS & JS)
    "theme": "darkly",
    "dark_mode_theme": "darkly",
    "custom_css": "css/national_prestige.css", # 🇺🇬 The Zeraki-Style & Flag CSS
    "custom_js": "js/national_flag.js",         # 🎬 The Live Flag Script
    "show_ui_builder": False,

    # 🔗 3. THE ANIMATED TOP TABS (The "Website" Navigation)
    "topmenu_links": [
        {"name": "HOME", "url": "/api/home/", "new_window": False},
        {"name": "ABOUT", "url": "/api/about/", "new_window": False},
        {"name": "ACADEMICS", "url": "/api/academics/", "new_window": False},
        {"name": "FINANCES", "url": "/api/finances/", "new_window": False},
        {"name": "NATIONAL REGISTRY", "url": "/api/registry/", "new_window": False}, # 💎 NEW
        {"name": "NATIONAL WAR-ROOM", "url": "/admin/api/financialcommandcenter/", "new_window": False},
    ],

    # 🏛️ 4. THE Hub Hub Hub Hub Hub SIDEBAR ORDER (THE COMMAND MAP)
    "navigation_expanded": True,
    "side_menu_order": [
        "api.OperationsHub",           # 1. The 12-Tab Grid Dashboard
        "api.NationalDataBridge",      # 2. PDF Auto-Arranger
        "api.SovereignRegistry",       # 3. A-Z Class Explorer
        "api.FeesReminder",            # 4. Mass Print Reminders
        "api.SovereignParentRegistry", # 5. Linked Guardian List
        "api.Student",                 # 6. Student Files
        "api.Staff",                   # 7. Teacher Force
        "api.School",                  # 8. Institution Setup
        "api.SchoolPayLedger",         # 9. Financial Records
        "api.Subject",                 # 10. Curriculum
        "auth.User",                   # 11. System Access
    ],

    # 💎 5. THE BURSAR COMMAND LINKS
    "custom_links": {
        "api": [
            {
                "name": "Operations Dashboard", 
                "url": "/api/ops-hub/", 
                "icon": "fas fa-rocket",
                "permissions": ["auth.view_user"]
            },
            {
                "name": "Financial Analytics", 
                "url": "/admin/api/financialcommandcenter/", 
                "icon": "fas fa-chart-line"
            },
        ]
    },
    
    # 🎨 6. EVERY SINGLE ICON MAPPED & PROTECTED
    "icons": {
        "api.OperationsHub": "fas fa-th-large",
        "api.NationalDataBridge": "fas fa-file-import", 
        "api.SovereignRegistry": "fas fa-shield-alt",
        "api.FeesReminder": "fas fa-bell",
        "api.SovereignParentRegistry": "fas fa-users-cog",
        "api.Student": "fas fa-user-graduate",
        "api.Staff": "fas fa-chalkboard-teacher",
        "api.School": "fas fa-university",
        "api.Parent": "fas fa-user-shield",
        "api.SchoolPayLedger": "fas fa-money-check-alt",
        "api.FeesTracker": "fas fa-wallet",
        "api.Transaction": "fas fa-file-invoice-dollar",
        "api.Subject": "fas fa-book",
        "api.SchoolPost": "fas fa-broadcast-tower",
        "api.NationalTopPerformer": "fas fa-trophy",
        "api.BioAndCareer": "fas fa-user-tie",
        "api.SystemSettings": "fas fa-cogs",
        "auth.User": "fas fa-user-lock",
        "auth.Group": "fas fa-users",
    },
    
    # 🕵️ 7. GLOBAL SETTINGS
    "show_sidebar": True,
    "navigation_expanded": True,
    "change_list_template": "admin/class_explorer.html", # Optional override
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

# 🛡️ THE Hub Hub Hub Hub Hub REDIRECT SHIELD
# Prevents Django from redirecting and losing your PIN/Login data
APPEND_SLASH = False


if IS_RENDER:
    DEBUG = False # 💎 Set to False for Production Security
    ALLOWED_HOSTS = ['unsccdc-system.onrender.com', 'unsccdc-hub.onrender.com', '.onrender.com']
    
    # 🛰️ Render-to-App Handshake
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
    SECURE_SSL_REDIRECT = True # Force HTTPS for National Trust
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
else:
    DEBUG = True
    ALLOWED_HOSTS = ['*', '172.24.144.47', 'localhost', '127.0.0.1']
    SECURE_SSL_REDIRECT = False