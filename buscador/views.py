from django.shortcuts import render, redirect
from .servicos import procurar_e_filtrar_produtos, buscar_analise_ia
from .models import HistoricoBusca  # <--- IMPORTANTE: Importamos o modelo que acabamos de criar
from django.contrib.auth import authenticate, login

# --- Função para processar o login com e-mail/senha digitados ---
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User

# --- Função para processar o login com e-mail ou usuário ---
def processar_login(request):
    if request.method == 'POST':
        # Captura o valor digitado (pode ser o username ou o email)
        identificador = request.POST.get('username') or request.POST.get('email')
        senha_input = request.POST.get('password')
        
       # ... código anterior ...
        if identificador and senha_input:
            # 1. Tenta autenticar direto pelo username
            user = authenticate(request, username=identificador, password=senha_input)
            
            # 2. Se falhar e o texto tiver '@', tenta descobrir o username pelo e-mail
            if user is None and '@' in identificador:
                # Usa filter().first() para evitar o erro de múltiplos utilizadores
                user_obj = User.objects.filter(email=identificador).first()
                if user_obj:
                    user = authenticate(request, username=user_obj.username, password=senha_input)
        
        if user is not None:
# ... restante código ...
            login(request, user)
            return redirect('home') # Vai direto para a tela de ofertas!
        else:
            # Se a senha ou usuário estiverem errados, volta para o login
            return redirect('/')
            
    return redirect('/')
# --- 1. Função da Tela de Login ---
def login_view(request):
    return render(request, 'buscador/tela_de_login.html')

# --- 2. Função da Tela Principal (Busca) ---
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