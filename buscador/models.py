from django.db import models
from django.db import models

class Produto(models.Model):
    nome = models.CharField(max_length=255)
    categoria = models.CharField(max_length=100, blank=True)
    descricao = models.TextField(blank=True)
    criado_em = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.nome

class HistoricoPreco(models.Model):
    produto = models.ForeignKey(Produto, on_delete=models.CASCADE, related_name='precos')
    loja = models.CharField(max_length=150)
    valor = models.DecimalField(max_digits=10, decimal_places=2)
    url_produto = models.URLField(max_length=500, blank=True)
    data_consulta = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.produto.nome} - R$ {self.valor} em {self.loja}"
# Create your models here.
