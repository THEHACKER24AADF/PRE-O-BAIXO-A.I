import requests
from google import genai
from django.conf import settings

# 1. Função que liga ao Mercado Livre
import requests

def procurar_e_filtrar_produtos(termo_busca):
    url = f"https://api.mercadolibre.com/sites/MLB/search?q={termo_busca}"
    
    # O nosso disfarce: fingimos ser o Google Chrome
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }
    
    try:
        # Adicionamos os headers aqui no requests.get
        resposta = requests.get(url, headers=headers)
        resposta.raise_for_status() 
        
        dados_brutos = resposta.json()
        produtos_enxutos = []
        
        for item in dados_brutos.get('results', [])[:3]:
            imagem_url = item.get('thumbnail', '')
            if imagem_url:
                imagem_url = imagem_url.replace("I.jpg", "O.jpg")
                
            produtos_enxutos.append({
                'titulo': item.get('title', 'Produto sem título'),
                'preco': item.get('price', 0),
                'link': item.get('permalink', '#'), 
                'imagem': imagem_url 
            })
            
        del dados_brutos 
        return produtos_enxutos
        
    except Exception as e:
        print(f"ERRO MERCADO LIVRE: {e}") 
        return []

# 2. Função que liga à Gemini (IA)
def buscar_analise_ia(produtos):
    cliente = genai.Client(api_key=settings.GEMINI_API_KEY)
    prompt = f"Analise estes produtos: {produtos}. Diga qual é o melhor custo-benefício."
    
    try:
        resposta = cliente.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt
        )
        return resposta.text
        
    except Exception as e:
        print(f"Erro na IA: {e}")
        return "Nossa IA detetive de preços está tomando um cafezinho agora devido à alta demanda! Mas você já pode conferir as melhores ofertas que separamos logo abaixo. Tente gerar a dica novamente em alguns instantes."