from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static  # Correction ici
from django.urls import path, include
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('Prosfera_App.urls')),
]

# Ajout du support des fichiers médias et statiques
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
urlpatterns += staticfiles_urlpatterns()
