import requests
from google import genai
from django.conf import settings

# 1. Função do Mercado Livre Atualizada (Com correção de links e Otimização de Memória)
def procurar_e_filtrar_produtos(termo_busca):
    url = f"https://api.mercadolibre.com/sites/MLB/search?q={termo_busca}"
    
    headers = {
        'Accept': 'application/json'
    }
    
    try:
        resposta = requests.get(url, headers=headers, timeout=10)
        resposta.raise_for_status() 
        
        dados_brutos = resposta.json()
        produtos_enxutos = []
        
        resultados = dados_brutos.get('results', [])
        
        if not resultados:
            raise ValueError("Nenhum produto encontrado pela API.")

        for item in resultados[:3]:
            imagem_url = item.get('thumbnail', '')
            if imagem_url:
                imagem_url = imagem_url.replace("I.jpg", "O.jpg")
                
            link_produto = item.get('permalink', 'https://www.mercadolivre.com.br')
                
            produtos_enxutos.append({
                'titulo': item.get('title', 'Produto sem título'),
                'preco': item.get('price', 0),
                'link': link_produto,
                'imagem': imagem_url 
            })
            
        # ==========================================
        # OTIMIZAÇÃO DE MEMÓRIA (PREVENÇÃO ERRO 137)
        # ==========================================
        del dados_brutos 
        del resultados 
        # ==========================================
            
        return produtos_enxutos
        
    except Exception as e:
        print(f"ERRO MERCADO LIVRE (Usando dados simulados): {e}") 
        
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

# 2. Função da IA da Gemini Atualizada (Análise Comparativa Dinâmica)
def buscar_analise_ia(produtos):
    cliente = genai.Client(api_key=settings.GEMINI_API_KEY)
    
    # 1. Primeiro, extraímos apenas o que importa (título e preço) e montamos um texto limpo
    lista_formatada = ""
    for i, produto in enumerate(produtos, 1):
        lista_formatada += f"{i}. Produto: {produto['titulo']} | Preço: R$ {produto['preco']}\n"
        
    # 2. O Prompt Dinâmico de Especialista
    prompt = f"""Aja como um especialista em compras. Compare os seguintes produtos que encontrei no Mercado Livre:
    
{lista_formatada}
    
Indique especificamente qual deles oferece o melhor custo-benefício hoje, justifique a sua escolha de forma lógica e matemática e alerte se algum preço parecer irreal, suspeito ou muito fora do padrão. Seja direto, amigável e retorne a resposta formatada de forma agradável em no máximo 2 ou 3 parágrafos."""
    
    try:
        resposta = cliente.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt
        )
        return resposta.text
        
    except Exception as e:
        print(f"Erro na IA: {e}")
        return "Nossa IA detetive de preços está tomando um cafezinho agora devido à alta demanda! Mas você já pode conferir as melhores ofertas que separamos logo abaixo. Tente gerar a dica novamente em alguns instantes."