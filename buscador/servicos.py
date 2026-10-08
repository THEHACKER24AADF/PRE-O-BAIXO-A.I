import requests
from google import genai
from django.conf import settings

# 1. Função do Mercado Livre Atualizada (Com correção de links do Plano B)
def procurar_e_filtrar_produtos(termo_busca):
    url = f"https://api.mercadolibre.com/sites/MLB/search?q={termo_busca}"
    
    # Cabeçalho simplificado (às vezes menos é mais para passar no filtro do ML)
    headers = {
        'Accept': 'application/json'
    }
    
    try:
        # Aumentámos um pouco o timeout para o caso da API estar lenta
        resposta = requests.get(url, headers=headers, timeout=10)
        resposta.raise_for_status() 
        
        dados_brutos = resposta.json()
        produtos_enxutos = []
        
        # O Mercado Livre costuma colocar os resultados dentro da chave 'results'
        resultados = dados_brutos.get('results', [])
        
        if not resultados:
            raise ValueError("Nenhum produto encontrado pela API.")

        for item in resultados[:3]:
            # Extrair a imagem
            imagem_url = item.get('thumbnail', '')
            if imagem_url:
                imagem_url = imagem_url.replace("I.jpg", "O.jpg")
                
            # Extrair o link real do produto (permalink)
            link_produto = item.get('permalink', 'https://www.mercadolivre.com.br')
                
            produtos_enxutos.append({
                'titulo': item.get('title', 'Produto sem título'),
                'preco': item.get('price', 0),
                'link': link_produto, # Link real do produto
                'imagem': imagem_url 
            })
            
        return produtos_enxutos
        
    except Exception as e:
        print(f"ERRO MERCADO LIVRE (Usando dados simulados): {e}") 
        
        # --- PLANO B: MOCK DATA (DADOS SIMULADOS) ---
        # Links dinâmicos: agora levam o usuário para a página de busca do produto no ML
        link_busca_ml = f'https://lista.mercadolivre.com.br/{termo_busca.replace(" ", "-")}'
        
        return [
            {
                'titulo': f'{termo_busca} - Oferta Verificada',
                'preco': 1599.90,
                'link': link_busca_ml, 
                'imagem': 'https://http2.mlstatic.com/D_NQ_NP_2X_798426-MLA46303251543_062021-F.webp'
            },
            {
                'titulo': f'{termo_busca} - Melhor Custo-Benefício',
                'preco': 1250.00,
                'link': link_busca_ml,
                'imagem': 'https://http2.mlstatic.com/D_NQ_NP_2X_798426-MLA46303251543_062021-F.webp'
            },
            {
                'titulo': f'{termo_busca} - Mais Vendido',
                'preco': 1800.50,
                'link': link_busca_ml,
                'imagem': 'https://http2.mlstatic.com/D_NQ_NP_2X_798426-MLA46303251543_062021-F.webp'
            }
        ]

# 2. Função da IA da Gemini
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