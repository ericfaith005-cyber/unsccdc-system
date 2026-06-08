from django.contrib import admin
from django.urls import path, include
from api.views import home_tab # 💎 Import the Enterprise Tab
from django.views.generic import TemplateView
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.staticfiles.urls import staticfiles_urlpatterns # ADD THIS
from django.views.generic import RedirectView
from django.shortcuts import redirect

def root_redirect(request):
    return redirect('/admin/')

urlpatterns = [
    path('', home_tab, name='software_home'),
    path('', root_redirect),
    path('', RedirectView.as_view(url='admin/')),
    path('admin/', admin.site.urls),
    path('api/', include('api.urls')),
    path('', TemplateView.as_view(template_name="index.html"), name='app_front_door'),
]

# FORCING MEDIA AND STATIC FILES TO APPEAR
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

# THIS IS THE SECRET KEY TO MAKE CSS WORK
urlpatterns += staticfiles_urlpatterns()