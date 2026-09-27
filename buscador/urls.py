from django.contrib import admin
from django.urls import path
from buscador import views  # Importa as funções que fizemos no views.py

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # Rota raiz (página inicial) chama a tela de login
    path('', views.login, name='login'),
    
    # Rota da busca (home)
    path('home/', views.home, name='home'),
]