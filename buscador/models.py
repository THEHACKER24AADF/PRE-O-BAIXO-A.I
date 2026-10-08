from django.db import models
from django.contrib.auth.models import User

class HistoricoBusca(models.Model):
    # Relaciona a busca com o usuário logado (permitimos nulo por enquanto caso esteja testando sem login)
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    
    # O que o usuário digitou (ex: "Notebook")
    termo = models.CharField(max_length=255)
    
    # A recomendação completa que a Gemini gerou
    dica_ia = models.TextField()
    
    # Salva automaticamente a data e hora em que a busca foi feita
    data_busca = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Busca: {self.termo} - Data: {self.data_busca.strftime('%d/%m/%Y')}"