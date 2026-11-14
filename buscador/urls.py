from django.urls import path
from . import views

urlpatterns = [
    path('', views.login_view, name='login'),
    path('processar-login/', views.processar_login, name='processar_login'), # <--- Esta é a linha crucial
    path('home/', views.home, name='home'),
]