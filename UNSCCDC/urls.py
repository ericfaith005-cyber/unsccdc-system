from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.staticfiles.urls import staticfiles_urlpatterns # ADD THIS

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('api.urls')),
]

# FORCING MEDIA AND STATIC FILES TO APPEAR
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

# THIS IS THE SECRET KEY TO MAKE CSS WORK
urlpatterns += staticfiles_urlpatterns()