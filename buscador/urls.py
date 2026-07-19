from django.urls import path
from . import views

urlpatterns = [
    # A página vazia '' é a primeira que abre (a tela de login)
    path('', views.login, name='login'),
    
    # A página /home é a tela de buscas
    path('home/', views.home, name='home'),
]