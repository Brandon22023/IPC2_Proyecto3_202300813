from django.contrib import admin
from django.urls import path
from django.conf.urls.static import static
from mi_app import views
from django.conf import settings
urlpatterns = [
    path('admin/', admin.site.urls),
    path("", views.inicio, name='inicio'),  # Página principal
    path('cargar_archivo/', views.cargar_archivo, name='cargar_archivo'),
    path('peticiones/', views.peticiones, name='peticiones'),
    path('ayuda/', views.ayuda, name='ayuda'),
]

# Agregar esta línea para servir archivos de medios
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)