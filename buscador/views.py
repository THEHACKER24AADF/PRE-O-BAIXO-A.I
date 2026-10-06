from django.shortcuts import render
from .servicos import procurar_e_filtrar_produtos, buscar_analise_ia

# 1. A função de login que estava a faltar
def login(request):
    # Alterámos para o nome exato que você usou
    return render(request, 'buscador/homee.html')

# 2. A função da home que já tínhamos feito
def home(request):
    termo_busca = request.GET.get('q') 
    contexto = {}

    if termo_busca:
        produtos = procurar_e_filtrar_produtos(termo_busca)
        dica_ia = buscar_analise_ia(produtos)
        
        contexto = {
            'termo_busca': termo_busca,
            'produtos': produtos,
            'dica_ia': dica_ia
        }

    return render(request, 'buscador/homee.html', contexto)