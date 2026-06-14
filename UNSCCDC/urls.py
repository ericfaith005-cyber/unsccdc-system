from django.contrib import admin
from django.urls import path, include
from api.views import home_tab # 💎 Import the Enterprise Tab
from django.views.generic import TemplateView, RedirectView
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.staticfiles.urls import staticfiles_urlpatterns # ADD THIS
from django.views.generic import RedirectView
from django.shortcuts import redirect
from api import views

def root_redirect(request):
    return redirect('/admin/')

urlpatterns = [
    path('', TemplateView.as_view(template_name="index.html"), name='app'),
    path('', views.parent_verify_view, name='parent_login'),
    path('', home_tab, name='software_home'),
    path('', root_redirect),
    path('', RedirectView.as_view(url='admin/')),
    path('admin/', admin.site.urls),
    path('api/', include('api.urls')),
    path('staff-login/', views.staff_hub_login, name='staff_login'),
    path('', TemplateView.as_view(template_name="index.html"), name='app_front_door'),
    path('manifest.json', TemplateView.as_view(
        template_name='manifest.json', 
        content_type='application/json'
    ), name='manifest.json'),
    path('manifest.json', RedirectView.as_view(url='/static/manifest.json')),
    path('flutter_service_worker.js', RedirectView.as_view(url='/static/flutter_service_worker.js')),
    path('icons/Icon-192.png', RedirectView.as_view(url='/static/icons/Icon-192.png')),
    path('icons/Icon-512.png', RedirectView.as_view(url='/static/icons/Icon-512.png')),
    path('favicon.png', RedirectView.as_view(url='/static/favicon.png')),
    path('staff-login/', include('api.urls')), # Link to staff views
    
    path('serviceworker.js', TemplateView.as_view(
        template_name='serviceworker.js', 
        content_type='application/javascript'
    ), name='serviceworker.js'),
]

# FORCING MEDIA AND STATIC FILES TO APPEAR
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

# THIS IS THE SECRET KEY TO MAKE CSS WORK
urlpatterns += staticfiles_urlpatterns()