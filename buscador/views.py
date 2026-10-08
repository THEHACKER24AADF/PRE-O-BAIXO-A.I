from django.shortcuts import render
from .servicos import procurar_e_filtrar_produtos, buscar_analise_ia
from .models import HistoricoBusca  # <--- IMPORTANTE: Importamos o modelo que acabamos de criar

def login(request):
    return render(request, 'buscador/homee.html')

def home(request):
    termo_busca = request.GET.get('q') 
    contexto = {}

    if termo_busca:
        produtos = procurar_e_filtrar_produtos(termo_busca)
        dica_ia = buscar_analise_ia(produtos)
        
        # --- NOVIDADE: Salvar no banco de dados ---
        # Só salvamos se realmente encontrou produtos para não encher o banco de lixo
        if produtos:
            novo_historico = HistoricoBusca(
                termo=termo_busca,
                dica_ia=dica_ia
            )
            
            # Se o usuário já estiver logado no sistema, atrelamos a busca a ele
            if request.user.is_authenticated:
                novo_historico.usuario = request.user
                
            novo_historico.save() # Confirma o salvamento no banco de dados!
        # ------------------------------------------
        
        contexto = {
            'termo_busca': termo_busca,
            'produtos': produtos,
            'dica_ia': dica_ia
        }

    return render(request, 'buscador/homee.html', contexto)