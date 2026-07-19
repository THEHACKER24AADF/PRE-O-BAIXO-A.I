from django.contrib import admin
from .models import Produto, HistoricoPreco

# Registrando as tabelas para elas aparecerem no painel
admin.site.register(Produto)
admin.site.register(HistoricoPreco)