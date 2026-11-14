from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # Suas rotas normais
    path('', include('buscador.urls')),
    
    # As rotas prontas do django-allauth para o Google
    path('accounts/', include('allauth.urls')),
]