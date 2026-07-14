from django.contrib import admin
from django.urls import path, include
from django.views.generic import TemplateView, RedirectView
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from api import views # 💎 Uses the module directly to avoid naming ghosts

urlpatterns = [
    path('', views.national_landing_page, name='app_root'),
    # 🏛️ 1. THE Hub Hub Hub Hub Hub Hub Hub FRONT DOOR (PWA / App Entry)
    # This is what people see at the main link
    path('', TemplateView.as_view(template_name="index.html"), name='app'),

    # 🏛️ 2. THE Hub Hub Hub Hub Hub Hub Hub MASTER OFFICE (Admin)
    path('admin/', admin.site.urls),

    # 🏛️ 3. THE Hub Hub Hub Hub Hub Hub Hub NATIONAL REGISTRY (API)
    path('api/', include('api.urls')),

    # 🔐 4. THE Hub Hub Hub Hub Hub Hub Hub STAFF PORTAL
    # 💎 THE Hub Hub Hub Hub Hub Hub Hub KEY FIX:
    # Changed 'staff_hub_login' to 'staff_hub_auth' to match your views.py!
    path('staff-login/', views.staff_hub_auth, name='staff_login'),

    # 📱 5. THE Hub Hub Hub Hub Hub Hub Hub PWA NATIONAL SATELLITE ASSETS
    path('serviceworker.js', TemplateView.as_view(
        template_name='serviceworker.js', 
        content_type='application/javascript'
    ), name='serviceworker.js'),

    path('manifest.json', TemplateView.as_view(
        template_name="manifest.json", 
        content_type='application/json'
    ), name='manifest.json'),

    # 🛰️ Redirection Shields for Icons
    path('flutter_service_worker.js', RedirectView.as_view(url='/static/flutter_service_worker.js')),
    path('icons/Icon-192.png', RedirectView.as_view(url='/static/icons/Icon-192.png')),
    path('icons/Icon-512.png', RedirectView.as_view(url='/static/icons/Icon-512.png')),
    path('favicon.png', RedirectView.as_view(url='/static/favicon.png')),
]

# 🖼️ FORCING MEDIA AND STATIC FILES TO APPEAR
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
urlpatterns += staticfiles_urlpatterns()