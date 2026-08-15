import os
from django.shortcuts import render, redirect
from google import genai
import requests
import urllib.parse

def login(request):
    if request.method == 'POST':
        # Pega o nome digitado no formulário (ou usa 'Visitante' se vier vazio)
        nome = request.POST.get('firstname', 'Visitante')
        
        # Salva o nome na "Sessão" do navegador do usuário
        request.session['nome_usuario'] = nome
        
        return redirect('home') 
        
    return render(request, 'buscador/tela_de_login.html') 

def home(request):
    resposta_ia = None
    termo_buscado = None
    erro = None
    produtos_reais = [] 
    
    # Resgata o nome salvo na sessão (Se não tiver nada, chama de Visitante)
    nome_usuario = request.session.get('nome_usuario', 'Visitante')

    if request.method == 'POST':
        termo_buscado = request.POST.get('produto', '').strip()

        if termo_buscado:
            # --- PARTE 1: MERCADO LIVRE (BLINDADO) ---
            try:
                termo_codificado = urllib.parse.quote(termo_buscado)
                url_ml = f"https://api.mercadolibre.com/sites/MLB/search?q={termo_codificado}&limit=3"
                
                headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'}
                resposta_ml = requests.get(url_ml, headers=headers)
                
                if resposta_ml.status_code == 200:
                    dados_ml = resposta_ml.json()
                    for item in dados_ml.get('results', []):
                        preco = item.get('price')
                        preco_formatado = f"R$ {preco:.2f}".replace('.', ',') if preco is not None else "Preço sob consulta"
                            
                        imagem_url = item.get('thumbnail', '')
                        if imagem_url:
                            imagem_url = imagem_url.replace('I.jpg', 'O.jpg')
                            
                        produtos_reais.append({
                            'titulo': item.get('title'),
                            'preco': preco_formatado,
                            'link': item.get('permalink'),
                            'imagem': imagem_url
                        })
            except Exception as e:
                print(f"Erro interno no ML: {e}") 

            if not produtos_reais:
                produtos_reais = [
                    {'titulo': f'{termo_buscado} - Destaque 1', 'preco': 'Ver no site', 'link': f'https://lista.mercadolivre.com.br/{termo_codificado}', 'imagem': 'https://http2.mlstatic.com/frontend-assets/ml-web-navigation/ui-navigation/5.19.1/mercadolibre/logo__large_plus.png'},
                    {'titulo': f'{termo_buscado} - Destaque 2', 'preco': 'Ver no site', 'link': f'https://lista.mercadolivre.com.br/{termo_codificado}', 'imagem': 'https://http2.mlstatic.com/frontend-assets/ml-web-navigation/ui-navigation/5.19.1/mercadolibre/logo__large_plus.png'},
                    {'titulo': f'{termo_buscado} - Destaque 3', 'preco': 'Ver no site', 'link': f'https://lista.mercadolivre.com.br/{termo_codificado}', 'imagem': 'https://http2.mlstatic.com/frontend-assets/ml-web-navigation/ui-navigation/5.19.1/mercadolibre/logo__large_plus.png'}
                ]

            # --- PARTE 2: INTELIGÊNCIA ARTIFICIAL ---
            try:
                # Pega a chave de forma segura do arquivo .env ou das variáveis de ambiente do servidor
                chave_api = os.getenv('CHAVE_API')
                client = genai.Client(api_key=chave_api)
                
                prompt = f"O usuário buscou por '{termo_buscado}'. Diga em um parágrafo rápido o que observar ao comprar isso para ter o melhor custo-benefício."

                response = client.models.generate_content(
                    model='gemini-2.5-flash', # (Nota: certifique-se de usar um modelo válido como o gemini-2.5-flash ou flash padrão)
                    contents=prompt
                )
                resposta_ia = response.text

            except Exception as e:
                erro = f"Ops! Tivemos um problema com a IA: {str(e)}"
        else:
            erro = "Por favor, digite o nome de um produto."

    # Adicionamos o nome do usuário no contexto para o HTML
    context = {
        'nome_usuario': nome_usuario, 
        'termo_buscado': termo_buscado,
        'resposta_ia': resposta_ia,
        'produtos_reais': produtos_reais, 
        'erro': erro
    }

    return render(request, 'buscador/home.html', context)