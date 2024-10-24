from django.contrib import admin
from django.urls import path

from mi_app import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path("", views.inicio, name='inicio'),  # Página principal
    path('cargar_archivo/', views.cargar_archivo, name='cargar_archivo'),
    path('peticiones/', views.peticiones, name='peticiones'),
    path('ayuda/', views.ayuda, name='ayuda'),
]