from django.shortcuts import render, redirect

# A tela inicial que o usuário vê (Login)
def login(request):
    # Se o usuário clicou no botão "Vamos lá" (enviou o formulário)
    if request.method == 'POST':
        # Aqui no futuro você validaria a senha no banco de dados.
        # Para a apresentação de sexta, nós apenas redirecionamos ele para a tela de busca!
        return redirect('home')
    
    # Se ele só está abrindo a página normalmente
    return render(request, 'buscador/tela_de_login.html')

# A segunda tela (Busca)
def home(request):
    return render(request, 'buscador/homee.html')