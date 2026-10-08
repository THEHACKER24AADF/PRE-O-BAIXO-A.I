from django.contrib import admin
from .models import HistoricoBusca

# Registamos o nosso novo modelo para podermos vê-lo no painel de administração (Admin)
admin.site.register(HistoricoBusca)